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

from django.contrib.auth import get_user_model
from django.db import transaction
from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework.serializers import (
    IntegerField,
    ModelSerializer,
    PrimaryKeyRelatedField,
    ReadOnlyField,
    SerializerMethodField,
    ValidationError,
)

from api.fields import Base64ImageField
from food.models import (
    Favourites,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingList,
    Subscription,
    Tag,
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


class MeUsersSerializer(UserSerializer):
    """Серилизатор пользователей."""

    is_subscribed = SerializerMethodField()

    class Meta(UserSerializer.Meta):
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
        )
        read_only_fields = ("is_subscribed",)

    def get_is_subscribed(self, obj) -> bool:
        """Возврвщает False если не подписан на этого пользователя."""

        user = self.context.get("request").user
        if user.is_anonymous:
            return False
        return Subscription.objects.filter(
            user=user,
            subscribed=obj,
        ).exists()


class MeUserCreateSerializer(UserCreateSerializer):
    """Серилизатор"""

    class Meta(MeUsersSerializer.Meta):
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "password",
        )


class SubscriptionsSerializer(MeUsersSerializer):
    """Серилизатор пользователей, на которых подписан текущий пользователь.
    В выдачу добавляются рецепты.
    # recipes_limit	- Количество объектов внутри поля recipes."""

    recipes = SerializerMethodField()
    recipes_count = SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "recipes",
            "recipes_count",
        )

    def get_recipes(self, obj):
        """мини список рецертов пользователя."""
        request = self.context.get("request")
        limit = request.GET.get("recipes_limit")
        recipes = Recipe.objects.filter(author=obj)
        if limit and limit.isdigit():
            recipes = recipes[: int(limit)]
        return RecipeMinifiedSerializer(
            recipes,
            many=True,
            context={"request": self.context.get("request")},
        ).data

    def get_recipes_count(self, obj):
        """Общее количество рецептов пользователя"""

        # Получать подписки текущего пользователя
        subscriptions = Subscription.objects.filter(user=obj)
        # Получить список пользователей, на которых подписан пользователь
        subscribed_users = subscriptions.values_list("subscribed", flat=True)
        # Подсчитывайте рецепты, созданные подписанными пользователями
        return Recipe.objects.filter(author__in=subscribed_users).count()

    def validate_following(self, value):
        """
        Запрет подписки на самого себя.
        """
        if value == self.context["request"].user:
            raise ValidationError("Нельзя подписаться на самого себя!")
        return value


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
    author = MeUsersSerializer()

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

    def get_is_favorited(self, obj) -> bool:
        """Рецепт находиться в избраном."""
        request = self.context.get("request")
        if request is None or request.user.is_anonymous:
            return False
        return Favourites.objects.filter(
            user=request.user,
            recipe=obj,
        ).exists()

    def get_is_in_shopping_cart(self, obj) -> bool:
        """Рецепт находиться в списке покупок."""
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

    class Meta:
        model = RecipeIngredient
        fields = (
            "id",
            "amount",
        )


class RecipeCreatSerializer(ModelSerializer):
    """Для сохранения ингредиентов и тегов рецепта потребуется
    переопределить методы create и update в ModelSerializer."""

    ingredients = IngredientCreatRecipeSerializize(
        many=True,
        source="recipe_ingredient",
    )
    image = Base64ImageField()
    tags = PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
    )

    class Meta:
        model = Recipe
        fields = (
            "ingredients",
            "tags",
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

    def validate(self, attrs):
        """Проверка на соответствие тегов и ингредиентов"""
        ingredients_list = []
        ingredients = attrs.get("recipe_ingredient")
        tags = attrs.get("tags")
        if not tags or len(tags) == 0:
            raise ValidationError("Рецепт должен иметь хотя бы один тег.")
        if not ingredients or len(ingredients) == 0:
            raise ValidationError("Необходимо указать хотя бы один ингредиент")
        for ingredient in ingredients:
            if ingredient.get('amount') < 1:
                raise ValidationError(
                    'Количество ингредиента не может быть меньше 1'
                )
            if not Ingredient.objects.filter(id=ingredient.get('id')).exists():
                raise ValidationError(f'Ингредиент{ingredient} не существует.')
            if ingredient.get('id') in ingredients_list:
                raise ValidationError(
                    f'В рецепте два одинаковых ингредиента {ingredient}'
                )
            ingredients_list.append(ingredient.get('id'))

        tags = attrs.get('tags')
        if len(set(tags)) != len(tags):
            raise ValidationError("Теги не должны повторяться.")
        for tag in tags:
            if not Ingredient.objects.filter(id=tag.get('id')).exists():
                raise ValidationError(f'Ингредиент{tag} не существует.')
        return attrs

    def create_ingredients(self, recipe, ingredients):
        """Метод для добавления ингредиентов при создания/изменения рецепта."""

        recipe_ingredient_objects = []
        for ingredient in ingredients:
            amount = ingredient["amount"]
            ingredient = get_object_or_404(
                Ingredient,
                pk=ingredient["id"],
            )
            recipe_ingredient_objects.append(
                RecipeIngredient(
                    recipe=recipe,
                    ingredient=ingredient,
                    amount=amount,
                )
            )
        RecipeIngredient.objects.bulk_create(recipe_ingredient_objects)

    @transaction.atomic
    def create(self, validated_data):

        ingredients_data = validated_data.pop("recipe_ingredient")
        tags_data = validated_data.pop("tags")
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags_data)
        for tag in tags_data:
            tag_obj = get_object_or_404(Tag, id=tag.id)
            recipe.tags.add(tag_obj)
        self.create_ingredients(recipe, ingredients_data)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        """Согласно спецификации, обновление рецептов должно
        быть реализовано через PUT, значит, при редактировании все поля
          модели рецепта должны полностью перезаписываться."""

        ingredients_data = validated_data.pop("recipe_ingredient")
        tags_data = validated_data.pop("tags")
        instance.tags.set(tags_data)
        RecipeIngredient.objects.filter(recipe=instance).delete()
        super().update(instance, validated_data)
        self.create_ingredients(instance, ingredients_data)
        instance.save()
        return instance
