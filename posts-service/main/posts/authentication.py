# authentication.py
from rest_framework import authentication
from rest_framework.exceptions import AuthenticationFailed


class HeaderJWTAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        user_id = request.headers.get('X-User-Id')

        if not user_id:
            return None

        try:
            class SimpleUser:
                def __init__(self, user_id):
                    self.id = user_id
                    self.user_id = user_id
                    self.is_authenticated = True
                    # Добавлять другие необходимые объекты пользователя (при необходимости)
                    self.username = request.headers.get('X-User-Username', '')
                    self.email = request.headers.get('X-User-Email', '')
                    self.pk = user_id

            user = SimpleUser(int(user_id))
            return user, None
        except (ValueError, TypeError):
            raise AuthenticationFailed('Invalid user ID')