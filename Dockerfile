FROM alpine:3.15
MAINTAINER @Lordslair

RUN adduser -h /code -u 1000 -D -H api

ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

ENV LOGURU_COLORIZE='true'
ENV LOGURU_DEBUG_COLOR='<cyan><bold>'

ENV PYTHONUNBUFFERED='True'
ENV PYTHONIOENCODING='UTF-8'

COPY                 requirements.txt /requirements.txt
COPY --chown=api:api /api             /code

RUN apk update --no-cache \
    && apk add --no-cache python3 \
    && apk add --no-cache --virtual .build-deps \
                                    gcc \
                                    g++ \
                                    libc-dev \
                                    libffi-dev \
                                    python3-dev \
                                    tzdata \
    && cp /usr/share/zoneinfo/Europe/Paris /etc/localtime \
    && cd /code \
    && su api -c "python3 -m ensurepip --upgrade \
                  && /code/.local/bin/pip3 install --user -U -r /requirements.txt" \
    && apk del .build-deps \
    && rm /requirements.txt

USER api
WORKDIR /code
ENV PATH="/code/.local/bin:${PATH}"

ENTRYPOINT ["/code/entrypoint.sh"]
