"""Helpers that pull from DPS API."""
import asyncio
import logging
import typing as T
import urllib
from datetime import datetime

import aiohttp
import pandas as pd
from txdps.distance import update_distances

BASE_API = "https://publicapi.txdpsscheduler.com/api"
HTTP_HEADERS = {"Origin": "https://public.txdpsscheduler.com"}
DEFAULT_SERVICE_ID = 71


def format_phone(num: int):
    """Format phone number as e.g. '(111) 111-1111'."""
    num_s = str(num)
    return f"({num_s[:3]}) {num_s[3:6]}-{num_s[6:]}"


def pull_zip_town(addr: str) -> T.Tuple[int, str]:
    """Pull the zip code and town name from an address.

    Usage:
    >>> addr = '6121 N Lamar, Austin 78752'
    >>> pull_zip_town(addr)
    (78752, 'Austin')
    >>> addr = '3506 Twin River Blvd, Corpus Christi 78410'
    >>> pull_zip_town(addr)
    (78410, 'Corpus Christi')
    """
    try:
        town, zip_code = addr.rsplit(",", 1)[-1].strip().rsplit(" ", 1)
        return zip_code, town
    except ValueError as exc:
        logging.critical(f"Failed to parse address: {addr}")
        raise exc


def pull_lat_long(url: str) -> T.Tuple[float, float]:
    """Pull the latitude and longitude for an address from a Google Maps URL.

    Usage:
    >>> url = 'http://maps.google.com/?saddr=&daddr=30.431045,-97.649429'
    >>> pull_lat_long(url)
    (30.431045, -97.649429)
    """
    query_params = dict(urllib.parse.parse_qsl(urllib.parse.urlsplit(url).query))
    lat, long = map(float, query_params["daddr"].split(","))
    return lat, long


async def get_site_info() -> T.Tuple[T.List[dict], int]:
    """Get DPS scheduler site-wide info (mostly for city and service lists).

    :return: list of cities, DPS ID for service offered
    """
    logging.info("Fetching scheduler site wide data...")
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{BASE_API}/SiteData", headers=HTTP_HEADERS) as res:
            res_body = await res.json(content_type="text/plain")
            return res_body["Cities"]


async def get_city_info(
    session, city: str, service_id: int = DEFAULT_SERVICE_ID, zip_code: int = None
) -> pd.DataFrame:
    """Get DPS locations with next available date for a service nearest to a specific city.

    :param session: aiohttp session
    :param city: find next available appointment dates for 5 DPS locations
        nearest this city
    :param service_id: find next available appointment dates for DPS services
        of given ID
    :param zip_code: find distance from DPS location to this zip code in miles
    """
    logging.info(f"Fetching data for city: '{city}'...")
    payload = {
        "TypeId": service_id,
        "ZipCode": "",
        # if you pass a city, it'll just find the 5 nearest DPS locations
        "CityName": city,
        # if you can go to the DPS any day of the week, pass 0 here
        "PreferredDay": 0,
    }

    async with session.post(
        f"{BASE_API}/AvailableLocation", json=payload, headers=HTTP_HEADERS
    ) as res:
        res_body = await res.json(content_type="text/plain")
        logging.info(f"Finished fetching data for city: '{city}'.")

        df = pd.DataFrame(res_body)

        df[["Latitude", "Longitude"]] = pd.DataFrame(
            df["MapUrl"].apply(pull_lat_long).tolist(), index=df.index
        )
        df[["ZipCode", "CityName"]] = pd.DataFrame(
            df["Address"].apply(pull_zip_town).tolist(), index=df.index
        )
        cols = [
            "Address",
            "Id",
            "Name",
            "NextAvailableDate",
            "Latitude",
            "Longitude",
            "ZipCode",
            "CityName",
        ]

        if zip_code:
            df = update_distances(df, zip_code)
            cols = cols + ["Distance"]

        df = df[cols]
        df["NextAvailableDate"] = pd.to_datetime(df["NextAvailableDate"])
        return df


async def get_appointment_info(
    session, site_name: str, site_id: int, service_id: int = DEFAULT_SERVICE_ID
):
    """Get specific info on the next available appointment for the given site."""
    logging.info(f"Fetching latest appointment data for location: '{site_name}'...")
    payload = {
        "LocationId": site_id,
        "TypeId": service_id,
        "SameDay": False,
        "StartDate": None,
        "PreferredDay": 0,
    }

    async with session.post(
        f"{BASE_API}/AvailableLocationDates", json=payload, headers=HTTP_HEADERS
    ) as res:
        res_body = await res.json(content_type="text/plain")
        logging.info(f"Finished fetching appointment data for location: '{site_name}'.")

        first_avail = res_body.get("LocationAvailabilityDates", [{}])[0].get(
            "AvailableTimeSlots", [{}]
        )[0]
        return {
            "ApptStartDateTime": first_avail.get("StartDateTime"),
            "ApptEndDateTime": first_avail.get("EndDateTime"),
            "ApptSlotId": first_avail.get("SlotId"),
            "ApptDuration": first_avail.get("Duration"),
            "Id": site_id,
        }


async def get_all_cities_info(
    cities: T.List[str], service_id: int = DEFAULT_SERVICE_ID, zip_code: int = None
) -> T.List[pd.DataFrame]:
    """Fetch per-city info concurrently."""
    async with aiohttp.ClientSession() as session:
        return await asyncio.gather(
            *[
                get_city_info(
                    session, city=city, service_id=service_id, zip_code=zip_code
                )
                for city in cities
            ]
        )


async def get_all_appts_info(
    df: pd.DataFrame, service_id: int = DEFAULT_SERVICE_ID
) -> T.List[pd.DataFrame]:
    """Fetch per-city info concurrently."""
    async with aiohttp.ClientSession() as session:
        return await asyncio.gather(
            *[
                get_appointment_info(
                    session, site_name=row["Name"], site_id=idx, service_id=service_id
                )
                for idx, row in df.iterrows()
            ]
        )


async def cancel(booking_id: int):
    """Cancel an existing booking."""
    async with aiohttp.ClientSession() as session:
        res = await session.post(
            f"{BASE_API}/CancelBooking",
            json={"BookingId": booking_id},
            headers=HTTP_HEADERS,
        )
        return await res.json(content_type="text/plain")


async def hold(
    slot_id: int,
    first_name: str,
    last_name: str,
    dob: datetime.date,
    last_4_ssn: int,
    card_number: int,
    email_address: str,
    phone_number: int,
    appt_time: str,
    appt_duration: int,
    site_id: int,
    **kwargs,
):
    """Book an appointment with the TX DPS."""
    common = {
        "FirstName": first_name,
        "LastName": last_name,
        "DateOfBirth": dob.strftime("%m/%d/%Y"),
        "Last4Ssn": last_4_ssn,
    }

    hold_payload = {"SlotId": slot_id, **common}
    # TODO: be less biased in my default payload
    book_payload = {
        "CardNumber": card_number,
        "Email": email_address,
        "CellPhone": format_phone(phone_number),
        "HomePhone": "",
        "ServiceTypeId": DEFAULT_SERVICE_ID,
        "BookingDateTime": appt_time,
        "BookingDuration": appt_duration,
        "SpanishLanguage": "N",
        "SiteId": site_id,
        "SendSms": True,
        "AdaRequired": False,
        **common,
    }

    async with aiohttp.ClientSession() as session:
        # hold
        res = await session.post(
            f"{BASE_API}/HoldSlot", json=hold_payload, headers=HTTP_HEADERS
        )
        await res.json(content_type="text/plain")

        # confirm
        res = await session.post(
            f"{BASE_API}/Booking", json=common, headers=HTTP_HEADERS
        )
        book_res = await res.json(content_type="text/plain")
        logging.debug(f"Booked appointment. {book_res}")

        # if you already had an appointment for the same service, you need
        # to cancel the old to book the new
        collision = next(
            (b for b in book_res if b["ServiceTypeId"] == DEFAULT_SERVICE_ID), None
        )
        if collision:
            endpoint = "RescheduleBooking"
        else:
            endpoint = "NewBooking"
        logging.info(f"Using endpoint: {endpoint}")

        res = await session.post(
            f"{BASE_API}/{endpoint}", json=book_payload, headers=HTTP_HEADERS
        )
        return await res.json(content_type="text/plain")
