import os
from celery import Celery
from celery.schedules import crontab


os.environ.setdefault('DJANGO_SETTINGS_MODULE','app.settings')


app =Celery('app')

app.config_from_object('django.conf:settings',namespace='CELERY')
app.conf.timezone = 'Europe/London'

app.conf.beat_schedule ={
    'scrape_result':{
        'task':'core.tasks.ScrapeResult',
        'schedule': crontab(minute=0, hour=0)
    }
}

app.autodiscover_tasks()