"""
Вьюсеты
Если вы решите использовать вьюсеты, то вам потребуется добавлять дополнительные action.
Не забывайте о том, что для разных action сериализаторы и уровни доступа (permissions) могут отличаться.

Некоторые методы, в том числе и action, могут быть похожи друг на друга. Избегайте дублирующегося кода.
"""

from rest_framework.viewsets import ModelViewSet

from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from api.serializers import (
    TagSerializer,
    RecipeSerializer,
    IngredientSerializer,
)
from food.models import (
    Tag,
    Recipe,
    Ingredient,
    Favourites,
    ShoppingList,
    Subscription,
)


class IngredientViewSet(ModelViewSet):
    """GET Список ингредиентов
    GET Получение ингредиента"""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class TagViewSet(ModelViewSet):
    """GET Cписок тегов
    GET Получение тега"""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class RecipeViewSet(ModelViewSet):
    """GET      Список рецептов
    POST    Создание рецепта
    GET     Получение рецепта
    PATCH   Обновление рецепта
    DEL     Удаление рецепта"""

    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer

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
        # user = request.user
        # serializer = UsersSerializer(user)
        # return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        methods=["GET"],
        detail=True,
        permission_classes=[IsAuthenticated],
    )
    def shopping_cart(self, request):
        """POST        Добавить рецепт в список покупок
        DEL        Удалить рецепт из списка покупок"""

    @action(
        methods=["GET"],
        detail=True,
        permission_classes=[IsAuthenticated],
    )
    def favorite(self, request):
        """POST  Добавить рецепт в избранное
        DEL  Удалить рецепт из избранного"""


class ShoppingCartViewSet(ModelViewSet):
    """POST  Добавить рецепт в список покупок
    DEL  Удалить рецепт из списка покупок"""


class DownloadShoppingCartViewSet(ModelViewSet):
    """Скачать файл со списком покупок.
    Это может быть TXT/PDF/CSV.
    Важно, чтобы контент файла удовлетворял требованиям задания.
    Доступно только авторизованным пользователям."""

    # permission_classes = [IsAuthenticated]


class FavoriteViewSet(ModelViewSet):
    """POST  Добавить рецепт в избранное
    DEL Удалить рецепт из избранного"""


class SubscriptionViewSet(ModelViewSet):
    """Возвращает пользователей, на которых подписан текущий пользователь.
    В выдачу добавляются рецепты."""


class SubscribeViewSet(ModelViewSet):
    """POST  Подписаться на пользователя
    DEL  Отписаться от пользователя
    Доступно только авторизованным пользователям"""
