#!/bin/sh

echo "`date +"%F %X"` Starting ..."
echo "FLASK    env    | $FLASK_ENV"
echo "GUNICORN chdir  | /code"
echo "GUNICORN bind   | $GUNICORN_HOST:$GUNICORN_PORT"
echo "GUNICORN w:t    | $GUNICORN_WORKERS:$GUNICORN_THREADS"
echo "GUNICORN reload | $GUNICORN_RELOAD"

exec gunicorn app:app \
				--chdir /code \
	      --bind $GUNICORN_HOST:$GUNICORN_PORT \
	      --log-file=- \
        --access-logfile=- \
        --error-logfile=- \
        --worker-tmp-dir /dev/shm \
        --workers=$GUNICORN_WORKERS \
        --threads=$GUNICORN_THREADS \
        --worker-class=gthread \
        $GUNICORN_RELOAD
