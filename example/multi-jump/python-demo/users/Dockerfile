FROM docker.pengyihao.top/library/python:3.12.4-bookworm

# RUN curl -sSL https://install.python-poetry.org | python -
COPY ./poetry-install.py /
RUN python /poetry-install.py
ENV PATH="$PATH:/root/.local/bin"

WORKDIR /app
COPY . /app
RUN poetry install

CMD ["sleep", "infinity"]
