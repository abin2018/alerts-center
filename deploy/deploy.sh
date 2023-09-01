#!/usr/bin/env bash

BASE_DIR=$(cd $(dirname "$0"); pwd)
cd ${BASE_DIR}

# 使用root
# 新建用户
# 配置virtualenv
# yum install mysql-devel

# 检查环境变量是否设置
vars_array=(SECRET_KEY PROFILE DB_HOST DB_NAME DB_USER DB_PASSWORD CELERY_MONITOR_DINGDING_API_URL \
            CELERY_MONITOR_DINGDING_API_SEC CELERY_BROKER_DB_HOST CELERY_BROKER_DB_PORT \
            CELERY_BROKER_DB_USER CELERY_BROKER_DB_PASSWORD CELERY_BROKER_DB_NUMBER \
            MONTNETS_API_USERID MONTNETS_API_PWD MONTNETS_API_URL MONTNETS_API_TMPLID \
            EGAOSU_USER_ID MAIL_HOST MAIL_USER MAIL_PASS)

for var in ${vars_array[@]} ; do
  if ! grep -q "export \<$var\>" ~/.bash_profile ; then
    echo "$var not set"
    exit
  fi
done

# 安装requirements
pip install -r requirements.txt

# 初始化目录
[ -d ~/apps ] || mkdir ~/apps
[ -d ~/apps/supervisor ] || mkdir ~/apps/supervisor
[ -d ~/apps/supervisor/log ] || mkdir ~/apps/supervisor/log
[ -d ~/apps/supervisor/conf.d ] || mkdir ~/apps/supervisor/conf.d

# 生成supervisor文件
cat > supervisord.conf <<eof
[unix_http_server]
file=$HOME/apps/supervisor/supervisord.sock   ; the path to the socket file

[supervisord]
logfile=$HOME/apps/supervisor/log/supervisord.log ; main log file; default $CWD/supervisord.log
logfile_maxbytes=50MB        ; max main logfile bytes b4 rotation; default 50MB
logfile_backups=10           ; # of main logfile backups; 0 means none, default 10
loglevel=info                ; log level; default info; others: debug,warn,trace
pidfile=$HOME/apps/supervisor/supervisord.pid ; supervisord pidfile; default supervisord.pid
nodaemon=false               ; start in foreground if true; default false
minfds=1024                  ; min. avail startup file descriptors; default 1024
minprocs=200                 ; min. avail process descriptors;default 200

[rpcinterface:supervisor]
supervisor.rpcinterface_factory = supervisor.rpcinterface:make_main_rpcinterface

[supervisorctl]
serverurl=unix://$HOME/apps/supervisor/supervisord.sock ; use a unix:// URL  for a unix socket

[include]
files=$HOME/apps/supervisor/conf.d/*.conf
eof

# 生成nginx配置文件
cat > alerts_center_nginx.conf <<eof
server {
    server_tokens off;
    ssl_protocols TLSv1.2;
    listen       5678 default_server;
    server_name  _;


   location / {
        proxy_send_timeout  600s;#后端服务器数据回传时间(代理发送超时)
        proxy_read_timeout  600s;#连接成功后，后端服务器响应时间(代理接收超时)
        proxy_pass http://127.0.0.1:9009;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header Host \$proxy_host;
        proxy_set_header X-Forwarded-For \$remote_addr;
        proxy_set_header Server-Addr \$server_addr;
        proxy_set_header Server-Port \$server_port;
        proxy_buffers 16 16k;
        proxy_buffer_size 16k;
    }

   location /static {
        alias $HOME/apps/alerts_center/statics;
   }
   error_page 404 /404.html;
      location = /usr/share/nginx/html/404.html {
   }

   error_page 500 502 503 504 /50x.html;
      location = /50x.html {
   }
}
eof

cat > ~/apps/supervisor/conf.d/celery.conf <<eof
[program:celery]
directory = $HOME/apps/alerts_center/
command = celery -A alerts_center worker -l INFO --beat
autostart = true
startretries = 3
redirect_stderr = true
stdout_logfile_maxbytes = 20MB
stdout_logfile_backups = 20
stdout_logfile = $HOME/apps/supervisor/log/celery.log
eof

cat > ~/apps/supervisor/conf.d/alerts-center.conf <<eof
[program:alerts-center]
command = uwsgi --http 127.0.0.1:9009 --enable-threads --chdir $HOME/apps/alerts_center/ --module alerts_center.wsgi --env DJANGO_SETTINGS_MODULE=alerts_center.settings.production --socket-timeout 300 --http-timeout 300 --threads 8
autostart = true
startretries = 3
redirect_stderr = true
stdout_logfile_maxbytes = 20MB
stdout_logfile_backups = 20
stdout_logfile=$HOME/apps/supervisor/log/alerts_center.log
stopsignal=QUIT
daemon=true
eof

# 复制文件
[ -d ~/apps/alerts_center ] && mv ~/apps/alerts_center ~/apps/alerts_center_bak_$(date +%s)
cp -r $(dirname ${BASE_DIR}) ~/apps/alerts_center
cd ~/apps/alerts_center

# 收集静态文件
echo "复制静态文件"
echo yes | python manage.py collectstatic
date

# 数据库迁移
echo "数据库迁移"
python manage.py makemigrations
python manage.py migrate
date

echo "生成内置配置..."
python manage.py init_meta_data
python manage.py init_alert_template
python manage.py init_period_task
date

echo "重启进程..."
if [ -f $HOME/apps/supervisor/supervisord.pid ] ; then
  supervisorctl restart all
  supervisorctl status
  date
fi


