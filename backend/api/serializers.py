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
from django.core.validators import MinValueValidator
from django.shortcuts import get_object_or_404
from django.db import transaction

# from rest_framework.validators import UniqueTogetherValidator
from rest_framework.serializers import (
    ModelSerializer,
    ImageField,
    ReadOnlyField,
    PrimaryKeyRelatedField,
    ValidationError,
    CharField,
    IntegerField,
    # CurrentUserDefault,
    SerializerMethodField,  # для создания дополнительных полей
)
from food.constants import FIELD_MIN_AMOUNT

from food.models import (
    Tag,
    Recipe,
    Ingredient,
    Favourites,
    ShoppingList,
    RecipeIngredient,
    Subscription,
)

User = get_user_model()


class RecipeMinifiedSerializer(ModelSerializer):
    """Серилизатор рецептов для страници подписок и избранного."""

    class Meta:
        model = Recipe
        fields = (
            "id",
            "name",
            "image",
            "cooking_time",
        )


class UsersSerializer(ModelSerializer):
    """Серилизатор пользователей."""

    is_subscribed = SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",  # есть в гет запросе
        )

    def get_is_subscribed(self, obj) -> bool:
        """Возврвщает False если не подписан на этого пользователя."""

        user = self.context.get("request").user
        if user.is_anonymous:
            return False
        return Subscription.objects.filter(
            user=user,
            subscribed=obj,
        ).exists()


class UserCreateSerializer(ModelSerializer):
    """Серилизатор"""

    class Meta:
        model = User
        fields = (
            "email",
            "username",
            "first_name",
            "last_name",
            "password",
        )

    # def create(self, validated_data):
    #     """Создание нового пользователя"""
    #     # return User.objects.create_user(**validated_data)


class SubscriptionsSerializer(ModelSerializer):
    """Серилизатор пользователей, на которых подписан текущий пользователь.
    В выдачу добавляются рецепты.."""

    email = ReadOnlyField(source="subscribed.email")
    id = ReadOnlyField(source="subscribed.id")
    username = ReadOnlyField(source="subscribed.username")
    first_name = ReadOnlyField(source="subscribed.first_name")
    last_name = ReadOnlyField(source="subscribed.last_name")
    is_subscribed = SerializerMethodField()
    recipes = SerializerMethodField()
    recipes_count = SerializerMethodField()

    class Meta:
        model = Subscription
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "recipes",  # "id":  "name": "image": "http:// "cooking_time": 1
            "recipes_count",
        )

    def get_is_subscribed(self, obj) -> bool:
        """Возврвщает False если не подписан на этого пользователя."""
        return True

    def get_recipes(self, obj):
        """мини список рецертов пользователя."""
        request = self.context.get("request")
        limit = request.GET.get("recipes_limit")
        recipes = Recipe.objects.filter(author=obj.subscribed)
        if limit and limit.isdigit():
            recipes = recipes[: int(limit)]
        return RecipeMinifiedSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        """Общее количество рецептов пользователя"""
        return Recipe.objects.filter(author=obj.subscribed).count()


#
#
#


class Base64ImageField(ImageField):
    """Кодирует картинку в строку base64."""

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith("data:image"):
            forma1t, imgstr = data.split(";base64,")
            ext = forma1t.split("/")[-1]

            data = ContentFile(base64.b64decode(imgstr), name="temp." + ext)

        return super().to_internal_value(data)


class TagSerializer(ModelSerializer):
    """Cериализатор модели Tags."""

    class Meta:
        model = Tag
        fields = ("id", "name", "color", "slug")
        read_only_fields = ("__all__",)


class IngredientSerializer(ModelSerializer):
    """Cериализатор модели"""

    class Meta:
        model = Ingredient
        fields = ("id", "name", "measurement_unit")
        read_only_fields = ("__all__",)


class RecipeIngredientSerializer(ModelSerializer):
    """сериализатор  ингредиентов с количеством для Pecipe."""

    id = ReadOnlyField(source="ingredient.id")
    name = ReadOnlyField(source="ingredient.name")
    measurement_unit = ReadOnlyField(source="ingredient.measurement_unit")
    amount = ReadOnlyField()

    class Meta:
        model = RecipeIngredient
        fields = ("id", "name", "measurement_unit", "amount")
        read_only_fields = (
            "id",
            "name",
            "measurement_unit",
        )


class RecipeGetSerializer(ModelSerializer):
    """Cериализатор для просмотра рецептов."""

    image = Base64ImageField()
    tags = TagSerializer(many=True)
    ingredients = RecipeIngredientSerializer(
        many=True,
        source="recipe_ingredient",
    )
    is_favorited = SerializerMethodField()
    is_in_shopping_cart = SerializerMethodField()
    author = UsersSerializer()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "tags",
            "author",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time",
        )
        read_only_fields = ("__all__",)

    def get_is_favorited(self, obj):
        """рецепт в избраном или False"""
        request = self.context.get("request")
        if request is None or request.user.is_anonymous:
            return False
        return Favourites.objects.filter(
            user=request.user,
            recipe=obj,
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        """рецепт в покупках или False"""
        request = self.context.get("request")
        if request is None or request.user.is_anonymous:
            return False
        return ShoppingList.objects.filter(
            user=request.user,
            recipe=obj,
        ).exists()


class IngredientCreatRecipeSerializize(ModelSerializer):
    """Сериализатор RecipeIngredient для создания рецепта"""

    id = IntegerField()
    amount = IntegerField()
    # id = PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    # amount = IntegerField(
    #     write_only=True,
    #     validators=(
    #         MinValueValidator(
    #             limit_value=FIELD_MIN_AMOUNT,
    #             message=(
    #                 f"""Количество ингредиента не может
    #                 быть меньше {FIELD_MIN_AMOUNT}""",
    #             ),
    #         ),
    #     ),
    # )

    class Meta:
        model = RecipeIngredient
        fields = (
            "id",
            "amount",
        )


class RecipeCreatSerializer(ModelSerializer):
    """POST DELET PUT лли PATCH
    Для сохранения ингредиентов и тегов рецепта потребуется
    переопределить методы create и update в ModelSerializer."""

    ingredients = IngredientCreatRecipeSerializize(
        many=True,
        source="recipe_ingredient",
        # write_only=True,
    )
    image = Base64ImageField()
    tags = PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
    )
    # author = UsersSerializer(read_only=True)

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

    def to_representation(self, instance):
        serializer = RecipeGetSerializer(
            instance,
            context={"request": self.context.get("request")},
        )
        return serializer.data

    # def validate(self, data):
    #     """Проверка на соответствие тегов и ингредиентов"""
    #     ingredients = data.get(""recipe_ingredient"")
    #     tags = data.get("tags")

    #     if not ingredients and not tags:
    #         raise ValidationError(
    #             "Необходимо указать хотя бы один ингредиент или тег"
    #         )
    #     base_ingredient = ingredient.id  # .get("id")
    # if RecipeIngredient.objects.filter(
    #     recipe=recipe, ingredient=base_ingredient
    # ).exists():
    #     raise ValidationError(
    #         {"errors": "нельзя добавить одинаковые ингредиенты"}
    #     )

    @transaction.atomic
    def create(self, validated_data):
        """Спринт 10/17 → Тема 1/3: Django Rest Framework → Урок 9/15"""

        ingredients_data = validated_data.pop("recipe_ingredient")
        tags_data = validated_data.pop("tags")
        recipe = Recipe.objects.create(
            **validated_data,
        )
        recipe.tags.set(tags_data)

        for ingredient in ingredients_data:
            amount = ingredient["amount"]
            ingredient_data = get_object_or_404(
                Ingredient,
                pk=ingredient["id"],
            )
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=ingredient_data,
                amount=amount,
            )
        return recipe

    def update(self, instance, validated_data):
        """Согласно спецификации, обновление рецептов должно
        быть реализовано через PUT, значит, при редактировании все поля
          модели рецепта должны полностью перезаписываться.."""

        ingredients_data = validated_data.pop("recipe_ingredient")
        tags_data = validated_data.pop("tags")
        instance.tags.clear()
        instance.tags.set(tags_data)
        RecipeIngredient.objects.filter(recipe=instance).delete()
        super().update(instance, validated_data)

        for ingredient in ingredients_data:
            amount = ingredient["amount"]
            ingredient_data = get_object_or_404(
                Ingredient,
                pk=ingredient["id"],
            )
            RecipeIngredient.objects.create(
                recipe=instance,
                ingredient=ingredient_data,
                amount=amount,
            )
        instance.save()
        return instance
