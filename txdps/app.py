"""Flask entrypoint."""
import os

import dash
import dash_bootstrap_components as dbc
from txdps.config import setup
from txdps.layout import create_layout, register_callbacks

setup()


def create_app():
    """Create Flask app."""
    app = dash.Dash(
        __name__,
        meta_tags=[{"name": "viewport", "content": "width=device-width"}],
        external_stylesheets=[dbc.themes.SKETCHY],
    )

    app.layout = create_layout(app)
    register_callbacks(app)
    return app


def run():
    """Run Flask app."""
    app = create_app()
    app.run_server(debug=True, port=int(os.getenv("PORT", 8050)), host="0.0.0.0")


if __name__ == "__main__":
    run()
