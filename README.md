# Advent Hunt Site

This is a Django web application that runs a puzzle hunt website. It was used for the [Advent Puzzle Hunt](https://2024.adventhunt.com) website in 2024. You can find additional discussion about design choices and deployment in [this blog post](https://www.jayqi.com/blog/advent-hunt-site-design-notes/).

Developed on and deployed on Python 3.11.9.

## Development

> [!NOTE]
> ### Requirements
>
> This project uses the following tools:
>
> - [**Just**](https://github.com/casey/just) as a command runner. Several convenience commands are defined in [`justfile`](./justfile).
> - [**uv**](https://github.com/astral-sh/uv) for managing Python dependencies.
>
> To print documentation for all available Just commands, run:
>
> ```bash
> just
> ```
>
> You can do things without Just by just inspecting the [`justfile`](./justfile) and copying and pasting out the commands. You can also do things without uv by using `pip` in place of `uv pip` and `pip-compile`/`pip-sync` from pip-tools in place of `uv pip compile`/`uv pip sync`.

### Python environment setup

1. Create and activate a Python 3.11.9 virtual environment. You can do this with your virtual environment tool of your choice. For example:
    ```bash
    python -m venv .venv
    source .venv/bin/activate
    ```
2. Install development dependencies:
    ```bash
    just requirements    # requires uv
    ```

### Running the site locally

#### Setup

1. Set up environment variables. This project can read from a `.env` file. Copy `.env.example` to `.env` and populate it according to the comments.
2. Create the database and run migrations:
    ```bash
    just migrate
    ```

#### Running the development server

```bash
just run
```

#### Creating a superuser

Make sure you have the `DJANGO_SUPERUSER_*` environment variables set in your `.env` file. Then run:

```bash
just createsuperuser
```

#### Creating demo data

```bash
just demo-data
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
```

### Compiling requirements (lockfile)

If you update any of the dependencies required by the application, you'll need to update the lockfiles. This requires either uv or pip-tools. Depending on which you're using, run:

```bash
just compile-requirements    # requires uv
```

## Deployment

You can deploy this application anywhere where you can deploy a Python application.

In general, it'll be most convenient to use a cloud platform-as-a-service. Some examples include:

- [Render](https://render.com/)—we used this for Advent Puzzle Hunt. A [blueprint file](https://docs.render.com/infrastructure-as-code) is in the repository ([`render.yaml`](./render.yaml)).
- [Heroku](https://www.heroku.com)—another widely known and commonly used hosting service.
- [Fly.io](https://fly.io/)

### Creating a superuser

Normally, you run `python manage.py createsuperuser` on the web server to create an initial admin user. This requires shell access to the web server.

Sometimes, free tiers of web hosts don't provide shell access (e.g., Render's free tier). As a workaround, the build script [`scripts/build.sh`](./scripts/build.sh) can run `createsuperuser` controlled by environment variables. First, make sure the following environment variables are set:

- `DJANGO_SUPERUSER_USERNAME`
- `DJANGO_SUPERUSER_PASSWORD`
- `DJANGO_SUPERUSER_EMAIL`
- `DJANGO_SUPERUSER_TEAM_NAME`

Then set the environment variable `CREATE_SUPERUSER=1` before `build.sh` runs. This will cause `build.sh` to run `createsuperuser --no-input` and read the values from the other environment variables. Don't forget to unset `CREATE_SUPERUSER` after running this once—it's not idempotent.

### Important environment variables

A lot of configuration is done via environment variables, which are read into [`project/settings.py`](./project/settings.py). You should be able to find sections in `settings.py` that match the documented sections below.

#### Hunt state

There are three states to the hunt website:

- `PREHUNT`: Before the hunt is "live" and the hunt story is revealed
- `LIVE`: While the hunt is "live"
- `ENDED`: After the hunt has "ended"—leaderboard is frozen, solutions are posted

These hunt states are controlled by two environment variables `HUNT_IS_LIVE_DATETIME` and `HUNT_IS_ENDED_DATETIME`. The current time is then checked against these two timestamps. If not set, `HUNT_IS_LIVE_DATETIME` is set to the current time at application start, and `HUNT_IS_ENDED_DATETIME` is set to 31 days in the future.

#### HTML Metadata

This controls the `<meta>` tag data in rendered views for things like website title and description. You must set these values.

- `META_TITLE` — Title for your website. Will be used in browser tabs, search engine results, and social media links.
- `META_DESCRIPTION` — Description for your website. Will be used in search engine results and social media links.
- `META_AUTHOR` — Author information. Will be used in search engine results and social media links.
- `META_KEYWORDS` — Comma-separated list of keywords for search engines.
- `META_OG_IMAGE` — OpenGraph image, used for social media links.
— `META_OG_IMAGE_PREHUNT` — (optional) OpenGraph image, used for social media links. Used when hunt is in the `PREHUNT` state.

#### Email

This app uses [django-allauth](https://docs.allauth.org/en/latest/) for auth and account management. It sends transactional emails for email verification and password resets.

You will need to set up a transactional email service provider to actually send any emails. We use [django-anymail](https://anymail.dev/en/stable/) to integrate a provider. See the `## Email` section of the [`project/settings.py`](./project/settings.py) to see the relevant environment variables. Currently, `project/settings.py` supports Mailgun and MailSender. You can easily add integration for any other provider that Anymail supports.

#### Error and Performance Monitoring

This app is set up with the Sentry SDK to send errors and performance data to a Sentry-compatible monitoring platform. Examples include [Sentry](https://sentry.io/) and [GlitchTip](https://glitchtip.com/).

#### Other settings

- `ACCOUNT_DISABLE_REGISTRATION` — Setting to `True` will disable signups. This can be useful if your site is deployed but you're still developing stuff and are not ready for real users.
- `ANNOUNCEMENT_MESSAGE` — If set, will display a message in a notification block at the top of all pages.
- `DISCORD_SERVER_LINK` — If set, logged in users will see this link in the navbar. Used for the hunt community Discord server invite link.
- `ROBOTS_DISALLOW_ALL` — Setting to `True` will set the `robots.txt` file to disallow everything. This will prevent search engines from crawling your site, and is useful if your site is deployed but you're still developing stuff and are not ready for real users.
