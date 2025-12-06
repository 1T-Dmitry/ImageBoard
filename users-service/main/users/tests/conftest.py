import os
import sys
import django


sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.test_settings')
django.setup()


import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def authenticated_client(api_client, user):
    api_client.force_authenticate(user=user)
    return api_client

@pytest.fixture
def user(db):
    user = User.objects.create(
        email='test@example.com',
        first_name='Test',
        last_name='User',
        is_active=True
    )
    user.set_password('testpass123')
    user.save()
    return user

@pytest.fixture
def another_user(db):
    return User.objects.create_user(
        email='another@example.com',
        password='testpass123',
        first_name='Another',
        last_name='User'
    )