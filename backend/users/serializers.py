from rest_framework import serializers
from rest_framework.serializers import (
    SerializerMethodField,
    ModelSerializer,
    CharField,
    ValidationError,
)
from rest_framework.validators import UniqueTogetherValidator
from django.contrib.auth import get_user_model

# from food.constants import (
#     EMAIL_MAX_LENGTH,
#     USERNAME_MAX_LENGTH,
# )

from food.models import Subscription

User = get_user_model()


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

    def get_is_subscraibed(self, obj) -> bool:
        """Возврвщает False если не подписан на этого пользователя."""
        user = self.context.get("request").user
        if not user.is_anonymous:
            return Subscription.objects.filter(user=user, author=obj).exists()
        return False

    # def create(self, validated_data):
    #     return User.objects.create_user(**validated_data)


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

    # def validate_username(self, value):
    #     if value == "me":
    #         raise serializers.ValidationError(
    #             'Имя пользователя "me" запрещено.',
    #         )
    #     return value

    def create(self, validated_data):
        """Создание нового пользователя"""
        return User.objects.create_user(**validated_data)


class SubscriptionSerializer(ModelSerializer):
    """Серилизатор выводит подписок текущего пользователя."""

    is_subscribed = SerializerMethodField()
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
            "is_subscribed",  # есть в гет запросе
            "recipes",
            "recipes_count",
        )
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

    def get_is_subscraiber(self, obj):
        """ """
        user = self.context.get("request").user
        if not user.is_anonymous:
            return Subscription.objects.filter(user=user, author=obj).exists()
        return False

    def get_recipes(self):
        """ """

    def get_recipes_count(self):
        """ """


class TokenSerializer(ModelSerializer):
    """Серилизатор"""

    username = CharField(required=True)
    confirmation_code = CharField(required=True)

    class Meta:
        model = User
        fields = ("username", "confirmation_code")
