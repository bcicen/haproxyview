#!/bin/bash

cd /app/haproxyview/
python2 cli.py &
gunicorn -w 8 -k eventlet --bind=0.0.0.0:8000 api:app
