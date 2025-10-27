from celery import Celery
from celery.schedules import crontab

from src.config import settings


celery_instance = Celery("tasks", broker=settings.DB_REDIS, include=["src.tasks.tasks"])

celery_instance.conf.beat_schedule = {
    "send_mail_checkin": {
        "task": "booking_today_checkin",  # имя задачи
        "schedule": crontab(minute="*/5"),  # каждый день в полночь
    },
}
