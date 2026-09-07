# CoinEasy GIPHY statistics

Collects the public GIF Views display from https://giphy.com/coineasy without AI, browser sessions, or GIPHY credentials. Only public aggregate statistics and collector code are published here.

`stats.json` is consumed by the CoinEasy Wix site's scheduled backend job. Counts such as `7.4M` are GIPHY's rounded public display, not exact analytics totals. `checkedAt` records when that display was actually fetched.

The collector retains the last verified JSON and fails the workflow on HTTP errors, malformed pages, ambiguous counts, or a decrease requiring review. Wix must retain its last verified value when this feed is unavailable or stale.

Run `python3 -m unittest discover -s tests -v`, then `python3 scripts/collect.py`. No dependencies or AI API calls are needed. Collection success is verified separately from the Wix import and public page display.

GitHub Actions fetches at 00:17, 06:17, 12:17 and 18:17 UTC. Wix imports at minute 47 of every hour to tolerate delayed source jobs. The homepage reads the CMS when loaded and once per minute while open. This is periodic synchronization, not a real-time GIPHY stream. Schedules can be delayed by either provider.

The feed contains the successful observation timestamp on every run, even when the rounded count is unchanged. Failure does not advance this timestamp. Wix rejects data older than 48 hours and preserves its prior value. GitHub records failures in Actions; no separate AI monitor or paid service is used.

`wix/` contains the deployed import function and job configuration. Run `node tests/test_wix.mjs` to test validation and failure behavior. To stop collection, disable the **Collect public GIPHY views** workflow; to stop imports, remove its job from Wix `jobs.config` and publish. The homepage will continue displaying the last stored count.
