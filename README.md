# Shazam API Test

A minimal script to check that your RapidAPI key works with the
[Shazam API by Api Dojo](https://rapidapi.com/apidojo/api/shazam) and to see
what the chart, search, and song-details endpoints return.

## Setup

1. Sign up at RapidAPI, open the Shazam API (Api Dojo), and subscribe to the
   free Basic plan on the **Pricing** tab.
2. Copy your key from the **Endpoints** tab (the `X-RapidAPI-Key` header).
3. In this folder:

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env               # Windows: copy .env.example .env
```

4. Open `.env` and paste your key in place of `your_key_here`.

## Run

```bash
python test_api.py                 # default search term
python test_api.py "bad bunny"     # your own search term
```

The script makes **4 requests** per run:

| Step | Endpoint | What it shows |
|---|---|---|
| 1 | `/charts/list` | All available charts and their IDs |
| 2 | `/charts/track` | Top 20 songs on the US chart |
| 3 | `/search` | Songs matching your search term |
| 4 | `/songs/v2/get-details` | Full details for the #1 chart song |

It also prints how many requests you have left on your plan, when the API
reports it.

## What to look at

Every full response is saved to `data/raw/` with a timestamp. Open them in
VS Code (or any JSON viewer) and note:

- How chart IDs are formatted and which countries are available
- Which fields each chart track includes (ID, title, artist, artwork, ...)
- What extra fields `get-details` adds, and whether it's worth the request

## Troubleshooting

- **401/403:** key is wrong, or you haven't subscribed to a plan.
- **429:** you've hit the rate limit or monthly quota.
- **404 or empty results:** endpoint paths or parameter names may have
  changed. Compare against the API's Endpoints tab and edit `test_api.py`.

`.env` and `data/raw/` are in `.gitignore`, so your key and raw data
won't be committed.
