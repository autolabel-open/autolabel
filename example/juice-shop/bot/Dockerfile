FROM docker.pengyihao.top/library/python:3.12.4-bookworm
USER root

RUN python -m pip install -i https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple --upgrade pip
RUN pip config set global.index-url https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple

# RUN curl -sSL https://install.python-poetry.org | python -
COPY ./poetry-install.py /
RUN python /poetry-install.py
ENV PATH="/root/.local/bin:$PATH"

RUN mkdir /root/bot
WORKDIR /root/bot
COPY . .
# RUN echo 'host_port: server:3000' > config.yaml
RUN echo 'placeholder: placeholder' > config.yaml
RUN poetry install

CMD sleep infinity
