from django import forms
from allauth.account.forms import SignupForm
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from .models import UserProfile, LLMModel


class CustomSignupForm(SignupForm):
    first_name = forms.CharField(max_length=30, label='First Name')
    last_name = forms.CharField(max_length=30, label='Last Name')

    def save(self, request):
        user = super(CustomSignupForm, self).save(request)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.save()
        # Create UserProfile
        UserProfile.objects.get_or_create(user=user)
        self.send_welcome_email(user)
        return user

    def send_welcome_email(self, user):
        subject = 'Welcome to Our Site'
        html_message = render_to_string('accounts/welcome_email.html', {'user': user})
        plain_message = strip_tags(html_message)
        from_email = settings.EMAIL_HOST_USER
        to = user.email

        send_mail(subject, plain_message, from_email, [to], html_message=html_message)


class UserProfileForm(forms.ModelForm):
    preferred_model = forms.ModelChoiceField(
        queryset=LLMModel.objects.all(), required=False
    )

    class Meta:
        model = UserProfile
        fields = ('openai_api_key', 'preferred_model')
