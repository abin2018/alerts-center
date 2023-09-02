# 使用python 3.11.4 作为基础镜像
FROM python:3.11.4
# 创建工作目录
RUN mkdir /alerts_center
# 切换工作目录
WORKDIR /alerts_center
# 将当前目录加入到工作目录中
ADD . /alerts_center
# 安装依赖
RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
# 对外暴露端口
#EXPOSE 9009
RUN chmod +x /alerts_center/wait-for-it.sh
# 执行启动脚本
ENTRYPOINT ["/bin/bash", "/alerts_center/run.sh"]
CMD ["run_django"]