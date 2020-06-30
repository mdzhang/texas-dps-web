# Deployment

## Setup

## Heroku

- Setup a [Heroku account](https://signup.heroku.com/)

```sh
# install CLI toolset
HOMEBREW_NO_AUTO_UPDATE=1 brew tap heroku/brew
HOMEBREW_NO_AUTO_UPDATE=1 brew install heroku
# login to account
heroku login
# create Heroku app
heroku create
# add the scheduler addon to the app
heroku addons:create scheduler:standard

# set config vars
heroku config:set \
  MAPBOX_TOKEN=$MAPBOX_TOKEN ALGOLIA_API_KEY=$ALGOLIA_API_KEY ALGOLIA_APP_ID=$ALGOLIA_APP_ID \
  S3_LOCATION=$S3_LOCATION AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID \
  SENTRY_AUTH_TOKEN=$SENTRY_AUTH_TOKEN SENTRY_DSN=$SENTRY_DSN \
  TWILIO_ACCOUNT_SID=$TWILIO_ACCOUNT_SID TWILIO_AUTH_TOKEN=$TWILIO_AUTH_TOKEN TWILIO_PHONE_NUMBER=$TWILIO_PHONE_NUMBER \
  SENDGRID_API_KEY=$SENDGRID_API_KEY
```

For the scheduled job, pick your interval and add a command like:

```sh
$ ./bin/txdps notify \
  --cities Austin Pflugerville --max-dist 15 \
  --min-date 2020-07-02 --max-date 2020-09-02 \
  --zip-code 78741 --email-address jujube@juju.me --phone-number 111111111
```

### Local

- set `HEROKU_APP` locally
- add Heroku remote:

```sh
heroku git:remote -a $HEROKU_APP
```

### Manual trigger

```sh
git checkout master
git push heroku master
```

## Sentry

Create an account and project. Note your org name and project slug. Note that `SENTRY_PROJECT` is the project _slug_, not the ID. So is `SENTRY_ORG`. You can create an auth token [here](https://sentry.io/settings/account/api/auth-tokens/). Finally, setup a GitHub integration at `https://sentry.io/settings/$SENTRY_ORG/integrations/github` to unbreak Circle Sentry releases

## CircleCI

See [`.circleci/config.yml`](./.circleci/config.yml).

You'll need to setup a new project and integrate it with a GitHub repo.

To let CircleCI trigger Heroku deploys, set the `HEROKU_APP_NAME` and `HEROKU_API_KEY` environment variables. You can generate an API key with `heroku authorizations:create`

To let CircleCI report Sentry releases, set the `SENTRY_ORG`, `SENTRY_PROJECT`, and `SENTRY_AUTH_TOKEN` environment variables.
