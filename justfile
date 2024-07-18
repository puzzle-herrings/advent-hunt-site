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
    uv pip sync dev-requirements.txt

# Create requirements lockfile
compile-requirements:
    uv pip compile requirements.in -o requirements.txt
