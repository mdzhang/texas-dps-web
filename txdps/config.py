"""Common setup logic."""
import logging
import os

import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration


def setup():
    """Set up logging and error reporting."""
    logging.basicConfig(level=logging.INFO)
    sentry_sdk.init(dsn=os.environ["SENTRY_DSN"], integrations=[FlaskIntegration()])
