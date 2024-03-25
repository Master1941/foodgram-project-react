from rest_framework.serializers import (
    SerializerMethodField,
    Serializer,
    ModelSerializer,
    CharField,
    RegexField,
    EmailField,
)
from django.contrib.auth import get_user_model
from food.constants import (
    EMAIL_MAX_LENGTH,
    USERNAME_MAX_LENGTH,
)

from food.models import Subscription

User = get_user_model()


class UsersSerializer(ModelSerializer):
    """ """

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

    def get_is_subscraiber(self):
        """ """


class SubscribeSerializer(Serializer):
    """ """

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


class TokenSerializer(Serializer):
    """ """

    username = CharField(required=True)
    confirmation_code = CharField(required=True)

    class Meta:
        model = User
        fields = ("username", "confirmation_code")


class UserCreateSerializer(ModelSerializer):
    """ """

    username = RegexField(
        regex=r"^[\w.@+-]+$", max_length=USERNAME_MAX_LENGTH, required=True
    )

    email = EmailField(
        max_length=EMAIL_MAX_LENGTH,
        required=True,
    )

    class Meta:
        model = User
        fields = (
            "username",
            "email",
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
