from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from food.constants import (COLOR_CODE_MAX_LENGTH, FIELD_MAX_AMOUNT,
                            FIELD_MAX_TIME, FIELD_MIN_AMOUNT, FIELD_MIN_TIME,
                            NAME_MAX_LENGTH, SLAG_LEN, UNIT_MAX_LENGTH)

User = get_user_model()


class Tag(models.Model):
    """Тег
    Атрибуты модели:
    Название.
    Цветовой код, например, #49B64E.
    Slug.
    Все поля обязательны для заполнения и уникальны.
    """

    name = models.CharField(
        "Название",
        max_length=NAME_MAX_LENGTH,
        unique=True,
    )
    color = models.CharField(
        "Цветовой код",
        max_length=COLOR_CODE_MAX_LENGTH,
    )
    slug = models.SlugField(
        "Слаг",
        max_length=SLAG_LEN,
    )

    class Meta:
        ordering = ("name",)
        verbose_name = "Тег"
        verbose_name_plural = "Теги"

    def __str__(self):
        return f"{self.name}"


class Ingredient(models.Model):
    """Ингредиент
    Данные об ингредиентах должны храниться в нескольких связанных таблицах.
    На стороне пользователя ингредиент должен содержать следующие атрибуты:
    Название.
    Количество.
    Единицы измерения.
    Все поля обязательны для заполнения.
    """

    name = models.CharField(
        "Название",
        max_length=NAME_MAX_LENGTH,
    )
    measurement_unit = models.CharField(
        "Единицы измерения",
        max_length=UNIT_MAX_LENGTH,
    )

    class Meta:

        ordering = ("name",)
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"
        constraints = [
            models.UniqueConstraint(
                fields=["name", "measurement_unit"],
                name="unique_name_measurement_unit",
            )
        ]

    def __str__(self):
        return f"{self.name}"


class Recipe(models.Model):
    """Рецепт
    Атрибуты модели:
    Автор публикации (пользователь).
    Название.
    Картинка.
    Текстовое описание.
    Ингредиенты — продукты для приготовления блюда по рецепту.
                    Множественное поле с выбором из предустановленного списка
                    и с указанием количества и единицы измерения.
    Тег. Можно установить несколько тегов на один рецепт.
    Время приготовления в минутах.
    Все поля обязательны для заполнения.
    """

    author = models.ForeignKey(
        User,
        verbose_name="Автор",
        on_delete=models.CASCADE,
    )
    name = models.CharField(
        "Название",
        max_length=NAME_MAX_LENGTH,
    )
    image = models.ImageField(
        upload_to="images/",
        verbose_name="Картинка, закодированная в Base64",
    )
    text = models.TextField("Описание")
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name="Список ингредиентов",
        through="RecipeIngredient",
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name="Список id тегов",
    )
    cooking_time = models.IntegerField(
        "Время приготовления",
        help_text="введите время приготовления в минутах",
        validators=[
            MinValueValidator(
                FIELD_MIN_TIME,
                f"Минимальное время приготовления {FIELD_MIN_TIME}",
            ),
            MaxValueValidator(
                FIELD_MAX_TIME,
                f"Минимальное время приготовления {FIELD_MAX_TIME}",
            ),
        ],
    )

    class Meta:
        default_related_name = "pecipes"
        ordering = ("name",)
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"
        constraints = (
            models.UniqueConstraint(
                fields=("name", "author"),
                name="unique_for_author",
            ),
        )

    def __str__(self):
        return f"{self.name}"


class RecipeIngredient(models.Model):
    """Связывает модели рецептов и ингридиентов
    и указывает кол-во ингридиента."""

    recipe = models.ForeignKey(
        Recipe,
        related_name="recipe_ingredient",
        verbose_name="рецепт",
        on_delete=models.CASCADE,
    )
    ingredient = models.ForeignKey(
        Ingredient,
        related_name="recipe_ingredient",
        verbose_name="ингредиент",
        on_delete=models.CASCADE,
    )
    amount = models.FloatField(
        "Количество",
        validators=[
            MinValueValidator(
                FIELD_MIN_AMOUNT,
                f"Ингредиентов должна быть не меньше {FIELD_MIN_AMOUNT}.",
            ),
            MaxValueValidator(
                FIELD_MAX_AMOUNT,
                f"Ингредиентов должна быть не более {FIELD_MAX_AMOUNT}.",
            ),
        ],
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["ingredient", "recipe"],
                name="unique_ingredient_recipe",
            )
        ]

    def __str__(self):
        return f"{self.ingredient}{self.amount} "


class ShoppingList(models.Model):
    """Список покупок"""

    user = models.ForeignKey(
        User,
        verbose_name="Пользователь",
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name="Рецепт",
        on_delete=models.CASCADE,
    )

    class Meta:
        ordering = ("recipe",)
        verbose_name = "Покупка"
        verbose_name_plural = "Покупки"
        default_related_name = "shopping_list"
        constraints = (
            models.UniqueConstraint(
                fields=["user", "recipe"],
                name="unique_user_recipe_shoppgng_list",
            ),
        )

    def __str__(self):
        return f"{self.recipe}"


class Subscription(models.Model):
    """ПОДПИСКИ"""

    user = models.ForeignKey(
        User,
        related_name="user",
        verbose_name="Пользователь",
        on_delete=models.CASCADE,
    )
    subscribed = models.ForeignKey(
        User,
        related_name="subscribed",
        verbose_name="Блогеры",
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        constraints = (
            models.UniqueConstraint(
                fields=("subscribed", "user"),
                name="unique_subscribed_user",
            ),
        )

    def clean(self):
        if self.user == self.subscribed:
            raise ValidationError("Вы не можете подписаться на самого себя.")

    def __str__(self):
        return f"{self.user} подписался на {self.subscribed}"


class Favourites(models.Model):
    """Избранные рецепты."""

    user = models.ForeignKey(
        User,
        verbose_name="Пользователь",
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="favorite",
    )

    class Meta:
        verbose_name = "Избранный рецепт"
        verbose_name_plural = "Избранные рецепты"
        constraints = (
            models.UniqueConstraint(
                fields=("user", "recipe"),
                name="unique_user_recipe_favourites",
            ),
        )

    def __str__(self):
        return f"{self.recipe.name}"
