from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView

from users.models import CustomUser


class UsersViewSet(ModelViewSet):
    """
    http://localhost/api/users/me/
    Текущий пользователь

    http://localhost/api/users/set_password/
    Изменение пароля

    """


class TokenLoginView(APIView):
    """Используется для авторизации по емейлу и паролю, чтобы далее использовать токен при запросах."""


class TokenLogoutView(APIView):
    """Удаляет токен текущего пользователя."""
