#!/usr/bin/env python3
"""
Set open hours and timezone on a GHL calendar.

Built for the NEW WINE DIGITAL "NewWine Chatbot Calendar", which shipped with
openHours = {} — meaning it offered ~23 hours a day, every day, from midnight.
An appointment-booking AI agent will happily book a 3am slot off that, so the
hours have to be bounded before any agent is connected to it.

Backs up the current calendar JSON to .tmp/ before writing. Idempotent: if the
calendar already matches the target config, it reports and exits without a write.

Usage:
    python execution/ghl_set_calendar_hours.py --dry-run
    python execution/ghl_set_calendar_hours.py
    python execution/ghl_set_calendar_hours.py --verify-only
"""

import argparse
import json
import os
import pathlib
import sys
import time
import urllib.error
import urllib.request

BASE = "https://services.leadconnectorhq.com"
API_VERSION = "2021-07-28"

# Cloudflare (error 1010) rejects urllib's default User-Agent on this host.
USER_AGENT = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")

# ---------------------------------------------------------------- target config
CALENDAR_ID = "D6PiIuMmDF9gie7kSAvy"      # NewWine Chatbot Calendar
TIMEZONE = "America/New_York"             # Eastern
OPEN_HOUR, CLOSE_HOUR = 8, 20             # 8am - 8pm
DAYS = [0, 1, 2, 3, 4, 5, 6]              # 0=Sun .. 6=Sat — all seven days

# GOTCHA: daysOfTheWeek accepts exactly ONE day per entry. Passing [0,1,2,3,4,5,6]
# in a single entry fails with "openHours.0.must be a valid day of week" — the error
# points at the entry, not the array, which reads like a value problem but isn't.
# Seven days = seven separate entries. Verified against the live API.
TARGET_OPEN_HOURS = [
    {
        "daysOfTheWeek": [day],
        "hours": [{
            "openHour": OPEN_HOUR, "openMinute": 0,
            "closeHour": CLOSE_HOUR, "closeMinute": 0,
        }],
    }
    for day in DAYS
]

ROOT = pathlib.Path(__file__).resolve().parent.parent


def load_env():
    env = {}
    path = ROOT / ".env"
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip()
    return env


def request(method, path, token, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(BASE + path, data=data, method=method, headers={
        "Authorization": f"Bearer {token}",
        "Version": API_VERSION,
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": USER_AGENT,
    })
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            raw = r.read().decode()
            return r.status, (json.loads(raw) if raw else {})
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()[:500]


def describe_slots(token, label):
    """Print the real bookable window so the change can be eyeballed."""
    now = int(time.time() * 1000)
    end = now + 7 * 86400 * 1000
    status, body = request(
        "GET", f"/calendars/{CALENDAR_ID}/free-slots?startDate={now}&endDate={end}", token)
    if status != 200:
        print(f"  [{status}] could not read slots: {body}")
        return
    days = sorted(k for k in body if k[:2] == "20")
    total = sum(len(body[d].get("slots", [])) for d in days)
    print(f"  {label}: {len(days)} day(s), {total} slot(s) over the next 7 days")
    for d in days[:4]:
        slots = body[d].get("slots", [])
        if slots:
            print(f"    {d}: {len(slots):>3} slots | {slots[0][11:16]} -> {slots[-1][11:16]} "
                  f"({slots[0][-6:]})")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="show the change, write nothing")
    ap.add_argument("--verify-only", action="store_true", help="just report current state")
    args = ap.parse_args()

    env = load_env()
    token = env.get("GHL_NEWWINE_API_KEY") or os.environ.get("GHL_NEWWINE_API_KEY")
    if not token:
        sys.exit("GHL_NEWWINE_API_KEY must be set in .env")

    status, body = request("GET", f"/calendars/{CALENDAR_ID}", token)
    if status != 200:
        sys.exit(f"[{status}] could not read calendar: {body}")
    cal = body.get("calendar", body)

    print(f"Calendar : {cal.get('name')} ({CALENDAR_ID})")
    print(f"Type     : {cal.get('calendarType')} | slot {cal.get('slotDuration')}"
          f"{cal.get('slotDurationUnit')} | autoConfirm={cal.get('autoConfirm')}")
    print(f"Current  : openHours={json.dumps(cal.get('openHours'))[:120]}")
    describe_slots(token, "BEFORE")

    if args.verify_only:
        return

    if cal.get("openHours") == TARGET_OPEN_HOURS:
        print("\nAlready matches target config. Nothing to do.")
        return

    backup_dir = ROOT / ".tmp"
    backup_dir.mkdir(exist_ok=True)
    backup = backup_dir / f"calendar_{CALENDAR_ID}_before.json"
    backup.write_text(json.dumps(cal, indent=2), encoding="utf-8")
    print(f"\nBackup   : {backup}")

    # GOTCHA: calendars have NO timezone field on this API — sending one returns
    # "property timezone should not exist". Open hours are interpreted in the
    # LOCATION timezone. While the location is Asia/Shanghai, 8am-8pm here means
    # 8pm-8am Eastern. The location timezone must be fixed before this is correct.
    payload = {"openHours": TARGET_OPEN_HOURS}
    print(f"Target   : {OPEN_HOUR:02d}:00-{CLOSE_HOUR:02d}:00 all 7 days, tz {TIMEZONE}")
    print(f"Payload  : {json.dumps(payload)}")

    if args.dry_run:
        print("\n[dry-run] no write performed.")
        return

    status, resp = request("PUT", f"/calendars/{CALENDAR_ID}", token, payload)
    if status not in (200, 201):
        sys.exit(f"\n[{status}] update failed: {resp}")

    print(f"\n[{status}] calendar updated.")
    describe_slots(token, "AFTER")


if __name__ == "__main__":
    main()
