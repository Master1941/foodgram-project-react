"""
Проект состоит из следующих страниц:

главная,
страница рецепта,
страница пользователя,
страница подписок,
избранное,
список покупок,
создание и редактирование рецепта.
"""

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

from users.views import UsersViewSet, TokenLoginView, TokenLogoutView
from api.views import (
    TagViewSet,
    RecipeViewSet,
    IngredientViewSet,
    ShoppingCartViewSet,
    SubscriptionViewSet,
    FavoriteViewSet,
    SubscribeViewSet,
)

app_name = "api"


router_v1 = DefaultRouter()
router_v1.register("users", UsersViewSet, basename="users")
router_v1.register("tags", TagViewSet, basename="tags")
router_v1.register("recipes", RecipeViewSet, basename="recipes")
router_v1.register("ingredients", IngredientViewSet, basename="ingredients")
router_v1.register(
    r"shopping_cart",
    ShoppingCartViewSet,
    basename="shopping_cart",
)
router_v1.register("favorite", FavoriteViewSet, basename="favorite")
router_v1.register(
    r"subscriptions",
    SubscriptionViewSet,
    basename="subscriptions",
)

router_v1.register(
    r"users/(?P<title_id>\d+)/subscribe/",
    SubscribeViewSet,
    basename="subscribe",
)


urlpatterns = [
    path("", include(router_v1.urls)),
    path(
        "auth/token/",
        include(
            [
                path("login/", TokenLoginView.as_view(), name="token_login"),
                path("logout/", TokenLogoutView.as_view(), name="token_logout")
            ]
        ),
    ),
]
