"""
is_favorited
integer
Enum: 0 1
Показывать только рецепты, находящиеся в списке избранного.

is_in_shopping_cart
integer
Enum: 0 1
Показывать только рецепты, находящиеся в списке покупок.

author
integer
Показывать рецепты только автора с указанным id.

tags
Array of strings
Example: tags=lunch&tags=breakfast
Показывать рецепты только с указанными тегами (по slug)
"""

from django_filters.rest_framework import FilterSet, filters

from food.models import Ingredient, Recipe, Tag, Subscription, Favourites
from django.contrib.auth import get_user_model

User = get_user_model()


class RecipeFilter(FilterSet):
    """Фильтрация по полям is_favorited is_in_shopping_cart author tags
    """

    tags = filters.ModelMultipleChoiceFilter(
        field_name="tags__slug",
        to_field_name="slug",
        queryset=Tag.objects.all(),
    )

    is_favorited = filters.BooleanFilter(
        method="get_is_favorited",
    )

    # is_in_shopping_cart = filters.BooleanFilter(
    #     method="is_in_shopping_cart",
    # )

    class Meta:
        model = Recipe
        fields = (
            "author",
            "tags",
            "is_favorited",
            # "is_in_shopping_cart",
        )

    def get_is_favorited(self, queryset, value):
        # if self.request.user.is_authenticated and value:
        #     return queryset.filter(user=self.request.user)
        return queryset

    # def get_is_in_shopping_cart(self, queryset, value):
    #     """   """