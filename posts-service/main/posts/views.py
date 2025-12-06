from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from .models import Post
from .serializers import PostSerializer, PostCreateSerializer, PostUpdateSerializer


class PostListView(generics.ListAPIView):
    """Просмотр списка опубликованных постов"""

    serializer_class = PostSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return Post.objects.filter(status='published').order_by('-created_at')


class PostCreateView(generics.CreateAPIView):
    """Создание нового поста"""

    serializer_class = PostCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save()


class PostDetailView(generics.RetrieveAPIView):
    """Просмотр деталей поста"""

    serializer_class = PostSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        # Показываем только опубликованные посты всем
        # и черновики/закрытые - только автору
        request = self.request
        queryset = Post.objects.all()

        if not request.user or not request.user.get('user_id'):
            return queryset.filter(status='published')

        user_id = request.user.get('user_id')
        return queryset.filter(
            status='published'
        ) | queryset.filter(
            author_id=user_id,
            status__in=['draft', 'closed', 'published']
        )


class PostUpdateView(generics.UpdateAPIView):
    """Редактирование поста"""

    serializer_class = PostUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user_id = self.request.user.get('user_id')
        return Post.objects.filter(
            author_id=user_id,
            status__in=['draft', 'published']
        )

    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        # Проверяем, можно ли редактировать
        if not instance.is_editable():
            return Response(
                {'error': 'Этот пост нельзя редактировать'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def publish_post(request, pk):
    """Опубликовать пост"""

    try:
        post = Post.objects.get(pk=pk, author_id=request.user.get('user_id'))
    except Post.DoesNotExist:
        return Response(
            {'error': 'Пост не найден или у вас нет прав'},
            status=status.HTTP_404_NOT_FOUND
        )

    if post.publish():
        return Response({'status': 'published', 'post_id': post.id})
    else:
        return Response(
            {'error': 'Невозможно опубликовать пост'},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def close_post(request, pk):
    """Закрыть пост"""
    try:
        post = Post.objects.get(pk=pk, author_id=request.user.get('user_id'))
    except Post.DoesNotExist:
        return Response(
            {'error': 'Пост не найден или у вас нет прав'},
            status=status.HTTP_404_NOT_FOUND
        )

    if post.close():
        return Response({'status': 'closed', 'post_id': post.id})
    else:
        return Response(
            {'error': 'Невозможно закрыть пост'},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def delete_post(request, pk):
    """Удалить пост (мягкое удаление)"""
    try:
        post = Post.objects.get(pk=pk, author_id=request.user.get('user_id'))
    except Post.DoesNotExist:
        return Response(
            {'error': 'Пост не найден или у вас нет прав'},
            status=status.HTTP_404_NOT_FOUND
        )

    post.soft_delete()
    return Response({'status': 'deleted', 'post_id': post.id}, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def my_posts(request):
    """Мои посты (все статусы)"""
    user_id = request.user.get('user_id')
    posts = Post.objects.filter(author_id=user_id).order_by('-created_at')
    serializer = PostSerializer(posts, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def my_drafts(request):
    """Мои черновики"""
    user_id = request.user.get('user_id')
    posts = Post.objects.filter(author_id=user_id, status='draft').order_by('-created_at')
    serializer = PostSerializer(posts, many=True)
    return Response(serializer.data)