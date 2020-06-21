import os
import typing as T

import dash_core_components as dcc
import dash_html_components as html
import dash_table
import pandas as pd
import plotly.express as px
from dash.dependencies import Input, Output

from distance import update_distances
from search import filter_df

px.set_mapbox_access_token(os.getenv("MAPBOX_TOKEN"))


def load_original_df():
    df = pd.read_csv("locations.csv").rename(
        {"Id": "SiteId", "Name": "SiteName"}, axis=1
    )
    df["NextAvailableDate"] = pd.to_datetime(df["NextAvailableDate"]).dt.date
    df["Distance"] = None
    return df[
        [
            "Distance",
            "NextAvailableDate",
            "SiteId",
            "SiteName",
            "CityName",
            "Address",
            "ZipCode",
            "Latitude",
            "Longitude",
        ]
    ]


def get_map(df: pd.DataFrame):
    if "IsSelected" not in df.columns:
        df["IsSelected"] = False

    return px.scatter_mapbox(
        df,
        lat="Latitude",
        lon="Longitude",
        zoom=5,
        hover_data=["SiteName"],
        color="IsSelected",
    )


def rename_col(colname: str):
    """Pretty rename dataframe columns for user-displayed data table."""
    return {
        "SiteId": "Site ID",
        "SiteName": "Site Name",
        "CityName": "City",
        "Address": "Address",
        "ZipCode": "Zip",
        "Distance": "Distance (miles)",
        "NextAvailableDate": "Next Available Date",
    }[colname]


def create_layout(app):
    """Create core Plotly Dash layout object.

    TODOs:

    - nice styling & header
    - add label w/ last updated date
    """
    dt_df = load_original_df()
    return html.Div(
        [
            html.H1("Texas DPS Locations & Upcoming Appointments"),
            dcc.Input(id="search", type="text", placeholder="Enter a search string",),
            dcc.Input(id="zip", type="number", placeholder="Enter your zip code",),
            dash_table.DataTable(
                id="txdps-datatable",
                columns=[
                    {
                        "name": rename_col(i),
                        "id": i,
                        "deletable": True,
                        "selectable": False,
                    }
                    for i in dt_df.columns
                    if i not in {"Latitude", "Longitude", "IsSelected"}
                ],
                data=dt_df.to_dict("records"),
                editable=True,
                sort_action="native",
                sort_mode="multi",
                column_selectable=False,
                row_selectable="multi",
                row_deletable=False,
                selected_columns=[],
                selected_rows=[],
                page_action="native",
                page_current=0,
                page_size=10,
            ),
            html.Div(id="txdps-datatable-container"),
            dcc.Graph(
                id="map",
                style={"width": "100%", "display": "inline-block"},
                figure=get_map(dt_df),
            ),
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
        [Output("txdps-datatable", "data"), Output("map", "figure")],
        [
            Input("zip", "value"),
            Input("search", "value"),
            Input("txdps-datatable", "selected_rows"),
        ],
    )
    def update_datatable(zip_code: int, query: str, selected_rows: T.List[int]):
        """Update datatable data when filters are updated.

        Specifically,
            when user updates zip code, update listed distance to DPS location.
            when filter is given, filter data
        """
        df = load_original_df()
        # apply filters on Algolia index first
        df = filter_df(df, query)
        df = update_distances(df, zip_code)

        df["IsSelected"] = df.index.isin(selected_rows)
        tx_map = get_map(df)

        return [df.to_dict("records"), tx_map]
