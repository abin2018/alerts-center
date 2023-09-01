# Django-django
export SECRET_KEY=''                                  # Django SECRET_KEY
export PROFILE='production'                                                                             # Django配置文件标记
export DB_HOST=''                                                                              # 数据库主机
export DB_NAME=''                                                                             # 数据库名
export DB_USER=''                                                                                    # 数据库用户名
export DB_PASSWORD=''                                                                          # 数据库密码

# Django-Celery
export CELERY_MONITOR_DINGDING_API_URL=''     # Celery任务失败时发送钉钉的WebhookURL
export CELERY_MONITOR_DINGDING_API_SEC=''                                                    # Celery任务失败时发送钉钉的Webhook密钥
export CELERY_BROKER_DB_HOST='127.0.0.1'                                                # Celery Broker主机
export CELERY_BROKER_DB_PORT=''                                                     # Celery Broker端口
export CELERY_BROKER_DB_USER=''                                                         # Celery Broker用户名
export CELERY_BROKER_DB_PASSWORD=''                                     # Celery Broker密码
export CELERY_BROKER_DB_NUMBER='0'                                      # Celery Broker DB


# Django-Message
export MONTNETS_API_USERID=''
export MONTNETS_API_PWD=''
export MONTNETS_API_URL=''
export MONTNETS_API_TMPLID=''

export MAIL_HOST=""
export MAIL_USER=""  # xxx是你的163邮箱用户名
export MAIL_PASS=""  # 口令是你设置的163授权密码