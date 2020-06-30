"""Functions for using Algolia for search."""
import logging
import os

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
    """Authenticate with Algolia and get index object."""
    client = SearchClient.create(ALGOLIA_APP_ID, ALGOLIA_API_KEY)
    return client.init_index("tx_dps_locations")


def create_index(uri: str):
    """Create and configure an Algolia index and fill it with objects.

    NB: Don't run this over and over; it'll use up all your freemium operations
    """
    df = pd.read_csv(uri)
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


def filter_df(df: pd.DataFrame, query: str):
    """Filter a dataframe based on a dash data table filter query."""
    logging.info(f"Filter query is: {query}")

    if query is None or not len(query.strip()):
        return df

    index = get_index()
    results = index.search(query, {"attributesToRetrieve": ["SiteId"]})
    site_ids = [s["SiteId"] for s in results["hits"]]
    return df[df.SiteId.isin(site_ids)]
