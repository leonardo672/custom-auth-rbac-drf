from rest_framework.response import Response
from functools import wraps
from .authentication import get_user_from_token


def admin_required(view_func):
    @wraps(view_func)
    def wrapper(self, request, *args, **kwargs):
        user = get_user_from_token(request)

        if not user:
            return Response({"error": "Unauthorized"}, status=401)

        if user.role != "ADMIN":
            return Response({"error": "Forbidden - admin only"}, status=403)

        request.user = user
        return view_func(self, request, *args, **kwargs)

    return wrapper