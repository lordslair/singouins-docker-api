FROM alpine:3.7
MAINTAINER @Lordslair

RUN apk update --no-cache \
    && apk add --no-cache python3 \
    && apk add --no-cache --virtual  .build-deps \
                                      python3-dev \
                                      libffi-dev \
                                      gcc \
                                      libc-dev \
                                      tzdata \
    && pip3 --no-cache-dir install -U discord.py \
                                      pyMySQL \
                                      numpy \
                                      SQLAlchemy \
                                      termcolor \
    && cp /usr/share/zoneinfo/Europe/Paris /etc/localtime \
    && apk del .build-deps

COPY *.py      /code/
COPY resources /code/resources
COPY utils     /code/utils

ENTRYPOINT ["/code/discord-bot.py"]
