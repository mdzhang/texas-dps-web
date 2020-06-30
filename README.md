# Texas DPS Web

Web front end to browse DPS appointment data.

Uses [Plotly Dash][dash] and [Algolia][algolia] for improved search. Provides [CLI](./docs/cli.md) for fetching source data.

## Contributing

### Requirements

- Python 3.x
- An [Algolia account][algolia]
- A [Mapbox account][mapbox]
- An [AWS account][aws]
- A [Sentry project](https://docs.sentry.io)

### Optional

- [httpie](https://httpie.org) and [jq](https://stedolan.github.io/jq/) for [Makefile](./Makefile) commands
- [AWS CLI](https://aws.amazon.com/cli/)
- [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli)
- [Sentry CLI](https://github.com/getsentry/sentry-cli)
- [CircleCI CLI](https://circleci.com/docs/2.0/local-cli/)

### Setup

Install Python packages:

```sh
pip install -r requirements.txt
```

Set environment variables:

```sh
export MAPBOX_TOKEN=xxx
export ALGOLIA_API_KEY=xxx
export ALGOLIA_APP_ID=xxx
export S3_LOCATION=s3://bucket/path
export SENTRY_DSN=
export SENTRY_ORG=
export SENTRY_PROJECT=
export SENTRY_AUTH_TOKEN=
```

#### First time search index setup

```sh
python txdps/search.py
```

### Run

```sh
FLASK_APP=txdps/app flask run
```

Then open localhost:5000

### Style

```sh
pre-commit run -a
```

You break it, you fix it :)

[algolia]: https://www.algolia.com/
[mapbox]: https://www.mapbox.com/
[dash]: https://plotly.com/dash/
[aws]: https://aws.amazon.com/resources/create-account/
