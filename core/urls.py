from . import views
from django.contrib import admin
from django.urls import path
from django.urls import include
from django.conf import settings
from django.conf.urls.static import static

# REF-003: Django URL Routing - Main URL configuration with include()
urlpatterns = [
    path('', views.home, name='home'),
    path('admin/', admin.site.urls),
    path('api/', include('jobs.urls')),
    path('api/users/', include('users.urls')),
    path('chat/', include('chat.urls')),
]
# REF-003: Django URL Routing - static() for serving uploaded media in development (Iteration 4)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

