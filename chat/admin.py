from django.contrib import admin
from .models import LLMModel, Chat

admin.site.register(Chat)
admin.site.register(LLMModel)
