FROM docker.pengyihao.top/library/python:3.9-slim
WORKDIR /app
COPY . /app

RUN python -m pip install -i https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple --upgrade pip
RUN pip config set global.index-url https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple
RUN pip install --no-cache-dir flask gunicorn loguru

EXPOSE 5000

ENV FLASK_APP=app.py
CMD ["gunicorn", "--workers", "4", "--bind", "0.0.0.0:5000", "app:app"]
