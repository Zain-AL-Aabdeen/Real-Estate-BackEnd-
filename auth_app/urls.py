from django.urls import path 
from . import views
from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView

urlpatterns = [
    # روابط تسجيل الدخول والحصول على التوكن وتحديثه
    path("login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    
    # رابط إنشاء الحساب
    path("register/", views.register, name="register"),
]