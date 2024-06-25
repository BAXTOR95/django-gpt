from django.contrib import admin
from .models import LLMModel, Chat, Message

admin.site.register(Chat)
admin.site.register(LLMModel)
admin.site.register(Message)
