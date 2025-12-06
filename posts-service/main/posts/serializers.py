from rest_framework import serializers
from .models import Post


class PostSerializer(serializers.ModelSerializer):
    """Базовый сериализатор для постов"""

    author_id = serializers.IntegerField(read_only=True)
    status = serializers.CharField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Post
        fields = [
            'id',
            'title',
            'content',
            'image_url',
            'author_id',
            'status',
            'created_at',
            'updated_at'
        ]

    def validate_title(self, value):
        if len(value.strip()) < 3:
            raise serializers.ValidationError("Заголовок слишком короткий")
        return value.strip()

    def validate_content(self, value):
        if len(value.strip()) < 10:
            raise serializers.ValidationError("Содержание слишком короткое")
        return value.strip()

    def validate_image_url(self, value):
        if not value.startswith(('http://', 'https://')):
            raise serializers.ValidationError("Некорректный URL изображения")
        return value


class PostCreateSerializer(PostSerializer):
    """Для создания поста"""

    class Meta(PostSerializer.Meta):
        fields = ['title', 'content', 'image_url']

    def create(self, validated_data):
        # Добавляем author_id из запроса
        request = self.context.get('request')
        validated_data['author_id'] = request.user.get('id')
        return Post.objects.create(**validated_data)


class PostUpdateSerializer(serializers.ModelSerializer):
    """Для редактирования поста"""

    class Meta:
        model = Post
        fields = ['title', 'content', 'image_url']

    def validate(self, attrs):
        instance = self.instance

        # Проверяем, можно ли редактировать пост
        if not instance.is_editable():
            raise serializers.ValidationError("Этот пост нельзя редактировать")

        # Проверяем, что пользователь - автор поста
        request = self.context.get('request')
        if instance.author_id != request.user.get('id'):
            raise serializers.ValidationError("Вы не можете редактировать чужой пост")

        return attrs

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance