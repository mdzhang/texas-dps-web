import dash_core_components as dcc
import dash_html_components as html
import dash_table
import pandas as pd
from dash.dependencies import Input, Output

from distance import update_distances
from search import filter_df


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


def rename_col(colname: str):
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
    """

    TODOs:

    - filter city from multi-select dropdown w/ typeahead
    - visualize on TX where DPS location is
    - add label w/ last updated date
    """
    dt_df = load_original_df()
    return html.Div(
        [
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
                    if i not in {"Latitude", "Longitude"}
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
        [Input("zip", "value"), Input("search", "value")],
    )
    def update_datatable(zip_code: int, query: str):
        """Update datatable data when filters are updated.

        Specifically,
            when user updates zip code, update listed distance to DPS location.
            when filter is given, filter data
        """
        df = load_original_df()
        # apply filters on Algolia index first
        df = filter_df(df, query)
        df = update_distances(df, zip_code)
        return df.to_dict("records")
