from django.urls import path

from . import views

urlpatterns = [
    path('', views.chat_interface, name='chat_interface'),
    path('load-chat/<int:chat_id>/', views.load_chat, name='load_chat'),
    path('create-chat/', views.create_chat, name='create_chat'),
    path(
        'update-chat-title/<int:chat_id>/',
        views.update_chat_title,
        name='update_chat_title',
    ),
    path('delete-chat/<int:chat_id>/', views.delete_chat, name='delete_chat'),
    path('select-model/<int:chat_id>/', views.select_model, name='select_model'),
]
