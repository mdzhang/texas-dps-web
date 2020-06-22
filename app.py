import dash
import dash_bootstrap_components as dbc

from layout import create_layout, register_callbacks

app = dash.Dash(
    __name__,
    meta_tags=[{"name": "viewport", "content": "width=device-width"}],
    external_stylesheets=[dbc.themes.SKETCHY],
)

server = app.server
app.layout = create_layout(app)
register_callbacks(app)

if __name__ == "__main__":
    app.run_server(debug=True)
