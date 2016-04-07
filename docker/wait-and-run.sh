#!/bin/bash

set -e

host="$1"
export PGPASSWORD=$POSTGRES_PASSWORD
until psql -h "$host" -U $POSTGRES_USER -c '\l'; do
      >&2 echo "Postgres is unavailable - sleeping"
      sleep 1
done

>&2 echo "Postgres is up - doing Django magic"
cd /root/pytrader

# http://stackoverflow.com/questions/23564529/chartit-is-not-a-valid-tag-librarydjango
sed -i  's/from django.utils import simplejson/import simplejson/' /usr/local/lib/python2.7/site-packages/chartit/templatetags/chartit.py
./manage.py syncdb --noinput
# For some reason I can't make it run from the subdir. I dont know Django too
# well.
cp ./docker/create_admin.py ./
./create_admin.py
./manage.py migrate --noinput
crontab /root/pytrader/docker/crontab_docker.txt
env > /tmp/.app.env
exec supervisord -n -c /root/pytrader/docker/supervisord.conf
