"""Create core Dash layout.

TODOs:

- nice styling
- add label w/ last updated date
- read df/CSV from S3
- mapbox bounding box select of columns
- histogram of next available date
- distance slider selector
"""
import os
import typing as T

import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import numpy as np
import pandas as pd
import plotly.express as px
from dash.dependencies import Input, Output, State

from distance import is_valid_zip, update_distances
from search import filter_df

px.set_mapbox_access_token(os.getenv("MAPBOX_TOKEN"))


def get_slider_marks():
    vals = np.linspace(0, 800, 5)
    return {int(v): {"label": str(int(v))} for v in vals}


def load_original_df():
    df = pd.read_csv("locations.csv").rename(
        {"Id": "SiteId", "Name": "SiteName"}, axis=1
    )
    df["NextAvailableDate"] = pd.to_datetime(df["NextAvailableDate"]).dt.date
    df["Distance"] = None
    df["IsSelected"] = False
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
            "IsSelected",
        ]
    ]


def update_df(query: str, zip_code: int, distance_range: T.List[int]):
    df = load_original_df()
    # apply filters on Algolia index first
    df = filter_df(df, query)
    df = update_distances(df, zip_code)

    if is_valid_zip(zip_code):
        df = df[
            (df["Distance"] >= distance_range[0])
            & (df["Distance"] <= distance_range[1])
        ]
    return df


def get_map(df: pd.DataFrame):
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


def get_filter_and_search_row():
    return dbc.Row(
        [
            dbc.Col(
                dbc.FormGroup(
                    [
                        dbc.Input(
                            id="search",
                            type="text",
                            placeholder="Enter a search string",
                        ),
                        dbc.FormText(
                            "Search on cities, DPS location names, zip codes, etc."
                        ),
                    ]
                ),
                width=3,
            ),
            dbc.Col(
                dbc.FormGroup(
                    [
                        dbc.Input(
                            id="zip", type="number", placeholder="Enter your zip code",
                        ),
                        dbc.FormText(
                            "Enter your zip code to estimate distance to DPS locations"
                        ),
                    ]
                ),
                width=3,
            ),
            dbc.Col(
                dbc.FormGroup(
                    [
                        dcc.RangeSlider(
                            id="distance-range",
                            min=0,
                            max=800,
                            value=[0, 800],
                            allowCross=False,
                            marks=get_slider_marks(),
                        ),
                        dbc.FormText("Select a distance range (miles)"),
                    ]
                ),
                width=6,
            ),
        ],
        style={"margin-top": "1rem"},
    )


def get_datatable(dt_df):
    return dash_table.DataTable(
        id="txdps-datatable",
        columns=[
            {"name": rename_col(i), "id": i, "deletable": True, "selectable": False,}
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
    )


def create_layout(app):
    """Create core Plotly Dash layout object."""
    dt_df = load_original_df()
    return html.Div(
        children=[
            dbc.NavbarSimple(
                brand="Texas DPS Locations & Upcoming Appointments",
                dark=True,
                color="primary",
            ),
            dbc.Container(
                [
                    get_filter_and_search_row(),
                    dbc.Row(get_datatable(dt_df), key="dps-data"),
                    dbc.Row(
                        dcc.Graph(
                            id="map",
                            style={"width": "100%", "height": "100%"},
                            figure=get_map(dt_df),
                        ),
                        key="graph",
                    ),
                ],
                style={"max-width": "90%"},
            ),
        ],
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
        Output("map", "figure"),
        [
            Input("txdps-datatable", "selected_rows"),
            Input("zip", "value"),
            Input("search", "value"),
            Input("distance-range", "value"),
        ],
        [State("txdps-datatable", "data")],
    )
    def recolor_map_dots(selected_rows, zip_code, query, distance_range, old_data):
        """Only show locations on map also in data table. Color by selected."""
        df_old = pd.DataFrame(old_data)
        selected_site_ids = df_old[df_old.index.isin(selected_rows)].SiteId.tolist()
        df = update_df(zip_code=zip_code, query=query, distance_range=distance_range)
        df["IsSelected"] = df.SiteId.isin(selected_site_ids)
        return get_map(df)

    @app.callback(
        Output("txdps-datatable", "data"),
        [
            Input("zip", "value"),
            Input("search", "value"),
            Input("distance-range", "value"),
        ],
    )
    def update_datatable(zip_code: int, query: str, distance_range: T.List[int]):
        """Update datatable data when filters are updated.

        Specifically,
            when user updates zip code, update listed distance to DPS location.
            when filter is given, filter data
        """
        df = load_original_df()
        df = update_df(zip_code=zip_code, query=query, distance_range=distance_range)

        return df.to_dict("records")

    @app.callback(
        Output("distance-range", "marks"), [Input("distance-range", "value")],
    )
    def update_slider_markers(distance_range: T.List[int]):
        """Update datatable data when filters are updated.

        Specifically,
            when user updates zip code, update listed distance to DPS location.
            when filter is given, filter data
        """
        marks = get_slider_marks()
        low, high = distance_range
        marks[low] = str(low)
        marks[high] = str(high)

        return marks
