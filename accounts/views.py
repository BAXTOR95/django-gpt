from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import UpdateView
from django.urls import reverse_lazy
from .models import User, UserProfile
from .forms import UserProfileForm
from django.utils.translation import gettext_lazy as _
from allauth.account.views import PasswordChangeView



class ProfileView(LoginRequiredMixin, UpdateView):
    model = UserProfile
    form_class = UserProfileForm
    template_name = 'accounts/profile.html'
    success_url = reverse_lazy('profile')

    def get_object(self, queryset=None):
        return self.request.user.userprofile

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # context['has_mfa'] = User.objects.filter(
        #     pk=self.request.user.pk, mfadevices__isnull=False
        # ).exists()
        return context


class CustomPasswordChangeView(PasswordChangeView):
    success_url = reverse_lazy('profile')
