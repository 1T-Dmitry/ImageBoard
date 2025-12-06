import pytest
from ..models import Post


class TestPostModel:
    """Тесты для модели Post"""

    def test_post_creation(self, db):
        """Тест создания поста"""

        post = Post.objects.create(
            title='Test Post',
            content='Test content',
            image_url='https://example.com/test.jpg',
            author_id=1,
            status='draft'
        )

        assert post.title == 'Test Post'
        assert post.content == 'Test content'
        assert post.author_id == 1
        assert post.status == 'draft'
        assert post.created_at is not None
        assert post.updated_at is not None

    def test_str_method(self, draft_post):
        """Тест строкового представления"""
        assert str(draft_post) == f"Draft Post (Черновик)"

    @pytest.mark.parametrize('initial_status, expected_result', [
        ('draft', True),
        ('published', True),
        ('closed', False),
        ('deleted', False),
    ])
    def test_is_editable_method(self, db, initial_status, expected_result):
        """Тест метода is_editable"""

        post = Post.objects.create(
            title='Test',
            content='Content',
            image_url='https://example.com/test.jpg',
            author_id=1,
            status=initial_status
        )
        assert post.is_editable() == expected_result

    def test_publish_method_success(self, draft_post):
        """Тест успешной публикации"""

        result = draft_post.publish()
        draft_post.refresh_from_db()

        assert result is True
        assert draft_post.status == 'published'

    def test_publish_method_failure(self, published_post):
        """Тест неудачной публикации (уже опубликован)"""

        result = published_post.publish()

        assert result is False
        assert published_post.status == 'published'

    def test_close_method_success(self, published_post):
        """Тест успешного закрытия"""

        result = published_post.close()
        published_post.refresh_from_db()

        assert result is True
        assert published_post.status == 'closed'

    def test_close_method_failure(self, draft_post):
        """Тест неудачного закрытия (не опубликован)"""

        result = draft_post.close()

        assert result is False
        assert draft_post.status == 'draft'

    def test_soft_delete_method(self, published_post):
        """Тест мягкого удаления"""

        published_post.soft_delete()
        published_post.refresh_from_db()

        assert published_post.status == 'deleted'

    def test_default_ordering(self, db):
        """Тест порядка сортировки по умолчанию"""

        post1 = Post.objects.create(
            title='Post 1',
            content='Content 1',
            image_url='https://example.com/1.jpg',
            author_id=1
        )

        post2 = Post.objects.create(
            title='Post 2',
            content='Content 2',
            image_url='https://example.com/2.jpg',
            author_id=1
        )

        posts = Post.objects.all()

        assert posts[0] == post2
        assert posts[1] == post1
