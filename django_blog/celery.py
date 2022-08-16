from celery import Celery
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_blog.settings')
app = Celery('django_blog')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
