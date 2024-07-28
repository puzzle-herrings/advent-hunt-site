#!/usr/bin/env bash

# Exit on error
set -o errexit

# Install requirements
if [[ $DEMO_DATA ]]; then
    pip install -r requirements/demo.txt
else
    pip install -r requirements/deploy.txt
fi

# Convert static asset files
python manage.py collectstatic --no-input

# Apply any outstanding database migrations
python manage.py migrate --no-input

if [[ $CREATE_SUPERUSER ]]; then
    echo "Creating superuser..."
    python manage.py createsuperuser --no-input
fi

if [[ $DEMO_DATA ]]; then
    python manage.py create_demo_data
fi
