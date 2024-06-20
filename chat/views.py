from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.template.response import TemplateResponse


def index(request):
    return render(request, 'index.html')

@login_required
def chat(request):
    return TemplateResponse(request, "single_chat.html")