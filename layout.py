import dash_core_components as dcc
import dash_html_components as html
import dash_table
import pandas as pd
from dash.dependencies import Input, Output, State

from utils import update_distances

df = pd.read_csv("locations.csv")


def load_df():
    return pd.read_csv("locations.csv")


def create_layout(app):
    """

    TODOs:

    - filter city from multi-select dropdown w/ typeahead
    - visualize on TX where DPS location is
    - add label w/ last updated date
    """
    return html.Div(
        [
            dcc.Input(id="zip", type="number", placeholder="Enter your zip code",),
            dash_table.DataTable(
                id="txdps-datatable",
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
            html.Div(id="txdps-datatable-container"),
        ]
    )


def register_callbacks(app):
    @app.callback(
        Output("txdps-datatable", "style_data_conditional"),
        [Input("txdps-datatable", "selected_columns")],
    )
    def update_styles(selected_columns):
        """Update table styling when user selects a column."""
        return [
            {"if": {"column_id": i}, "background_color": "#D2F3FF"}
            for i in selected_columns
        ]

    @app.callback(
        Output("txdps-datatable", "data"),
        [Input("zip", "value")],
        [State("txdps-datatable", "data")],
    )
    def recalculate_distances(zip_code: int, data):
        """When user updates zip code, update listed distance to DPS location."""
        df = update_distances(pd.DataFrame(data), zip_code)
        return df.to_dict("records")
