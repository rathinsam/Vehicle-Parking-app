from celery import Celery
from celery.schedules import crontab
from config import Config

celery = Celery('tasks', broker=Config.CELERY_BROKER_URL, 
                backend=Config.CELERY_RESULT_BACKEND,
                include=['tasks'])
celery.conf.timezone = 'Asia/Kolkata'

# # Auto-discover tasks from tasks.py
# celery.autodiscover_tasks(['tasks'])

# Periodic Tasks Schedule
celery.conf.beat_schedule = {
    'send-daily-reservation-reminder': {
        'task': 'tasks.send_daily_reminder',
        'schedule': crontab(hour=12, minute=39),  # Every day at 9 AM
    },
    'send-monthly-report': {
        'task': 'tasks.send_monthly_report',
        'schedule': crontab(day_of_month=1, hour=8, minute=0),  # 1st day of month at 8 AM
    },
    'test-hello-task': {
        'task': 'tasks.print_hello',
        'schedule': 10.0,  # Every 10 seconds
    }
}

