imageboard-microservices/
├── docker-compose.yml          # Основной compose файл
├── docker-compose.dev.yml      # Для разработки
├── docker-compose.base.yml     # Базовая инфраструктура
├── .env.example                # Шаблон переменных окружения
├── nginx/                      # Nginx конфигурации
├── api-gateway/                # API Gateway сервис
├── users-service/              # Сервис пользователей
├── posts-service/              # Сервис постов
├── comments-service/           # Сервис комментариев
├── notifications-service/      # Сервис уведомлений
├── analytics-service/          # Сервис аналитики
└── monitoring/                 # Мониторинг (Prometheus+Grafana)

🎯 API Эндпоинты
API Gateway (порт 8000)
Базовый URL: http://localhost:8000/api/

Сервис пользователей (/api/users/)
Регистрация: POST /api/users/register/
Принимает:
{
  "username": "string",
  "email": "string@example.com",
  "password": "string",
  "first_name": "string (optional)",
  "last_name": "string (optional)"
}
Возвращает:
{
  "id": "integer",
  "username": "string",
  "email": "string",
  "token": "string (JWT)",
  "created_at": "datetime"
}
Коды ошибок:
400 - Неверные данные, пользователь уже существует
422 - Ошибка валидации

Авторизация: POST /api/users/login/
Принимает:
{
  "username": "string",
  "password": "string"
}
Возвращает:
{
  "token": "string (JWT)",
  "user_id": "integer",
  "username": "string"
}
Коды ошибок:
401 - Неверные учетные данные
400 - Отсутствуют обязательные поля

Профиль пользователя: GET /api/users/profile/{id}/

Сервис постов (/api/posts/):
Получение списка постов: GET /api/posts/
Query параметры:
page - номер страницы (пагинация)
limit - количество постов на странице
ordering - сортировка (created_at, -created_at, likes_count)
Возвращает:
{
  "count": "integer",
  "next": "string (url следующей страницы)",
  "previous": "string (url предыдущей страницы)",
  "results": [
    {
      "id": "integer",
      "title": "string",
      "content": "string",
      "image_url": "string (optional)",
      "author": {
        "id": "integer",
        "username": "string"
      },
      "created_at": "datetime",
      "updated_at": "datetime",
      "likes_count": "integer",
      "comments_count": "integer"
    }
  ]
}

Создание поста: POST /api/posts/
Заголовки: Authorization: Bearer <JWT_TOKEN>
Принимает (multipart/form-data):
{
  "title": "string (max 255 chars)",
  "content": "string",
  "image": "file (optional, jpg/png)"
}
Возвращает:
{
  "id": "integer",
  "title": "string",
  "content": "string",
  "image_url": "string/null",
  "author": "integer",
  "created_at": "datetime",
  "likes_count": 0
}
Коды ошибок:
401 - Не авторизован
400 - Ошибка валидации
413 - Файл слишком большой

Детали поста: GET /api/posts/{id}/
Возвращает:
{
  "id": "integer",
  "title": "string",
  "content": "string",
  "image_url": "string/null",
  "author": {
    "id": "integer",
    "username": "string"
  },
  "created_at": "datetime",
  "updated_at": "datetime",
  "likes": [
    {
      "user_id": "integer",
      "username": "string"
    }
  ],
  "likes_count": "integer",
  "comments_count": "integer"
}
Коды ошибок:
404 - Пост не найден

Лайк поста: POST /api/posts/{id}/like/
Заголовки: Authorization: Bearer <JWT_TOKEN>
Возвращает:
{
  "post_id": "integer",
  "liked": "boolean",
  "likes_count": "integer",
  "message": "string"
}
Коды ошибок:
401 - Не авторизован
404 - Пост не найден

Сервис комментариев (/api/comments/):
Комментарии к посту: GET /api/comments/?post_id={id}
Возвращает:
[
  {
    "id": "integer",
    "post_id": "integer",
    "author": {
      "id": "integer",
      "username": "string"
    },
    "content": "string",
    "created_at": "datetime",
    "updated_at": "datetime",
    "parent": "integer/null (для вложенных комментариев)"
  }
]

Добавление комментария: POST /api/comments/
Заголовки: Authorization: Bearer <JWT_TOKEN>
Принимает:
{
  "post_id": "integer",
  "content": "string",
  "parent": "integer (optional, для ответов)"
}
Возвращает:
{
  "id": "integer",
  "post_id": "integer",
  "author": "integer",
  "content": "string",
  "created_at": "datetime",
  "parent": "integer/null"
}
Коды ошибок:
400 - Ошибка валидации
404 - Пост не найден
401 - Не авторизован

Сервис уведомлений (/api/notifications/):
Получение уведомлений пользователя: GET /api/notifications/
Заголовки: Authorization: Bearer <JWT_TOKEN>
Query параметры: unread_only - true/false (только непрочитанные)
Возвращает:
[
  {
    "id": "integer",
    "type": "string (LIKE, COMMENT, REPLY, SYSTEM)",
    "message": "string",
    "data": {
      "post_id": "integer (optional)",
      "comment_id": "integer (optional)",
      "actor_id": "integer"
    },
    "read": "boolean",
    "created_at": "datetime"
  }
]

Отметить как прочитанное: PATCH /api/notifications/{id}/mark-read/
Заголовки: Authorization: Bearer <JWT_TOKEN>
Возвращает:
{
  "id": "integer",
  "read": "boolean"
}
Коды ошибок:
404 - Уведомление не найдено
403 - Не принадлежит пользователю

Сервис аналитики (/api/analytics/):
Статистика постов: GET /api/analytics/posts/stats/?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD
Заголовки: Authorization: Bearer <JWT_TOKEN> (требуются права администратора)

Возвращает:
{
  "period": {
    "start_date": "string",
    "end_date": "string"
  },
  "total_posts": "integer",
  "posts_per_day": "float",
  "most_active_users": [
    {
      "user_id": "integer",
      "username": "string",
      "posts_count": "integer"
    }
  ],
  "likes_statistics": {
    "total_likes": "integer",
    "avg_likes_per_post": "float",
    "most_liked_post": {
      "post_id": "integer",
      "title": "string",
      "likes_count": "integer"
    }
  }
}

Пользовательская активность: GET /api/analytics/user-activity/?user_id={id}
Заголовки: Authorization: Bearer <JWT_TOKEN>
Возвращает:
{
  "user_id": "integer",
  "period": "last_30_days",
  "posts_created": "integer",
  "comments_written": "integer",
  "likes_given": "integer",
  "activity_timeline": [
    {
      "date": "string",
      "posts": "integer",
      "comments": "integer",
      "likes": "integer"
    }
  ]
}


📊 Kafka Топики
Основные топики:
user-events - события пользователей (регистрация, логин)
post-events - события постов (создание, удаление, лайки)
comment-events - события комментариев
notification-events - события уведомлений
analytics-events - события для аналитики

🔧 Общие коды ошибок
Успешные ответы:
200 - OK
201 - Создано успешно
204 - Нет содержимого

Ошибки клиента:
400 - Неверный запрос
401 - Не авторизован
403 - Доступ запрещен
404 - Не найдено
405 - Метод не разрешен
409 - Конфликт (например, повторное создание)
413 - Слишком большой запрос
422 - Ошибка валидации данных

Ошибки сервера:
500 - Внутренняя ошибка сервера
502 - Ошибка шлюза
503 - Сервис недоступен
504 - Таймаут шлюза

📝 Примечания
Аутентификация: Все защищенные эндпоинты требуют JWT токен в заголовке Authorization: Bearer <token>
Пагинация: Все списковые эндпоинты используют пагинацию по умолчанию (20 элементов на страницу)
Лимиты:
Размер загружаемых изображений: не более 5MB
Длина контента поста: не более 5000 символов
Длина комментария: не более 1000 символов
Валидация: Все входные данные валидируются на стороне сервера
События: Важные действия (лайки, комментарии) генерируют события Kafka для обработки другими сервисами