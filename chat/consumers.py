import json
import uuid
import logging
import re

from django.utils import timezone
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from asgiref.sync import async_to_sync
from django.template.loader import render_to_string
from .models import Chat, Message
from accounts.models import UserProfile
from openai import AsyncOpenAI

logger = logging.getLogger(__name__)


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

        if self.chat and self.user_profile and self.user_profile.openai_api_key:
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

    async def receive(self, text_data):
        logger.info(f"Received WebSocket message: {text_data}")
        try:
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
                raise ValueError("No LLM model specified")

            try:
                openai_response = await client.chat.completions.create(
                    model=model,
                    messages=self.messages,
                    stream=True,
                )

                ai_message_content = []
                async for chunk in openai_response:
                    message_chunk = chunk.choices[0].delta.content or ''
                    formatted_chunk = message_chunk.replace("\n", "<br>")
                    await self.send(
                        text_data=f'<div id="{message_id}" hx-swap-oob="beforeend">{formatted_chunk}</div>'
                    )
                    ai_message_content.append(message_chunk)

                # Save AI message
                full_ai_message = ''.join(ai_message_content)
                await self.save_message(full_ai_message, False)

                # Add the AI response to the history
                self.messages.append({"role": "assistant", "content": full_ai_message})

            except Exception as e:
                error_message = f"An error occurred: {str(e)}"
                await self.send(
                    text_data=f'<div id="{message_id}" hx-swap-oob="beforeend">{error_message}</div>'
                )
        except Exception as e:
            logger.error(f"Error processing WebSocket message: {str(e)}")

    async def generate_chat_title(self, first_message):
        client = AsyncOpenAI(api_key=self.user_profile.openai_api_key)
        try:
            response = await client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "Generate a short, descriptive title (5 words max) for a chat that starts with this message:",
                    },
                    {"role": "user", "content": first_message},
                ],
                max_tokens=10,
            )
            new_title = response.choices[0].message.content.strip()
            await self.update_chat_title(new_title)
        except Exception as e:
            logger.error(f"Error generating chat title: {str(e)}")

    @database_sync_to_async
    def update_chat_title(self, new_title):
        self.chat.title = re.sub(r'[^\w\s]', '', new_title)
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
