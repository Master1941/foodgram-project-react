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
from django.contrib.auth import get_user_model
from django_filters import FilterSet, filters
from food.models import Ingredient, Recipe, Tag

User = get_user_model()


class RecipeFilter(FilterSet):
    """Фильтрация по полям is_favorited is_in_shopping_cart author tags"""

    tags = filters.ModelMultipleChoiceFilter(
        field_name="tags__slug",
        to_field_name="slug",
        queryset=Tag.objects.all(),
    )

    is_favorited = filters.BooleanFilter(
        method="get_is_favorited",
    )

    class Meta:
        model = Recipe
        fields = (
            "author",
            "tags",
            "is_favorited",
        )

    def get_is_favorited(self, queryset, ыва, ываe):
        if self.request.user.is_authenticated:
            return queryset.filter(favorite__user=self.request.user)
        return queryset


class IngredientFilter(FilterSet):
    """Ищите ингредиенты по полю name регистронезависимо:
    по вхождению в начало названия,
    по вхождению в произвольном месте.
    Сортировка в таком случае должна быть от первых ко вторым."""

    name = filters.CharFilter(method="")

    class Meta:
        model = Ingredient
        fields = ("name",)
