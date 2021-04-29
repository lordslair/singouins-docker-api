#!/bin/sh

echo "`date +"%F %X"` Loading Python scripts ..."
mkdir  /code
cd     /code
wget   https://github.com/lordslair/singouins-docker/archive/master.zip -O /tmp/sep.zip &&
unzip  /tmp/sep.zip -d /tmp/ &&
cp -a  /tmp/singouins-docker-master/api/* /code/ &&
rm -rf /tmp/singouins-docker-master &&
rm -rf /tmp/sep.zip &&
wget -q https://api.github.com/repos/lordslair/singouins-docker/commits/master -O - 2&>1 | grep '^  .sha' | cut -d'"' -f4 > /code/.git
echo "`date +"%F %X"` Loading done ..."

exec gunicorn app:app \
	      --bind $GUNICORN_HOST:$GUNICORN_PORT \
	      --log-file=- \
        --access-logfile=- \
        --error-logfile=- \
        --worker-tmp-dir /dev/shm \
        --workers=$GUNICORN_WORKERS \
        --threads=$GUNICORN_THREADS \
        --worker-class=gthread \
        $GUNICORN_RELOAD
