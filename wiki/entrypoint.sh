#!/bin/sh

echo "`date +"%F %X"` Building Python dependencies and system set-up ..."

apk update --no-cache \
    && apk add --no-cache python3 git py3-pip \
    && apk add --no-cache --virtual .build-deps \
                                    python3-dev \
                                    libffi-dev \
                                    gcc \
                                    libc-dev \
                                    tzdata \
    && pip --no-cache-dir install -U Flask \
                                     Flask-Login \
                                     Flask-WTF \
                                     Flask-Bcrypt \
                                     Markdown \
                                     Pygments \
                                     WTForms \
                                     python-markdown-math \
    && cp /usr/share/zoneinfo/Europe/Paris /etc/localtime \
    && apk del .build-deps \
    && mkdir /usr/local/flask-wiki \
    && cd /usr/local/flask-wiki \
    && git clone https://github.com/mjiao5151/wiki.git . \
    && pip install -e .

echo "`date +"%F %X"` Build done ..."

exec wiki --directory=$FLASK_DIR web \
          --host=$FLASK_HOST \
          --port=$FLASK_PORT \
          $FLASK_DEBUG
