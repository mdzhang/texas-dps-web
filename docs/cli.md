# CLI

In addition to the web frontend to explore DPS appointment data, a CLI tool to find, reserve, and release appointments with the Texas DPS is also provided.

## Requirements

In addition to those in the main [README](../README.md):

- A [Twilio account](https://www.twilio.com/docs/usage/tutorials/how-to-use-your-free-trial-account) if you want to notify with SMS
- A [Sendgrid account](https://sendgrid.com/pricing/) if you want to notify with Sendgrid

## Usage

Follow setup in main [README](../README.md).

Set additional required environment variables:

```sh
SENDGRID_API_KEY=
SENTRY_AUTH_TOKEN=
SENTRY_DSN=
SENTRY_ORG=
SENTRY_PROJECT=
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
TWILIO_PHONE_NUMBER=
```

To grab all locations with their next available date and distance from zip code `78741` and write them to `locations.csv`, but only print the top `10` locations within `50` miles:

```sh
$ bin/txdps pull --cache-file locations.csv --zip-code 78741 -n 10 --max-dist 50
```

Once you figure out the cities you want to limit on, to automatically book any slot for Driver's License services between `2020-07-02` and `2020-09-02` that pops up in a DPS location in `Austin` or `Pflugerville` within `15` miles of zip code `78741` using a permit ID # of `999999999`, and the following personal details:

```sh
$ bin/txdps scan_and_autohold \
  --cities Austin Pflugerville --max-dist 15 \
  --min-date 2020-07-02 --max-date 2020-09-02 \
  --zip-code 78741 --email-address jujube@juju.me --phone-number 111111111
  --first-name Juju --last-name Be --dob 1990-01-01 --last-4-ssn 1111 --card-number 999999999
```

If successful, you'll get an email and text that includes the confirmation number.

If you decide to cancel you can:

```sh
bin/txdps cancel --conf-num 555555
  --first-name Juju --last-name Be --dob 1990-01-01 \
  --last-4-ssn 1111 --card-number 999999999
```
