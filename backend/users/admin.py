"""
Как должна быть настроена админка
В интерфейс админ-зоны нужно вывести необходимые поля моделей и настроить фильтры:

вывести все модели с возможностью редактирования и удаление записей;
для модели пользователей добавить фильтр списка по email и имени пользователя;
для модели рецептов:
в списке рецептов вывести название и имя автора рецепта;
добавить фильтры по автору, названию рецепта, тегам;
на странице рецепта вывести общее число добавлений этого рецепта в избранное;
для модели ингредиентов:
в список вывести название ингредиента и единицы измерения;
добавить фильтр по названию.
"""

from django.contrib import admin
from food.models import Recipe, Tag, Ingredient


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "color_code", "slug")


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ("name", "quantity", "unit")


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ("title", "author")
    list_filter = ("author", "title", "tags")
