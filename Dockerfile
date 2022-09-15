FROM alpine:3.15

RUN adduser -h /code -u 1000 -D -H api

ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

ARG LOGURU_DATE="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
ARG LOGURU_LEVEL="<level>level={level: <8}</level> | "
ARG LOGURU_MSG="<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
ENV LOGURU_FORMAT=$LOGURU_DATE$LOGURU_LEVEL$LOGURU_MSG
ENV LOGURU_COLORIZE='true'
ENV LOGURU_DEBUG_COLOR='<cyan><bold>'

ENV PYTHONUNBUFFERED='True'
ENV PYTHONIOENCODING='UTF-8'

COPY                 requirements.txt /requirements.txt
COPY --chown=api:api /api             /code

WORKDIR /code
ENV PATH="/code/.local/bin:${PATH}"
ENV TZ="Europe/Paris"

RUN apk update --no-cache \
    && apk add --no-cache python3=3.9.13-r1 \
                          tzdata=2022c-r0 \
    && apk add --no-cache --virtual .build-deps \
                                    gcc=10.3.1_git20211027-r0 \
                                    g++=10.3.1_git20211027-r0 \
                                    libc-dev=0.7.2-r3 \
                                    libffi-dev=3.4.2-r1 \
                                    python3-dev=3.9.13-r1 \
    && su api -c "python3 -m ensurepip --upgrade \
                  && pip3 install --user -U -r /requirements.txt" \
    && apk del .build-deps \
    && rm /requirements.txt

USER api

ENTRYPOINT ["/usr/bin/python3", "app.py"]
