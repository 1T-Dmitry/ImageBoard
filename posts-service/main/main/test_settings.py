from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


SECRET_KEY = 'test-secret-key-for-tests-only'

DEBUG = False

ALLOWED_HOSTS = []


INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'posts.apps.PostsConfig',
]

MIDDLEWARE = []

ROOT_URLCONF = 'main.urls'

WSGI_APPLICATION = 'main.wsgi.application'


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

MIGRATION_MODULES = {
    'posts': None,
}

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'