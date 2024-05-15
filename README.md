# "Продуктовый помощник"

### Проект доступен по адресу: http://158.160.77.129:8888/

## 1. [Описание](#1)
## 2. [Для запуска на сервере](#2)
## 3. [Запустить проект локально](#3)
## 4. [Заполнить БД](#4)
## 5. [Примеры запросов к API](#5)
## 6. [Об авторе](#6)
____
## 1. Описание <a id=1></a>
«Фудграм» — сайтом, на котором пользователи будут публиковать рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Пользователям сайта также будет доступен сервис «Список покупок». Он позволит создавать список продуктов, которые нужно купить для приготовления выбранных блюд.

### Стек технологий: 
[![Python](https://img.shields.io/badge/Python-3776AB?style=plastic&logo=python&logoColor=092E20&labelColor=white
)](https://www.python.org/)
[![Django](https://img.shields.io/badge/django-092E20?style=plastic&logo=django&logoColor=092E20&labelColor=white
)](https://www.djangoproject.com/)
[![Django REST Framework](https://img.shields.io/badge/-Django_REST_framework-DC143C?style=plastic
)](https://www.django-rest-framework.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=plastic&logo=postgresql&labelColor=white
)](https://www.postgresql.org/)
[![Nginx](https://img.shields.io/badge/NGINX-009639?style=plastic&logo=nginx&logoColor=%23009639&labelColor=white
)](https://nginx.org/ru/)
[![gunicorn](https://img.shields.io/badge/Gunicorn-499848?style=plastic&logo=gunicorn&labelColor=white
)](https://gunicorn.org/)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=plastic&logo=docker&labelColor=white
)](https://www.docker.com/)
[![GitHub%20Actions](https://img.shields.io/badge/GitHub_actions-2088FF?style=plastic&logo=githubactions&labelColor=white
)](https://github.com/features/actions)
[![Docker-compose](https://img.shields.io/badge/Docker_compose-2496ED?style=plastic&logo=docker&labelColor=white
)](https://docs.docker.com/compose/)

## Для запуска на сервере: <a id=2></a>
Установите на сервер docker 
Подробно об установке можно узнать на [официальном сайте](https://docs.docker.com/engine/install/).
Поочерёдно выполните на сервере команды для установки Docker и Docker Compose для Linux. 
```bash
sudo apt update
sudo apt install curl
curl -fSL https://get.docker.com -o get-docker.sh
sudo sh ./get-docker.sh
sudo apt install docker-compose-plugin
```
1. На сервере создайте директорию foodgram:
```bash
mkdir foodgram
```
2. Скопируйте из репозитория файлы, расположенные в директории infra:
```bash
scp /путь/к/файлу пользователь@хост:/путь/на/сервере/docker-compose.production.yml
```
3. В директории foodgram создайте файл .env
```bash
sudo nano .env
```
4. Файл .env должен быть заполнен следующими данными:
```python
POSTGRES_USER=django_user
POSTGRES_PASSWORD=mysecretpassword
POSTGRES_DB=django
DB_NAME=foodgram 
DB_HOST=db
DB_PORT=5432
SECRET_KEY=Key
ALLOWED_HOSTS='Здесь указать имя или IP хоста' (Для локального запуска - 127.0.0.1)
DEBUG=False
TEST_DATABASES=False
```
5. Выполняет миграции и сбор статики. В директории infra следует выполнить команды:
```  bash
sudo docker compose -f docker-compose.production.yml exec backend python manage.py migrate
sudo docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic
sudo docker compose -f docker-compose.production.yml exec backend cp -r /app/collected_static/. /backend_static/static/
```
6. Для создания суперпользователя, выполните команду:
```bash
sudo docker compose -f docker-compose.production.yml exec backend python manage.py createsuperuser
```
7. На сервере в редакторе nano откройте конфиг "внешнего" Nginx:
```bash
sudo nano /etc/nginx/sites-enabled/default
```

Добавим настройки location в секции server

```conf
location / {
    proxy_set_header Host $http_host;
    proxy_pass http://127.0.0.1:8888;
}
```

Чтобы убедиться, что в конфиге нет ошибок — выполните команду проверки конфигурации:

```bash
sudo nginx -t 
```

Если всё в порядке, то в консоли появится такой ответ:
```bash
nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
nginx: configuration file /etc/nginx/nginx.conf test is successful 
```

Перезагрузите конфиг Nginx:
```bash
sudo service nginx reload 
```

## Запустить проект локально, а фронтенд в контейнере: <a id=3></a>
Удобно использовать при разработке.
Клонировать репозиторий :
```bash
git clone git@github.com:Master1941/foodgram-project-react.git
```  
создайте файл .env в дериктории `infra_dev`
```bash
touch foodgram-project-react/infra_dev/.env
```
пример заполнения файла .env
```python
POSTGRES_USER=django_user
POSTGRES_PASSWORD=mysecretpassword
POSTGRES_DB=django
DB_NAME=foodgram 
DB_HOST=db
DB_PORT=5432
SECRET_KEY=Key
ALLOWED_HOSTS=127.0.0.1 # Для локального запуска 
DEBUG=True
TEST_DATABASES=True  # SQLite
```
Запустить docker-compose из дериктории `infra_dev`:
```bash
docker-compose up
```
После окончания сборки контейнеров выполнить миграции:
```bash
python manage.py migrate
```
Создать суперпользователя:
```bash
python manage.py createsuperuser
```

## Заполнить БД <a id=4></a>

команда для заполнения из csv файла
```
import_ingredient_csv   - заполняет таблицу с ингредиентами.
import_tags_csv         - заполняет таблицу с тегами.
import_all_csv   - заполняет таблицы пользователя, рецептов, тегов, ингредиентов.
```
для проекта локально развернутого в контейнерах, из дериктории `infra`
```bash
docker-compose exec backend python manage.py import_all_csv
```
для проекта развернутого на сервере, из дериктории `foodgram`
```bash
sudo docker compose -f docker-compose.production.yml import_all_csv
```
для проекта развернутого локально, из дериктории `beckend`
```bash
python manage.py import_all_csv
```
## Примеры запросов к API <a id=5></a>
Документация к API находится по адресу: <http://localhost/api/docs>.

Получение и удаление токена

```
POST /api/auth/token/login/
POST /api/auth/token/logout/
```

Регистрация нового пользователя: 

```
POST /api/users/
```

Получение данных своей учетной записи:

```
GET /api/users/me/
```

Получение страницы пользователя и списка всех пользователей
```
GET /api/users/:id/
GET /api/users/?page=1&limit=3
```

Подписка на пользователя и отписка

```
POST /api/users/:id/subscribe/?recipes_limit=3
DELETE /api/users/:id/subscribe/
```

Подписки пользователя
```
GET /api/users/subscriptions/
```

Получение рецепта и списка рецептов
```
GET /api/recipes/:id/
GET /api/recipes/
```

Создание, обновление и удаление рецепта
```
POST /api/recipes/
PATCH /api/recipes/:id/
DELETE /api/recipes/:id/
```

Добавление рецепта в избранное и удаление из избранного
```
POST /api/recipes/:id/favorite/
DELETE /api/recipes/:id/favorite/
```

Добавление рецепта в список покупок и удаление из списка покупок
```
POST /api/recipes/:id/shopping_cart/
DELETE /api/recipes/:id/shopping_cart/
```

Скачать список покупок
```
GET /api/recipes/download_shopping_cart/
```
# Автор <a id=6></a>
Буканов Александр Михайлович
Python-разработчик (Backend)
E-mail: abukanov89@bk.ru
Telegram: @Aleksandr_Bukanov