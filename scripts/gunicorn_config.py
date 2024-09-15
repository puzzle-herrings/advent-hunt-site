from environs import Env

env = Env()
env.read_env()

max_requests = env.int("GUNICORN_MAX_REQUESTS", default=0)
max_requests_jitter = env.int("GUNICORN_MAX_REQUESTS_JITTER", default=0)

workers = env.int("GUNICORN_WORKERS", default=1)
