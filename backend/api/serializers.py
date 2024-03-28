"""
Сериализаторы
При публикации рецепта фронтенд кодирует картинку в строку base64;
 на бэкенде её необходимо декодировать и сохранить как файл.
 Для этого будет удобно создать кастомный тип поля для картинки,
 переопределив метод сериализатора to_internal_value.

Для сохранения ингредиентов и тегов рецепта потребуется переопределить
методы create и update в ModelSerializer.

Согласно спецификации, обновление рецептов должно быть реализовано через PUT,
значит,
при редактировании все поля модели рецепта должны полностью перезаписываться.

Используйте подходящие типы related-полей;
для некоторых данных вам потребуется использовать SerializerMethodField.
"""

import base64
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from rest_framework.serializers import (
    ModelSerializer,
    ImageField,
    StringRelatedField,
    SlugRelatedField,  # получить строковые представления связанных объектов и передать их в указанное поле вместо id.
    ValidationError,
    CurrentUserDefault,
    SerializerMethodField,  # для создания дополнительных полей
    ValidationError,
    Field,
)
from rest_framework.validators import UniqueTogetherValidator

from food.models import Tag, Recipe, Ingredient, Favourites, RecipeIngredient
from users.serializers import UsersSerializer

User = get_user_model()


class Base64ImageField(ImageField):
    """Кодирует картинку в строку base64."""

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith("data:image"):
            format, imgstr = data.split(";base64,")
            ext = format.split("/")[-1]

            data = ContentFile(base64.b64decode(imgstr), name="temp." + ext)

        return super().to_internal_value(data)


class TagSerializer(ModelSerializer):
    """Cериализатор модели Tags."""

    class Meta:
        model = Tag
        fields = ("id", "name", "color", "slug")
        read_only_fields = ("__all__",)


class FavoriteSerializer(ModelSerializer):
    """ """

    class Meta:
        model = Favourites
        fields = (
            "id",
            "name",
            "image",
            "cooking_time",
        )


class RecipeGetSerializer(ModelSerializer):
    """Cериализатор модели"""


class RecipeCreatSerializer(ModelSerializer):
    """Для сохранения ингредиентов и тегов рецепта потребуется
    переопределить методы create и update в ModelSerializer."""

    class Meta:
        model = Recipe
        fields = (
            "ingredients",
            # id": 1123,
            # "amount": 10
            "tags",
            # 1,
            # 2
            "image",
            "name",
            "text",
            "cooking_time",
        )


class IngredientSerializer(ModelSerializer):
    """Cериализатор модели"""

    class Meta:
        model = Ingredient
        fields = ("id", "name", "measurement_unit")


class RecipeSerializer(ModelSerializer):
    """Cериализатор модели"""

    image = Base64ImageField(required=False, allow_null=True)
    tags = StringRelatedField(many=True, read_only=True)
    author = UsersSerializer()
    ingredients = IngredientSerializer()
    is_favorited = SerializerMethodField()
    is_in_shopping_cart = SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "tags",
            # "id": 0,
            # "name": "Завтрак",
            # "color": "#E26C2D",
            # "slug": "breakfast"
            "author",
            # "email": "user@example.com",
            # "id": 0,
            # "username": "string",
            # "first_name": "Вася",
            # "last_name": "Пупкин",
            # "is_subscribed": false
            "ingredients",
            # "id": 0,
            # "name": "Картофель отварной",
            # "measurement_unit": "г",
            # "amount": 1
            "is_favorited",
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time",
        )

    def is_favorited(self):
        """ """

    def is_in_shopping_cart(self):
        """ """

    def create(self, validated_data):
        """Спринт 10/17 → Тема 1/3: Django Rest Framework → Урок 9/15"""
        if "tag" not in self.initial_data:
            post = Recipe.objects.create(**validated_data)
            return post
        tags_data = validated_data.pop("tag")
        post = Recipe.objects.create(**validated_data)
        for tag_data in tags_data:
            tag, _ = Tag.objects.get_or_create(**tag_data)
            TagRecipe.objects.create(tag=tag, post=post)
        return post

    # def update(self, instance, validated_data):
    #     """Для сохранения ингредиентов и тегов рецепта потребуется
    #     переопределить методы create и update в ModelSerializer. """

    #     instance.name = validated_data.get("name", instance.name)
    #     instance.color = validated_data.get("color", instance.color)
    #     instance.birth_year = validated_data.get("birth_year", instance.birth_year)
    #     instance.image = validated_data.get("image", instance.image)
    #     if "achievements" in validated_data:
    #         achievements_data = validated_data.pop("achievements")
    #         lst = []
    #         for achievement in achievements_data:
    #             current_achievement, status = Achievement.objects.get_or_create(
    #                 **achievement
    #             )
    #             lst.append(current_achievement)
    #         instance.achievements.set(lst)

    #     instance.save()
    #     return instance
