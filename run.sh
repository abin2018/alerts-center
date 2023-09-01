#!/usr/bin/env bash

# 遇到错误则退出
set -o errexit
# 遇到未绑定变量退出
set -o nounset
# 管道中只要有一个子命令失败则退出
set -o pipefail

/bin/bash /alerts_center/wait-for-it.sh -q -t 30 alerts_center_mysql:3306
/bin/bash /alerts_center/wait-for-it.sh -q -t 30 alerts_center_redis:6379

cmd=$1

if [ $cmd -eq "run_celery" ] ; then
  celery -A alerts_center worker -l INFO --beat
else
  # 迁移数据库
  python manage.py migrate
  # 收集静态文件
  python manage.py collectstatic
  # 启动uwsgi
  uwsgi --http :9009 \
        --enable-threads \
        --chdir /alerts_center/ \
        --module alerts_center.wsgi \
        --env DJANGO_SETTINGS_MODULE=alerts_center.settings.production \
        --socket-timeout 300 \
        --http-timeout 300 \
        --threads 8 \
        --static-map /static=/alerts_center/statics
fi
