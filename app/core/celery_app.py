from celery import Celery

from .config import settings

celery = Celery("celery_app", broker=settings.BROKER, backend=settings.BACKEND, include=['app.utils.sendmail'])
celery.conf.acks_late = True
