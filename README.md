# Advent Hunt Site

This is a Django web application that runs a puzzle hunt website. It was used for the [Advent Puzzle Hunt](https://www.adventhunt.com) website in 2024.

Developed on and deployed on Python 3.11.9.

> [!NOTE]
> This project uses [Just](https://github.com/casey/just) as a command runner. Several convenience commands are defined in [`justfile`](./justfile). You can print available commands by running:
>
> ```bash
> just
> ```
>
> Many of the Just commands use [uv](https://github.com/astral-sh/uv) for managing dependencies.


## Development

### Environment setup

1. Create and activate a Python 3.11.9 virtual environment. You can do this with your virtual environment tool of your choice. For example:
    ```bash
    python -m venv .venv
    source .venv/bin/activate
    ```
2. Install development dependencies:
    ```bash
    just requirements
    # or
    python -m pip install -r requirements/dev.txt
    ```

### Running the site locally

#### Setup

1. Set up environment variables. This project can read from a `.env` file. Copy `.env.example` to `.env` and populate it according to the comments.
2. Create the database and run migrations:
    ```bash
    just migrate
    # or
    python manage.py migrate
    ```

#### Running the development server

```bash
just run
# or
python manage.py runserver
```

#### Creating a superuser

Make sure you have the `DJANGO_SUPERUSER_*` environment variables set in your `.env` file. Then run:

```bash
just createsuperuser
# or
python manage.py createsuperuser
```

#### Creating demo data

```bash
just demo-data
# or
python manage.py create_demo_data
```

### Repository organization

```
.
├── huntsite/       # Application code
├── justfile        # Convenience command definitions
├── manage.py       # Django command-line utility
├── project/        # Project settings (settings.py, wsgi.py)
├── pyproject.toml  # Tool configuration
├── render.yaml     # Deployment blueprint for Render hosting service
├── requirements/   # Package dependencies
├── scripts/        # Scripts for deployment, testing, etc.
├── static/         # Static assets
└── templates/      # View templates
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
uv pip compile requirements/deploy.in -o requirements/deploy.txt
uv pip compile requirements/demo.in -o requirements/demo.txt
uv pip compile requirements/dev.in -o requirements/dev.txt
# or
pip-compile requirements/deploy.in -o requirements/deploy.txt
pip-compile compile requirements/demo.in -o requirements/demo.txt
pip-compile compile requirements/dev.in -o requirements/dev.txt
```

## Deployment

You can deploy this application anywhere where you can deploy a Python application.

In general, it'll be most convenient to use a cloud platform-as-a-service. Some examples include:

- [Render](https://render.com/)—we used this for Advent Puzzle Hunt. A [blueprint file](https://docs.render.com/infrastructure-as-code) is in the repository ([`render.yaml`](./render.yaml)).
- [Heroku](https://www.heroku.com)—probably the most widely known and used hosting service.
- [Fly.io](https://fly.io/)

### Important environment variables

A lot of configuration is done via environment variables, which are read into [`project/settings.py`](./project/settings.py). You should be able to find sections in `settings.py` that match the documented sections below.

#### Hunt State

The variable `HUNT_IS_LIVE_DATETIME` optionally lets you switch control behavior before and after a nominal "start" time for the hunt. A context processor `hunt_is_live` sets a boolean context variable `hunt_is_live` indicating whether the current time is before or after `HUNT_IS_LIVE_DATETIME`. If not set, it will be set to the current time when the application starts up.

#### HTML Metadata

This controls the `<meta>` tag data in rendered views for things like website title and description. You must set these values.

- `META_TITLE` — Title for your website. Will be used in browser tabs, search engine results, and social media links.
- `META_DESCRIPTION` — Description for your website. Will be used in search engine results and social media links.
- `META_AUTHOR` — Author information. Will be used in search engine results and social media links.
- `META_KEYWORDS` — Comma-separated list of keywords for search engines.
- `META_OG_IMAGE` — OpenGraph image, used for social media links.
— `META_OG_IMAGE_PREHUNT` — (optional) OpenGraph image, used for social media links. Used if before `HUNT_IS_LIVE_DATETIME`.

#### Email

This app uses [django-allauth](https://docs.allauth.org/en/latest/) for auth and account management. It sends transactional emails for email verification and password resets.

You will need to set up a transactional email service provider to actually send any emails. We use [django-anymail](https://anymail.dev/en/stable/) to integrate a provider. See the `## Email` section of the [`project/settings.py`](./project/settings.py) to see the relevant environment variables. Currently, `project/settings.py` supports Mailgun and MailSender. You can easily add integration for any other provider that Anygun supports.

#### Error and Performance Monitoring

This app is set up with the Sentry SDK to send errors and performance data to a Sentry-compatible monitoring platform. Examples include [Sentry](https://sentry.io/) and [GlitchTip](https://glitchtip.com/).

#### Other settings

- `ACCOUNT_DISABLE_REGISTRATION` — Setting to `True` will disable signups. This can be useful if your site is deployed but you're still developing stuff and are not ready for real users.
- `ROBOTS_DISALLOW_ALL` — Setting to `True` will set the `robots.txt` file to disallow everything. This will prevent search engines from crawling your site, and is useful if your site is deployed but you're still developing stuff and are not ready for real users.
