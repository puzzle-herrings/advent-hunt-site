default:
  just --list

run:
    python manage.py runserver

makemigrations:
    python manage.py makemigrations

migrate: makemigrations
    python manage.py migrate

drop-db:
    rm db.sqlite3 || true

delete-migrations: drop-db
    rm huntsite/puzzles/migrations/0*.py || true
    rm huntsite/teams/migrations/0*.py || true
