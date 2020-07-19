"""Common setup logic."""
import logging
import os

import sentry_sdk


def setup():
    """Set up logging and error reporting."""
    logging.basicConfig(level=logging.INFO)

    integrations = []

    try:
        from sentry_sdk.integrations.flask import FlaskIntegration

        integrations.append(FlaskIntegration())
    except sentry_sdk.integrations.DidNotEnable as exc:
        logging.warn(exc)

    sentry_sdk.init(dsn=os.environ["SENTRY_DSN"], integrations=integrations)
