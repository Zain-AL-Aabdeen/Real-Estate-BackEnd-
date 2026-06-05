from django.contrib import admin
from django.urls import path, include, re_path # أضفنا re_path هنا

# 1. استيراد المكتبات الخاصة بـ Swagger
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# 2. إعداد واجهة التوثيق لتشمل تفاصيل مشروعك مع خانة الحماية والتوكن
schema_view = get_schema_view(
   openapi.Info(
      title="Real Estate & Prediction API",
      default_version='v1',
      description="التوثيق الشامل لواجهات برمجة التطبيقات الخاصة بالحسابات ومحرك التوقعات العقارية",
      contact=openapi.Contact(email="admin@example.com"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
   
   # 🚨 هذا هو الجزء الناقص الذي يظهر خانة الـ Token في السويدجر ⬇️
   security_definitions={
       'Bearer': {
           'type': 'apiKey',
           'name': 'Authorization',
           'in': 'header',
           'description': "اكتب في الخانة: 'Bearer' متبوعة بمسافة ثم التوكن الخاص بك"
       }
   },
)
urlpatterns = [
    path('admin/', admin.site.urls),
    
    # روابط الحسابات (تسجيل دخول، إنشاء حساب، تحديث التوكن)
    path('auth/', include('auth_app.urls')),
    
    # روابط محرك التوقعات والذكاء الاصطناعي والأرشيف
    path('predection/', include('prediction_app.urls')),

    # 3. مسارات توثيق Swagger و Redoc التي تم إضافتها
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]