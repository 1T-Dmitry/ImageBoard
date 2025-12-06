import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.reverse import reverse

User = get_user_model()


class TestRegisterAPI:
    """Тесты для регистрации пользователя"""

    @pytest.fixture
    def url(self):
        return reverse('register')

    def test_register_success(self, api_client, url, db):
        """Тест успешной регистрации"""
        data = {
            'email': 'newuser@example.com',
            'password': 'TestPass123',
            'password_confirm': "TestPass123",
            'first_name': 'John',
            'last_name': 'Doe'
        }

        response = api_client.post(url, data)

        assert response.status_code == status.HTTP_201_CREATED
        assert 'user' in response.data
        assert 'access' in response.data
        assert 'refresh' in response.data
        assert response.data['user']['email'] == data['email']
        assert 'password' not in response.data['user']

    def test_register_invalid_data(self, api_client, url, db):
        """Тест регистрации с невалидными данными"""
        data = {
            'email': 'invalid-email',
            'password': '123'  # слишком короткий пароль
        }

        response = api_client.post(url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'email' in response.data
        assert 'password' in response.data

    def test_register_duplicate_email(self, api_client, url, user, db):
        """Тест регистрации с существующим email"""
        data = {
            'email': 'test@example.com',
            'password': 'TestPass123',
            'password_confirm': 'TestPass123',
            'first_name': 'Another',
            'last_name': 'User',
        }

        response = api_client.post(url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'email' in response.data


class TestLoginAPI:
    """Тесты для входа пользователя"""

    @pytest.fixture
    def url(self):
        return reverse('login')

    def test_login_success(self, api_client, url, user):
        """Тест успешного входа"""

        data = {
            'email': 'test@example.com',
            'password': 'testpass123'
        }

        response = api_client.post(url, data)

        assert response.status_code == status.HTTP_200_OK
        assert 'user' in response.data
        assert 'access' in response.data
        assert 'refresh' in response.data
        assert response.data['user']['email'] == user.email

    def test_login_banned_user(self, api_client, url, db):
        """Тест входа заблокированного пользователя"""

        banned_user = User.objects.create_user(
            email='banned@example.com',
            password='testpass123',
            is_banned=True
        )

        data = {
            'email': 'banned@example.com',
            'password': 'testpass123'
        }

        response = api_client.post(url, data)

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert 'error' in response.data
        assert 'заблокирована' in response.data['error']

    def test_login_wrong_credentials(self, api_client, url, db):
        """Тест входа с неверными учетными данными"""

        data = {
            'email': 'wrong@example.com',
            'password': 'wrongpass'
        }

        response = api_client.post(url, data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert 'error' in response.data


class TestProfileAPI:
    """Тесты для профиля пользователя"""

    @pytest.fixture
    def url(self):
        return reverse('profile')

    def test_get_profile_authenticated(self, authenticated_client, url, user):
        """Тест получения профиля аутентифицированным пользователем"""
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['email'] == user.email
        assert response.data['first_name'] == user.first_name
        assert response.data['last_name'] == user.last_name

    def test_get_profile_unauthenticated(self, api_client, url):
        """Тест получения профиля без аутентификации"""
        response = api_client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestUserByIdAPI:
    """Тесты для получения пользователя по ID"""

    def test_get_user_by_id_success(self, authenticated_client, another_user):
        """Тест успешного получения пользователя по ID"""
        url = reverse('user-by-id', kwargs={'user_id': another_user.id})
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == another_user.id
        assert response.data['email'] == another_user.email

    def test_get_user_by_id_not_found(self, authenticated_client):
        """Тест получения несуществующего пользователя"""
        url = reverse('user-by-id', kwargs={'user_id': 999})
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert 'error' in response.data

    def test_get_user_by_id_unauthenticated(self, api_client, user):
        """Тест получения пользователя по ID без аутентификации"""
        url = reverse('user-by-id', kwargs={'user_id': user.id})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED