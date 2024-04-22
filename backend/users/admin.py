from django.contrib import admin

from food.models import (Favourites, Ingredient, Recipe, RecipeIngredient,
                         ShoppingList, Subscription, Tag)
from users.models import CustomUser

admin.site.empty_value_display = "Не задано"


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
    )
    list_filter = (
        "email",
        "username",
    )


class RecipeInLine(admin.TabularInline):

    model = RecipeIngredient
    extra = 2


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "author",
    )
    list_filter = (
        "author",
        "name",
        "tags",
    )
    search_fields = (
        "name",
        "text",
    )
    filter_horizontal = ("ingredients",)
    inlines = (RecipeInLine,)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "measurement_unit",
    )
    list_filter = (
        "name",
    )


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "color",
        "slug",
    )
    list_filter = ("name",)


@admin.register(Favourites)
class FavouritesAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "recipe",
    )
    search_fields = ("user__username",)


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "subscribed",
    )
    search_fields = (
        "user__username",
        "subscribed__username",
    )


@admin.register(ShoppingList)
class ShoppingListAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "user",
        "recipe",
    )
    search_fields = (
        "user__username",
        "recipe__name",
    )
