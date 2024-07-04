from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import handler403
from accounts.views import handler403 as rate_limit_handler
from two_factor.urls import urlpatterns as tf_urls

handler403 = rate_limit_handler

urlpatterns = [
    path('', include('pages.urls')),
    path('', include('core.urls')),
    path('', include(tf_urls)),
    path('admin/', admin.site.urls),
    path('chat/', include('chat.urls')),
    path('accounts/', include('allauth.urls')),
    path('accounts/', include('accounts.urls')),
    path('__reload__/', include('django_browser_reload.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
