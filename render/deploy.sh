# WSGI
python -m gunicorn advent_hunt.wsgi:application

# ASGI
# python -m gunicorn advent_hunt.asgi:application -k uvicorn.workers.UvicornWorker
