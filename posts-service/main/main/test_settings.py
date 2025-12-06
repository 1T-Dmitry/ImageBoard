import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent


# Quick-start development settings - unsuitable for production
SECRET_KEY = 'test-secret-key-for-tests-only'

DEBUG = False

ALLOWED_HOSTS = []


# Application definition - оставляем только минимально необходимые приложения
INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'posts.apps.PostsConfig',
]

MIDDLEWARE = []

ROOT_URLCONF = 'main.urls'

WSGI_APPLICATION = 'main.wsgi.application'


# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Используйте миграции для создания таблиц
MIGRATION_MODULES = {
    'posts': None,  # Отключаем миграции, будем создавать таблицы вручную
}

# Password validation
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = 'static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'