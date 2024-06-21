from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import login, logout
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from .forms import UserRegistrationForm, UserProfileForm
from .models import UserProfile


class CustomLoginView(LoginView):
    template_name = 'registration/login.html'


class RegisterView(CreateView):
    form_class = UserRegistrationForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy('profile')

    def form_valid(self, form):
        user = form.save(commit=False)
        user.set_password(form.cleaned_data['password'])
        user.save()
        if not UserProfile.objects.filter(user=user).exists():
            UserProfile.objects.create(user=user)
        login(self.request, user)
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.get_form()
        return context


class ProfileView(LoginRequiredMixin, UpdateView):
    form_class = UserProfileForm
    template_name = 'registration/profile.html'
    success_url = reverse_lazy('profile')

    def get_object(self):
        return self.request.user.userprofile


def custom_logout(request):
    logout(request)
    return redirect('index')
