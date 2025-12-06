from django.db import models


class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    image_url = models.URLField(max_length=500)
    author_id = models.IntegerField()  # ID пользователя из users-service
    status = models.CharField(
        max_length=20,
        choices=[
            ('draft', 'Черновик'),
            ('published', 'Опубликован'),
            ('closed', 'Закрыт'),
            ('deleted', 'Удален')
        ],
        default='draft'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'posts'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"

    def publish(self):
        """Опубликовать пост"""
        if self.status == 'draft':
            self.status = 'published'
            self.save(update_fields=['status', 'updated_at'])
            return True
        return False

    def close(self):
        """Закрыть пост"""
        if self.status == 'published':
            self.status = 'closed'
            self.save(update_fields=['status', 'updated_at'])
            return True
        return False

    def soft_delete(self):
        """Мягкое удаление"""
        self.status = 'deleted'
        self.save(update_fields=['status', 'updated_at'])

    def is_editable(self):
        """Можно ли редактировать пост"""
        return self.status in ['draft', 'published']