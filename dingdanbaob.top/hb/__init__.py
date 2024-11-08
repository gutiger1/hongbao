default_app_config = 'hb.apps.HbConfig'

from hongbao.celery import app as celery_app

__all__ = ['celery_app']
