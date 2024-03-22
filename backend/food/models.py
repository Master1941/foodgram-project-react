from django.db import models

from food.constants import MAX

from users.models import CustomUser

User = CustomUser


class Tag(models.Model):
    """Тег
    Атрибуты модели:
    Название.
    Цветовой код, например, #49B64E.
    Slug.
    Все поля обязательны для заполнения и уникальны.
    """

    name = models.CharField(max_length=255, unique=True)
    color_code = models.CharField(max_length=7)
    slug = models.SlugField(unique=True)

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

    name = models.CharField(max_length=255)
    quantity = models.FloatField()
    unit = models.CharField(max_length=50)

    class Meta:

        ordering = ("name",)
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"

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

    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to="images/", null=True, default=None)
    description = models.TextField("Текстовое описание")
    ingredients = models.ManyToManyField(
        Ingredient,
        related_name="recipe",
        verbose_name="рецепт",
        # through="RecipeIngredient"
    )

    tags = models.ManyToManyField(
        Tag,
        related_name="recipe",
        verbose_name="рецепт",
    )
    
    cooking_time = models.IntegerField()

    class Meta:

        ordering = ("title",)
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"

    def __str__(self):
        return f"{self.title}"


class Purchases(models.Model):
    """ПОКУПКИ"""

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

    class Meta:

        ordering = ("recipe",)
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"

    def __str__(self):
        return f"{self.recipe}"


class Subscription(models.Model):
    """ПОДПИСКИ"""

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subscribed_user = models.ForeignKey(
        User, related_name="subscribed_to", on_delete=models.CASCADE
    )

    class Meta:

        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"

    def __str__(self):
        return f"{self.subscribed_user}"


class Favourites(models.Model):
    """ИЗБРАННОЕ"""

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

    class Meta:

        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"

    def __str__(self):
        return f"{self.recipe}"
