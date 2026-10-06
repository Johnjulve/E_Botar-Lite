from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # v1 API Routes
    path('api/v1/common/', include('apps.common.urls')),
    path('api/v1/auth/', include('apps.accounts.urls')),
    path('api/v1/elections/', include('apps.elections.urls')),
    path('api/v1/candidates/', include('apps.candidates.urls')),
    path('api/v1/voting/', include('apps.voting.urls')),
    
    # Legacy / Backward compatibility API Routes
    path('api/common/', include('apps.common.urls')),
    path('api/auth/', include('apps.accounts.urls')),
    path('api/elections/', include('apps.elections.urls')),
    path('api/candidates/', include('apps.candidates.urls')),
    path('api/voting/', include('apps.voting.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
