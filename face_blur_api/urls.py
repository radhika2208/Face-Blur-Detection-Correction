from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.conf import settings
from django.conf.urls.static import static

from detection.views import dashboard_view

schema_view = get_schema_view(
    openapi.Info(
        title="Face Blur Detection API",
        default_version='v1',
        description="API for detecting and correcting blurred faces in images",
        contact=openapi.Contact(email="radhikapiplani8527@gmail.com"),
        license=openapi.License(name="Dummy License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path("", dashboard_view, name="dashboard"),
    path('api/', include('detection.urls')),
    # Swagger for executing apis
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

