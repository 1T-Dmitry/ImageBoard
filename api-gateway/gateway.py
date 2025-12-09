from flask import Flask, request, jsonify
import requests
import jwt
from functools import wraps
import os

app = Flask(__name__)

SERVICES = {
    'users': 'http://users-service:8001',
    'posts': 'http://posts-service:8002',
    'commnets': 'http://posts-service:8003',
}

JWT_SECRET = os.environ.get('JWT_SECRET', 'django-insecure-0(1bdu-nzf+%5xp960pac28f^a1^fez)mmxfj54_#lfe7v8ct4')


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return jsonify({'error': 'Token is missing'}), 401
        
        # Проверяем формат заголовка
        parts = auth_header.split(' ')
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            return jsonify({'error': 'Invalid authorization header format. Expected: Bearer <token>'}), 401
        
        try:
            token = parts[1]  # Безопасное получение токена
            payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
            request.user = payload
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        except Exception as e:
            return jsonify({'error': f'Token verification failed: {str(e)}'}), 401
        
        return f(*args, **kwargs)
    return decorated


# Публичные маршруты
@app.route('/api/auth/register', methods=['POST'])
def register():
    response = requests.post(
        f"{SERVICES['users']}/register/",
        json=request.json,
        timeout=30
    )
    return response.content, response.status_code, response.headers.items()


@app.route('/api/auth/login', methods=['POST'])
def login():
    response = requests.post(
        f"{SERVICES['users']}/login/",
        json=request.json,
        timeout=30
    )
    return response.content, response.status_code, response.headers.items()


# Защищённый маршрут
@app.route('/api/<service>/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
@token_required
def proxy(service, path):
    if service not in SERVICES:
        return jsonify({'error': 'Service not found'}), 404

    if service == 'auth':
        return jsonify({'error': 'Unauthorized'}), 401

    # Добавляем завершающий слэш, если его нет
    if not path.endswith('/'):
        path = path + '/'

    # Forward request to appropriate service
    url = f"{SERVICES[service]}/{path}"

    # Forward headers
    headers = {key: value for key, value in request.headers if key != 'Host'}
    headers['X-User-Id'] = str(request.user.get('user_id'))

    try:
        response = requests.request(
            method=request.method,
            url=url,
            headers=headers,
            data=request.get_data(),
            params=request.args,
            cookies=request.cookies,
            allow_redirects=False,
            timeout=30
        )

        return response.content, response.status_code, response.headers.items()
    except requests.RequestException as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    services_status = {}

    for service_name, service_url in SERVICES.items():
        try:
            response = requests.get(f"{service_url}/health", timeout=5)
            services_status[service_name] = {
                'status': 'up' if response.status_code == 200 else 'down',
                'code': response.status_code
            }
        except requests.RequestException:
            services_status[service_name] = {'status': 'down', 'code': 0}

    return jsonify({
        'gateway': 'up',
        'services': services_status
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)