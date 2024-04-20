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
import django_filters
from django.contrib.auth import get_user_model
from django.db.models import Q
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
    is_in_shopping_cart = filters.BooleanFilter(
        method="filter_is_in_shopping_cart",
    )
    is_favorited = filters.BooleanFilter(
        method="filter_is_favorited",
    )

    class Meta:
        model = Recipe
        fields = (
            "author",
            "tags",
            "is_favorited",
            "is_in_shopping_cart",
        )

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if self.request.user.is_authenticated:
            return queryset.filter(shopping_list__user=self.request.user)
        return queryset

    def filter_is_favorited(self, queryset, name, value):
        if self.request.user.is_authenticated:
            return queryset.filter(favorite__user=self.request.user)
        return queryset


class IngredientFilter(django_filters.FilterSet):
    """Ищите ингредиенты по полю name регистронезависимо:
    по вхождению в начало названия,
    по вхождению в произвольном месте.
    Сортировка в таком случае должна быть от первых ко вторым."""

    name = django_filters.CharFilter(method="filter_by_name")

    class Meta:
        model = Ingredient
        fields = ["name"]

    def filter_by_name(self, queryset, name, value):
        return queryset.filter(
            Q(name__istartswith=value) | Q(name__icontains=value)
        )
