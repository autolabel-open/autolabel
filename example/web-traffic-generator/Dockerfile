FROM docker.pengyihao.top/library/python:3.12

RUN pip install requests

COPY . /app
WORKDIR /app

CMD ["python", "gen.py"]
