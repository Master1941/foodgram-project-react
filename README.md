# Foodgram

### Проект доступен по адресу: http://158.160.77.129:8888/

## Описание
    «Фудграм» — сайтом, на котором пользователи будут публиковать рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Пользователям сайта также будет доступен сервис «Список покупок». Он позволит создавать список продуктов, которые нужно купить для приготовления выбранных блюд.

## Стек технологий
    [![Python](https://img.shields.io/badge/-Python-464646?style=flat-square&logo=Python)](https://www.python.org/)
    [![Django](https://img.shields.io/badge/-Django-464646?style=flat-square&logo=Django)](https://www.djangoproject.com/)
    [![Django REST Framework](https://img.shields.io/badge/-Django%20REST%20Framework-464646?style=flat-square&logo=Django%20REST%20Framework)](https://www.django-rest-framework.org/)
    [![PostgreSQL](https://img.shields.io/badge/-PostgreSQL-464646?style=flat-square&logo=PostgreSQL)](https://www.postgresql.org/)
    [![Nginx](https://img.shields.io/badge/-NGINX-464646?style=flat-square&logo=NGINX)](https://nginx.org/ru/)
    [![gunicorn](https://img.shields.io/badge/-gunicorn-464646?style=flat-square&logo=gunicorn)](https://gunicorn.org/)
    [![docker](https://img.shields.io/badge/-Docker-464646?style=flat-square&logo=docker)](https://www.docker.com/)
    [![GitHub%20Actions](https://img.shields.io/badge/-GitHub%20Actions-464646?style=flat-square&logo=GitHub%20actions)](https://github.com/features/actions)


## Для запуска на сервере :
1. На сервере создайте директорию foodgram:
    ```
    mkdir foodgram
    ```
2. Скопируйте из репозитория файлы, расположенные в директории infra:
    ```
    scp /путь/к/файлу пользователь@хост:/путь/на/сервере/docker-compose.production.yml
    ```
3. В директории foodgram создайте файл .env
    ```
    sudo nano .env
    ```
4. Файл .env должен быть заполнен следующими данными:
    ```
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
    ```  
    sudo docker compose -f docker-compose.production.yml exec backend python manage.py migrate
    sudo docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic
    sudo docker compose -f docker-compose.production.yml exec backend cp -r /app/collected_static/. /backend_static/static/
    ```
6. Для создания суперпользователя, выполните команду:
    ```
    sudo docker compose -f docker-compose.production.yml exec backend python manage.py createsuperuser
    ```
7. На сервере в редакторе nano откройте конфиг "внешнего" Nginx:
    ```
    sudo nano /etc/nginx/sites-enabled/default
    ```
    
    - Добавим настройки location в секции server
   
    ```
    location / {
        proxy_set_header Host $http_host;
        proxy_pass http://127.0.0.1:8888;
    }
    ```
    
    - Чтобы убедиться, что в конфиге нет ошибок — выполните команду проверки конфигурации:
    
    ```
    sudo nginx -t 
    ```
    
    - Если всё в порядке, то в консоли появится такой ответ:
    ```
    nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
    nginx: configuration file /etc/nginx/nginx.conf test is successful 
    ```
    
    - Перезагрузите конфиг Nginx:
    ```
    sudo service nginx reload 
    ```

## Как запустить проект локально в контейнерах:
    Клонировать репозиторий :

    ```
    git@github.com:Master1941/foodgram-project-react.git
    ``` 
    перейти в дерикторию infra
    ```
    cd foodgram-project-react/infra
    ``` 
    создайте файл .env 
    ```
    touch .env
    ```
    
    ```
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
    Запустить docker-compose:

    ```
    docker-compose up

    ```

    После окончания сборки контейнеров выполнить миграции:

    ```
    docker-compose exec web python manage.py migrate

    ```

    Создать суперпользователя:

    ```
    docker-compose exec web python manage.py createsuperuser

    ```

    Загрузить статику:

    ```
    docker-compose exec web python manage.py collectstatic --no-input 

    ```

    Проверить работу проекта по ссылке:

    ```
    http://localhost/
    ```



## Как запустить проект локально а фронттенд в контейнере:


## Заполнить БД
    
    команда для заполнения из csv файла
    ```
    import_ingredient_csv   - заполняет таблицу с ингредиентами
    import_tags_csv         - заполняет таблицу с тегами
    import_all_csv   - заполняет таблицы пользователя рецептов тегов ингредиентов
    ```
    для проекта локально развернутого в контейнерах из дериктории infra
    ```
    docker-compose exec backend python manage.py import_all_csv
    ```
    для проекта развернутого на сервере из дериктории infra
    ```
    sudo docker compose -f docker-compose.production.yml import_all_csv
    ```
    для проекта развернутого локально из дериктории beckend
    ```
    python manage.py import_all_csv
    ```

# Автор
    Буканов Александр Михайлович
    Python-разработчик (Backend)
    E-mail: abukanov89@bk.ru
    Telegram: @Aleksandr_Bukanov