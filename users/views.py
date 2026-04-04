from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import RegisterSerializer, LoginSerializer
from .models import User, AuthToken
from .security import verify_password
from .authentication import get_user_from_token # our custom function

class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User created"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserListView(APIView):

    def get(self, request):
        user = get_user_from_token(request)
        if not user:
            return Response({"error": "Unauthorized"}, status=401)

        users = User.objects.filter(is_active=True)
        data = [
            {
                "id": u.id,
                "first_name": u.first_name,
                "last_name": u.last_name,
                "middle_name": u.middle_name,
                "email": u.email,
                "created_at": u.created_at,
            }
            for u in users
        ]
        return Response(data, status=status.HTTP_200_OK)

class LoginView(APIView):

    def post(self, request):
        serializer = LoginSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "Invalid credentials"}, status=401)

        if not user.is_active:
            return Response({"error": "User disabled"}, status=403)

        if not verify_password(password, user.password_hash):
            return Response({"error": "Invalid credentials"}, status=401)

        token = AuthToken.objects.create(user=user)

        return Response({
            "token": str(token.token)
        })


class LogoutView(APIView):

    def post(self, request):
        user = get_user_from_token(request)
        if not user:
            return Response({"error": "Unauthorized"}, status=401)

        token = request.headers.get("Authorization").split(" ")[1]
        AuthToken.objects.filter(token=token).delete()

        return Response({"message": "Logged out successfully"})


class DeleteUserView(APIView):

    def delete(self, request):
        user = get_user_from_token(request)
        if not user:
            return Response({"error": "Unauthorized"}, status=401)

        user.is_active = False
        user.save()

        token = request.headers.get("Authorization").split(" ")[1]
        AuthToken.objects.filter(token=token).delete()

        return Response({"message": "User deactivated"})


class UpdateProfileView(APIView):

    def put(self, request):
        user = get_user_from_token(request)
        if not user:
            return Response({"error": "Unauthorized"}, status=401)

        user.first_name = request.data.get("first_name", user.first_name)
        user.last_name = request.data.get("last_name", user.last_name)
        user.middle_name = request.data.get("middle_name", user.middle_name)

        user.save()

        return Response({"message": "Profile updated"})