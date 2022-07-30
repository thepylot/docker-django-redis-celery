import os
from celery import Celery


os.environ.setdefault('DJANGO_SETTINGS_MODULE','core.settings')


app =Celery('core')

app.config_from_object('django.conf:settings',namespace='CELERY')

app.conf.beat_schedule ={
    'scrape_result':{
        'task':'scrape.tasks.ScrapeResult',
        'schedule': 600.0
    }
}

app.autodiscover_tasks()