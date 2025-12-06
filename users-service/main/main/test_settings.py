DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

DEBUG = False
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]