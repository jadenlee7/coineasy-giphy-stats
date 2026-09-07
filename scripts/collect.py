"""AI 없이 CoinEasy 공개 GIPHY 조회수를 확인해 정적 JSON으로 저장한다."""
import json
import re
import sys
import urllib.request
from datetime import datetime, timezone
from decimal import Decimal
from html.parser import HTMLParser
from pathlib import Path

SOURCE = "https://giphy.com/coineasy"
OUTPUT = Path(__file__).resolve().parents[1] / "stats.json"


class VisibleText(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.hidden = 0
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style", "template"}:
            self.hidden += 1

    def handle_endtag(self, tag):
        if tag in {"script", "style", "template"}:
            self.hidden = max(0, self.hidden - 1)

    def handle_data(self, data):
        if not self.hidden:
            self.parts.append(data)


def parse_display(html):
    parser = VisibleText()
    parser.feed(html)
    text = " ".join(parser.parts)
    if not re.search(r"\bCoinEasy\b", text, re.I):
        raise ValueError("Expected CoinEasy channel identity")
    matches = re.findall(r"(?<![\w.,])([0-9][0-9,]*(?:\.[0-9]+)?\s*[KMB]?)\s+GIF\s+Views\b", text, re.I)
    values = {re.sub(r"\s+", "", value).upper() for value in matches}
    if len(values) != 1:
        raise ValueError("Expected one unambiguous GIF Views count")
    return values.pop()


def approximate_views(display):
    match = re.fullmatch(r"([0-9][0-9,]*(?:\.[0-9]+)?)([KMB]?)", display)
    if not match:
        raise ValueError("Invalid view count")
    multiplier = {"": 1, "K": 1000, "M": 1000000, "B": 1000000000}[match[2]]
    value = Decimal(match[1].replace(",", "")) * multiplier
    if value <= 0 or value != value.to_integral_value():
        raise ValueError("Invalid numeric view count")
    return int(value)


def collect():
    # 로그인, 브라우저 세션, AI API를 사용하지 않는 공개 페이지 요청이다.
    with urllib.request.urlopen(SOURCE, timeout=25) as response:
        if response.status != 200 or response.url.rstrip("/") != SOURCE:
            raise ValueError("Unexpected response or redirect")
        if "text/html" not in response.headers.get("Content-Type", ""):
            raise ValueError("Unexpected content type")
        data = response.read(2_000_001)
    if len(data) > 2_000_000:
        raise ValueError("Response exceeds limit")
    display = parse_display(data.decode("utf-8"))
    views = approximate_views(display)
    if OUTPUT.exists():
        previous = json.loads(OUTPUT.read_text())
        if views < previous["approximateViews"]:
            raise ValueError("Count decreased; retaining last verified value for review")
    payload = {
        "schemaVersion": 1,
        "channel": "coineasy",
        "source": SOURCE,
        "display": display,
        "approximateViews": views,
        "precision": "giphy-public-rounded-display",
        "checkedAt": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    temp = OUTPUT.with_suffix(".tmp")
    temp.write_text(json.dumps(payload, indent=2) + "\n")
    temp.replace(OUTPUT)
    print(json.dumps(payload))


if __name__ == "__main__":
    try:
        collect()
    except Exception as exc:
        print(f"Collection failed; previous stats preserved: {exc}", file=sys.stderr)
        sys.exit(1)
