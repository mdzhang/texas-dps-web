"""Utility functions chunky enough to be separated from main layout module."""
import logging
import math
import typing as T

import numpy as np
import pandas as pd
from uszipcode import SearchEngine

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


def is_valid_zip(zip_code: int):
    """See if the given value is a valid US zip code."""
    search = SearchEngine(simple_zipcode=True)
    origin_zip = search.by_zipcode(zip_code)

    return origin_zip.zipcode is not None


def haversine_distance(
    origin: T.Tuple[float, float], destination: T.Tuple[float, float], unit="mi"
) -> float:
    """Get the Haversine distance between two points on the Earth.

    Taken from https://gist.github.com/rochacbruno/2883505

    :param origin: origin point lat long as tuple
    :param destination: destination point lat long as tuple
    :param unit: Pass 'km' for kilometers, 'mi' for miles,
        'ft' for feet, 'm' for meters.
    """
    lat1, lon1 = origin
    lat2, lon2 = destination
    radius = {"km": 6371, "mi": 3959, "ft": 3959 * 5280, "m": 6371 * 1000}.get(unit)

    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) * math.sin(dlat / 2) + math.cos(
        math.radians(lat1)
    ) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) * math.sin(dlon / 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    d = radius * c

    return d


def update_distances(df: pd.DataFrame, zip_code: int):
    """Update distance column based on provided ZIP code."""
    search = SearchEngine(simple_zipcode=True)
    origin_zip = search.by_zipcode(zip_code)

    if origin_zip.zipcode is None:
        df["Distance"] = None
        return df

    origin_latlong = (origin_zip.lat, origin_zip.lng)

    df["Distance"] = df[["Latitude", "Longitude"]].apply(
        lambda row: round(
            haversine_distance(origin_latlong, (row["Latitude"], row["Longitude"])), 2,
        ),
        axis=1,
    )

    return df


def split_filter_part(filter_part: str):
    """Extract filter field, operator, and value from filter query.

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
                    try:
                        value = float(value_part)
                    except ValueError:
                        value = value_part

                # word operators need spaces after them in the filter string,
                # but we don't want these later
                return name, operator_type[0].strip(), value

    return [None] * 3


def filter_df(df: pd.DataFrame, filter_query: str):
    """Filter a dataframe based on a dash data table filter query."""
    logging.info(f"Filter query is: {filter_query}")

    if filter_query is None:
        return df

    filtering_expressions = filter_query.split(" && ")
    for filter_part in filtering_expressions:
        col_name, operator, filter_value = split_filter_part(filter_part)
        col = df[col_name]
        dtype = col.dtype

        if operator in ("eq", "ne", "lt", "le", "gt", "ge"):
            # these operators match pandas series operator method names
            df = df.loc[getattr(col, operator)(filter_value)]
        elif operator == "contains":
            if dtype != np.dtype("O"):
                col = col.astype(str)
                filter_value = str(filter_value)

            df = df.loc[col.str.contains(filter_value)]
        elif operator == "datestartswith":
            # this is a simplification of the front-end filtering logic,
            # only works with complete fields in standard format
            df = df.loc[col.str.startswith(filter_value)]

    return df
