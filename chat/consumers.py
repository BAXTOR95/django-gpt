import json
import uuid
import logging
import re
from pathlib import Path

from django.utils import timezone
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from asgiref.sync import async_to_sync
from django.template.loader import render_to_string
from .models import Chat, Message
from accounts.models import UserProfile
from openai import AsyncOpenAI
from chat.templatetags.chat_filters import markdown_to_html
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)


def read_prompt(filename):
    return Path(f'./chat/prompts/{filename}.txt').read_text()


def _batch_messages(messages, n):
    """Yield successive n-sized batches from list of messages."""
    for i in range(0, len(messages), n):
        yield messages[i : i + n]


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.chat_id = self.scope['url_route']['kwargs']['chat_id']
        self.user = self.scope['user']
        logger.info(
            f"WebSocket connect attempt for chat {self.chat_id} by user {self.user}"
        )
        self.chat = await self.get_chat(self.chat_id)

        if not self.chat:
            logger.warning(f"Chat {self.chat_id} not found for user {self.user}")
            await self.close()
            return

        self.user_profile = await self.get_user_profile()

        if self.chat and self.user_profile:
            self.messages = await self.load_chat_history()
            await self.channel_layer.group_add(
                f"chat_{self.chat_id}", self.channel_name
            )
            await self.accept()
        else:
            await self.close()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            f"chat_{self.chat_id}", self.channel_name
        )

    @retry(
        stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def get_ai_response(self, client, model, messages):
        try:
            return await client.chat.completions.create(
                model=model,
                messages=messages,
                stream=True,
                stream_options={"include_usage": True},
            )
        except Exception as e:
            logger.error(f"Error getting AI response: {str(e)}")
            raise

    async def receive(self, text_data):
        logger.info(f"Received WebSocket message: {text_data}")
        try:
            if not self.user_profile.openai_api_key:
                await self.send_error_message(
                    "OpenAI API key is missing. Please add it in your profile settings."
                )
                return

            text_data_json = json.loads(text_data)
            message_text = text_data_json['message']
            logger.info(f"Parsed message: {message_text}")

            # Render and send user message
            user_message_html = render_to_string(
                'ws/chat_message.html',
                {
                    'message_text': message_text,
                    'is_system': False,
                    'user': self.user,
                    'message': {'timestamp': timezone.now()},
                },
            )
            await self.send(text_data=user_message_html)

            # Save user message
            await self.save_message(message_text, True)

            # Add the new user message to the history
            self.messages.append({"role": "user", "content": message_text})

            # If this is the first message, generate a title
            if len(self.messages) == 1:
                await self.generate_chat_title(message_text)

            # Create empty AI message
            message_id = f"message-{uuid.uuid4().hex}"
            empty_ai_message_html = render_to_string(
                'ws/chat_message.html',
                {
                    'message_text': '',
                    'is_system': True,
                    'message_id': message_id,
                    'user': self.user,
                    'message': {'timestamp': timezone.now()},
                },
            )
            await self.send(text_data=empty_ai_message_html)

            # Get AI response
            client = AsyncOpenAI(api_key=self.user_profile.openai_api_key)
            model = await self.get_model_name()

            if not model:
                raise self.send_error_message("No LLM model specified")

            logger.debug(
                f"""CONFIG:
            Model: {model}
            User: {self.user}
            Chat ID: {self.chat_id}
            Message: {message_text}
            """
            )

            MAX_CONTEXT_MESSAGES = 20  # Adjust as needed
            batched_messages = list(
                _batch_messages(
                    self.messages[-MAX_CONTEXT_MESSAGES:], MAX_CONTEXT_MESSAGES
                )
            )

            try:
                openai_response = await self.get_ai_response(
                    client, model, batched_messages[-1]
                )

                ai_message_content = []
                async for chunk in openai_response:
                    if chunk.choices:
                        message_chunk = chunk.choices[0].delta.content or ''
                        ai_message_content.append(message_chunk)

                        # Convert the accumulated message to HTML
                        html_content = markdown_to_html(''.join(ai_message_content))

                        await self.send(
                            text_data=f'<div id="{message_id}" hx-swap-oob="innerHTML">{html_content}</div>'
                        )
                    elif chunk.usage:
                        # Update user's token usage
                        await self.update_token_usage(chunk.usage)

                # Save AI message
                full_ai_message = ''.join(ai_message_content)
                await self.save_message(full_ai_message, False)

                # Add the AI response to the history
                self.messages.append({"role": "assistant", "content": full_ai_message})

                # Check token limit
                warning = await self.check_token_limit()
                if warning:
                    await self.send_error_message(warning)

            except Exception as e:
                error_message = (
                    f"An error occurred while communicating with the LLM: {str(e)}"
                )
                await self.send_error_message(error_message)
        except Exception as e:
            logger.error(f"Error processing WebSocket message: {str(e)}")

    async def send_error_message(self, message):
        error_html = render_to_string('ws/error_message.html', {'message': message})
        await self.send(text_data=error_html)

    async def generate_chat_title(self, first_message):
        client = AsyncOpenAI(api_key=self.user_profile.openai_api_key)
        try:
            system_prompt = read_prompt('chat_title_generator')
            response = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": first_message},
                ],
                max_tokens=10,
            )
            new_title = response.choices[0].message.content.strip()
            await self.update_chat_title(new_title)
            await self.update_token_usage(response.usage)
        except Exception as e:
            logger.error(f"Error generating chat title: {str(e)}")

    @database_sync_to_async
    def update_token_usage(self, usage):
        self.user_profile.openai_api_usage += usage.total_tokens
        self.user_profile.save()

    @database_sync_to_async
    def check_token_limit(self):
        limit_percentage = (
            self.user_profile.openai_api_usage / self.user_profile.openai_api_quota
        ) * 100
        if limit_percentage > 80:
            return f"Warning: You have used {limit_percentage:.2f}% of your API quota."
        return None

    @database_sync_to_async
    def update_chat_title(self, new_title):
        self.chat.title = re.sub(r'[^\w\s:"]', '', new_title)
        self.chat.save()
        async_to_sync(self.channel_layer.group_send)(
            f"chat_{self.chat_id}",
            {'type': 'chat_title_update', 'new_title': new_title},
        )

    async def chat_title_update(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    'type': 'chat_title_update',
                    'chat_id': self.chat_id,
                    'new_title': event['new_title'],
                }
            )
        )

    @database_sync_to_async
    def get_model_name(self):
        if self.chat.llm_model:
            return self.chat.llm_model.name
        return (
            self.user_profile.preferred_model.name
            if self.user_profile.preferred_model
            else None
        )

    @database_sync_to_async
    def get_chat(self, chat_id):
        try:
            return Chat.objects.get(id=chat_id, user=self.user)
        except Chat.DoesNotExist:
            return None

    @database_sync_to_async
    def load_chat_history(self):
        messages = Message.objects.filter(chat=self.chat).order_by('id')
        return [
            {"role": "user" if msg.is_user else "assistant", "content": msg.content}
            for msg in messages
        ]

    @database_sync_to_async
    def get_user_profile(self):
        try:
            return UserProfile.objects.get(user=self.user)
        except UserProfile.DoesNotExist:
            return None

    @database_sync_to_async
    def save_message(self, content, is_user):
        Message.objects.create(chat=self.chat, content=content, is_user=is_user)
