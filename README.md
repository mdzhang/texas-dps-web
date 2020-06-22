# Texas DPS Web

Web front end to browse DPS appointment data.

Uses [Plotly Dash][dash], data fetchable using the [TX DPS CLI](https://github.com/mdzhang/texas-dps), and [Algolia][algolia] for improved search.

## Contributing

### Requirements

- Python 3.x
- An [Algolia account][algolia]
- A [Mapbox account][mapbox]
- An [AWS account][aws]

### Optional

- [AWS CLI](https://aws.amazon.com/cli/)
- [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli)
- [Sentry CLI](https://github.com/getsentry/sentry-cli)
- [CircleCi CLI](https://circleci.com/docs/2.0/local-cli/)

### Setup

Install Python packages:

```sh
pip install -r requirements.txt
```

Set Mapbox, Algolia, Sentry, and AWS environment variables:

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
python search.py
```

#### First time Heroku setup

- Setup a [Heroku account](https://signup.heroku.com/)

```sh
# install CLI toolset
HOMEBREW_NO_AUTO_UPDATE=1 brew tap heroku/brew
HOMEBREW_NO_AUTO_UPDATE=1 brew install heroku
# login to account
heroku login
# create Heroku app
heroku create
# set config vars
heroku config:set \
  MAPBOX_TOKEN=$MAPBOX_TOKEN ALGOLIA_API_KEY=$ALGOLIA_API_KEY ALGOLIA_APP_ID=$ALGOLIA_APP_ID \
  S3_LOCATION=$S3_LOCATION AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID \
  SENTRY_AUTH_TOKEN=$SENTRY_AUTH_TOKEN SENTRY_DSN=$SENTRY_DSN SENTRY_ORG=$SENTRY_ORG SENTRY_PROJECT=$SENTRY_PROJECT
```

### Run

```sh
python app.py
```

Then open <localhost:8050|localhost:8050>

[algolia]: https://www.algolia.com/
[mapbox]: https://www.mapbox.com/
[dash]: https://plotly.com/dash/
[aws]: https://aws.amazon.com/resources/create-account/
