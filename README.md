# Texas DPS Web

Web front end to browse DPS appointment data.

Uses [Plotly Dash][dash], data fetchable using the [TX DPS CLI](https://github.com/mdzhang/texas-dps), and [Algolia][algolia] for improved search.

## Contributing

### Requirements

- Python 3.x
- An [Algolia account][algolia]
- A [Mapbox account][mapbox]

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

[algolia]: https://www.algolia.com/
[mapbox]: https://www.mapbox.com/
[dash]: https://plotly.com/dash/
