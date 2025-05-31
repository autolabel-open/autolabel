FROM docker.pengyihao.top/library/centos:6

RUN sed -i 's|^mirrorlist=|#mirrorlist=|g' /etc/yum.repos.d/CentOS-Base.repo && \
    sed -i 's|^#baseurl=http://mirror.centos.org/centos/$releasever|baseurl=http://vault.centos.org/6.10|g' /etc/yum.repos.d/CentOS-Base.repo

RUN yum install -y gcc make glibc-devel

COPY hook_glibc_attacker.c /hook_glibc_attacker.c
COPY ip_list.h /ip_list.h
COPY Makefile /Makefile
COPY configure.py /configure.py
COPY config_attack.py /config_attack.py

RUN make clean
RUN make hook_glibc_attacker.so
