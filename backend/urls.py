from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
   openapi.Info(
      title="Real Estate & Prediction API",
      default_version='v1',
      description="التوثيق الشامل لواجهات برمجة التطبيقات الخاصة بالحسابات ومحرك التوقعات العقارية",
      contact=openapi.Contact(email="admin@example.com"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # روابط الحسابات
    path('auth/', include('auth_app.urls')),
    
    # روابط محرك التوقعات والذكاء الاصطناعي
    path('predection/', include('prediction_app.urls')),

    # مسارات توثيق Swagger و Redoc
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]