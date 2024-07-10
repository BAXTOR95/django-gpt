from django.urls import path
from .views import ProfileView, CustomPasswordChangeView
from allauth.account.views import EmailView

urlpatterns = [
    path('profile/', ProfileView.as_view(), name='profile'),
    path('email/', EmailView.as_view(), name='account_email'),
    path('password/change/', CustomPasswordChangeView.as_view(), name='account_change_password'),
]
