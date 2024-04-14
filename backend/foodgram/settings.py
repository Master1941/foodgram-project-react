import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv("SECRET_KEY", "key")

DEBUG = os.getenv("DEBUG", "True") == "True"

ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "127.0.0.1 localhost").split()

print(ALLOWED_HOSTS)

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "django_filters",
    "rest_framework.authtoken",
    "djoser",
    "api.apps.ApiConfig",
    "food.apps.FoodConfig",
    "users.apps.UsersConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "foodgram.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "foodgram.wsgi.application"

TEST_DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

PROD_DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("POSTGRES_DB"),
        "USER": os.getenv("POSTGRES_USER"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD"),
        "HOST": os.getenv("DB_HOST"),
        "PORT": os.getenv("DB_PORT"),
    }
}

if os.getenv("TEST_DATABASES") == "True":
    print("  <SQLite> " * 10)
else:
    print(" <PostgreSQL> " * 10)

DATABASES = (
    TEST_DATABASES
    if os.getenv("TEST_DATABASES", default="False") == "True"
    else PROD_DATABASES
)
# print(DATABASES)

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

LANGUAGE_CODE = "ru-ru"

TIME_ZONE = "Europe/Moscow"

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = (
    BASE_DIR / "collected_static"
)  # из этой дериктории копируем в /backend_static/static/

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

AUTH_USER_MODEL = "users.CustomUser"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

DJOSER = {
    "LOGIN_FIELD": "email",  # авторизация по  email  !!!!!!!!!!!!!!!!!!!!!!!!
    "SEND_ACTIVATION_EMAIL": False,  # Отправлять ли пользователям электронное письмо с активацией после регистрации.
    # 'USER_ID_FIELD': 'id',
    "SERIALIZERS": {
        "user": "api.serializers.MeUsersSerializer",
        "user_create": "api.serializers.MeUserCreateSerializer",
    },
    "PERMISSIONS":{
        'activation': ['rest_framework.permissions.AllowAny'],
        'password_reset': ['rest_framework.permissions.AllowAny'],
        'password_reset_confirm': ['rest_framework.permissions.AllowAny'],
        'set_password': ['djoser.permissions.CurrentUserOrAdmin'],
        'username_reset': ['rest_framework.permissions.AllowAny'],
        'username_reset_confirm': ['rest_framework.permissions.AllowAny'],
        'set_username': ['djoser.permissions.CurrentUserOrAdmin'],
        'user_create': ['rest_framework.permissions.AllowAny'],
        'user_delete': ['djoser.permissions.CurrentUserOrAdmin'],
        # 'user': ['djoser.permissions.CurrentUserOrAdmin'],

        'user': ['rest_framework.permissions.IsAuthenticatedOrReadOnly'],  # <<<
        'user_list': ['rest_framework.permissions.IsAuthenticatedOrReadOnly'],  # <<

        'token_create': ['rest_framework.permissions.AllowAny'],
        'token_destroy': ['rest_framework.permissions.IsAuthenticated'],
    },
}

REST_FRAMEWORK = {
    # "DEFAULT_RENDERER_CLASSES": [
    #     # МОЖНО ОТКЛЮЧИТЬ АПИ БРАУЗЕРА (НУЖНО В РЕЛИЗЕ)
    # ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    # AllowAny — всё разрешено, любой пользователь (и даже аноним) может выполнить любой запрос.
    # IsAuthenticated — только аутентифицированные пользователи имеют доступ к API и могут выполнить любой запрос. Остальным вернётся ответ "401 Unauthorized".
    # IsAuthenticatedOrReadOnly — то же, что и в предыдущем доступе, но анонимы могут делать запросы на чтение; запросы на создание, удаление или редактирование информации доступны только аутентифицированным пользователям.
    # IsAdminUser — выполнение запросов запрещено всем, кроме пользователей с правами администратора, тех, для которых свойство user.is_staff равно True.
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.TokenAuthentication",
    ],
}
