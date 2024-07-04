from django.urls import path
from .views import RateLimitedLoginView, ProfileView

urlpatterns = [
    path('login/', RateLimitedLoginView.as_view(), name='account_login'),
    path('profile/', ProfileView.as_view(), name='profile'),
]
