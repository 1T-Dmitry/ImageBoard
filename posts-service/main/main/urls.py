from django.urls import path
from posts import views

urlpatterns = [
    # Просмотр постов
    path('', views.PostListView.as_view(), name='post-list'),
    path('<int:pk>/', views.PostDetailView.as_view(), name='post-detail'),

    # Создание поста
    path('create/', views.PostCreateView.as_view(), name='post-create'),

    # Редактирование поста
    path('<int:pk>/edit/', views.PostUpdateView.as_view(), name='post-update'),

    # Действия с постами
    path('<int:pk>/publish/', views.publish_post, name='post-publish'),
    path('<int:pk>/close/', views.close_post, name='post-close'),
    path('<int:pk>/delete/', views.delete_post, name='post-delete'),

    # Мои посты
    path('my/', views.my_posts, name='my-posts'),
    path('my/drafts/', views.my_drafts, name='my-drafts'),
]