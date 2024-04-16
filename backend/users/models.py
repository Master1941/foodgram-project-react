"""Обязательные поля для пользователя:

логин, (string <= 150 characters
пароль,
email,
имя,
фамилия.

Уровни доступа пользователей:

гость (неавторизованный пользователь),
авторизованный пользователь,
администратор.
"""

from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models

from food.constants import (EMAIL_MAX_LENGTH, FIRST_NAME_MAX_LENGTH,
                            LAST_NAME_MAX_LENGTH, PASSWORD_MAX_LENGTH,
                            USERNAME_MAX_LENGTH)

username_validator = RegexValidator(
    regex=r"^[\w.@+-]+$",
    message="""Имя пользователя должно содержать только буквы,
        цифры или символы: .@+-""",
    code="invalid_username",
)


class CustomUser(AbstractUser):

    username = models.CharField(
        "Логин",
        help_text="Укажите логин",
        unique=True,
        max_length=USERNAME_MAX_LENGTH,
        validators=[username_validator],
    )
    email = models.EmailField(
        "E-mail",
        unique=True,
        max_length=EMAIL_MAX_LENGTH,
    )
    first_name = models.CharField(
        "Имя",
        max_length=FIRST_NAME_MAX_LENGTH,
    )
    last_name = models.CharField(
        "Фамилия",
        max_length=LAST_NAME_MAX_LENGTH,
    )
    password = models.CharField(
        "Пароль",
        max_length=PASSWORD_MAX_LENGTH,
    )

    class Meta:

        verbose_name = "пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ("username",)

    def __str__(self):
        return f"{self.username}"
