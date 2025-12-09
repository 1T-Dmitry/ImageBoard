from rest_framework import serializers

from comments.models.Comment import Comment
from comments.services.PostServiceClient import PostServiceClient
from comments.services.UserServiceClient import UserServiceClient


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для комментариев"""

    user_data = serializers.SerializerMethodField(read_only=True)
    post_data = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Comment
        fields = [
            'id',
            'user_id',
            'post_id',
            'user_data',
            'post_data',
            'text',
            'image_url',
            'is_updated',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_updated']

    @staticmethod
    def get_user_data(obj):
        """Получение данных пользователя из внешнего сервиса"""
        try:
            user_data = UserServiceClient.get_user(obj.user_id)
            if user_data:
                # Возвращаем только необходимые поля (настроить по потребности)
                return {
                    'id': user_data.get('id'),
                }
        except Exception as e:
            pass
        return None

    @staticmethod
    def get_post_data(self, obj):
        """Получение данных поста из внешнего сервиса"""
        try:
            post_data = PostServiceClient.get_post(obj.post_id)
            if post_data:
                # Возвращаем только необходимые поля (настроить по потребности)
                return {
                    'id': post_data.get('id'),
                }
        except Exception as e:
            pass
        return None

    @staticmethod
    def validate_user_id(self, value):
        """Валидация существования пользователя"""
        if not UserServiceClient.get_user(value):
            raise serializers.ValidationError("Пользователь не существует")
        return value

    @staticmethod
    def validate_post_id(self, value):
        """Валидация существования поста"""
        if not PostServiceClient.get_post(value):
            raise serializers.ValidationError("Пост не существует")
        return value

    def create(self, validated_data):
        """Создание комментария"""
        validated_data['is_updated'] = False
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """Обновление комментария"""
        instance = super().update(instance, validated_data)
        instance.is_updated = True
        instance.save()
        return instance