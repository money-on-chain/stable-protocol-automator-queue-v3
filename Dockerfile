FROM python:3.10-slim

LABEL maintainer='martin.mulone@moneyonchain.com'

ARG TZ=UTC

RUN apt-get update && \
    apt-get install -y --no-install-recommends tzdata && \
    ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && \
    echo $TZ > /etc/timezone && \
    dpkg-reconfigure -f noninteractive tzdata && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir -p /home/www-data/app/automator && \
    chown -R www-data:www-data /home/www-data

ARG CONFIG=config.json

WORKDIR /home/www-data/app/automator/
COPY --chown=www-data:www-data app_run_automator.py ./
COPY --chown=www-data:www-data $CONFIG ./config.json
COPY --chown=www-data:www-data automator/ ./automator/

ENV PATH="$PATH:/home/www-data/app/automator/"
ENV AWS_DEFAULT_REGION="us-west-1"
ENV PYTHONPATH="/home/www-data/app/automator/"

USER www-data

CMD ["python", "./app_run_automator.py"]
