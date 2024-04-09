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
from rest_framework.permissions import (
    IsAuthenticated,
    AllowAny,
)
from rest_framework.decorators import action
from djoser.serializers import SetPasswordSerializer

from api.serializers import (
    TagSerializer,
    IngredientSerializer,
    RecipeGetSerializer,
    RecipeCreatSerializer,
    UsersSerializer,
    UserCreateSerializer,
    SubscriptionsSerializer,
    RecipeMinifiedSerializer,

)
from api.filters import RecipeFilter
from api.pagination import CustomPageNumberPagination
from food.models import (
    Tag,
    Recipe,
    Ingredient,
    Favourites,
    ShoppingList,
    Subscription,
    RecipeIngredient,
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
    pagination_class = CustomPageNumberPagination

    def get_serializer_class(self):
        """будет использоваться сериализатор `RecipeGetSerializer`
        а для остальных методов будет использоваться `RecipeCreateSerializer`
        """

        if self.action in ("retrieve", "list"):
            return UsersSerializer
        return UserCreateSerializer

    @action(
        methods=["GET"],
        detail=False,
        permission_classes=[AllowAny],
    )
    def me(self, request):
        """получение профиля автора."""
        user = self.request.user
        serializer = UsersSerializer(user, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        methods=["POST"],
        detail=False,
        permission_classes=[IsAuthenticated],
    )
    def set_password(self, request):
        """Изменение пароля текущего пользователя."""

        serializer = SetPasswordSerializer(request.user, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(
                {"Пароль успешно изменен"},
                status=status.HTTP_204_NO_CONTENT,
            )
        return Response("Пароль не изменен", status=status.HTTP_400_BAD_REQUEST)

    @action(
        methods=["GET"],
        detail=False,
        permission_classes=[AllowAny],
    )
    def subscriptions(self, request):
        """Возвращает пользователей,
        на которых подписан текущий пользователь.
        В выдачу добавляются рецепты.."""

        user = request.user
        if user.is_authenticated:
            users_subscribed = Subscription.objects.filter(user=user)
            pages = self.paginate_queryset(users_subscribed)
            serializer = SubscriptionsSerializer(
                pages,
                many=True,
                context={"request": request},
            )
            return self.get_paginated_response(serializer.data)
        else:
            return Response(
                {"Учетные данные не были предоставлены."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

    @action(
        methods=["POST", "DELETE"],
        detail=True,
        permission_classes=[IsAuthenticated],
    )
    def subscribe(self, request, **kwargs):
        """POST Подписаться на пользователя
        DEL  Отписаться от пользователя."""

        subscribed = get_object_or_404(User, id=kwargs["pk"])
        user = request.user
        if not user.is_anonymous:
            if request.method == "POST":
                # Добавление рецепта в избранное
                if not Subscription.objects.filter(
                    user=user,
                    subscribed=subscribed,
                ).exists():
                    Subscription.objects.create(
                        user=user,
                        subscribed=subscribed,
                    )
                    serializer = RecipeMinifiedSerializer(subscribed)
                    return Response(
                        data=serializer.data,
                        status=status.HTTP_201_CREATED,
                    )
                else:
                    return Response(
                        {"Автор уже в подписках."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            if request.method == "DELETE":
                # Удаление рецепта из избранного
                if Subscription.objects.filter(
                    user=user,
                    subscribed=subscribed,
                ).exists():
                    Subscription.objects.filter(
                        user=user,
                        subscribed=subscribed,
                    ).delete()
                    return Response(
                        {"Автор успешно удален из подписок."},
                        status=status.HTTP_200_OK,
                    )
                else:
                    return Response({"Автор не найден в иподписках"})
            else:
                return Response(
                    {"detail": "Метод не разрешен"},
                    status=status.HTTP_405_METHOD_NOT_ALLOWED,
                )
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
    permission_classes = (AllowAny,)


class TagViewSet(ModelViewSet):
    """GET Cписок тегов
    GET Получение тега"""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    http_method_names = ("get",)
    permission_classes = (AllowAny,)


class RecipeViewSet(ModelViewSet):
    """Страница доступна всем пользователям.
    Доступна фильтрация по избранному, автору, списку покупок и тегам."""

    queryset = Recipe.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = CustomPageNumberPagination

    def get_serializer_class(self):
        """Будет использоваться сериализатор `RecipeGetSerializer`
        а для остальных методов
        будет использоваться `RecipeCreateSerializer`"""

        if self.action in ("list", "retrieve"):
            return RecipeGetSerializer
        return RecipeCreatSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(methods=["GET"], detail=False, permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        """Скачать файл со списком покупок. Это может быть TXT/PDF/CSV.
        Важно, чтобы контент файла удовлетворял требованиям задания.
        Доступно только авторизованным пользователям."""
        # user = request.user
        # if not user.is_anonymous:

        # list_ingredients =  RecipeIngredient.objects.filter(
        #     recipe__shopping_list__user=request.user
        # ).values("recipe__name", "recip__mesuremet_unit").annotation(
        #     amount_sum=Sum("amount")
        # )

        # serializer = UsersSerializer(user)
        # return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        methods=["POST", "DELETE"],
        detail=True,
        permission_classes=[IsAuthenticated],
    )
    def shopping_cart(self, request, **kwargs):
        """POST  Добавить рецепт в список покупок
        DEL     Удалить рецепт из списка покупок"""

        recipe = get_object_or_404(Recipe, id=kwargs["pk"])
        user = request.user
        if not user.is_anonymous:
            if request.method == "POST":
                # Добавление рецепта в покупки
                if not ShoppingList.objects.filter(
                    user=user,
                    recipe=recipe,
                ).exists():
                    ShoppingList.objects.create(
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
                        {"Рецепт уже в корзине"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            if request.method == "DELETE":
                # Удаление рецепта из избранного
                if ShoppingList.objects.filter(
                    user=user,
                    recipe=recipe,
                ).exists():
                    ShoppingList.objects.filter(
                        user=user,
                        recipe=recipe,
                    ).delete()
                    return Response(
                        {"Рецепт успешно удален из избранного"},
                        status=status.HTTP_200_OK,
                    )
                else:
                    return Response({"Рецепт не найден в избранном"})
            else:
                return Response(
                    {"detail": "Метод не разрешен"},
                    status=status.HTTP_405_METHOD_NOT_ALLOWED,
                )
        else:
            return Response(
                {"Учетные данные не были предоставлены."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

    @action(
        methods=[
            "POST",
            "DELETE",
        ],
        detail=True,
        permission_classes=[IsAuthenticated],
    )
    def favorite(self, request, **kwargs):
        """POST  Добавить рецепт в избранное
        DEL  Удалить рецепт из избранного"""

        recipe = get_object_or_404(Recipe, id=kwargs["pk"])
        user = request.user
        if not user.is_anonymous:
            if request.method == "POST":
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
            if request.method == "DELETE":
                # Удаление рецепта из избранного
                if Favourites.objects.filter(
                    user=user,
                    recipe=recipe,
                ).exists():
                    Favourites.objects.filter(
                        user=user,
                        recipe=recipe,
                    ).delete()
                    return Response(
                        {"Рецепт успешно удален из избранного"},
                        status=status.HTTP_200_OK,
                    )
                else:
                    return Response({"Рецепт не найден в избранном"})
            else:
                return Response(
                    {"detail": "Метод не разрешен"},
                    status=status.HTTP_405_METHOD_NOT_ALLOWED,
                )
        else:
            return Response(
                {"Учетные данные не были предоставлены."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
