"""Flask entrypoint."""
import os

import dash
import dash_bootstrap_components as dbc
from txdps.config import setup
from txdps.layout import create_layout, register_callbacks

setup()

app = dash.Dash(
    __name__,
    meta_tags=[{"name": "viewport", "content": "width=device-width"}],
    external_stylesheets=[dbc.themes.SKETCHY],
)

server = app.server
app.layout = create_layout(app)
register_callbacks(app)

if __name__ == "__main__":
    app.run_server(debug=True, port=int(os.getenv("PORT", 8050)), host="0.0.0.0")
