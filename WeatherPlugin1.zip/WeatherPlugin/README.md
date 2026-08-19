# WeatherPlugin

Query Taiwan CWA (Central Weather Administration) 36-hour weather forecast
by sending a keyword message, e.g. `天气 臺北市`.

## Setup

1. Register at https://opendata.cwa.gov.tw and apply for a free
   Authorization API Key.
2. Open `components/event_listener/default.py` and set `CWA_API_KEY` to
   your key.
3. Location names must match the official Traditional Chinese names used
   by CWA (e.g. 臺北市, 高雄市, 臺中市).

## Known uncertainty

The dataset ID `F-C0032-001` and its field names (`Wx`, `MinT`, `MaxT`,
`PoP`) are based on general knowledge of the CWA open data API and were
not verified live. If the reply shows a parsing error, check the current
CWA API documentation for the dataset's actual field names and adjust
`components/event_listener/default.py` accordingly.
