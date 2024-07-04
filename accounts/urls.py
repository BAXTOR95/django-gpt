from django.urls import path
from .views import RateLimitedTwoFactorLoginView, ProfileView
from .two_factor_custom import CustomSetupView

urlpatterns = [
    path('login/', RateLimitedTwoFactorLoginView.as_view(), name='account_login'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('two_factor/setup/', CustomSetupView.as_view(), name='two_factor_setup'),
]
