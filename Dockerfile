FROM python:3.9.10-slim-buster

MAINTAINER Joseph Ziegler "joseph@josephziegler.com"

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential python3-dev supervisor apt-utils && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY ./requirements.txt ./
RUN pip install --upgrade pip && \
    pip3 install -r requirements.txt

COPY . .
COPY uwsgi.ini /etc/uwsgi/
COPY supervisord.conf /etc/

CMD ["/usr/bin/supervisord"]
