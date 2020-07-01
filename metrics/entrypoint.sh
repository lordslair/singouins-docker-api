#!/bin/sh

echo "`date +"%F %X"` Building Python dependencies and system set-up ..."

apk update --no-cache \
    && apk add --no-cache python3 py3-pip \
    && apk add --no-cache --virtual .build-deps \
                                    gcc \
                                    libc-dev \
                                    python3-dev \
                                    libffi-dev \
                                    tzdata \
    && pip3 --no-cache-dir install -U -r https://raw.githubusercontent.com/lordslair/sep-backend/master/metrics/requirements.txt \
    && cp /usr/share/zoneinfo/Europe/Paris /etc/localtime \
    && apk del .build-deps

echo "`date +"%F %X"` Build done ..."

echo "`date +"%F %X"` Loading Python scripts ..."
mkdir /code && cd /code
wget https://raw.githubusercontent.com/lordslair/sep-backend/master/metrics/metrics.py
chmod 755 /code/metrics.py
wget https://raw.githubusercontent.com/lordslair/sep-backend/master/metrics/mod_mysql.py
echo "`date +"%F %X"` Loading done ..."

exec python3 /code/metrics.py
