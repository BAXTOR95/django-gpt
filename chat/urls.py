from django.urls import path

from .views import index, chat, toggle_theme

urlpatterns = [
    path('', index, name='index'),
    path('chat/', chat, name='chat'),
    path('toggle-theme/', toggle_theme, name='toggle-theme'),
]
