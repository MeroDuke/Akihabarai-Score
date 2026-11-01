"""GitHub-only download snapshots and reports; no desktop dependencies."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone, date
from html import escape
import json
import os
from pathlib import Path
from urllib.request import Request, urlopen


ASSETS = {
    "AkihabaraiScore-windows.zip": "Windows",
    "AkihabaraiScore-linux-x86_64.tar.gz": "Linux",
}
REPOSITORY = "MeroDuke/Akihabarai-Score"


def github_pages(path, token, request=urlopen):
    """Numbered pagination stays on the known API host, including asset lists."""
    result = []
    for page in range(1, 10001):
        headers = {"Accept": "application/vnd.github+json", "User-Agent": "AS-download-metrics"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        req = Request(f"https://api.github.com/{path}?per_page=100&page={page}", headers=headers)
        with request(req, timeout=30) as response:
            batch = json.load(response)
        if not isinstance(batch, list):
            raise ValueError("GitHub response is not a list")
        result.extend(batch)
        if len(batch) < 100:
            return result
    raise ValueError("GitHub pagination limit exceeded")


def fetch_releases(token, request=urlopen):
    releases = github_pages(f"repos/{REPOSITORY}/releases", token, request)
    for release in releases:
        if not release["draft"] and not release["prerelease"]:
            release["assets"] = github_pages(
                f"repos/{REPOSITORY}/releases/{int(release['id'])}/assets", token, request
            )
    return releases


def snapshot(releases, timestamp):
    observed = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    if observed.utcoffset() is None:
        raise ValueError("Snapshot time must include a timezone")
    assets = []
    seen = set()
    for release in releases:
        if release["draft"] or release["prerelease"]:
            continue
        for asset in release["assets"]:
            platform = ASSETS.get(asset["name"])
            if platform is None:
                continue
            count = asset["download_count"]
            if type(count) is not int or count < 0:
                raise ValueError("Invalid download count")
            key = (int(release["id"]), int(asset["id"]))
            if key in seen:
                raise ValueError("Duplicate release asset")
            seen.add(key)
            assets.append({"release_id": key[0], "asset_id": key[1],
                           "tag": release["tag_name"], "name": asset["name"],
                           "platform": platform, "downloads": count})
    return {"observed_at": observed.astimezone(timezone.utc).isoformat(),
            "assets": sorted(assets, key=lambda a: (a["release_id"], a["asset_id"]))}


def anomalies(previous, current):
    def indexed(sample):
        return {(a["release_id"], a["asset_id"]): a for a in sample["assets"]}
    old, new = indexed(previous), indexed(current)
    events = []
    for key in sorted(old.keys() - new.keys()):
        events.append(f"Removed asset: {old[key]['tag']} / {old[key]['name']} / id {key[1]}")
    for key in sorted(new.keys() - old.keys()):
        events.append(f"New asset: {new[key]['tag']} / {new[key]['name']} / id {key[1]}")
    for key in sorted(old.keys() & new.keys()):
        if new[key]["downloads"] < old[key]["downloads"]:
            events.append(f"Counter decreased: asset {key[1]} ({old[key]['downloads']} -> {new[key]['downloads']})")
    return events


def chart(history):
    days = sorted(history)
    first = date.fromisoformat(days[0])
    span = max(1, (date.fromisoformat(days[-1]) - first).days)
    series = {}
    for day in days:
        for a in history[day]["assets"]:
            key = (a["tag"], a["platform"])
            series.setdefault(key, {})[day] = series.get(key, {}).get(day, 0) + a["downloads"]
    maximum = max([1] + [v for values in series.values() for v in values.values()])
    colors = ["#0072b2", "#d55e00", "#009e73", "#cc79a7", "#967000", "#6d64d8"]
    height = 400 + 23 * len(series)
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="960" height="{height}" viewBox="0 0 960 {height}" role="img">',
             '<title>AS application downloads by release and platform</title>',
             '<desc>Observed cumulative counts, not unique users. Missing days and asset changes break lines.</desc>',
             '<style>text{font:14px sans-serif;fill:#222}.bg{fill:#fff}@media(prefers-color-scheme:dark){text{fill:#eee}.bg{fill:#161b22}}</style>',
             f'<rect class="bg" width="960" height="{height}"/>',
             '<text x="60" y="28">Application downloads · observed cumulative counts</text>',
             f'<text x="60" y="52">UTC: {escape(history[days[-1]]["observed_at"])}</text>']
    for i in range(5):
        y = 330 - i * 60
        parts.extend([f'<path d="M60 {y}H900" stroke="#888" stroke-opacity=".3"/>',
                      f'<text x="8" y="{y+5}">{maximum*i/4:g}</text>'])
    def point(day, value):
        return 60 + (date.fromisoformat(day) - first).days / span * 840, 330 - value / maximum * 240
    for index, (key, values) in enumerate(sorted(series.items())):
        color = colors[index % len(colors)]
        previous_day = None
        for day, value in sorted(values.items()):
            x, y = point(day, value)
            # Do not imply observation across missing days or replaced/deleted assets.
            if previous_day and (date.fromisoformat(day) - date.fromisoformat(previous_day)).days == 1:
                old_ids = {a["asset_id"] for a in history[previous_day]["assets"] if (a["tag"], a["platform"]) == key}
                new_ids = {a["asset_id"] for a in history[day]["assets"] if (a["tag"], a["platform"]) == key}
                if old_ids == new_ids and value >= values[previous_day]:
                    px, py = point(previous_day, values[previous_day])
                    parts.append(f'<path d="M{px:g} {py:g}L{x:g} {y:g}" fill="none" stroke="{color}" stroke-width="2"/>')
            parts.append(f'<circle cx="{x:g}" cy="{y:g}" r="4" fill="{color}"><title>{escape(str(key))}: {day}: {value}</title></circle>')
            previous_day = day
        parts.append(f'<text x="60" y="{407+index*23}" style="fill:{color}">{escape(key[0])} / {key[1]} ({values[max(values)]})</text>')
    parts.extend([f'<text x="60" y="355">{days[0]}</text>',
                  f'<text x="800" y="355">{days[-1]}</text>',
                  '<text x="60" y="380">No interpolation across gaps; own and automated downloads may be included.</text>', '</svg>'])
    return "\n".join(parts)


def write_reports(output, history):
    days = sorted(history)
    latest = history[days[-1]]
    totals = {platform: sum(a["downloads"] for a in latest["assets"] if a["platform"] == platform)
              for platform in ("Windows", "Linux")}
    events = []
    for before, after in zip(days, days[1:]):
        gap = (date.fromisoformat(after) - date.fromisoformat(before)).days
        if gap > 1:
            events.append(f"{after}: {gap-1} missing day(s) since {before}")
        events.extend(f"{after}: {event}" for event in anomalies(history[before], history[after]))
    output.mkdir(parents=True, exist_ok=True)
    def dump(name, value):
        (output / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    dump("history.json", {"schema_version": 1, "repository": REPOSITORY, "days": history})
    dump("events.json", events)
    for platform, total in totals.items():
        dump(f"{platform.lower()}.json", {"schemaVersion": 1,
             "label": f"{platform} downloads · {days[-1]} UTC", "message": str(total), "color": "blue"})
    (output / "downloads.svg").write_text(chart(history), encoding="utf-8")
    lines = ["# AS release downloads", "", f"Last successful observation (UTC): **{latest['observed_at']}**", "",
             "![Downloads](downloads.svg)", "", "## Current published stable application assets", "",
             "| Release | Platform | Downloads | Asset ID |", "| --- | --- | ---: | ---: |"]
    for a in latest["assets"]:
        tag = a["tag"].replace("|", "\\|").replace("\n", " ")
        lines.append(f"| {tag} | {a['platform']} | {a['downloads']} | {a['asset_id']} |")
    lines += ["", "Counts include own/repeated/automated downloads, not unique people or active users.",
              "Only the two named application archives count; dependency sources, drafts and prereleases do not.",
              "Totals cover currently present stable assets, not all historically deleted files.",
              "The first successful sample per UTC day is retained. Missing days are not reconstructed.",
              "On API failure the last successful dated report remains unchanged; check its date.", "", "## Gaps and asset/counter changes", ""]
    lines += [f"- {event}" for event in events] or ["No changes observed between retained samples."]
    (output / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def run(output, timestamp, collect):
    path = output / "history.json"
    history = {}
    if path.exists():
        document = json.loads(path.read_text(encoding="utf-8"))
        if document["schema_version"] != 1 or document["repository"] != REPOSITORY:
            raise ValueError("Unexpected history schema/repository")
        history = document["days"]
    # Validate time before any network or writes, including repeat invocations.
    observed = snapshot([], timestamp)["observed_at"]
    day = observed[:10]
    if history and day < max(history):
        raise ValueError("Refusing an out-of-order observation")
    if day not in history:
        sample = snapshot(collect(), timestamp)  # Any fetch/validation failure leaves history untouched.
        history = {**history, day: sample}
    write_reports(output, history)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--fixture", type=Path, help="Offline complete release list for tests/preview")
    parser.add_argument("--at", default=None, help="Observation ISO timestamp; normally current UTC")
    args = parser.parse_args()
    timestamp = args.at or datetime.now(timezone.utc).isoformat()
    def collect():
        if args.fixture:
            return json.loads(args.fixture.read_text(encoding="utf-8"))
        return fetch_releases(os.environ.get("GH_TOKEN", ""))
    run(args.output, timestamp, collect)


if __name__ == "__main__":
    main()
