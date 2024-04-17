"""
В интерфейс админ-зоны нужно вывести необходимые поля моделей и
 настроить фильтры:
    вывести все модели с возможностью редактирования и удаление записей;
    для модели пользователей добавить фильтр списка по email и
      имени пользователя;

    для модели рецептов:
    в списке рецептов вывести название и имя автора рецепта;
    добавить фильтры по автору, названию рецепта, тегам;
    на странице рецепта вывести общее число добавлений этого рецепта в
      избранное;

    для модели ингредиентов:
    в список вывести название ингредиента и единицы измерения;
    добавить фильтр по названию.
    ------------------------------------------------------------------
    В классе IceCreamAdmin можно указать:
какие поля будут показаны на странице списка объектов
 (свойство list_display, это кортеж);
какие поля можно редактировать прямо на странице списка объектов
 (свойство list_editable, кортеж);
search_fields — кортеж с перечнем полей, по которым будет проводиться поиск.
 Форма поиска отображается над списком элементов.
list_filter — кортеж с полями, по которым можно фильтровать записи.
 Фильтры отобразятся справа от списка элементов.
В кортеже list_display_links указывают поля, при клике на которые можно
 перейти на страницу просмотра и редактирования записи.
   По умолчанию такой ссылкой служит первое отображаемое поле.
"""

from django.contrib import admin
from food.models import (
    Favourites,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingList,
    Subscription,
    Tag,
)
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
    # Указываем, для каких связанных моделей нужно включить такой интерфейс:
    filter_horizontal = ("ingredients",)
    # # Добавляем вставку на страницу управления объектом модели Category:
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
