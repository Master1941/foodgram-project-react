# Проверим, что анонимному пользователю доступна главная страница проекта.
# test_routes.py
from http import HTTPStatus
import pytest
from django.urls import reverse


@pytest.mark.parametrize(
    "name",  # Имя параметра функции.
    # Значения, которые будут передаваться в name.
    ("api:users", "api:recipe", "api:tags", "api:ingredients"),
)
# Указываем имя изменяемого параметра в сигнатуре теста.
def test_pages_availability_for_anonymous_user(client, name):
    """тест всех адресов, доступныч для анонимных пользователей."""
    url = reverse(name)  # Получаем ссылку на нужный адрес.
    response = client.get(url)  # Выполняем запрос.
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize("name", ("api:users", "api:recipe", "api:tags", "api:ingredients"))
def test_pages_availability_for_auth_user(not_author_client, name):
    """Тестирование доступности страниц для авторизованного пользователя."""
    url = reverse(name)
    response = not_author_client.get(url)
    assert response.status_code == HTTPStatus.OK


# Добавляем к тесту ещё один декоратор parametrize; в его параметры
# нужно передать фикстуры-клиенты и ожидаемый код ответа для каждого клиента.
@pytest.mark.parametrize(
    # parametrized_client - название параметра,
    # в который будут передаваться фикстуры;
    # Параметр expected_status - ожидаемый статус ответа.
    "parametrized_client, expected_status",
    # В кортеже с кортежами передаём значения для параметров:
    (
        ("not_author_client", HTTPStatus.NOT_FOUND),
        ("author_client", HTTPStatus.OK),
    ),
)
# нужно создать обьект в бд
# Параметризуем тестирующую функцию:
@pytest.mark.parametrize(
    "name",
    ("api:users", "api:recipe", "api:tags", "api:ingredients"),
)
def test_pages_availability_for_author(
    parametrized_client,
    name,
    note,
    expected_status,
):
    url = reverse(name, args=(note.slug,))
    # Делаем запрос от имени клиента parametrized_client:
    response = parametrized_client.get(url)
    # Ожидаем ответ страницы, указанный в expected_status:
    assert response.status_code == expected_status
