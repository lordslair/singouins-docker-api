FROM node:12-alpine
MAINTAINER @Lordslair

RUN apk update --no-cache \
    && apk add --no-cache dumb-init git

ARG USER_HOME_DIR="/tmp"
ARG APP_DIR="/app"
ARG USER_ID=1000
ARG NG_CLI_VERSION=10.2.0

LABEL angular-cli=$NG_CLI_VERSION node=$NODE_VERSION

#reduce logging, disable angular-cli analytics for ci environment
ENV NPM_CONFIG_LOGLEVEL=warn NG_CLI_ANALYTICS=false

#angular-cli rc0 crashes with .angular-cli.json in user home
ENV HOME "$USER_HOME_DIR"

RUN set -xe \
    && mkdir -p $USER_HOME_DIR \
    && chown $USER_ID $USER_HOME_DIR \
    && chmod a+rw $USER_HOME_DIR \
    && mkdir -p $APP_DIR \
    && chown $USER_ID $APP_DIR \
    && chown -R node /usr/local/lib /usr/local/include /usr/local/share /usr/local/bin \
    && (cd "$USER_HOME_DIR"; su node -c "npm install -g @angular/cli@$NG_CLI_VERSION; npm cache clean --force")

ENTRYPOINT ["/usr/bin/dumb-init", "--"]
