# WSGI
python -m gunicorn project.wsgi:application

# ASGI
# python -m gunicorn project.asgi:application -k uvicorn.workers.UvicornWorker
