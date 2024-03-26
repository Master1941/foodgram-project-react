from django.contrib.auth import get_user_model
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from users.serializers import (
    UsersSerializer,
    UserCreateSerializer,
    SubscriptionSerializer,
)
from food.models import Subscription

User = get_user_model()


class UsersViewSet(ModelViewSet):
    """
    Пользователи
    http://localhost/api/users/
    http://localhost/api/users/{id}/

    http://localhost/api/users/me/
    http://localhost/api/users/set_password/
    Подписки
    http://localhost/api/users/subscriptions/
    http://localhost/api/users/{id}/subscribe/
    http://localhost/api/users/{id}/subscribe/
    """

    queryset = User.objects.all()
    serializer_class = UsersSerializer
    http_method_names = ["GET", "POST", "DEL"]
    permission_classes = IsAuthenticated

    @action(
        methods=["GET"],
        detail=False,
        permission_classes=[IsAuthenticated],
    )
    def me(self, request):
        """получение профиля автора."""
        user = request.user
        serializer = UsersSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        methods=["POST"],
        detail=False,
        permission_classes=[IsAuthenticated],
    )
    def set_password(self, request):
        """Изменение пароля текущего пользователя."""

    @action(
        methods=["GET"],
        detail=False,
        permission_classes=[IsAuthenticated],
    )
    def subscriptions(self, request):
        """Возвращает пользователей,
        на которых подписан текущий пользователь.
        В выдачу добавляются рецепты.."""
        user = request.user
        subscription = Subscription.objects.filter(user=user)
        serializer = SubscriptionSerializer(
            subscription,
            manyu=True,
        )

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        methods=["POST", "DEL"],
        detail=True,
        permission_classes=[IsAuthenticated],
    )
    def subscribe(self, request):
        """POST Подписаться на пользователя
        DEL  Отписаться от пользователя."""


class TokenLoginView(APIView):
    """Используется для авторизации по емейлу и паролю,
    чтобы далее использовать токен при запросах."""


class TokenLogoutView(APIView):
    """Удаляет токен текущего пользователя."""
