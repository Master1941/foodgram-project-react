"""
Пагинация
Для реализации пагинации воспользуйтесь стандартным пагинатором DRF.
Вам нужно будет лишь переопределить название поля,
отвечающего за количество результатов в выдаче.
"""

from rest_framework.pagination import PageNumberPagination


class CustomPageNumberPagination(PageNumberPagination):
    """Переопределить название поля,
    отвечающего за количество результатов в выдаче."""

    page_size_query_param = "limit"

    # Количество объектов на странице рецептов пользователей подписок
    page_size = 6
    # recipes_limit	  # Количество объектов внутри поля recipes.
