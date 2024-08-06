# Print this help documentation
help:
  just --list

# Run the development server
run:
    python manage.py runserver

# Make migrations
makemigrations:
    python manage.py makemigrations

# Make migrations and run them
migrate: makemigrations
    python manage.py migrate

# Drop the development sqlite database
drop-db:
    rm db.sqlite3 || true

# Delete all migrations and regenerate them. Will drop the database.
delete-migrations: drop-db
    rm huntsite/puzzles/migrations/0*.py || true
    rm huntsite/teams/migrations/0*.py || true

# Sync requirements in current virtual environment
requirements:
    uv pip sync requirements/dev.txt

# Create requirements lockfile
compile-requirements:
    uv pip compile requirements/deploy.in -o requirements/deploy.txt
    uv pip compile requirements/demo.in -o requirements/demo.txt
    uv pip compile requirements/dev.in -o requirements/dev.txt

# Lint the project
lint:
    ruff format --check project huntsite
    ruff check project huntsite
    djlint templates --check
    djlint templates --lint


# Autoformat the project
format:
    ruff format project huntsite
    ruff check --fix project huntsite
    djlint templates --reformat

# Run tests
test:
    DEPLOY_ENVIRONMENT=test pytest

createsuperuser:
    python manage.py createsuperuser --noinput

demo-data:
    python manage.py create_demo_data

# Locust load testing - browsing
locust-browsing:
    locust -f scripts/locustfile.py --tags browsing

# Locust load testing - solving
locust-solving:
    locust -f scripts/locustfile.py --tags solving
