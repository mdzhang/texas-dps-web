import os

import dash
import dash_bootstrap_components as dbc
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

from layout import create_layout, register_callbacks

sentry_sdk.init(dsn=os.environ["SENTRY_DSN"], integrations=[FlaskIntegration()])


app = dash.Dash(
    __name__,
    meta_tags=[{"name": "viewport", "content": "width=device-width"}],
    external_stylesheets=[dbc.themes.SKETCHY],
)

server = app.server
app.layout = create_layout(app)
register_callbacks(app)

if __name__ == "__main__":
    app.run_server(debug=True, port=int(os.getenv('PORT', 8050)), host='0.0.0.0')
