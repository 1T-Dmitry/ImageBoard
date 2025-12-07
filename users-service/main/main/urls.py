from django.urls import path
from users import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('profile/', views.profile, name='profile'),
    path('<int:user_id>/', views.user_by_id, name='user-by-id'),
    path('health/', views.health, name='health'),
]
