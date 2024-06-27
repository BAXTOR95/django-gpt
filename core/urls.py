from django.urls import path
from . import views

urlpatterns = [
    path('toggle-theme/', views.toggle_theme, name='toggle-theme'),
]
