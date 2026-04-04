from .models import AuthToken


def get_user_from_token(request):
    auth_header = request.headers.get("Authorization")

    if not auth_header:
        return None

    try:
        prefix, token = auth_header.split(" ")
    except ValueError:
        return None

    if prefix != "Bearer":
        return None

    try:
        auth = AuthToken.objects.select_related("user").get(token=token)
        return auth.user
    except AuthToken.DoesNotExist:
        return None