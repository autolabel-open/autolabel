FROM docker.pengyihao.top/library/python:3.12

RUN python -m pip install -i https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple --upgrade pip
RUN pip config set global.index-url https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple
RUN pip install loguru rich requests
ADD ./app /app

CMD ["/bin/bash", "-c", "sleep infinity"]
