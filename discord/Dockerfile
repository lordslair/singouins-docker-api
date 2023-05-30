FROM alpine:3.17

RUN adduser -h /code -u 1000 -D -H discord

ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

ARG LOGURU_DATE="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
ARG LOGURU_LEVEL="<level>level={level: <8}</level> | "
ARG LOGURU_MSG="<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
ENV LOGURU_FORMAT=$LOGURU_DATE$LOGURU_LEVEL$LOGURU_MSG
ENV LOGURU_COLORIZE='true'

COPY --chown=discord:discord /discord/requirements.txt /code/requirements.txt
COPY --chown=discord:discord /discord/commands.py      /code/commands.py
COPY --chown=discord:discord /discord/tasks.py         /code/tasks.py
COPY --chown=discord:discord /discord/variables.py     /code/variables.py
COPY --chown=discord:discord /discord/subcommands      /code/subcommands
COPY --chown=discord:discord /nosql                    /code/nosql

WORKDIR /code
ENV PATH="/code/.local/bin:${PATH}"
ENV TZ="Europe/Paris"

RUN apk update --no-cache \
    && apk add --no-cache python3=~3.10 \
                          tzdata>=2023 \
    && apk add --no-cache --virtual .build-deps \
                                    gcc=~12.2 \
                                    libc-dev=~0.7 \
                                    python3-dev=~3.10 \
    && su discord -c "python3 -m ensurepip --upgrade \
                     && pip3 install --user -U -r requirements.txt \
                     && rm requirements.txt" \
    && apk del .build-deps

USER discord
