"""Utility functions chunky enough to be separated from main layout module."""
import math
import typing as T

import pandas as pd
from uszipcode import SearchEngine

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
