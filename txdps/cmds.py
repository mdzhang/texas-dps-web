"""Commands invoked from CLI."""
import asyncio
import functools
import logging
import os
import sys
import typing as T
from datetime import datetime, timedelta

import pandas as pd
from apscheduler.schedulers.blocking import BlockingScheduler
from tabulate import tabulate

from txdps.alerts import notify_email, notify_phone
from txdps.api import cancel as _cancel
from txdps.api import get_all_appts_info, get_all_cities_info, get_site_info
from txdps.api import hold as _hold
from txdps.api import list_appointments as _list_appointments
from txdps.app import run as run_web
from txdps.search import create_index


def _pretty_print(df: pd.DataFrame, n: int):
    """Pretty print the head of the data frame to stdout."""
    n = int(n)
    s = tabulate(df.head(n), headers="keys", tablefmt="psql")
    print(s)
    return s


def _refresh_df(cities: T.List[str] = None, zip_code: int = None) -> pd.DataFrame:
    """Pull DPS and appointment info from the API and return in dataframe."""
    if not cities:
        cities = asyncio.run(get_site_info())

    # load most of the data we need here
    all_dfs = asyncio.run(get_all_cities_info(cities=cities, zip_code=zip_code))
    # since looking up all locations nearest to a specific city can return
    # the same location for 2 different cities, deduplicate on DPS location id
    return (
        pd.concat(all_dfs)
        .set_index("Id")
        .drop_duplicates()
        .sort_values("NextAvailableDate")
    )


def pull_and_upload(uri: str):
    """Pull latest DPS appointment data and reupload to S3."""
    df = _refresh_df()
    df.to_csv(uri)
    logging.info(f"Updated file at URI with {len(df)} rows: {uri}")


def pull(
    use_cache: bool,
    cache_file: str,
    cities: T.List[str],
    zip_code: int,
    max_dist: float,
    n: int,
):
    """Pull DPS and appointment info from cache file or API and pretty print."""
    if use_cache:
        logging.info(f"Using cache at {cache_file}")
        df = pd.read_csv(cache_file)
        df["NextAvailableDate"] = pd.to_datetime(df["NextAvailableDate"])
    else:
        df = _refresh_df(cities=cities, zip_code=zip_code)
        df.to_csv(cache_file)

    if max_dist > 0:
        logging.info(f"Limiting to locations within {max_dist} miles.")
        df = df[df["Distance"] <= max_dist]

    _pretty_print(df, n)


def notify_slot(df: pd.DataFrame, phone_number: int, email_address: str):
    """Send email or SMS messages that new DPS slots have opened up."""
    if df is None or not len(df):
        logging.info("No slots matching criteria to notify on.")
        return

    max_len = df["Name"].apply(len).sort_values(ascending=False).values[0]
    fmt_str = "{0:" + str(max_len + 1) + "} (ID: {1}) @ {2:20} ({3} min), Slot ID: {4}"
    slot_msgs = "\n".join(
        df.reset_index()[
            ["Name", "Id", "ApptStartDateTime", "ApptSlotId", "ApptDuration"]
        ]
        .apply(
            lambda r: fmt_str.format(
                r["Name"],
                r["Id"],
                r["ApptStartDateTime"],
                r["ApptDuration"],
                r["ApptSlotId"],
            ),
            axis=1,
        )
        .tolist()
    )
    msg = (
        "Slots have opened up at the following DPS locations "
        "matching your criteria:\n\n" + slot_msgs + "\n\n"
    )

    logging.info(msg)

    if phone_number:
        notify_phone(msg=msg, phone_number=phone_number)

    if email_address:
        notify_email(
            msg=msg,
            email_address=email_address,
            subject="New Texas DPS Appointments Available",
        )


def _find_matching_slots(
    cities: T.List[str],
    zip_code: int,
    max_dist: float,
    min_date: datetime.date,
    max_date: datetime.date,
    phone_number: int,
    email_address: str,
    **kwargs,
):
    df = _refresh_df(cities=cities, zip_code=zip_code)
    df["NextAvailableDate"] = pd.to_datetime(df["NextAvailableDate"])
    df = df[
        (df.NextAvailableDate > min_date)
        & (df.NextAvailableDate < max_date)
        & (df["Distance"] <= max_dist)
    ]

    if not len(df):
        logging.info("No appointments found.")
        return

    appt_dicts = asyncio.run(get_all_appts_info(df=df))
    df2 = pd.DataFrame(appt_dicts).set_index("Id")
    df3 = df.join(df2, lsuffix="", rsuffix="")
    return df3


def notify(
    cities: T.List[str],
    zip_code: int,
    max_dist: float,
    min_date: datetime.date,
    max_date: datetime.date,
    phone_number: int,
    email_address: str,
    **kwargs,
):
    """Pull latest DPS appt info, limit using criteria, and notify on match."""
    df = _find_matching_slots(
        cities=cities,
        zip_code=zip_code,
        max_dist=max_dist,
        min_date=min_date,
        max_date=max_date,
        phone_number=phone_number,
        email_address=email_address,
    )

    return notify_slot(df, phone_number, email_address)


def scan_and_autohold(
    cities: T.List[str],
    zip_code: int,
    max_dist: float,
    min_date: datetime.date,
    max_date: datetime.date,
    first_name: str,
    last_name: str,
    dob: datetime.date,
    last_4_ssn: int,
    card_number: int,
    phone_number: int,
    email_address: str,
    **kwargs,
):
    """Pull latest DPS appt info, limit using criteria, and notify on match."""
    if not max_date:
        appts = asyncio.run(
            _list_appointments(
                first_name=first_name,
                last_name=last_name,
                dob=dob,
                last_4_ssn=last_4_ssn,
            )
        )

        # HACK
        if os.getenv("APPLY_PLANO_HACK") is not None:
            appts = [a for a in appts if a["SiteName"] != "Plano"]

        if len(appts):
            # e.g. 2020-12-22T15:50:00
            max_date = datetime.strptime(
                sorted((a["BookingDateTime"] for a in appts))[0], "%Y-%m-%dT%H:%M:%S"
            )
            logging.info(f"Using max date {max_date.isoformat()}")
        else:
            max_date = datetime.date(datetime.now()) + timedelta(months=1)

    df = _find_matching_slots(
        cities=cities,
        zip_code=zip_code,
        max_dist=max_dist,
        min_date=min_date,
        max_date=max_date,
        phone_number=phone_number,
        email_address=email_address,
    )

    if df is None or not len(df):
        logging.info("No slots matching criteria. Nothing to hold")
        return

    # use whatever DPS location is closest
    best_appt = (
        df.sort_values("Distance", ascending=True)
        .head(1)
        .reset_index()
        .to_dict(orient="records")[0]
    )

    return hold(
        first_name=first_name,
        last_name=last_name,
        dob=dob,
        last_4_ssn=last_4_ssn,
        card_number=card_number,
        email_address=email_address,
        phone_number=phone_number,
        appt_time=best_appt["ApptStartDateTime"],
        appt_duration=best_appt["ApptDuration"],
        site_id=best_appt["Id"],
        slot_id=best_appt["ApptSlotId"],
    )


def cancel(conf_num: int, dob: str, first_name: str, last_4_ssn: int, last_name: str):
    """Cancel a DPS appointment booking."""
    res = asyncio.run(_cancel(conf_num, dob, first_name, last_4_ssn, last_name))
    logging.info(f"Appointment {conf_num} cancelled. {res}")


def hold(phone_number: int, email_address: str, **kwargs):
    """Reserve an appointment."""
    res = asyncio.run(
        _hold(phone_number=phone_number, email_address=email_address, **kwargs)
    )

    def report(msg: str):
        if phone_number:
            notify_phone(msg=msg, phone_number=phone_number)

        if email_address:
            notify_email(msg=msg, email_address=email_address)

    if res.get("ErrorMessage") is not None:
        msg = f"Almost! Failed to book appointment.\n\n{res['ErrorMessage']}"
        logging.fatal(msg)
        report(msg)
        raise ValueError(msg)

    conf_num = res["Booking"]["ConfirmationNumber"]
    url = f"https://public.txdpsscheduler.com?b={conf_num}"
    msg = f"""DPS appointment booked! See details at: {url}
Confirmation number is {conf_num}; use this to cancel.
"""
    logging.info(msg)
    report(msg)


def schedule(interval: int, **kwargs):
    """Start a long running process to re-run the data pull every <interval> min."""
    sched = BlockingScheduler()
    fn = functools.partial(pull_and_upload, **kwargs)
    sched.add_job(fn, "interval", minutes=interval)

    try:
        sched.start()
    except KeyboardInterrupt:
        sys.exit(0)


__all__ = [
    "cancel",
    "create_index",
    "hold",
    "notify",
    "pull",
    "pull_and_upload",
    "run_web",
    "scan_and_autohold",
    "schedule",
]
