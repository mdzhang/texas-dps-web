web: gunicorn -b 0.0.0.0:${PORT:-5000} "txdps.wsgi:server" --access-logfile - --error-logfile -
data-refresh: ./bin/txdps schedule --uri=$S3_LOCATION --interval=$REFRESH_INTERVAL
