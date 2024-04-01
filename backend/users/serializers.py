# # from rest_framework import serializers
# from rest_framework.serializers import (
#     SerializerMethodField,
#     ModelSerializer,
#     # CharField,
#     ValidationError,
# )
# from rest_framework.validators import UniqueTogetherValidator
# from django.contrib.auth import get_user_model

# from food.models import Subscription, Recipe
# from api.serializers import RecipeFavoriteSerializer

# User = get_user_model()


# class RecipeMinifiedSerializer(ModelSerializer):
#     """Серилизатор рецептов для страници подписок."""

#     class Meta:
#         model = Recipe
#         fields = (
#             "id",
#             "name",
#             "image",
#             "cooking_time",
#         )


# class UsersSerializer(ModelSerializer):
#     """Серилизатор"""

#     is_subscribed = SerializerMethodField()

#     class Meta:
#         model = User
#         fields = (
#             "email",
#             "id",
#             "username",
#             "first_name",
#             "last_name",
#             "is_subscribed",  # есть в гет запросе
#         )

#     def get_is_subscribed(self, obj) -> bool:
#         """Возврвщает False если не подписан на этого пользователя."""
#         request = self.context.get("request")
#         if request is None or request.user.is_anonymous:
#             return False
#         return Subscription.objects.filter(
#             user=request.user,
#             author=obj,
#         ).exists()


# class UserCreateSerializer(ModelSerializer):
#     """Серилизатор"""

#     class Meta:
#         model = User
#         fields = (
#             "email",
#             "username",
#             "first_name",
#             "last_name",
#             "password",
#         )

#     def create(self, validated_data):
#         """Создание нового пользователя"""
#         return User.objects.create_user(**validated_data)


# class SubscriptionSerializer(ModelSerializer):
#     """Серилизатор пользователей, на которых подписан текущий пользователь.
#     В выдачу добавляются рецепты.."""

#     is_subscribed = SerializerMethodField()
#     recipes = RecipeFavoriteSerializer(
#         many=True,
#         read_only=True,
#         source="recipe_ingredient",
#     )
#     recipes_count = SerializerMethodField()

#     class Meta:
#         model = User
#         fields = (
#             "email",
#             "id",
#             "username",
#             "first_name",
#             "last_name",
#             "is_subscribed",  # Подписан ли текущий пользователь на этого
#             "recipes",  # Array of objects (RecipeMinified)
#             # "id": 0,
#             # "name": "string",
#             # "image": "http://foodgram.example.org/media/recipes/images/image.jpeg",
#             # "cooking_time": 1
#             "recipes_count",  # Общее количество рецептов пользователя
#         )
#         validators = [
#             UniqueTogetherValidator(
#                 queryset=Subscription.objects.all(),
#                 fields=("user", "subscribed_user"),
#                 message=("Вы уже подписаны на этого автора!"),
#             )
#         ]

#     def validate_following(self, value):
#         """Запрет подписки на самого себя."""

#         if value == self.context["request"].user:
#             raise ValidationError("Нельзя подписаться на самого себя!")
#         return value

#     def get_is_subscraiber(self, obj):
#         """ """
#         user = self.context.get("request").user
#         if not user.is_anonymous:
#             return Subscription.objects.filter(user=user, author=obj).exists()
#         return False

#     def get_recipes(self):
#         """ """

#     def get_recipes_count(self):
#         """Общее количество рецептов пользователя"""

