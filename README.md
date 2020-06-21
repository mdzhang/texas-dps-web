# Texas DPS Web

Web front end to browse DPS appointment data.

Uses [Plotly Dash](https://plotly.com/dash/) and data fetchable using the [TX DPS CLI](https://github.com/mdzhang/texas-dps).

## Contributing

### Requirements

- Python 3.x
- An [Algolia account](https://www.algolia.com/)
- A [Mapbox account](https://www.mapbox.com/)

### Setup

Install Python packages:

```sh
pip install -r requirements.txt
```

Set Mapbox token, Algolia API key, and Algolia app ID as environment variables:

```sh
export MAPBOX_TOKEN=xxx
export ALGOLIA_API_KEY=xxx
export ALGOLIA_APP_ID=xxx
```

### Run

```sh
python app.py
```

Then open <localhost:8050>
