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
import webcolors
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from rest_framework.serializers import (
    ModelSerializer,
    ImageField,
    SlugRelatedField,
    ValidationError,
    CurrentUserDefault,
    SerializerMethodField,  # для создания дополнительных полей в сериализаторе, значения которых вычисляются с помощью метода сериализатора.
    ValidationError,
    Field,
)
from rest_framework.validators import UniqueTogetherValidator

from food.models import Tag, Recipe, Ingredient, Subscription

User = get_user_model()


class Base64ImageField(ImageField):
    """ """

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith("data:image"):
            format, imgstr = data.split(";base64,")
            ext = format.split("/")[-1]

            data = ContentFile(base64.b64decode(imgstr), name="temp." + ext)

        return super().to_internal_value(data)


class TagSerializer(ModelSerializer):
    """ """

    class Meta:
        model = Tag
        fields = "__all__"
        read_only_fields = ("__all__",)


class RecipeSerializer(ModelSerializer):
    """ """

    image = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = Recipe
        fields = "__all__"

    def update(self, instance, validated_data):
        instance.name = validated_data.get("name", instance.name)
        instance.color = validated_data.get("color", instance.color)
        instance.birth_year = validated_data.get("birth_year", instance.birth_year)
        instance.image = validated_data.get("image", instance.image)
        if "achievements" in validated_data:
            achievements_data = validated_data.pop("achievements")
            lst = []
            for achievement in achievements_data:
                current_achievement, status = Achievement.objects.get_or_create(
                    **achievement
                )
                lst.append(current_achievement)
            instance.achievements.set(lst)

        instance.save()
        return instance


class IngredientSerializer(ModelSerializer):
    """ """

    class Meta:
        model = Ingredient
        fields = "__all__"


class SubscribeSerializer(ModelSerializer):
    """Серилизатор подписок."""

    user = SlugRelatedField(
        slug_field="username",
        read_only=True,
        default=CurrentUserDefault(),
    )
    subscribed_user = SlugRelatedField(
        slug_field="username",
        queryset=User.objects.all(),
    )

    class Meta:
        model = Subscription
        fields = ("user", "subscribed_user")
        validators = [
            UniqueTogetherValidator(
                queryset=Subscription.objects.all(),
                fields=("user", "subscribed_user"),
                message=("Вы уже подписаны на этого автора!"),
            )
        ]

    def validate_following(self, value):
        """Запрет подписки на самого себя."""

        if value == self.context["request"].user:
            raise ValidationError("Нельзя подписаться на самого себя!")
        return value
