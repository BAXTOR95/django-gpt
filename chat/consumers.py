import json
import uuid
from channels.generic.websocket import AsyncWebsocketConsumer
from django.template.loader import render_to_string
from django.conf import settings
from openai import AsyncOpenAI


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.messages = []
        await super().connect()

    async def receive(self, text_data=None):
        text_data_json = json.loads(text_data)
        message_text = text_data_json['message']

        # show user's message
        user_message_html = render_to_string(
            'ws/chat_message.html',
            {
                'message_text': message_text,
                'is_system': False,
            },
        )
        await self.send(text_data=user_message_html)
        self.messages.append(
            {
                "role": "user",
                "content": message_text,
            }
        )

        message_id = f"message-{uuid.uuid4().hex}"

        system_message_html = render_to_string(
            'ws/chat_message.html',
            {
                'message_text': '',
                'is_system': True,
                'message_id': message_id,
            },
        )

        await self.send(text_data=system_message_html)

        client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        openai_response = await client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=self.messages,
            stream=True,
        )

        chunks = []  # collect all the chunks in this list
        async for chunk in openai_response:
            message_chunk = chunk.choices[0].delta.content or ''
            print('message:', message_chunk)
            formatted_chunk = message_chunk.replace("\n", "<br>")
            # markdown_chunk = markdown.markdown(formatted_chunk, extensions=['tables'])
            await self.send(
                text_data=f'<div id="{message_id}" hx-swap-oob="beforeend">{formatted_chunk}</div>'
            )
            chunks.append(formatted_chunk)

        self.messages.append(
            {
                'role': 'system',
                'content': ''.join(chunks),
            }
        )
