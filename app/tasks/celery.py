from celery import Celery
from celery.schedules import crontab

celery = Celery(
    "tasks",
    "redis://localhost",
    include=["app.tasks.tasks"]
)

# Настройки Celery
celery.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Europe/Moscow",
    enable_utc=False,
)

# Настройка периодических задач
celery.conf.beat_schedule = {
    "check-expired-medicines": {
        "task": "app.tasks.tasks.check_expired_medicines",
        "schedule": crontab(minute="*/1"),  # Ежедневно в 00:00
    },
}