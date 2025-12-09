import requests
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

class PostServiceClient:
    @staticmethod
    def get_post(post_id):
        try:
            response = requests.get(
                f"{settings.POSTS_SERVICE_URL}/{post_id}/",
                timeout=5
            )
            if response.status_code == 200:
                return response.json()
        except requests.RequestException as e:
            logger.error(f"Failed to fetch post {post_id}: {e}")
        return None
