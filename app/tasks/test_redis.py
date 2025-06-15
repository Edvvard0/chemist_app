import redis


r = redis.Redis(host='localhost', port=6380, db=0, username='my_user', password='my_user_password')

try:
    info = r.info()
    print(info['redis_version'])
    response = r.ping()
    if response:
        print("Подключение успешно!")
    else:
        print("Не удалось подключиться к Redis.")
except redis.exceptions.RedisError as e:
    print(f"Ошибка: {e}")

