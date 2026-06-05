from django.urls import path 
from . import views

urlpatterns = [
    path("User_History/", views.User_History, name="user_history"),
    path("Get_Price/", views.Get_Price, name="get_price"),
]