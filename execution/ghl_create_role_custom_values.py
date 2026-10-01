#!/usr/bin/env python3
"""
Create the role-email custom values in a GHL sub-account.

Source: Google Sheet "Roles" tab (Dmytro, 2026-07-30):
    Setter setter@agencydomain.com / SDR sdr@... / PM pm@... / QA qa@... / CSM csm@...

Why custom values instead of user records
-----------------------------------------
Dmytro's plan is to save the 5 role users in the snapshot and change their emails
per client on install. GHL snapshots do NOT include users - users are per-location
and are not a snapshot asset - so internal notifications pointed at a user record
break the moment the snapshot is installed.

Custom values ARE a snapshot asset. Pointing every Send Internal Notification at
{{custom_values.sdr_email}} keeps Dmytro's exact concept ("just change the emails")
while surviving the snapshot. On install you change 5 values in one screen.

DEMO_BOOKING_LINK is seeded with a loud placeholder on purpose. Several task #2
workflows (WF-03, WF-05, WF-07, WF-11) use {{user.calendar_link}}, which renders
EMPTY unless a user is assigned to the contact - and nothing in the spec ever
assigns one. This custom value is the fix. A visible placeholder is safer than a
blank: if it ever reaches a customer email, it is obvious rather than silent.

Idempotent: skips any custom value whose name already exists. Re-running is safe.

Usage:
    python execution/ghl_create_role_custom_values.py --prefix EAI --dry-run
    python execution/ghl_create_role_custom_values.py --prefix EAI
"""

import argparse
import json
import os
import sys
import urllib.error
import urllib.request

BASE = "https://services.leadconnectorhq.com"
API_VERSION = "2021-07-28"

PLACEHOLDER_LINK = "REPLACE_WITH_DEMO_CALENDAR_LINK"

# (name, value)
CUSTOM_VALUES = [
    ("Setter Email", "setter@agencydomain.com"),
    ("SDR Email",    "sdr@agencydomain.com"),
    ("PM Email",     "pm@agencydomain.com"),
    ("QA Email",     "qa@agencydomain.com"),
    ("CSM Email",    "csm@agencydomain.com"),
    ("Demo Booking Link", PLACEHOLDER_LINK),
]


def load_env(path):
    env = {}
    if not os.path.exists(path):
        return env
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip()
    return env


def call(method, path, token, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(f"{BASE}{path}", data=data, method=method)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Version", API_VERSION)
    req.add_header("Accept", "application/json")
    req.add_header("User-Agent", "curl/8.0.1")
    if data:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            raw = resp.read().decode()
            return resp.status, (json.loads(raw) if raw else {})
    except urllib.error.HTTPError as e:
        raw = e.read().decode()
        try:
            return e.code, json.loads(raw)
        except json.JSONDecodeError:
            return e.code, {"raw": raw[:300]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prefix", default="EAI",
                    help="env var prefix, e.g. EAI for GHL_EAI_API_KEY")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    env = load_env(os.path.join(root, ".env"))
    p = f"{args.prefix.upper()}_" if args.prefix else ""
    token = env.get(f"GHL_{p}API_KEY")
    loc = env.get(f"GHL_{p}LOCATION_ID")
    if not token or not loc:
        sys.exit(f"GHL_{p}API_KEY and GHL_{p}LOCATION_ID must be set in .env")

    status, data = call("GET", f"/locations/{loc}/customValues", token)
    if status != 200:
        sys.exit(f"Cannot list custom values ({status}): {json.dumps(data)[:200]}")
    existing = {c.get("name", "").strip().lower(): c
                for c in data.get("customValues", [])}

    print(f"location {loc}")
    print(f"existing custom values: {len(existing)}")
    if args.dry_run:
        print("MODE: dry run, nothing will be written")
    print()

    created = skipped = failed = 0
    keys = []

    for name, value in CUSTOM_VALUES:
        hit = existing.get(name.lower())
        if hit:
            print(f"  SKIP     {name}  (exists, key={hit.get('fieldKey')})")
            keys.append((name, hit.get("fieldKey"), hit.get("value")))
            skipped += 1
            continue
        if args.dry_run:
            print(f"  WOULD    {name} = {value}")
            continue

        st, resp = call("POST", f"/locations/{loc}/customValues", token,
                        {"name": name, "value": value})
        if st in (200, 201):
            cv = resp.get("customValue") or resp
            print(f"  CREATED  {name} = {value}")
            print(f"           key = {cv.get('fieldKey')}")
            keys.append((name, cv.get("fieldKey"), value))
            created += 1
        else:
            msg = resp.get("message") or json.dumps(resp)[:200]
            print(f"  FAILED   {name} ({st}) {msg}")
            failed += 1

    print(f"\ncreated={created} skipped={skipped} failed={failed}")

    if keys:
        # GHL returns fieldKey already wrapped, e.g. "{{ custom_values.sdr_email }}".
        # Print it verbatim - do not add braces.
        print("\nMerge fields to use in Send Internal Notification recipients:")
        for name, key, value in keys:
            print(f"  {name:<20} {key}")
        if any(v == PLACEHOLDER_LINK for _, _, v in keys):
            print(f"\n  Demo Booking Link is still {PLACEHOLDER_LINK}.")
            print("  Set it to the real booking URL once the demo calendar exists.")

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
