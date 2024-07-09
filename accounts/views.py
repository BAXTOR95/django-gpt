from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import UpdateView
from django.urls import reverse_lazy
from .models import UserProfile
from .forms import UserProfileForm
from django.contrib import messages
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _
from django_ratelimit.exceptions import Ratelimited
from django_otp import user_has_device
from allauth.account.views import LoginView as AllAuthLoginView
from two_factor.views import LoginView as TwoFactorLoginView


class CustomLoginView(AllAuthLoginView, TwoFactorLoginView):
    template_name = 'allauth/account/login.html'


class ProfileView(LoginRequiredMixin, UpdateView):
    model = UserProfile
    form_class = UserProfileForm
    template_name = 'accounts/profile.html'
    success_url = reverse_lazy('profile')

    def get_object(self, queryset=None):
        return self.request.user.userprofile

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['has_2fa'] = user_has_device(self.request.user)
        return context
