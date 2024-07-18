# Advent Hunt Site

This is a Django web application that runs a puzzle hunt website.

## Requirements

Requires Python 3.11.9.

```bash
pip install -r dev-requirements.txt
```

## Deployment

...

## Development

...

### justfile

This project uses [Just](https://github.com/casey/just) as a command runner. Several convenience commands are defined in [`justfile`](./justfile). You can print available commands by running:

```bash
just
```

### Compiling requirements (lockfile)

This requires either uv or pip-tools. Depending on which you're using, run:

```bash
just compile-requirements    # requires uv
# or
uv pip compile requirements.in -o requirements.txt
# or
pip-compile requirements.in -o requirements.txt
```
