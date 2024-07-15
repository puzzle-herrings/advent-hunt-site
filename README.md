# Advent Hunt Site

This is a Django web application that runs a puzzle hunt website.

## Running

```bash
pip install -r requirements.txt
```

## Deployment

## Development

### Compiling requirements (lockfile)

This requires either uv or pip-tools. Depending on which you're using, run:

```bash
uv pip compile requirements.in -o requirements.txt
# or
pip-compile requirements.in -o requirements.txt
```
