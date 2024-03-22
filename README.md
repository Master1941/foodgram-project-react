# praktikum_new_diplom
```
Запустите заготовку проекта

Репозиторий foodgram-project-react, склонируйте его к себе на компьютер.

Затем, находясь в папке infra, выполните команду docker-compose up.

По адресу http://localhost изучите фронтенд веб-приложения,
по адресу http://localhost/api/docs/ — спецификацию API. 
```

план "разработки Futgram"

1 создать ветки для разработки
  - для проекта Dev
  - для обвязки (пока не забыл настроить докер) Infra
  - ветка общая для проверки работы
  - комитить стабильные версии кода , писать понятные коммиты
  - 

2 пока не забыл как настроить докер nginx gunicorn
  - докер nginx gunicorn
  - записать секреты
  - 

3 создать приложение foodgram
 - выписать все Urls 
 - написать модели
 - юзера 
 - регистрация
 - вьюхи
 - использовать логи (57 минута вебинара )
 - использовать типизацию
 - 

4 написать тесты 5 шт 
 - все юрл поднялись проверить статусы
 - что приложение поднялось
 - 

5 добавить 
 - валилацию 
 - пагинацию 
 - сортировку
 - написать READMI.md
 - env.exsampele рабочии левые ключи
 - 

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