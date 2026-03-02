FROM python:3.11.14-alpine

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY ./src /app/src
COPY ./main.py /app/main.py

ENV PYTHONPATH=/app

RUN addgroup -S chronicle && adduser -S chronicle -G chronicle
USER chronicle

WORKDIR /app

CMD ["python", "main.py"]