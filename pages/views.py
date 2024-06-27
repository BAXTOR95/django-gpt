from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required


def home(request):
    if request.user.is_authenticated:
        return redirect('chat_interface')
    return render(request, 'pages/home.html')


@login_required
def dashboard(request):
    return redirect('chat_interface')
