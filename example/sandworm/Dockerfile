FROM docker.pengyihao.top/library/centos:7.9.2009

RUN sed -e "s|^mirrorlist=|#mirrorlist=|g" \
    -e "s|^#baseurl=http://mirror.centos.org/centos/\$releasever|baseurl=https://mirrors.tuna.tsinghua.edu.cn/centos-vault/7.9.2009|g" \
    -e "s|^#baseurl=http://mirror.centos.org/\$contentdir/\$releasever|baseurl=https://mirrors.tuna.tsinghua.edu.cn/centos-vault/7.9.2009|g" \
    -i.bak \
    /etc/yum.repos.d/CentOS-*.repo

COPY files/docker/systemctl.py /usr/bin/systemctl

RUN yum -y install cronie && systemctl enable crond

# Note: this script is invoked via sudo

# install apache web server and SSL module
# this is used for the PHP webshell TTPs
RUN yum install httpd openssl php mod_ssl -y

# set apache web server to start on system boot
RUN systemctl enable httpd

# restart apache to ensure TLS  and PHP modules load
RUN systemctl restart httpd.service

# create directories needed for privEsc via SUID binary
RUN mkdir -p /var/www/html/include/tools

# create check.sh, used for the SUID binary TTP
RUN echo "ps auxf | grep -i httpd" > /var/www/html/include/tools/check.sh
RUN echo "netstat -antp | grep -i httpd" >> /var/www/html/include/tools/check.sh
RUN chmod 744 /var/www/html/include/tools/check.sh

# give apache user ownership of the html dir
RUN chown -R apache:apache /var/www/html

RUN yum -y install openssh-server openssh-clients passwd

# 添加新用户并设置密码
RUN useradd myuser && \
    echo 'myuser:MYPASSWORD' | chpasswd

RUN sed -i 's/^#PermitRootLogin yes/PermitRootLogin yes/' /etc/ssh/sshd_config
RUN sed -i 's/^#PasswordAuthentication yes/PasswordAuthentication yes/' /etc/ssh/sshd_config
RUN sed -i 's/^#PermitEmptyPasswords no/PermitEmptyPasswords no/' /etc/ssh/sshd_config

# 生成 SSH 需要的密钥
RUN ssh-keygen -A

RUN yum -y install net-tools

RUN yum -y install sudo
RUN echo "ALL            ALL = (ALL) NOPASSWD: ALL" >> /etc/sudoers

RUN rm /var/run/httpd/httpd.pid

COPY ./suid-binary /tmp/suid-binary

# setup the SUID binary
RUN mv /tmp/suid-binary /bin/backup
RUN chown root:root /bin/backup
RUN chmod 4755 /bin/backup

RUN ssh-keygen -t rsa -N '' -C 'SSH Key' -f '/root/.ssh/id_rsa'

CMD ["/usr/bin/systemctl"]
