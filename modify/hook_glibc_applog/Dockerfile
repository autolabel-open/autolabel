FROM docker.pengyihao.top/library/centos:6

RUN sed -i 's|^mirrorlist=|#mirrorlist=|g' /etc/yum.repos.d/CentOS-Base.repo && \
    sed -i 's|^#baseurl=http://mirror.centos.org/centos/$releasever|baseurl=http://vault.centos.org/6.10|g' /etc/yum.repos.d/CentOS-Base.repo

RUN yum install -y gcc make glibc-devel

COPY hook_glibc_applog.c /hook_glibc_applog.c
COPY Makefile /Makefile

RUN make
