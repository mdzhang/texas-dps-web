"""Gunicorn entrypoint."""
from txdps.app import create_app
from txdps.config import setup

setup()

app = create_app()
server = app.server
