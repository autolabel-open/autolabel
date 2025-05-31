FROM docker.pengyihao.top/library/ubuntu:22.04

RUN apt-get update
RUN apt-get install -y ca-certificates

RUN echo "deb https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ jammy main restricted universe multiverse" > /etc/apt/sources.list && \
    echo "deb https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ jammy-updates main restricted universe multiverse" >> /etc/apt/sources.list && \
    echo "deb https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ jammy-backports main restricted universe multiverse" >> /etc/apt/sources.list && \
    echo "deb http://security.ubuntu.com/ubuntu/ jammy-security main restricted universe multiverse" >> /etc/apt/sources.list

RUN apt-get update
RUN apt-get install -y python3 python3-pip python-is-python3
RUN apt-get install -y openssh-server
RUN apt-get install -y curl sshpass

RUN pip install rich requests

ADD . /app
WORKDIR /app

CMD ["sleep", "infinity"]
