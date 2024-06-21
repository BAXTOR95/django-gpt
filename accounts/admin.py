from django.contrib import admin
from .models import UserProfile, LLMModel

admin.site.register(UserProfile)
admin.site.register(LLMModel)
