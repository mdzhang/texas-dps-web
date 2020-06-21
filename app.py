import dash

from layout import create_layout, register_callbacks

app = dash.Dash(
    __name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}]
)

server = app.server
app.layout = create_layout(app)
register_callbacks(app)

if __name__ == "__main__":
    app.run_server(debug=True)
