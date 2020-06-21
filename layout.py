import typing as T

import dash_core_components as dcc
import dash_html_components as html
import dash_table
import pandas as pd
from dash.dependencies import Input, Output, State

from utils import filter_df, is_valid_zip, update_distances


def load_original_df():
    df = pd.read_csv("locations.csv").rename(
        {"Id": "SiteId", "Name": "SiteName"}, axis=1
    )
    df["NextAvailableDate"] = pd.to_datetime(df["NextAvailableDate"])
    return df


def load_datatable_df():
    df = load_original_df()
    return df[
        [
            "SiteId",
            "SiteName",
            "CityName",
            "Address",
            "ZipCode",
            "Distance",
            "NextAvailableDate",
        ]
    ]


def create_layout(app):
    """

    TODOs:

    - filter city from multi-select dropdown w/ typeahead
    - visualize on TX where DPS location is
    - add label w/ last updated date
    """
    dt_df = load_datatable_df()
    return html.Div(
        [
            dcc.Input(id="zip", type="number", placeholder="Enter your zip code",),
            dash_table.DataTable(
                id="txdps-datatable",
                columns=[
                    {"name": i, "id": i, "deletable": True, "selectable": False}
                    for i in dt_df.columns
                ],
                data=dt_df.to_dict("records"),
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
        [Input("zip", "value"), Input("txdps-datatable", "filter_query")],
        [State("txdps-datatable", "data")],
    )
    def recalculate_distances(zip_code: int, filter_query: str, data: T.List[dict]):
        """Update datatable data when filters are updated.

        Specifically,
            when user updates zip code, update listed distance to DPS location.
            when filter is given, filter data
        """
        df = pd.DataFrame(data)
        if filter_query is None and not is_valid_zip(zip_code):
            df = load_datatable_df()
        else:
            df = filter_df(df, filter_query)
            df = update_distances(df, zip_code)
        print(len(df))
        return df.to_dict("records")
