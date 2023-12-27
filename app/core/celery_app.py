from celery import Celery

celery = Celery("celery_app", broker="pyamqp://guest@localhost//", backend='rpc://', include=['app.utils.sendmail'])
