import os
from celery import Celery


os.environ.setdefault('DJANGO_SETTINGS_MODULE','app.settings')


app =Celery('app')

app.config_from_object('django.conf:settings',namespace='CELERY')

app.conf.beat_schedule ={
    'scrape_result':{
        'task':'core.tasks.ScrapeResult',
        'schedule': 60.0
    }
}

app.autodiscover_tasks()