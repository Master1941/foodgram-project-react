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
