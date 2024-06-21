from django.contrib.auth.models import User
from django.db import models


class LLMModel(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    openai_api_key = models.CharField(max_length=255, blank=True, null=True)
    preferred_model = models.ForeignKey(
        LLMModel, on_delete=models.SET_NULL, null=True, blank=True
    )

    def __str__(self):
        return self.user.username
