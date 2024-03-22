from django.contrib.auth.models import AbstractUser

from django.db import models

"""Обязательные поля для пользователя:

логин,
пароль,
email,
имя,
фамилия.

Уровни доступа пользователей:

гость (неавторизованный пользователь),
авторизованный пользователь,
администратор.
"""


class CustomUser(AbstractUser):
    ADMIN = "admin"
    GUEST = "guest"
    USER = "user"
    MODERATOR = "moderator"

    USER_TYPE = (
        (GUEST, "Гость"),
        (USER, "Авторизованный пользователь"),
        (ADMIN, "Администратор"),
        (MODERATOR, "модератор"),
    )
    # username = models.CharField(
    #     verbose_name="Логин",
    #     help_text="Укажите логин",
    #     unique=True,
    #     max_length=150
    # )
    # email = models.EmailField(verbose_name="E-mail", unique=True)
    # first_name = models.CharField(verbose_name="Имя", blank=True, max_length=150)
    # last_name = models.CharField(verbose_name="Фамилия", blank=True, max_length=150)

    user_type = models.CharField(
        verbose_name="Уровень доступа", choices=USER_TYPE, default=USER, max_length=20
    )

    class Meta:
        verbose_name = "пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ("username",)

    @property
    def is_admin(self):
        return self.is_staff or self.user_type == CustomUser.ADMIN

    @property
    def is_moderator(self):
        return self.user_type == CustomUser.MODERATOR

    def __str__(self):
        return f"{self.username}"
