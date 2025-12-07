import os
import sys
import pytest
import django

# Настраиваем Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.test_settings')

django.setup()

# Теперь импортируем всё остальное
from model_bakery import baker
from ..models import Post
from rest_framework.test import APIClient


@pytest.fixture
def api_client():
    """Фикстура для API клиента"""
    return APIClient()


@pytest.fixture
def authenticated_client(api_client):
    """Фикстура для аутентифицированного пользователя"""

    user_data = {'user_id': 1, 'username': 'testuser', 'email': 'test@example.com'}
    api_client.force_authenticate(user=user_data)
    return api_client


@pytest.fixture
def another_authenticated_client(api_client):
    """Фикстура для другого аутентифицированного пользователя"""

    user_data = {'user_id': 2, 'username': 'otheruser', 'email': 'other@example.com'}
    api_client.force_authenticate(user=user_data)
    return api_client


@pytest.fixture
def post_data():
    """Тестовые данные для создания поста"""

    return {
        'title': 'Test Post Title',
        'content': 'This is a test post content with enough length.',
        'image_url': 'https://example.com/image.jpg'
    }


@pytest.fixture
def published_post(db):
    """Фикстура для опубликованного поста"""

    return baker.make(
        Post,
        title='Published Post',
        content='Published content',
        image_url='https://example.com/published.jpg',
        author_id=1,
        status='published'
    )


@pytest.fixture
def draft_post(db):
    """Фикстура для черновика"""

    return baker.make(
        Post,
        title='Draft Post',
        content='Draft content',
        image_url='https://example.com/draft.jpg',
        author_id=1,
        status='draft'
    )


@pytest.fixture
def closed_post(db):
    """Фикстура для закрытого поста"""

    return baker.make(
        Post,
        title='Closed Post',
        content='Closed content',
        image_url='https://example.com/closed.jpg',
        author_id=1,
        status='closed'
    )


@pytest.fixture
def deleted_post(db):
    """Фикстура для удаленного поста"""

    return baker.make(
        Post,
        title='Deleted Post',
        content='Deleted content',
        image_url='https://example.com/deleted.jpg',
        author_id=1,
        status='deleted'
    )


@pytest.fixture
def other_user_post(db):
    """Фикстура для поста другого пользователя"""

    return baker.make(
        Post,
        title='Other User Post',
        content='Other user content',
        image_url='https://example.com/other.jpg',
        author_id=2,
        status='published'
    )
