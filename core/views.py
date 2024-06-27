# core/views.py
from django.http import JsonResponse


def toggle_theme(request):
    if request.method == 'POST':
        new_theme = 'dark' if request.POST.get('theme') == 'true' else 'light'
        # Update user's theme setting in the database if necessary
        return JsonResponse({'success': True, 'theme': new_theme})
    return JsonResponse({'success': False})
