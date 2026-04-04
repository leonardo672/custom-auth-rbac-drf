from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.urls import path
from .views import RegisterView, UserListView, LoginView, LogoutView, DeleteUserView, UpdateProfileView

urlpatterns = [
    path('register/', RegisterView.as_view()),
    path('login/', LoginView.as_view()),
    path('users/', UserListView.as_view()),
    path("logout/", LogoutView.as_view()),
    path("delete/", DeleteUserView.as_view()),
    path("profile/", UpdateProfileView.as_view()),

]