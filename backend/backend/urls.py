from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/common/', include('apps.common.urls')),
    path('api/auth/', include('apps.accounts.urls')),
    path('api/elections/', include('apps.elections.urls')),
    path('api/candidates/', include('apps.candidates.urls')),
    path('api/voting/', include('apps.voting.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
