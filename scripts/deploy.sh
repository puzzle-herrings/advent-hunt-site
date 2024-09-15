#!/usr/bin/env bash

# WSGI
python -m gunicorn project.wsgi:application -c scripts/gunicorn_config.py

# ASGI
# python -m gunicorn project.asgi:application -k uvicorn.workers.UvicornWorker
