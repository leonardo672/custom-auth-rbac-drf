from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.urls import path
from .views import RegisterView, UserListView, LoginView

urlpatterns = [
    path('register/', RegisterView.as_view()),
    path('login/', LoginView.as_view()),
    path('users/', UserListView.as_view()),
]