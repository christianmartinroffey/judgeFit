import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'judgeFit.settings')

app = Celery('judgeFit')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
