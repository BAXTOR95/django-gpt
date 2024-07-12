from django.contrib.auth.models import AbstractUser
from django.db import models


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
    openai_api_quota = models.IntegerField(
        default=1000000
    )  # Default to 1 million tokens
    openai_api_usage = models.IntegerField(default=0)
    preferred_model = models.ForeignKey(
        'chat.LLMModel', on_delete=models.SET_NULL, null=True, blank=True
    )

    def __str__(self):
        return f"{self.user.username}'s profile"

    def has_sufficient_quota(self):
        return self.openai_api_usage < self.openai_api_quota

    def get_usage_percentage(self):
        return (self.openai_api_usage / self.openai_api_quota) * 100 if self.openai_api_quota > 0 else 0
