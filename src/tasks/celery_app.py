from celery import Celery
from celery.schedules import crontab

from src.config import settings


celery_instance = Celery(
    "tasks",
    broker=settings.DB_REDIS,
    include=[
        "src.tasks.tasks"
    ]
)

celery_instance.conf.beat_schedule = {
    "Lubos-nazvanis": {
        "task": "booking_today_checkin",  # имя задачи
        "schedule": crontab(hour=0, minute=0),  # каждый день в полночь
    },
}