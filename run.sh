#!/usr/bin/env bash

# 遇到错误则退出
set -o errexit
# 遇到未绑定变量退出
set -o nounset
# 管道中只要有一个子命令失败则退出
set -o pipefail

/bin/bash /alerts_center/wait-for-it.sh -t 100 alerts_center_mysql:3306 || { echo "3306 connect fail"; exit 2; }
/bin/bash /alerts_center/wait-for-it.sh -t 100 alerts_center_redis:6379 || { echo "6379 connect fail"; exit 2; }

cmd=$1

if [ $cmd == "run_celery" ] ; then
  # 等待migrate执行完成，否则会报错找不到定时任务相关的表
  /bin/bash /alerts_center/wait-for-it.sh -t 100 alerts_center_django:9009 || { echo "9009 connect fail"; exit 2; }
  exec celery -A alerts_center worker -l INFO --beat
else
  # 迁移数据库
  python manage.py migrate
  # 收集静态文件
  python manage.py collectstatic --noinput
  # 生成内置配置
  echo "生成内置配置..."
  python manage.py init_meta_data
  python manage.py init_alert_template
  python manage.py init_period_task
  # 初始化superuser
  if [ -f .superuser_created ] ; then
    echo "Superuser already created."
  else
    python manage.py createsuperuser --noinput
    echo "Superuser created!"
    touch .superuser_created
  fi
  # 启动uwsgi
  exec uwsgi --http :9009 \
        --enable-threads \
        --chdir /alerts_center/ \
        --module alerts_center.wsgi \
        --env DJANGO_SETTINGS_MODULE=alerts_center.settings.production \
        --socket-timeout 300 \
        --http-timeout 300 \
        --threads 8 \
        --static-map /static=/alerts_center/statics
fi
