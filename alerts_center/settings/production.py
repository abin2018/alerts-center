from .base import *
import os

# 生产环境设置为False
DEBUG = False

# 读取环境变量中的所有配置
# SECRET_KEY
SECRET_KEY = os.environ.get('SECRET_KEY')   # 生产环境重新生成
# 数据库配置
DB_HOST = os.environ.get('DB_HOST')
DB_NAME = os.environ.get('DB_NAME')
DB_USER = os.environ.get('DB_USER')
DB_PASSWORD = os.environ.get('DB_PASSWORD')


# Celery相关
CELERY_BROKER_DB_HOST = os.environ.get('CELERY_BROKER_DB_HOST')
CELERY_BROKER_DB_PORT = os.environ.get('CELERY_BROKER_DB_PORT')
CELERY_BROKER_DB_USER = os.environ.get('CELERY_BROKER_DB_USER', '')
CELERY_BROKER_DB_PASSWORD = os.environ.get('CELERY_BROKER_DB_PASSWORD')
CELERY_BROKER_DB_NUMBER = os.environ.get('CELERY_BROKER_DB_NUMBER', 0)

# 线上有可能需要修改此文件，否则无法通过IP或域名访问访问，若使用Nginx转发则不需要
SERVICE_HOST = os.environ.get('SERVICE_HOST', '127.0.0.1')
ALLOWED_HOSTS = [SERVICE_HOST]  # 生产环境保持默认为空即可（一般使用nginx做反向代理），测试环境可配置本地IP或域名

# 日志文件目录
LOGS_DIR = 'logs'

# 静态文件目录
STATIC_ROOT = 'statics'

# 上线后需要修改此部分配置，生产环境使用MySQL数据库
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'HOST': DB_HOST,
        'NAME': DB_NAME,
        'USER': DB_USER,
        'PASSWORD': DB_PASSWORD,
    }
}
# Celery settings, 如果celery设置了密码，可在此修改
# Broker配置，使用Redis作为消息中间件
CELERY_BROKER_URL = 'redis://{}:{}@{}:{}/{}'.format(CELERY_BROKER_DB_USER,
                                                    CELERY_BROKER_DB_PASSWORD,
                                                    CELERY_BROKER_DB_HOST,
                                                    CELERY_BROKER_DB_PORT,
                                                    CELERY_BROKER_DB_NUMBER)


# 生产环境日志配置，测试环境可以使用终端输出，生产环境设置了DEBUG=True，需要设置日志
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,  # 默认不覆盖root logger
    'formatters': {
        'basic': {
            'format': '%(asctime)s %(name)s %(lineno)d %(levelname)s %(message)s'
        }
    },
    'handlers': {
        'django_logfile': {        # 所有django本身的日志handler
            'class': 'logging.FileHandler',  # 线上环境可以考虑使用轮询
            'filename': os.path.join(LOGS_DIR, 'django.log'),
            'formatter': 'basic'
        },
        'custom_logfile': {  # 所有自定义的日志handler
            'class': 'logging.FileHandler',  # 线上环境可以考虑使用轮询
            'filename': os.path.join(LOGS_DIR, 'running.log'),
            'formatter': 'basic'
        },
    },
    'loggers': {
        'django': {     # 重写内置的logger，会输出所有日志
            'handlers': ['django_logfile'],
        },
        'custom': {
            'handlers': ['custom_logfile'],
        }
    },
}
