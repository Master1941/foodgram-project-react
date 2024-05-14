from django.contrib.auth import get_user_model
from django.db import transaction
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework.serializers import (IntegerField,
                                        ModelSerializer,
                                        PrimaryKeyRelatedField, ReadOnlyField,
                                        SerializerMethodField, ValidationError)

from api.fields import Base64ImageField
from food.models import (Favourites, Ingredient, Recipe, RecipeIngredient,
                         ShoppingList, Subscription, Tag)

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

        return Recipe.objects.filter(author=obj).count()


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
            if ingredient.get("amount") < 1:
                raise ValidationError(
                    "Количество ингредиента не может быть меньше 1"
                )
            if not Ingredient.objects.filter(id=ingredient.get("id")).exists():
                raise ValidationError(f"Ингредиент{ingredient} не существует.")
            if ingredient.get("id") in ingredients_list:
                raise ValidationError(
                    f"В рецепте два одинаковых ингредиента {ingredient}"
                )
            ingredients_list.append(ingredient.get("id"))

        if len(set(tags)) != len(tags):
            raise ValidationError("Теги не должны повторяться.")
        for tag in tags:
            if not Ingredient.objects.filter(id=tag.id).exists():
                raise ValidationError(f"тэг {tag} не существует.")
        return attrs

    def create_ingredients(self, recipe, ingredients):
        """Метод для добавления ингредиентов при создания/изменения рецепта."""

        recipe_ingredient_objects = []
        for ingredient in ingredients:
            amount = ingredient["amount"]
            ingredient_id = ingredient['id']
            recipe_ingredient_objects.append(
                RecipeIngredient(
                    recipe=recipe,
                    ingredient_id=ingredient_id,
                    amount=amount,
                )
            )
        RecipeIngredient.objects.bulk_create(recipe_ingredient_objects)

    def create_tags(self, recipe, tags_data):
        """Метод для добавления tags при создания/изменения рецепта."""

        recipe.tags.set(tags_data)

    @transaction.atomic
    def create(self, validated_data):

        ingredients_data = validated_data.pop("recipe_ingredient")
        tags_data = validated_data.pop("tags")
        recipe = Recipe.objects.create(**validated_data)
        self.create_tags(recipe, tags_data)
        self.create_ingredients(recipe, ingredients_data)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        """Согласно спецификации, обновление рецептов должно
        быть реализовано через PUT, значит, при редактировании все поля
          модели рецепта должны полностью перезаписываться."""

        ingredients_data = validated_data.pop("recipe_ingredient")
        tags_data = validated_data.pop("tags")
        RecipeIngredient.objects.filter(recipe=instance).delete()
        super().update(instance, validated_data)
        self.create_tags(instance, tags_data)
        self.create_ingredients(instance, ingredients_data)
        return instance
