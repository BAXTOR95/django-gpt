from django.contrib.auth.models import AbstractUser
from django.db import models
from chat.models import LLMModel


class User(AbstractUser):
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.username


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=30, blank=True)
    birth_date = models.DateField(null=True, blank=True)

    openai_api_key = models.CharField(max_length=255, blank=True, null=True)
    preferred_model = models.ForeignKey(
        LLMModel, on_delete=models.SET_NULL, null=True, blank=True
    )

    def __str__(self):
        return f"{self.user.username}'s profile"
