FROM python:3.9.10-slim-buster as compile-image

LABEL Joseph Ziegler "joseph@josephziegler.com"

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential python3-dev apt-utils && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /opt/venv

# Create virtual environment
RUN python3 -m venv .

# Make sure virtualenv is used
ENV PATH="/opt/venv/bin:$PATH"

COPY ./requirements.txt ./
RUN pip install --upgrade pip && \
    pip3 install -r requirements.txt

# ---------------------------------------

FROM python:3.9.10-slim-buster as running-image

RUN apt-get update && \
    apt-get install -y --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*
WORKDIR /opt/app
COPY . .
COPY --from=compile-image /opt/venv ./venv
RUN useradd appuser
RUN chown -R appuser /opt/app

USER appuser
ENV PATH="/opt/app/venv/bin:$PATH"

CMD ["/opt/app/venv/bin/uwsgi", "--ini", "/opt/app/uwsgi.ini", "--die-on-term" ]
