"""
Проект состоит из следующих страниц:

главная,
страница рецепта,
страница пользователя,
страница подписок,
избранное,
список покупок,
создание и редактирование рецепта.

Пользователи
http://localhost/api/users/
http://localhost/api/users/{id}/
http://localhost/api/users/me/
http://localhost/api/users/set_password/
Подписки
http://localhost/api/users/subscriptions/
http://localhost/api/users/{id}/subscribe/
http://localhost/api/users/{id}/subscribe/
токен
http://localhost/api/auth/token/login/
http://localhost/api/auth/token/logout/

Теги
http://localhost/api/tags/
http://localhost/api/tags/{id}/

Рецепты
http://localhost/api/recipes/
http://localhost/api/recipes/{id}/
Список покупок
http://localhost/api/recipes/download_shopping_cart/
http://localhost/api/recipes/{id}/shopping_cart/
Избранное
http://localhost/api/recipes/{id}/favorite/

Ингредиенты
http://localhost/api/ingredients/
http://localhost/api/ingredients/{id}/
"""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (IngredientViewSet, MeUsersViewSet, RecipeViewSet,
                       TagViewSet)

app_name = "api"

router_v1 = DefaultRouter()
router_v1.register("users", MeUsersViewSet, basename="users")
router_v1.register("tags", TagViewSet, basename="tags")
router_v1.register("recipes", RecipeViewSet, basename="recipes")
router_v1.register("ingredients", IngredientViewSet, basename="ingredients")

urlpatterns = [
    path("", include(router_v1.urls)),
    # path(
    #     "users/subscriptions/",
    #     MeUsersViewSet.as_view({"get": "subscriptions"}),
    #     name="user-subscriptions",
    # ),
    # path(
    #     "users/<int:pk>/subscribe/",
    #     MeUsersViewSet.as_view({"post": "subscribe", "delete": "subscribe"}),
    #     name="user-subscribe",
    # ),
    # # только нужные эндпоинты из djoser
    # path(
    #     "users/",
    #     UserViewSet.as_view({"get": "list", "post": "create"}),
    #     name="user-list",
    # ),
    # path(
    #     "users/<int:pk>/",
    #     UserViewSet.as_view({"get": "retrieve"}),
    #     name="user-detail",
    # ),
    # path("users/me/", UserViewSet.as_view({"get": "me"}), name="user-me"),
    # path(
    #     "users/set_password/",
    #     UserViewSet.as_view({"post": "set_password"}),
    #     name="user-set-password",
    # ),
    # path("", include("djoser.urls")),
    path("auth/", include("djoser.urls.authtoken")),  # Работа с токенами
]
