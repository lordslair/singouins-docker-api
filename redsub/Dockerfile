FROM alpine:3.15

RUN adduser -h /code -u 1000 -D -H redsub

ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

ARG LOGURU_DATE="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
ARG LOGURU_LEVEL="<level>level={level: <8}</level> | "
ARG LOGURU_MSG="<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
ENV LOGURU_FORMAT=$LOGURU_DATE$LOGURU_LEVEL$LOGURU_MSG
ENV LOGURU_COLORIZE='true'
ENV LOGURU_DEBUG_COLOR='<cyan><bold>'

COPY --chown=redsub:redsub /redsub/requirements.txt /code/requirements.txt
COPY --chown=redsub:redsub /redsub/main.py          /code/main.py
COPY --chown=redsub:redsub /nosql                   /code/nosql

WORKDIR /code
ENV PATH="/code/.local/bin:${PATH}"
ENV TZ="Europe/Paris"

RUN apk update --no-cache \
    && apk add --no-cache python3=3.9.13-r1 \
                          tzdata=2022c-r0 \
    && su redsub -c "python3 -m ensurepip --upgrade \
                     && pip3 install --user -U -r requirements.txt \
                     && rm /requirements.txt"

USER redsub

ENTRYPOINT ["/code/main.py"]
