FROM docker.pengyihao.top/library/python:3.12.4-bookworm
USER root

COPY ./poetry-install.py /
RUN python /poetry-install.py

# RUN curl -sSL https://install.python-poetry.org | python -
ENV PATH="/root/.local/bin:$PATH"

RUN mkdir /root/bot
WORKDIR /root/bot
COPY . .
# RUN echo 'host_port: server:3000' > config.yaml
RUN echo 'placeholder: placeholder' > config.yaml
RUN poetry install

CMD sleep infinity

# poetry run python main.py
