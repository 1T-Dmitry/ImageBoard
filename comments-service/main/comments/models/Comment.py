from django.db import models


class Comment(models.Model):
    """Модель комментария"""

    user_id = models.IntegerField()
    post_id = models.IntegerField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    text = models.TextField(max_length=1000)

    image_url = models.URLField(max_length=500)

    is_updated = models.BooleanField(default=False)

    class Meta:
        db_table = 'comments'

        ordering = ['-created_at']

        indexes = [
            models.Index(fields=['post_id', 'created_at']),
        ]

        verbose_name = 'комментарий'
        verbose_name_plural = 'комментарии'

    def __str__(self):
        return f"Комментарий: {self.id} к посту {self.post_id} от пользователя {self.user_id}"
