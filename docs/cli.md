# Texas DPS CLI

CLI tool to find, reserve, and release appointments with the Texas DPS.

## Requirements

In addition to those in the main [README](../README.md):

- A [Twilio account](https://www.twilio.com/docs/usage/tutorials/how-to-use-your-free-trial-account) if you want to notify with SMS
- A [Sendgrid account](https://sendgrid.com/pricing/) if you want to notify with Sendgrid

## Usage

To grab all locations with their next available date and distance from zip code `78741` and write them to `locations.csv`, but only print the top `10` locations within `50` miles:

```
$ python txdps.py pull --cache-file locations.csv --zip-code 78741 -n 10 --max-dist 50
```

Once you figure out the cities you want to limit on, to text `1111111111` and email `jujube@juju.me` on any slot for Driver's License services between `2020-07-02` and `2020-09-02` that pops up in a DPS location in `Austin` or `Pflugerville` within `15` miles of zip code `78741`:

```
$ python txdps.py notify \
  --cities Austin Pflugerville --max-dist 15 \
  --min-date 2020-07-02 --max-date 2020-09-02 \
  --zip-code 78741 --email-address jujube@juju.me --phone-number 111111111
```

You'll get a message like:

```
Slots have opened up at the following DPS locations matching your criteria:

Pflugerville Mega Center  (ID: 660) @ 2020-09-04T10:00:00  (60 min), Slot ID: 270438
Austin North              (ID: 604) @ 2020-09-09T12:30:00  (45 min), Slot ID: 365776
Austin South              (ID: 605) @ 2020-09-22T11:45:00  (60 min), Slot ID: 468189
```

Pick a slot. Note that for `Austin South              (ID: 605) @ 2020-09-22T11:45:00  (60 min), Slot ID: 468189`, `605` is the site id, `60` is the appointment duration, `468189` is the slot id, and `2020-09-22T11:45:00` is the appointment time. Use these, and add your personal details, to reserve the appointment. See `python txdps.py hold --help` for more on how to do this.

When you hold a slot, you'll see an output like:

```
INFO:root:See your appointment at: https://public.txdpsscheduler.com?b=555555555
INFO:root:Appointment booking id is 555555; use this to cancel.
```

If you decide to cancel you can:

```sh
python txdps.py cancel --booking-id 555555
```
