FROM alpine:3.15
MAINTAINER @Lordslair

COPY requirements.txt /requirements.txt
COPY /api             /code

RUN apk update --no-cache \
    && apk add --no-cache python3 py3-pip \
    && apk add --no-cache --virtual .build-deps \
                                    gcc \
                                    g++ \
                                    libc-dev \
                                    libffi-dev \
                                    python3-dev \
                                    tzdata \
    && pip --no-cache-dir install -U -r /requirements.txt \
    && cp /usr/share/zoneinfo/Europe/Paris /etc/localtime \
    && apk del .build-deps \
    && rm /requirements.txt

ENTRYPOINT ["/code/entrypoint.sh"]
