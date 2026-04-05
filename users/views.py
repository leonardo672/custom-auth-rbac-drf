from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import RegisterSerializer, LoginSerializer
from .models import User, AuthToken
from .security import verify_password
from .authentication import get_user_from_token # our custom function
import bcrypt
from .decorators import admin_required


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

        if user.role != "ADMIN":
            return Response({"error": "Forbidden"}, status=403)

        users = User.objects.filter(is_active=True)

        data = [
            {
                "id": u.id,
                "email": u.email,
                "role": u.role
            }
            for u in users
        ]

        return Response(data)

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


class MeView(APIView):

    def get(self, request):
        user = get_user_from_token(request)
        if not user:
            return Response({"error": "Unauthorized"}, status=401)

        return Response({
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "role": user.role
        })

class AdminCreateUserView(APIView):

    @admin_required
    def post(self, request):

        required_fields = [
            "first_name",
            "last_name",
            "middle_name",
            "email",
            "password",
            "confirm_password"
        ]

        for field in required_fields:
            if not request.data.get(field):
                return Response(
                    {"error": f"{field} is required"},
                    status=400
                )

        password = request.data.get("password")
        confirm_password = request.data.get("confirm_password")

        if password != confirm_password:
            return Response(
                {"error": "Passwords do not match"},
                status=400
            )

        if User.objects.filter(email=request.data.get("email")).exists():
            return Response(
                {"error": "Email already exists"},
                status=400
            )

        password_hash = bcrypt.hashpw(
            password.encode(),
            bcrypt.gensalt()
        ).decode()

        role = request.data.get("role", "USER")

        if role not in ["USER", "ADMIN"]:
            return Response({"error": "Invalid role"}, status=400)

        user = User.objects.create(
            first_name=request.data.get("first_name"),
            last_name=request.data.get("last_name"),
            middle_name=request.data.get("middle_name"),
            email=request.data.get("email"),
            password_hash=password_hash,
            role=role
        )

        return Response({
            "message": "User created",
            "id": user.id,
            "role": user.role
        }, status=201)


class ChangeUserRoleView(APIView):

    @admin_required
    def patch(self, request, user_id):

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)

        role = request.data.get("role")

        if role not in ["USER", "ADMIN"]:
            return Response({"error": "Invalid role"}, status=400)

        user.role = role
        user.save()

        return Response({
            "message": "Role updated",
            "user_id": user.id,
            "role": user.role
        })