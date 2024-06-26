from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.template.response import TemplateResponse
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.template.loader import render_to_string
from .models import Chat, LLMModel, Message
from accounts.models import UserProfile


@login_required
def chat_interface(request):
    chats = Chat.objects.filter(user=request.user).order_by('-created_at')
    llm_models = LLMModel.objects.all()
    current_chat = chats.first()  # Default to the most recent chat
    messages = Message.objects.filter(chat=current_chat) if current_chat else []

    user_profile = UserProfile.objects.get(user=request.user)
    preferred_model = user_profile.preferred_model

    context = {
        'chats': chats,
        'current_chat': current_chat,
        'messages': messages,
        'llm_models': llm_models,
        'preferred_model': preferred_model,
    }
    return render(request, 'chat/chat_base.html', context)


@login_required
def load_chat(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id, user=request.user)
    messages = chat.messages.all()
    llm_models = LLMModel.objects.all()
    chats = Chat.objects.filter(user=request.user).order_by('-created_at')

    user_profile = UserProfile.objects.get(user=request.user)
    preferred_model = user_profile.preferred_model

    context = {
        'current_chat': chat,
        'messages': messages,
        'llm_models': llm_models,
        'chats': chats,
        'preferred_model': preferred_model,
    }

    return TemplateResponse(request, 'chat/components/chat_content.html', context)


@login_required
@require_POST
def create_chat(request):
    user_profile = UserProfile.objects.get(user=request.user)
    preferred_model = user_profile.preferred_model

    chat = Chat.objects.create(
        user=request.user, title="New Chat", llm_model=preferred_model
    )
    chats = Chat.objects.filter(user=request.user).order_by('-created_at')
    return TemplateResponse(
        request, 'chat/components/sidebar.html', {'chats': chats, 'current_chat': chat}
    )


@login_required
@require_POST
def update_chat_title(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id, user=request.user)
    new_title = request.POST.get('title')
    if new_title:
        chat.title = new_title
        chat.save()
    chats = Chat.objects.filter(user=request.user).order_by('-created_at')
    return TemplateResponse(
        request, 'chat/components/sidebar.html', {'chats': chats, 'current_chat': chat}
    )


@login_required
@require_POST
def delete_chat(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id, user=request.user)
    chat.delete()
    chats = Chat.objects.filter(user=request.user).order_by('-created_at')
    return TemplateResponse(request, 'chat/components/sidebar.html', {'chats': chats})


@login_required
@require_POST
def select_model(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id, user=request.user)
    model_id = request.POST.get('model_id')
    if model_id:
        chat.llm_model = get_object_or_404(LLMModel, id=model_id)
        chat.save()
    llm_models = LLMModel.objects.all()
    user_profile = UserProfile.objects.get(user=request.user)
    preferred_model = user_profile.preferred_model
    return TemplateResponse(
        request,
        'chat/components/chat_header.html',
        {
            'current_chat': chat,
            'llm_models': llm_models,
            'preferred_model': preferred_model,
        },
    )


def toggle_theme(request):
    if request.method == 'POST':
        # Get the new theme from the POST request (add logic to handle this)
        new_theme = 'dark' if request.POST.get('theme') == 'true' else 'light'
        # Update user's theme setting in the database if necessary
        return JsonResponse({'success': True, 'theme': new_theme})
    return JsonResponse({'success': False})
