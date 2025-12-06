import requests
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

class UserServiceClient:
    @staticmethod
    def get_user(user_id):
        try:
            response = requests.get(
                f"{settings.USERS_SERVICE_URL}/api/users/{user_id}/",
                timeout=5
            )
            if response.status_code == 200:
                return response.json()
        except requests.RequestException as e:
            logger.error(f"Failed to fetch user {user_id}: {e}")
        return None
