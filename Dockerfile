FROM python:3.8.9

COPY requirements.txt requirements.txt
RUN pip install -U pip && pip install -r requirements.txt && pip install gunicorn

COPY ./api /app/api
COPY ./bin /app/bin
COPY ./common /app/common
COPY wsgi.py /app/wsgi.py
WORKDIR /app

RUN useradd demo
USER demo

EXPOSE 8080

ENTRYPOINT ["bash", "/app/bin/run.sh"]
