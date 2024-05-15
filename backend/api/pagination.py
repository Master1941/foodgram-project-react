from rest_framework.pagination import PageNumberPagination


class CustomPageNumberPagination(PageNumberPagination):
    """Переопределить название поля,
    отвечающего за количество результатов в выдаче."""

    page_size_query_param = "limit"
    page_size = 6
