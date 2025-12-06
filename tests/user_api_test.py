import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from users.models import User


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def test_user_data():
    return {
        'email': 'test@example.com',
        'first_name': 'John',
        'last_name': 'Doe',
        'password': 'SecurePass123!',
        'password_confirm': 'SecurePass123!'
    }


@pytest.fixture
def test_user(test_user_data):
    """Создание тестового пользователя"""
    user = User.objects.create_user(
        email=test_user_data['email'],
        first_name=test_user_data['first_name'],
        last_name=test_user_data['last_name'],
        password=test_user_data['password']
    )
    return user


@pytest.fixture
def test_user2():
    """Создание второго тестового пользователя"""
    return User.objects.create_user(
        email='user2@example.com',
        first_name='Jane',
        last_name='Smith',
        password='AnotherPass123!'
    )


@pytest.fixture
def admin_user():
    """Создание пользователя с ролью администратора"""
    user = User.objects.create_user(
        email='admin@example.com',
        first_name='Admin',
        last_name='User',
        password='AdminPass123!',
        role='admin'
    )
    return user


@pytest.fixture
def banned_user():
    """Создание заблокированного пользователя"""
    user = User.objects.create_user(
        email='banned@example.com',
        first_name='Banned',
        last_name='User',
        password='BannedPass123!',
        is_banned=True
    )
    return user


@pytest.mark.django_db
class TestRegisterAPI:
    """Тесты для эндпоинта регистрации"""

    def test_register_success(self, api_client, test_user_data):
        """Успешная регистрация пользователя"""
        url = reverse('register')
        response = api_client.post(url, test_user_data, format='json')

        assert response.status_code == status.HTTP_201_CREATED
        assert 'user' in response.data
        assert 'refresh' in response.data
        assert 'access' in response.data

        user_data = response.data['user']
        assert user_data['email'] == test_user_data['email']
        assert user_data['first_name'] == test_user_data['first_name']
        assert user_data['last_name'] == test_user_data['last_name']
        assert 'password' not in user_data
        assert 'password_confirm' not in user_data

        # Проверяем, что пользователь создан в базе
        assert User.objects.filter(email=test_user_data['email']).exists()

    def test_register_duplicate_email(self, api_client, test_user, test_user_data):
        """Регистрация с уже существующим email"""
        url = reverse('register')
        response = api_client.post(url, test_user_data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'email' in response.data

    def test_register_password_mismatch(self, api_client):
        """Регистрация с несовпадающими паролями"""
        url = reverse('register')
        data = {
            'email': 'new@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'password': 'Password123!',
            'password_confirm': 'Different123!'
        }

        response = api_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'password' in response.data

    def test_register_weak_password(self, api_client):
        """Регистрация со слабым паролем"""
        url = reverse('register')
        data = {
            'email': 'new@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'password': '123',
            'password_confirm': '123'
        }

        response = api_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'password' in response.data

    def test_register_missing_fields(self, api_client):
        """Регистрация с отсутствующими обязательными полями"""
        url = reverse('register')

        # Отсутствует email
        data = {
            'first_name': 'Test',
            'last_name': 'User',
            'password': 'Password123!',
            'password_confirm': 'Password123!'
        }

        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestLoginAPI:
    """Тесты для эндпоинта входа"""

    def test_login_success(self, api_client, test_user, test_user_data):
        """Успешный вход"""
        url = reverse('login')
        data = {
            'email': test_user_data['email'],
            'password': test_user_data['password']
        }

        response = api_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert 'user' in response.data
        assert 'refresh' in response.data
        assert 'access' in response.data

        user_data = response.data['user']
        assert user_data['email'] == test_user_data['email']

    def test_login_wrong_password(self, api_client, test_user):
        """Вход с неправильным паролем"""
        url = reverse('login')
        data = {
            'email': test_user.email,
            'password': 'wrongpassword'
        }

        response = api_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert 'error' in response.data

    def test_login_nonexistent_user(self, api_client):
        """Вход несуществующего пользователя"""
        url = reverse('login')
        data = {
            'email': 'nonexistent@example.com',
            'password': 'somepassword'
        }

        response = api_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert 'error' in response.data

    def test_login_banned_user(self, api_client, banned_user):
        """Вход заблокированного пользователя"""
        url = reverse('login')
        data = {
            'email': banned_user.email,
            'password': 'BannedPass123!'
        }

        response = api_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert 'error' in response.data
        assert 'заблокирована' in response.data['error']

    def test_login_missing_credentials(self, api_client):
        """Вход без указания учетных данных"""
        url = reverse('login')

        # Без email
        data = {'password': 'somepassword'}
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

        # Без password
        data = {'email': 'test@example.com'}
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestProfileAPI:
    """Тесты для эндпоинта профиля"""

    def test_get_profile_authenticated(self, api_client, test_user):
        """Получение профиля аутентифицированным пользователем"""
        api_client.force_authenticate(user=test_user)
        url = reverse('profile')

        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['email'] == test_user.email
        assert response.data['first_name'] == test_user.first_name
        assert response.data['last_name'] == test_user.last_name
        assert 'id' in response.data

    def test_get_profile_unauthenticated(self, api_client):
        """Получение профиля без аутентификации"""
        url = reverse('profile')

        response = api_client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestUserByIdAPI:
    """Тесты для эндпоинта получения пользователя по ID"""

    def test_get_user_by_id_exists(self, api_client, test_user):
        """Получение существующего пользователя по ID"""
        url = reverse('user-by-id', args=[test_user.id])

        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == test_user.id
        assert response.data['email'] == test_user.email

    def test_get_user_by_id_nonexistent(self, api_client):
        """Получение несуществующего пользователя"""
        url = reverse('user-by-id', args=[999])  # Несуществующий ID

        response = api_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert 'error' in response.data

    def test_get_user_by_id_zero_id(self, api_client):
        """Получение пользователя с ID=0"""
        url = reverse('user-by-id', args=[0])

        response = api_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_user_by_id_negative_id(self, api_client):
        """Получение пользователя с отрицательным ID"""
        url = reverse('user-by-id', args=[-1])

        response = api_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestIntegration:
    """Интеграционные тесты"""

    def test_register_login_flow(self, api_client):
        """Полный цикл: регистрация -> вход -> получение профиля"""
        # 1. Регистрация
        register_url = reverse('register')
        user_data = {
            'email': 'integration@example.com',
            'first_name': 'Integration',
            'last_name': 'Test',
            'password': 'TestPass123!',
            'password_confirm': 'TestPass123!'
        }

        register_response = api_client.post(register_url, user_data, format='json')
        assert register_response.status_code == status.HTTP_201_CREATED

        access_token = register_response.data['access']

        # 2. Получение профиля с токеном
        profile_url = reverse('profile')
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

        profile_response = api_client.get(profile_url)
        assert profile_response.status_code == status.HTTP_200_OK
        assert profile_response.data['email'] == user_data['email']

    def test_multiple_users_operations(self, api_client, test_user, test_user2):
        """Операции с несколькими пользователями"""
        # Вход первым пользователем
        api_client.force_authenticate(user=test_user)

        # Получение профиля первого пользователя
        profile_response = api_client.get(reverse('profile'))
        assert profile_response.status_code == status.HTTP_200_OK
        assert profile_response.data['email'] == test_user.email

        # Получение второго пользователя по ID
        user2_response = api_client.get(reverse('user-by-id', args=[test_user2.id]))
        assert user2_response.status_code == status.HTTP_200_OK
        assert user2_response.data['email'] == test_user2.email


@pytest.mark.django_db
class TestUserDataValidation:
    """Тесты валидации данных пользователя"""

    def test_user_serializer_fields(self, test_user):
        """Проверка полей сериализатора пользователя"""
        serializer = UserSerializer(test_user)
        data = serializer.data

        expected_fields = {
            'id', 'email', 'first_name', 'last_name', 'avatar_url',
            'role', 'is_banned', 'created_at'
        }

        assert set(data.keys()) == expected_fields

    def test_user_create_serializer_fields(self):
        """Проверка полей сериализатора создания пользователя"""
        from users.serializers import UserCreateSerializer

        serializer = UserCreateSerializer()
        expected_fields = {'email', 'first_name', 'last_name', 'password', 'password_confirm'}

        assert set(serializer.fields.keys()) == expected_fields