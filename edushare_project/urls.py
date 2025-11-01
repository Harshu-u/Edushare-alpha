from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core import views as core_views # Import core views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/register/', core_views.register_view, name='register'),
    path('accounts/', include('django.contrib.auth.urls')), 
    
    # 3. Include URLs from all your new apps
    path('notes/', include('notes.urls')),
    path('categories/', include('categories.urls')),

    # Core app (dashboard, landing page) must be last
    path('', include('core.urls')), 
]

# Serve media files (uploaded notes) in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # This also serves static files
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)