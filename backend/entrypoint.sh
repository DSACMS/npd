#!/bin/bash

python manage.py collectstatic --clear --noinput;
gunicorn --bind 0.0.0.0:8000 --workers 3 app.wsgi:application