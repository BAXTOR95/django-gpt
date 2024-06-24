from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.template.response import TemplateResponse
from django.http import JsonResponse
from .models import Chat, LLMModel


def index(request):
    return render(request, 'index.html')


@login_required
def chat(request):
    recent_chats = Chat.objects.filter(user=request.user).order_by('-created_at')[:5]
    llm_models = LLMModel.objects.all()

    context = {
        'recent_chats': recent_chats,
        'llm_models': llm_models,
    }

    return TemplateResponse(request, "single_chat.html", context)


def toggle_theme(request):
    if request.method == 'POST':
        # Get the new theme from the POST request (add logic to handle this)
        new_theme = 'dark' if request.POST.get('theme') == 'true' else 'light'
        # Update user's theme setting in the database if necessary
        return JsonResponse({'success': True, 'theme': new_theme})
    return JsonResponse({'success': False})
