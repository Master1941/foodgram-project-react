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
    ReadOnlyField,
    # CharField,
    # SlugRelatedField,
    # получить строковые представления связанных объектов
    # и передать их в указанное поле вместо id.
    ValidationError,
    # CurrentUserDefault,
    SerializerMethodField,  # для создания дополнительных полей
    # Field,
)
from rest_framework.validators import UniqueTogetherValidator
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
    """Серилизатор"""

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

    def create(self, validated_data):
        """Создание нового пользователя"""
        # return User.objects.create_user(**validated_data)


class SubscriptionsSerializer(ModelSerializer):
    """Серилизатор пользователей, на которых подписан текущий пользователь.
    В выдачу добавляются рецепты.."""
    email = ReadOnlyField(source='subscribed.email')
    id = ReadOnlyField(source='subscribed.id')
    username = ReadOnlyField(source='subscribed.username')
    first_name = ReadOnlyField(source='subscribed.first_name')
    last_name = ReadOnlyField(source='subscribed.last_name')
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
            "is_subscribed",  # Подписан ли текущий пользователь на этого
            "recipes",  # Array of objects (RecipeMinified)
                # "id": 0,
                # "name": "string",
                # "image": "http://foodgram.example.org/media/recipes/images/image.jpeg",
                # "cooking_time": 1
            "recipes_count",  # Общее количество рецептов пользователя
        )
        # validators = [
        #     UniqueTogetherValidator(
        #         queryset=Subscription.objects.all(),
        #         fields=("user", "subscribed_user"),
        #         message=("Вы уже подписаны на этого автора!"),
        #     )
        # ]

    # def validate_following(self, value):
    #     """Запрет подписки на самого себя."""

    #     if value == self.context["request"].user:
    #         raise ValidationError("Нельзя подписаться на самого себя!")
    #     return value

    def get_is_subscribed(self, obj):
        """поле отображает подписки пользователя. """
        user = self.context.get("request").user
        if not user.is_anonymous:
            return Subscription.objects.filter(user=user, author=obj).exists()
        return False

    def get_recipes(self, obj):
        """мини список рецертов пользователя. """
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        recipes = Recipe.objects.filter(author=obj.subscribed)
        if limit and limit.isdigit():
            recipes = recipes[:int(limit)]
        return RecipeMinifiedSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        """Общее количество рецептов пользователя"""
        return Recipe.objects.filter(author=obj.subscribed).count()


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


class RecipeIngredientSerializer(ModelSerializer):
    """сериализатор  ингредиентов с количеством для Pecipe."""

    id = ReadOnlyField(source="ingredient.id", read_only=True)
    name = ReadOnlyField(source="ingredient.name", read_only=True)
    measurement_unit = ReadOnlyField(
        source="ingredient.measurement_unit", read_only=True
    )
    amount = ReadOnlyField()

    class Meta:
        model = RecipeIngredient
        fields = ("id", "name", "measurement_unit", "amount")


class RecipeGetSerializer(ModelSerializer):
    """Cериализатор для просмотра рецептов."""

    image = Base64ImageField()  # required=False, allow_null=True)
    tags = TagSerializer(
        many=True,
        read_only=True,
    )

    ingredients = RecipeIngredientSerializer(
        many=True,
        read_only=True,
        source="recipe_ingredient",
    )
    is_favorited = SerializerMethodField()
    is_in_shopping_cart = SerializerMethodField()
    author = UsersSerializer(
        read_only=True,
    )

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

    ingredients = IngredientCreatRecipeSerializize()
    image = Base64ImageField()

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

    # def create(self, validated_data):
    #     """Спринт 10/17 → Тема 1/3: Django Rest Framework → Урок 9/15"""
    #     if "tag" not in self.initial_data:
    #         post = Recipe.objects.create(**validated_data)
    #         return post
    #     tags_data = validated_data.pop("tag")
    #     post = Recipe.objects.create(**validated_data)
    #     for tag_data in tags_data:
    #         tag, _ = Tag.objects.get_or_create(**tag_data)
    #         TagRecipe.objects.create(tag=tag, post=post)
    #     return post

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
