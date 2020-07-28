#!/bin/sh

echo "`date +"%F %X"` Building Python dependencies and system set-up ..."

apk update --no-cache \
    && apk add --no-cache python3 \
    && apk add --no-cache --virtual  .build-deps \
                                      python3-dev \
                                      libffi-dev \
                                      gcc \
                                      libc-dev \
                                      tzdata \
    && pip3 --no-cache-dir install -U discord.py \
                                      pyMySQL \
                                      SQLAlchemy \
    && cp /usr/share/zoneinfo/Europe/Paris /etc/localtime \
    && apk del .build-deps

echo "`date +"%F %X"` Build done ..."

echo "`date +"%F %X"` Loading Python scripts ..."
mkdir  /code && cd /code
wget   https://github.com/lordslair/sep-backend/archive/master.zip -O /code/sep.zip &&
unzip  /code/sep.zip -d /code/ &&
cp -a  /code/sep-backend-master/discord/* /code/ &&
rm -rf /code/sep-backend-master /code/sep.zip
echo "`date +"%F %X"` Loading done ..."

exec python3 -u /code/discord-bot.py
