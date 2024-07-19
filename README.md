# Advent Hunt Site

This is a Django web application that runs a puzzle hunt website.

## Requirements

Requires Python 3.11.9.

```bash
pip install -r dev-requirements.txt
```

## Deployment

...

## Development and deployment

> [!NOTE]
> This project uses [Just](https://github.com/casey/just) as a command runner. Several convenience commands are defined in [`justfile`](./justfile). You can print available commands by running:
>
> ```bash
> just
> ```

### Setup

1. Create and activate a Python 3.11.9 virtual environment. You can do this with your virtual environment tool of your choice. For example:
    ```bash
    python -m venv .venv
    source .venv/bin/activate
    ```
2. Install dependencies:
    ```bash
    just requirements
    # or
    python -m pip install -r dev-requirements.txt
    ```
3. Set up environment variables. This project can read from a `.env` file. Copy `.env.example` to `.env` and populate it according to the comments.
4. Create and migrate the database:
    ```bash
    just migrate
    # or
    python manage.py migrate
    ```

### Running the hunt site locally

```bash
just run
# or
python manage.py runserver
```

### Creating a superuser

If you have `
```bash
just createsuperuser
# or
python manage.py createsuperuser
```

### Creating demo data

```bash
just demo-data
# or
python manage.py create_demo_data
```

### Making migrations

If you change any of the database models, you'll need to generate database migrations. Run:

```bash
just migrate
# or
python manage.py makemigrations
python manage.py migrate
```

### Compiling requirements (lockfile)

If you update any of the dependencies required by the application, you'll need to update the lockfiles. This requires either uv or pip-tools. Depending on which you're using, run:

```bash
just compile-requirements    # requires uv
# or
uv pip compile requirements.in -o requirements.txt
uv pip compile dev-requirements.in -o dev-requirements.txt
# or
pip-compile requirements.in -o requirements.txt
pip-compile dev-requirements.in -o dev-requirements.txt
```
