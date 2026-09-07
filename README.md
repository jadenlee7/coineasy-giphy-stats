# CoinEasy GIPHY statistics

Collects the public GIF Views display from https://giphy.com/coineasy without AI, browser sessions, or GIPHY credentials. Only public aggregate statistics and collector code are published here.

`stats.json` is consumed by the CoinEasy Wix site's scheduled backend job. Counts such as `7.4M` are GIPHY's rounded public display, not exact analytics totals. `checkedAt` records when that display was actually fetched.

The collector retains the last verified JSON and fails the workflow on HTTP errors, malformed pages, ambiguous counts, or a decrease requiring review. Wix must retain its last verified value when this feed is unavailable or stale.

Run `python3 -m unittest discover -s tests -v`, then `python3 scripts/collect.py`. No dependencies or AI API calls are needed. Collection success is verified separately from the Wix import and public page display.
