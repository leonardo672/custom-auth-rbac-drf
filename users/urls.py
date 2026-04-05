from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.urls import path
from .views import RegisterView, UserListView, LoginView, LogoutView, DeleteUserView, UpdateProfileView, MeView, AdminCreateUserView, ChangeUserRoleView

urlpatterns = [
    path('register/', RegisterView.as_view()),
    path('login/', LoginView.as_view()),
    path('users/', UserListView.as_view()),
    path("logout/", LogoutView.as_view()),
    path("delete/", DeleteUserView.as_view()),
    path("profile/", UpdateProfileView.as_view()),
    path("me/", MeView.as_view()),
    path("admin/create-user/", AdminCreateUserView.as_view()),
    path("admin/change-role/<int:user_id>/", ChangeUserRoleView.as_view()),


]