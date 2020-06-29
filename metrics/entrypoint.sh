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
    && pip3 --no-cache-dir install -U -r /code/requirements.txt \
    && cp /usr/share/zoneinfo/Europe/Paris /etc/localtime \
    && apk del .build-deps

echo "`date +"%F %X"` Build done ..."

exec /code/metrics.py
