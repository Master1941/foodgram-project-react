from rest_framework.viewsets import ModelViewSet
from food.models import Tag
from api.serializers import TagSerializer


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


class ShoppingCartViewSet(ModelViewSet):
    """POST  Добавить рецепт в список покупок
    DEL  Удалить рецепт из списка покупок"""


class DownloadShoppingCartViewSet(ModelViewSet):
    """Скачать файл со списком покупок.
    Это может быть TXT/PDF/CSV.
    Важно, чтобы контент файла удовлетворял требованиям задания.
    Доступно только авторизованным пользователям."""


class FavoriteViewSet(ModelViewSet):
    """POST  Добавить рецепт в избранное
    DEL   Удалить рецепт из избранного"""


class SubscriptionViewSet(ModelViewSet):
    """Возвращает пользователей, на которых подписан текущий пользователь.
    В выдачу добавляются рецепты."""


class SubscribeViewSet(ModelViewSet):
    """POST  Подписаться на пользователя
    DEL  Отписаться от пользователя
    Доступно только авторизованным пользователям"""


class IngredientViewSet(ModelViewSet):
    """GET Список ингредиентов
    GET Получение ингредиента"""
