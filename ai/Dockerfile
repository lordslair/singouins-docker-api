FROM alpine:3.18

RUN adduser -h /code -u 1000 -D -H ai

ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

ARG LOGURU_DATE="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
ARG LOGURU_LEVEL="<level>level={level: <8}</level> | "
ARG LOGURU_MSG="<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
ENV LOGURU_FORMAT=$LOGURU_DATE$LOGURU_LEVEL$LOGURU_MSG

COPY --chown=ai:ai /ai    /code
COPY --chown=ai:ai /nosql /code/nosql

WORKDIR /code
ENV PATH="/code/.local/bin:${PATH}"

RUN apk update --no-cache \
    && apk add --no-cache \
        "python3>=3.11" \
        "tzdata>=2023" \
    && su ai -c \
        "python3 -m ensurepip --upgrade && \
        pip3 install --user -U -r requirements.txt && \
        rm requirements.* Dockerfile"

USER ai

ENTRYPOINT ["/usr/bin/python3", "main.py"]
