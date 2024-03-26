from rest_framework import serializers
from rest_framework.serializers import (
    SerializerMethodField,
    ModelSerializer,
    CharField,
)
from django.contrib.auth import get_user_model
from food.constants import (
    EMAIL_MAX_LENGTH,
    USERNAME_MAX_LENGTH,
)

from food.models import Subscription

User = get_user_model()


class UsersSerializer(ModelSerializer):
    """Серилизатор"""

    # is_subscribed = SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            # "is_subscribed",  # есть в гет запросе
        )

    # def get_is_subscraiber(self):
    #     """Возврвщает False если не подписан на этого пользователя."""


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

    def validate_username(self, value):
        if value == "me":
            raise serializers.ValidationError(
                'Имя пользователя "me" запрещено.',
            )
        return value


class SubscriptionSerializer(ModelSerializer):
    """Серилизатор"""

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

    def get_is_subscraiber(self):
        """ """

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
