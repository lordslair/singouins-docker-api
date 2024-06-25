FROM alpine:3.19

RUN adduser -h /code -u 1000 -D -H ai

ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

COPY --chown=ai:ai /ai/bestiaire        /code/bestiaire
COPY --chown=ai:ai /ai/tests            /code/tests
COPY --chown=ai:ai /ai/utils            /code/utils
COPY --chown=ai:ai /ai/main.py          /code/main.py
COPY --chown=ai:ai /ai/requirements.txt /code/requirements.txt
COPY --chown=ai:ai /mongo               /code/mongo
COPY --chown=ai:ai /nosql               /code/nosql

WORKDIR /code
ENV PATH="/code/.local/bin:${PATH}"

RUN apk update --no-cache \
    && apk add --no-cache \
        "python3>=3.11" \
        "py3-pip>=23" \
        "tzdata>=2023" \
    && su ai -c \
        "pip3 install --break-system-packages --user -U -r requirements.txt \
        && rm requirements.txt"

USER ai

ENTRYPOINT ["/usr/bin/python3", "main.py"]
