import dash_html_components as html
import dash_table
import pandas as pd
from dash.dependencies import Input, Output

df = pd.read_csv("locations.csv")


def create_layout(app):
    """

    TODOs:

    - filter city from multi-select dropdown w/ typeahead
    - visualize on TX where DPS location is
    - update distance based on user provided location
    - add label w/ last updated date
    """
    return html.Div(
        [
            dash_table.DataTable(
                id="datatable-interactivity",
                columns=[
                    {"name": i, "id": i, "deletable": True, "selectable": True}
                    for i in df.columns
                ],
                data=df.to_dict("records"),
                editable=True,
                filter_action="native",
                sort_action="native",
                sort_mode="multi",
                column_selectable="single",
                row_selectable="multi",
                row_deletable=True,
                selected_columns=[],
                selected_rows=[],
                page_action="native",
                page_current=0,
                page_size=10,
            ),
            html.Div(id="datatable-interactivity-container"),
        ]
    )


def register_callbacks(app):
    @app.callback(
        Output("datatable-interactivity", "style_data_conditional"),
        [Input("datatable-interactivity", "selected_columns")],
    )
    def update_styles(selected_columns):
        return [
            {"if": {"column_id": i}, "background_color": "#D2F3FF"}
            for i in selected_columns
        ]
