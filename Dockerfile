FROM python:3.10

# Autor
LABEL maintainer='martin.mulone@moneyonchain.com'

RUN apt-get update && \
    apt-get install -y \
        locales

RUN echo $TZ > /etc/timezone && \
    apt-get update && apt-get install -y tzdata && \
    rm /etc/localtime && \
    ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && \
    dpkg-reconfigure -f noninteractive tzdata && \
    apt-get clean

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt


RUN mkdir /home/www-data && mkdir /home/www-data/app \
    && mkdir /home/www-data/app/automator

ARG CONFIG=config.json

WORKDIR /home/www-data/app/automator/
COPY app_run_automator.py ./
ADD $CONFIG ./config.json
COPY automator/ ./automator/
ENV PATH="$PATH:/home/www-data/app/automator/"
ENV AWS_DEFAULT_REGION="us-west-1"
ENV PYTHONPATH="/home/www-data/app/automator/"

CMD ["python", "./app_run_automator.py"]
