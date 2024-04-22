from collections import defaultdict
from datetime import date

from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from api.filters import IngredientFilter, RecipeFilter
from api.pagination import CustomPageNumberPagination
from api.permissions import IsAdminAuthorOrReadOnly
from api.serializers import (IngredientSerializer, RecipeCreatSerializer,
                             RecipeGetSerializer, RecipeMinifiedSerializer,
                             SubscriptionsSerializer, TagSerializer)
from food.models import (Favourites, Ingredient, Recipe, RecipeIngredient,
                         ShoppingList, Subscription, Tag)

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
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_permissions(self):
        if self.action == "me":
            return (IsAuthenticated(),)
        return super().get_permissions()

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
        if user == subscribed:
            return Response(
                {"errors": "На себя нельзя подписаться на самого себя"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if request.method == "POST":
            return self.subscribe_user(user, subscribed)
        elif request.method == "DELETE":
            return self.unsubscribe_user(user, subscribed)

        return Response(
            {"detail": "Метод не разрешен"},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    def subscribe_user(self, user, subscribed):
        """POST Подписаться на пользователя"""

        if not Subscription.objects.filter(
            user=user,
            subscribed=subscribed,
        ).exists():
            Subscription.objects.create(
                user=user,
                subscribed=subscribed,
            )
            serializer = self.get_serializer(subscribed)
            return Response(
                data=serializer.data,
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {"Автор уже в подписках."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def unsubscribe_user(self, user, subscribed):
        """DEL  Отписаться от пользователя."""

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
            status=status.HTTP_400_BAD_REQUEST,
        )


class IngredientViewSet(ModelViewSet):
    """GET Список ингредиентов
    GET Получение ингредиента"""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    http_method_names = ("get",)
    permission_classes = (IsAuthenticatedOrReadOnly,)

    filterset_class = IngredientFilter
    filter_backends = (DjangoFilterBackend,)
    search_fields = ("name",)


class TagViewSet(ModelViewSet):
    """GET Cписок тегов
    GET Получение тега"""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    http_method_names = ("get",)
    permission_classes = (IsAuthenticatedOrReadOnly,)


class RecipeViewSet(ModelViewSet):
    """Страница доступна всем пользователям.
    Рецепты на всех страницах сортируются по дате публикации (новые — выше).
    Доступна фильтрация по избранному, автору, списку покупок и тегам."""

    queryset = Recipe.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = CustomPageNumberPagination
    permission_classes = [IsAdminAuthorOrReadOnly,
                          IsAuthenticatedOrReadOnly,]

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
        """Скачать файл TXT со списком покупок.
        Доступно только авторизованным пользователям."""

        today_cart = date.today()

        user = request.user
        list_ingredients = (
            RecipeIngredient.objects.filter(recipe__shopping_list__user=user)
            .values(
                "ingredient__name",
                "ingredient__measurement_unit",
            )
            .annotate(amount_sum=Sum("amount"))
        )

        summed_ingredients = defaultdict(float)
        for item in list_ingredients:
            key = (
                item["ingredient__name"],
                item["ingredient__measurement_unit"],
            )
            summed_ingredients[key] += item["amount_sum"]

        shopping_list = [f"Список продуктов на {today_cart}:\n \n"]
        for key, value in summed_ingredients.items():
            name = key[0]
            unit = key[1]
            shopping_list.append(f"{name}: {value} {unit}\n")

        filename = f"список_покупок_{date.today()}.txt"
        response = HttpResponse(shopping_list, content_type="text/plain")
        response["Content-Disposition"] = f"attachment; filename={filename}"
        return response

    def add_a_recipe_to_the_list(self, user, Model, kwargs):
        """Метод для добавления рецепта в список избранного или покупок.
        При попытке добавить несуществующий рецепт в избранное
        должен вернуться ответ со статусом 400"""

        try:
            recipe = Recipe.objects.get(id=kwargs["pk"])
        except Recipe.DoesNotExist:
            return Response(
                {"detail": "Рецепт не найден"},
                status=status.HTTP_400_BAD_REQUEST,
            )
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
            {"detail": "Рецепт уже есть в списке покупок/избранного."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def delete_a_recipe_in_the_list(self, user, Model, kwargs):
        """Метод для удаления рецепта из списока избранного или покупок."""

        recipe = get_object_or_404(Recipe, id=kwargs["pk"])
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
                status=status.HTTP_204_NO_CONTENT,
            )
        return Response(
            {"Рецепт не найден в избранном"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    @action(
        methods=["POST", "DELETE"],
        detail=True,
        permission_classes=[IsAuthenticated],
    )
    def shopping_cart(self, request, **kwargs):
        """POST  Добавить рецепт в список покупок
        DEL Удалить рецепт из списка покупок."""

        user = request.user
        if request.method == "POST":
            return self.add_a_recipe_to_the_list(
                kwargs=kwargs,
                user=user,
                Model=ShoppingList,
            )
        elif request.method == "DELETE":
            return self.delete_a_recipe_in_the_list(
                kwargs=kwargs,
                user=user,
                Model=ShoppingList,
            )
        return Response(
            {"detail": "Метод не разрешен"},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    @action(
        methods=["POST", "DELETE"],
        detail=True,
        permission_classes=[IsAuthenticated],
    )
    def favorite(self, request, **kwargs):
        """POST  Добавить рецепт в избранное
        DEL  Удалить рецепт из избранного."""

        user = request.user
        if request.method == "POST":
            return self.add_a_recipe_to_the_list(
                kwargs=kwargs,
                user=user,
                Model=Favourites,
            )
        elif request.method == "DELETE":
            return self.delete_a_recipe_in_the_list(
                kwargs=kwargs,
                user=user,
                Model=Favourites,
            )
        return Response(
            {"detail": "Метод не разрешен"},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )
