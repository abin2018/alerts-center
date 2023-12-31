"""
Django settings for alerts_center project.

Generated by 'django-admin startproject' using Django 4.2.2.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'simpleui',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'smart_selects',
    'django_celery_beat',
    'django_celery_results',
    'apps.alerting',
    'apps.meta_info',
    'apps.on_call',
    'apps.system_config',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'alerts_center.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'alerts_center.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'zh-hans'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = False

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# smart-select jquery_url配置
JQUERY_URL = 'https://libs.baidu.com/jquery/2.1.4/jquery.min.js'

# Celery settings
CELERY_BROKER_URL = 'redis://:@127.0.0.1:6379/0'  # Broker配置，使用Redis作为消息中间件
CELERY_RESULT_BACKEND = 'django-db'  # Backends配置，生产环境建议使用django ORM，需提前安装django-celery-results
CELERY_RESULT_SERIALIZER = 'json'  # 结果序列化方案
CELERY_TIMEZONE = 'Asia/Shanghai'
CELERY_TASK_TRACK_STARTED = True
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
CELERY_TASK_TIME_LIMIT = 30 * 60
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'  # 定时任务，需要提前安装django-celery-beat
DJANGO_CELERY_BEAT_TZ_AWARE = False

# simpleui settings
SIMPLEUI_STATIC_OFFLINE = True
SIMPLEUI_HOME_INFO = False
SIMPLEUI_ANALYSIS = False
SIMPLEUI_HOME_ICON = 'fa fa-eye'
SIMPLEUI_LOGO = '/static/logo.png'
SIMPLEUI_CONFIG = {
    # 是否使用系统默认菜单，自定义菜单时建议关闭。
    'system_keep': False,
    # 用于菜单排序和过滤, 不填此字段为默认排序和全部显示。空列表[] 为全部不显示.
    'menu_display': [
        '告警配置',
        '值班信息',
        # '任务管理',
        '权限认证',
        '系统管理'
    ],
    # 设置是否开启动态菜单, 默认为False. 如果开启, 则会在每次用户登陆时刷新展示菜单内容。一般建议关闭。
    'dynamic': False,
    'menus': [
        {
            'name': '告警配置',
            'icon': 'fas fa-fire-alt',
            'models': [
                {'name': '告警源', 'icon': 'fas fa-arrow-circle-right',
                 'url': '/admin/alerting/alertsource/'},
                {'name': '告警内容', 'icon': 'fas fa-bell',
                 'url': '/admin/alerting/alertcontent/'},
                {'name': '告警模板', 'icon': 'fa fa-th-list',
                 'url': '/admin/alerting/alerttemplate/'},
                {'name': '告警目标', 'icon': 'fas fa-user-circle',
                 'url': '/admin/alerting/alerttarget/'},
                {'name': '告警规则', 'icon': 'fas fa-circle-notch',
                 'url': '/admin/alerting/alertrules/'},
                {'name': '告警抑制', 'icon': 'far fa-window-restore',
                 'url': '/admin/alerting/alertinhibition/'},
                ]
        },
        {
            'name': '值班信息',
            'icon': 'fas fa-moon',
            'models': [
                {'name': '值班角色', 'icon': 'fa fa-th-list',
                 'url': '/admin/on_call/oncallrole/'},
                {'name': '值班人员', 'icon': 'fas fa-user-md',
                 'url': '/admin/on_call/oncallstuff/'},
            ]
        },
        {
            'name': '任务管理',
            'icon': 'fas fa-thumbtack',
            'models': [
                {
                    'name': '定时任务',
                    'icon': 'fas fa-tasks',
                    'url': '/admin/django_celery_beat/periodictask/'
                },
                {
                    'name': 'Celery任务执行结果',
                    'icon': 'fas fa-poll',
                    'url': '/admin/django_celery_results/taskresult/'
                },
            ]
        },
        {
            'app': 'auth',
            'name': '权限认证',
            'icon': 'fas fa-user-shield',
            'models': [
                {
                    'name': '用户列表',
                    'icon': 'fa fa-user',
                    'url': 'auth/user/'
                },
                {
                    'name': '用户组',
                    'icon': 'fa fa-th-list',
                    'url': 'auth/group/'
                }
            ]
        },
        {
            'name': '系统管理',
            'icon': 'fas fa-thumbtack',
            'models': [
                {
                    'name': '系统配置',
                    'icon': 'fas fa-tasks',
                    'url': '/admin/system_config/systemconfigure/'
                },
                {
                    'name': '定时任务',
                    'icon': 'fas fa-tasks',
                    'url': '/admin/django_celery_beat/periodictask/'
                },
                {
                    'name': '任务执行结果',
                    'icon': 'fas fa-poll',
                    'url': '/admin/django_celery_results/taskresult/'
                },
            ]
        },
    ]
}

