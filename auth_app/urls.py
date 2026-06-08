from django.urls import path
from .views import register_user
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    # رابط التسجيل (api/auth/register/)
    path('register/', register_user, name='register'),
    
    # روابط تسجيل الدخول وتوليد التوكن عبر JWT
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]