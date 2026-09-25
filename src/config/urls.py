from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)



from django.urls import include, path

urlpatterns = [
    path("api/v1/", include("api.user.urls")),
    path("admin/", admin.site.urls ),


    
    # --- API App Routes ---
    path('api/users/', include('apps.users.urls')),
    # Central API router (categories, products, carts, orders)
    path('api/', include('api.urls')),

    # --- Swagger/OpenAPI Documentation ---
    # 1. The raw schema endpoint (JSON/YAML)
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    
    # 2. Swagger UI (The interactive documentation)
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    
    # 3. Redoc UI (An alternative documentation style)
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

# Serve media and static files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
