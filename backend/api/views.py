"""
Вьюсеты
Если вы решите использовать вьюсеты,
то вам потребуется добавлять дополнительные action.

Не забывайте о том, что для разных action сериализаторы и
уровни доступа (permissions) могут отличаться.

Некоторые методы, в том числе и action,
могут быть похожи друг на друга. Избегайте дублирующегося кода.
"""

from datetime import date

from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import filters, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from api.filters import RecipeFilter
from api.pagination import CustomPageNumberPagination
from api.serializers import (
    IngredientSerializer,
    RecipeCreatSerializer,
    RecipeGetSerializer,
    RecipeMinifiedSerializer,
    SubscriptionsSerializer,
    TagSerializer,
)
from food.models import (
    Favourites,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingList,
    Subscription,
    Tag,
)

User = get_user_model()


class MeUsersViewSet(UserViewSet):
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

    pagination_class = CustomPageNumberPagination
    queryset = User.objects.all()
    permission_classes = (IsAuthenticated,)

    @action(
        methods=["GET"],
        detail=False,
        permission_classes=[IsAuthenticated],
        serializer_class=SubscriptionsSerializer,
    )
    def subscriptions(self, request):
        """Возвращает пользователей,
        на которых подписан текущий пользователь.
        В выдачу добавляются рецепты.."""

        user = request.user
        users_subscribed = User.objects.filter(subscribed__user=user)
        pages = self.paginate_queryset(users_subscribed)
        serializer = SubscriptionsSerializer(
            pages,
            many=True,
            context={"request": request},
        )
        return self.get_paginated_response(serializer.data)

    @action(
        methods=["POST", "DELETE"],
        detail=True,
        permission_classes=[IsAuthenticated],
        serializer_class=SubscriptionsSerializer,
    )
    def subscribe(self, request, **kwargs):
        """POST Подписаться на пользователя
        DEL  Отписаться от пользователя."""

        subscribed = get_object_or_404(User, id=kwargs["id"])
        user = request.user

        if request.method == "POST":
            return self.subscribe_user(user, subscribed)
        elif request.method == "DELETE":
            return self.unsubscribe_user(user, subscribed)

        return Response(
            {"detail": "Метод не разрешен"},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    def subscribe_user(self, user, subscribed):

        if not Subscription.objects.filter(
            user=user,
            subscribed=subscribed,
        ).exists():
            Subscription.objects.create(
                user=user,
                subscribed=subscribed,
            )
            return Response(
                {"Подписка успешно создана."},
                status=status.HTTP_201_CREATED,
            )

        return Response(
            {"Автор уже в подписках."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def unsubscribe_user(self, user, subscribed):

        if Subscription.objects.filter(
            user=user,
            subscribed=subscribed,
        ).exists():
            Subscription.objects.filter(
                user=user,
                subscribed=subscribed,
            ).delete()
            return Response(
                {"Успешная отписка"},
                status=status.HTTP_204_NO_CONTENT,
            )

        return Response(
            {"Автор не найден в иподписках"},
            status=status.HTTP_404_NOT_FOUND,
        )


class IngredientViewSet(ModelViewSet):
    """GET Список ингредиентов
    GET Получение ингредиента"""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    http_method_names = ("get",)
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ["name"]


class TagViewSet(ModelViewSet):
    """GET Cписок тегов
    GET Получение тега"""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    http_method_names = ("get",)
    permission_classes = (IsAuthenticatedOrReadOnly,)


class RecipeViewSet(ModelViewSet):
    """Страница доступна всем пользователям.
    Доступна фильтрация по избранному, автору, списку покупок и тегам."""

    queryset = Recipe.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = CustomPageNumberPagination
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        """Будет использоваться сериализатор `RecipeGetSerializer`
        а для остальных методов
        будет использоваться `RecipeCreateSerializer`"""

        if self.action in ("list", "retrieve"):
            return RecipeGetSerializer
        return RecipeCreatSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        methods=["GET"],
        detail=False,
        permission_classes=[IsAuthenticated],
    )
    def download_shopping_cart(self, request):
        """Скачать файл со списком покупок. Это может быть TXT/PDF/CSV.
        Важно, чтобы контент файла удовлетворял требованиям задания.
        Доступно только авторизованным пользователям."""
        user = request.user
        username = user.username
        list_ingredients = (
            RecipeIngredient.objects.filter(recipe__shopping_list__user=user)
            .values(
                "ingredient__name",
                "ingredient__measurement_unit",
            )
            .annotate(amount_sum=Sum("amount"))
        )
        today_cart = date.today()
        filename = f"{username}_shopping_list_{today_cart}.txt"  # не работает
        shopping_list = [f"Список продуктов на {today_cart}:\n \n"]
        for ingredient in list_ingredients:
            name = ingredient["ingredient__name"]
            amount = ingredient["amount_sum"]
            unit = ingredient["ingredient__measurement_unit"]
            shopping_list.append(f"{name}: {amount} {unit}\n")
        response = HttpResponse(
            shopping_list,
            content_type="text/plain",
        )
        response["Content-Disposition"] = f'attachment; filename="{filename}"'

        return response

    def add_a_recipe_to_the_list(self, user, Model, recipe):
        """Метод для добавления рецепта в список избранного или покупок."""

        if not Model.objects.filter(
            user=user,
            recipe=recipe,
        ).exists():
            Model.objects.create(
                user=user,
                recipe=recipe,
            )
            serializer = RecipeMinifiedSerializer(recipe)
            return Response(
                data=serializer.data,
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {"Рецепт уже в корзине"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def delete_a_recipe_in_the_list(self, user, Model, recipe):
        """Метод для удаления рецепта из списока избранного или покупок."""

        if Model.objects.filter(
            user=user,
            recipe=recipe,
        ).exists():
            Model.objects.filter(
                user=user,
                recipe=recipe,
            ).delete()
            return Response(
                {"Рецепт успешно удален из избранного"},
                status=status.HTTP_200_OK,
            )
        else:
            return Response({"Рецепт не найден в избранном"})

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
        if request.method == "POST":
            return self.add_a_recipe_to_the_list(
                recipe=recipe,
                user=user,
                Model=ShoppingList,
            )
        elif request.method == "DELETE":
            return self.delete_a_recipe_in_the_list(
                recipe=recipe,
                user=user,
                Model=ShoppingList,
            )
        return Response(
            {"detail": "Метод не разрешен"},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
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
        if request.method == "POST":
            return self.add_a_recipe_to_the_list(
                recipe=recipe,
                user=user,
                Model=Favourites,
            )
        elif request.method == "DELETE":
            return self.delete_a_recipe_in_the_list(
                recipe=recipe,
                user=user,
                Model=Favourites,
            )
        return Response(
            {"detail": "Метод не разрешен"},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )
