from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# 设置 Django 的默认 settings 模块
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hongbao.settings')

app = Celery('hongbao')

# 从 settings.py 中读取 celery 相关配置
app.config_from_object('django.conf:settings', namespace='CELERY')

# 自动发现所有已注册的 Django app 中的任务
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
