# Foodgram

### Проект доступен по адресу: http://158.160.77.129:8888/

## Описание
«Фудграм» — сайтом, на котором пользователи будут публиковать рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Пользователям сайта также будет доступен сервис «Список покупок». Он позволит создавать список продуктов, которые нужно купить для приготовления выбранных блюд.

## Стек технологий
- Python
- Django
- Django REST Framework
- PostgreSQL
- Docker
- Github Actions

## Для запуска на сервере :
1. На сервере создайте директорию foodgram;
2. Скопируйте из репозитория файлы, расположенные в директории infra:
    - docker-compose.yml
3. В директории foodgram создайте файл .env (пустой)
4. Файл .env должен быть заполнен следующими данными:
   - POSTGRES_USER=django_user
   - POSTGRES_PASSWORD=mysecretpassword
   - POSTGRES_DB=django
   - DB_NAME=foodgram 
   - DB_HOST=db
   - DB_PORT=5432
   - SECRET_KEY=Key
   - ALLOWED_HOSTS=127.0.0.1 localhost
   - DEBUG=False
   - TEST_DATABASES=True
 5. В директории infra следует выполнить команды:
```
docker-compose up -d
docker-compose exec backend python manage.py makemigrations
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py collectstatic --no-input
```
6. Для создания суперпользователя, выполните команду:
```
docker-compose exec backend python manage.py createsuperuser
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
 ### Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone git@github.com:Master1941/foodgram-project-react.git

```

```
cd backend
```

Cоздать и активировать виртуальное окружение:

```
python -m venv env
```

* Если у вас Linux/macOS

    ```
    source env/bin/activate
    ```

* Если у вас windows

    ```
    source env/scripts/activate
    ```

```
python -m pip install --upgrade pip
```

Установить зависимости из файла requirements.txt:

```
pip install -r requirements.txt
```

Выполнить миграции:

```
python manage.py migrate
```

Запустить проект:

```
python manage.py runserver
```
