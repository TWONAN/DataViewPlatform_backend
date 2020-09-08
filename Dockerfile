[root@twonan VisualData_backend]# vim Dockerfile
FROM docker.io/python:3.6.4-stretch
MAINTAINER XHN

# 设置工作目录，作用是启动容器后直接进入的目录名称
WORKDIR /app
copy . /app
copy ./sources.list /etc/apt/sources.list

RUN apt-get update && \
apt-get install apt-transport-https && \
apt-get install ca-certificates && \
apt-get install gcc

ENV TZ=Asia/Shanghai
ENV PIPURL "https://mirrors.aliyun.com/pypi/simple/"

RUN echo $TZ > /etc/timezone
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime

RUN pip install --upgrade pip -i ${PIPURL} && \
pip --no-cache-dir install -i ${PIPURL} -r requirements.txt