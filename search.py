"""Functions for using Algolia for search."""
import os
import sys

import pandas as pd
from algoliasearch.search_client import SearchClient

ALGOLIA_APP_ID = os.getenv("ALGOLIA_APP_ID")
ALGOLIA_API_KEY = os.getenv("ALGOLIA_API_KEY")

FILTER_OPERATORS = [
    ["ge ", ">="],
    ["le ", "<="],
    ["lt ", "<"],
    ["gt ", ">"],
    ["ne ", "!="],
    ["eq ", "="],
    ["contains "],
    ["datestartswith "],
]


def get_index():
    client = SearchClient.create(ALGOLIA_APP_ID, ALGOLIA_API_KEY)
    return client.init_index("tx_dps_locations")


def create_index():
    """Create and configure an Algolia index and fill it with objects.

    NB: Don't run this over and over; it'll use up all your freemium operations
    """
    df = pd.read_csv("locations.2.csv")
    # this is the only thing that changes; in order to not drive up
    # the number of Algolia operations, which costs $$$,
    # just index on relatively static fields
    del df["NextAvailableDate"]
    df["objectID"] = df["SiteId"]
    records = df.to_dict("records")
    index = get_index()
    index.replace_all_objects(records)
    index.set_settings(
        {
            "searchableAttributes": list(
                set(df.columns)
                - set(["objectID", "Latitude", "Longitude"])  # noqa: C405
            )
        }
    )


def split_filter_part(filter_part: str):
    """Extract filter field, operator, and value from Dash DataTable filter query.

    Taken from https://dash.plotly.com/datatable/filtering
    """
    for operator_type in FILTER_OPERATORS:
        for operator in operator_type:
            if operator in filter_part:
                name_part, value_part = filter_part.split(operator, 1)
                start_idx = name_part.find("{") + 1
                end_idx = name_part.rfind("}")
                name = name_part[start_idx:end_idx]

                value_part = value_part.strip()
                v0 = value_part[0]
                if v0 == value_part[-1] and v0 in ("'", '"', "`"):
                    value = value_part[1:-1].replace("\\" + v0, v0)
                else:
                    value = value_part

                # word operators need spaces after them in the filter string,
                # but we don't want these later
                return name, operator_type[0].strip(), value

    return [None] * 3


def get_algolia_query(filter_query: str):
    """Convert dash DataTable query to Algolia query."""
    filtering_expressions = filter_query.split(" && ")

    filt_vals = []
    for part in filtering_expressions:
        col, op, val = split_filter_part(part)
        filt_vals.append(val)
    return " ".join(filt_vals)


def filter_df(df: pd.DataFrame, query: str):
    """Filter a dataframe based on a dash data table filter query."""
    print(f"Filter query is: {query}")

    if query is None or not len(query.strip()):
        return df

    # ag_filter_query = get_algolia_query(filter_query)

    index = get_index()
    results = index.search(query, {"attributesToRetrieve": ["SiteId"]})
    site_ids = [s["SiteId"] for s in results["hits"]]
    return df[df.SiteId.isin(site_ids)]


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "recreate":
        create_index()
    elif cmd == "search":
        df = pd.read_csv("locations.2.csv")
        filter_df(df, "{SiteId} contains 5")
