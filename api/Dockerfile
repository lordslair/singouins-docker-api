FROM alpine:3.19

RUN adduser -h /code -u 1000 -D -H api

ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

COPY --chown=api:api /api   /code
COPY --chown=api:api /nosql /code/nosql

WORKDIR /code
ENV PATH="/code/.local/bin:${PATH}"

RUN apk update --no-cache \
    && apk add --no-cache \
        "python3>=3.11" \
        "py3-pip>=23" \
        "tzdata>=2023" \
    && apk add --no-cache --virtual .build-deps \
        "gcc=~12.2" \
        "g++=~12.2" \
        "libc-dev=~0.7" \
        "libffi-dev=~3.4" \
        "python3-dev>=3.11" \
    && su api -c \
        "pip3 install --break-system-packages --user -U -r requirements.txt && \
        rm requirements.* Dockerfile" \
    && apk del .build-deps

USER api

ENTRYPOINT ["/usr/bin/python3", "app.py"]
