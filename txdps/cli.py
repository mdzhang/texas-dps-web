"""CLI entrypoint."""
import argparse
import importlib
import re
import sys
from datetime import datetime, timedelta

from txdps.config import setup


def parse_date(s: str):
    """Get a datetime from a YYYY-MM-DD string."""
    return datetime.strptime(s, "%Y-%m-%d")


def get_parser():
    """Get a parser for pulling CLI arguments."""
    parser = argparse.ArgumentParser(
        description="Script for interacting with Texas DPS scheduler API"
    )

    # the result of parse_args will store the subcommand used in its
    # 'command' attribute
    subparsers = parser.add_subparsers(dest="command")
    today = datetime.date(datetime.now())

    all_args = {
        "booking_id": dict(
            flag="--booking-id",
            help="Appointment booking id unique to location, service, date, and time.",
            required=True,
        ),
        "slot_id": dict(
            flag="--slot-id",
            help="Appointment slot id unique to location, service, date, and time.",
            required=True,
        ),
        "first_name": dict(
            flag="--first-name",
            help="Your first name, like your real one.",
            required=True,
        ),
        "last_name": dict(
            flag="--last-name",
            help="Your last name, like your real one.",
            required=True,
        ),
        "dob": dict(
            flag="--dob",
            type=parse_date,
            help="Your date of birth as YYYY-MM-DD",
            required=True,
        ),
        "last_4_ssn": dict(
            flag="--last-4-ssn",
            type=int,
            help="Last 4 digits of your SSN",
            required=True,
        ),
        "card_number": dict(
            flag="--card-number", type=int, help="Your TX license #", required=True
        ),
        "email_address": dict(
            flag="--email-address", help="Have the DPS send emails to this address"
        ),
        "phone_number": dict(
            flag="--phone-number",
            help="Have the DPS send texts to this cell",
            type=lambda s: int(re.sub(r"[^\d]", "", s)),
        ),
        "site_id": dict(
            flag="--site-id", type=int, help="DPS location ID (as in notification msg)"
        ),
        "appt_time": dict(
            flag="--appt-time", type=str, help="Appt time (as in notification msg)"
        ),
        "appt_duration": dict(
            flag="--appt-duration",
            type=int,
            help="Appt duration (as in notification msg)",
        ),
        "cities": dict(
            flag="--cities",
            nargs="*",
            help="Only look at DPS locations in these cities",
            default=[],
        ),
        "zip_code": dict(
            flag="--zip-code",
            default=78741,
            help="Use this zip to find distances max dist will be compared against",
        ),
        "max_dist": dict(
            flag="--max-dist",
            type=float,
            default=50,
            help="Don't notify if slot locations are more than this many miles away",
        ),
        "min_date": dict(
            flag="--min-date",
            type=parse_date,
            default=today,
            help="Don't notify if only slots are before this date",
        ),
        "max_date": dict(
            flag="--max-date",
            type=parse_date,
            default=today + timedelta(days=14),
            help="Don't notify if only slots are after this date",
        ),
        "use_cache": dict(
            flag="--use-cache",
            action="store_true",
            help="Re-use local CSV cache file instead of refetching from API",
        ),
        "cache_file": dict(
            flag="--cache-file",
            default="locations.csv",
            help="Write available dates per location to local CSV file at this path",
        ),
        "uri": dict(
            flag="--uri",
            required=True,
            help="S3 URI to read/write fetched appointment data from/to",
        ),
        "n": dict(
            flag="-n",
            default=30,
            help="Print out this many locations with the next soonest availabilities",
        ),
    }
    notify_args = (
        "cities",
        "email_address",
        "max_date",
        "max_dist",
        "min_date",
        "phone_number",
        "zip_code",
    )
    hold_args = (
        "appt_duration",
        "appt_time",
        "card_number",
        "dob",
        "email_address",
        "first_name",
        "last_4_ssn",
        "last_name",
        "phone_number",
        "site_id",
        "slot_id",
    )

    cmd_args = {
        "schedule": {"help": "Like notify, but run on a schedule", "args": notify_args},
        "cancel": {"help": "Cancel a DPS appointment booking", "args": ("booking_id",)},
        "hold": {"help": "Hold a DPS appointment slot", "args": hold_args},
        "scan_and_autohold": {
            "help": (
                "Search for a slot matching the given criteria. If one is found "
                "book it right away and send a phone and/or email notification"
            ),
            "args": set(hold_args + notify_args)
            - {"slot_id", "site_id", "appt_time", "appt_duration"},
        },
        "notify": {
            "help": (
                "Search for a slot matching the given criteria. If one is found "
                "send a phone or email notification"
            ),
            "args": notify_args,
        },
        "pull": {
            "help": (
                "Finds the next available date for a new Driver License "
                "appointment in Texas DPS locations."
            ),
            "args": ("use_cache", "cache_file", "cities", "zip_code", "max_dist", "n"),
        },
        "pull_and_upload": {
            "help": (
                "Finds the next available date for a new Driver License "
                "appointment in Texas DPS locations, and uploads results to S3"
            ),
            "args": ("uri",),
        },
        "create_index": {"help": "Setup search index in Algolia.", "args": ("uri",)},
        "run_web": {"help": "Run web frontend.", "args": ()},
    }

    for cmd, spec in cmd_args.items():
        # dynamically import command function and register on globals
        cmd_module = importlib.import_module("txdps.cmds")
        cmd_fn = getattr(cmd_module, cmd)
        globals().update({cmd: cmd_fn})

        subparser = subparsers.add_parser(cmd, help=spec["help"])
        for arg in spec["args"]:
            argspec = all_args[arg]
            flag = argspec.pop("flag")
            subparser.add_argument(flag, **argspec)
            # args reused by different subparsers; popping flag
            # will lead to KeyError unless restored here
            argspec["flag"] = flag

    return parser


def main():
    """CLI entrypoint."""
    assert sys.version_info >= (3, 7), "Script requires Python 3.7+."

    parser = get_parser()
    args = parser.parse_args()

    # convert argparse Namespace object to dict
    kwargs = vars(args)
    cmd = kwargs.pop("command")

    if cmd is None:
        parser.print_help()
        sys.exit(2)

    # find function matching argparse subcommand name in module namespace
    # and invoke
    fn = globals()[cmd]
    fn(**kwargs)


if __name__ == "__main__":
    setup()
    main()
