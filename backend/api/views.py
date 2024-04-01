"""
Вьюсеты
Если вы решите использовать вьюсеты,
то вам потребуется добавлять дополнительные action.

Не забывайте о том, что для разных action сериализаторы и
уровни доступа (permissions) могут отличаться.

Некоторые методы, в том числе и action,
могут быть похожи друг на друга. Избегайте дублирующегося кода.
"""

from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated, IsAuthenticated, AllowAny
from rest_framework.decorators import action
from rest_framework.views import APIView

from api.serializers import (
    TagSerializer,
    IngredientSerializer,
    RecipeGetSerializer,
    RecipeCreatSerializer,
    UsersSerializer,
    UserCreateSerializer,
    SubscriptionSerializer,
    RecipeMinifiedSerializer,
)

from api.pagination import PageNumberPagination
from food.models import (
    Tag,
    Recipe,
    Ingredient,
    Favourites,
    # ShoppingList,
    Subscription,
    # RecipeIngredient,
)

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
    # http_method_names = ["GET", "POST", "DEL"]
    permission_classes = (AllowAny,)
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["username", "email"]

    def get_serislizer_class(self):
        """будет использоваться сериализатор `RecipeGetSerializer`
        а для остальных методов будет использоваться `RecipeCreateSerializer`"""

        if self.action in ("retrieve", "list"):
            return UsersSerializer
        return UserCreateSerializer

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
    def subscribe(self, request, **kwargs):
        """POST Подписаться на пользователя
        DEL  Отписаться от пользователя."""
        recipe = get_object_or_404(Recipe, id=kwargs["pk"])
        user = self.request.user
        if not user.is_anonymous:
            if self.action == "create":
                # Добавление рецепта в избранное
                if not Favourites.objects.filter(
                    user=user,
                    recipe=recipe,
                ).exists():
                    Favourites.objects.create(
                        user=user,
                        recipe=recipe,
                    )
                    serializer = RecipeMinifiedSerializer(recipe)
                    return Response(
                        data=serializer.data,
                        status=status.HTTP_201_CREATED,
                    )
                else:
                    return Response(
                        {"Рецепт уже в избранном"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            elif self.action == "destroy":
                # Удаление рецепта из избранного
                if Favourites.objects.filter(
                    user=request.user,
                    recipe=recipe,
                ).exists():
                    Favourites.objects.filter(
                        user=request.user,
                        recipe=recipe,
                    ).delete()
                    return Response({"Рецепт успешно удален из избранного"})
                else:
                    return Response({"Рецепт не найден в избранном"})
        else:
            return Response(
                {"Учетные данные не были предоставлены."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

class IngredientViewSet(ModelViewSet):
    """GET Список ингредиентов
    GET Получение ингредиента"""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    http_method_names = ("get",)


class TagViewSet(ModelViewSet):
    """GET Cписок тегов
    GET Получение тега"""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    http_method_names = ("get",)


class RecipeViewSet(ModelViewSet):
    """Страница доступна всем пользователям.
    Доступна фильтрация по избранному, автору, списку покупок и тегам."""

    serializer_class = RecipeGetSerializer
    queryset = Recipe.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ("author",)
    pagination_class = PageNumberPagination

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(methods=["GET"], detail=False, permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        """Скачать файл со списком покупок. Это может быть TXT/PDF/CSV.
        Важно, чтобы контент файла удовлетворял требованиям задания.
        Доступно только авторизованным пользователям."""
        # user = request.user

        # RecipeIngredient.objects.filter(
        #     recipe__shopping_list__user=request.user
        # ).values("recipe__name", "recip__mesuremet_unit").annotation(
        #     amount_sum=Sum("amount")
        # )

        # serializer = UsersSerializer(user)
        # return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=["POST", "DEL"], detail=True, permission_classes=[IsAuthenticated])
    def shopping_cart(self, request):
        """POST  Добавить рецепт в список покупок
        DEL     Удалить рецепт из списка покупок"""

    @action(
        methods=[
            "POST",
            "DEL",
        ],
        detail=True,
        permission_classes=[IsAuthenticated],
    )
    def favorite(self, request, **kwargs):
        """POST  Добавить рецепт в избранное
        DEL  Удалить рецепт из избранного"""

        recipe = get_object_or_404(Recipe, id=kwargs["pk"])
        user = self.request.user
        if not user.is_anonymous:
            if self.action == "create":
                # Добавление рецепта в избранное
                if not Favourites.objects.filter(
                    user=user,
                    recipe=recipe,
                ).exists():
                    Favourites.objects.create(
                        user=user,
                        recipe=recipe,
                    )
                    serializer = RecipeMinifiedSerializer(recipe)
                    return Response(
                        data=serializer.data,
                        status=status.HTTP_201_CREATED,
                    )
                else:
                    return Response(
                        {"Рецепт уже в избранном"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            elif self.action == "destroy":
                # Удаление рецепта из избранного
                if Favourites.objects.filter(
                    user=request.user,
                    recipe=recipe,
                ).exists():
                    Favourites.objects.filter(
                        user=request.user,
                        recipe=recipe,
                    ).delete()
                    return Response({"Рецепт успешно удален из избранного"})
                else:
                    return Response({"Рецепт не найден в избранном"})
        else:
            return Response(
                {"Учетные данные не были предоставлены."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

    def get_serislizer_class(self):
        """Будет использоваться сериализатор `RecipeGetSerializer`
        а для остальных методов
        будет использоваться `RecipeCreateSerializer`"""

        if self.action in ("list", "retrieve"):
            return RecipeGetSerializer
        return RecipeCreatSerializer
