from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import UpdateView
from django.urls import reverse_lazy
from .models import UserProfile
from .forms import UserProfileForm
from django.contrib import messages
from django.shortcuts import render
from allauth.account.views import LoginView
from django.utils.translation import gettext_lazy as _
from django_ratelimit.decorators import ratelimit
from django_ratelimit.exceptions import Ratelimited


class RateLimitedLoginView(LoginView):
    @ratelimit(key='ip', rate='5/5m', method=['GET', 'POST'], block=True)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


def handler403(request, exception=None):
    if isinstance(exception, Ratelimited):
        messages.error(request, _("Too many login attempts. Please try again later."))
        return render(request, "account/login.html", status=403)
    return render(request, "403.html", status=403)


class ProfileView(LoginRequiredMixin, UpdateView):
    model = UserProfile
    form_class = UserProfileForm
    template_name = 'accounts/profile.html'
    success_url = reverse_lazy('profile')

    def get_object(self, queryset=None):
        return self.request.user.userprofile
