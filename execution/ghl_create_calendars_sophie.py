#!/usr/bin/env python3
"""
Sophie Orozco - create the 9 Calendly-replacement calendars in GHL.

Source: Chris Orozco's email, 2026-07-23.

IMPORTANT - availability is a placeholder.
Chris supplied names, durations, buffers and descriptions, but NOT the working
hours for Kelsey, Koral or Luann. Every calendar below is created with a
placeholder Mon-Fri 09:00-17:00 America/New_York AND with isActive=False, so
nothing is bookable until a human sets the real hours and activates it.
Do not activate these until the real availability is confirmed.

Idempotent: skips any calendar whose name already exists.

Usage:
    python execution/ghl_create_calendars_sophie.py --dry-run
    python execution/ghl_create_calendars_sophie.py
"""

import argparse
import json
import os
import sys
import urllib.error
import urllib.request

BASE = "https://services.leadconnectorhq.com"
API_VERSION = "2021-07-28"

KELSEY = "WNaqGq1TS25bugRDfHMK"
KORAL = "4th6TLoTL60anzmElcOl"
LUANN = "zk8QWcB4Xm295Ld2O9gL"

RESET_DESCRIPTION = (
    "This is a private confidential clarity call designed to help you pause the "
    "chaos, get grounded, and understand what is actually happening in your "
    "relationship. It is not couples therapy and it is not a surface level "
    "conversation. It is a focused space to slow things down, identify what is "
    "driving the disconnect, and clarify what needs to shift for real change to "
    "become possible.\n\n"
    "You do not need your partner to attend or be on board. What matters is your "
    "willingness to show up honestly and look at your role. If our work is the "
    "right fit we will outline what support could look like. If not you will still "
    "leave with clarity. For most people showing up to this call is the first "
    "meaningful step toward stabilizing their relationship and changing the "
    "direction it is heading."
)

# Placeholder only. Replace before activating.
PLACEHOLDER_HOURS = [
    {
        "daysOfTheWeek": [d],
        "hours": [{"openHour": 9, "openMinute": 0, "closeHour": 17, "closeMinute": 0}],
    }
    for d in (1, 2, 3, 4, 5)
]

# (name, slug, minutes, buffer_minutes, [user_ids], description, is_round_robin)
CALENDARS = [
    ("Relationship Reset Call with Kelsey", "reset-kelsey", 60, 15,
     [KELSEY], RESET_DESCRIPTION, False),
    ("Follow Up with Kelsey", "followup-kelsey", 30, 0,
     [KELSEY], "", False),

    ("Relationship Reset Call with Koral", "reset-koral", 60, 15,
     [KORAL], RESET_DESCRIPTION, False),
    ("Follow Up with Koral", "followup-koral", 30, 0,
     [KORAL], "", False),

    ("Relationship Reset Call with Luann", "reset-luann", 60, 15,
     [LUANN], RESET_DESCRIPTION, False),
    ("Follow Up with Luann", "followup-luann", 30, 0,
     [LUANN], "", False),
    ("Client Onboarding Call", "client-onboarding", 30, 0,
     [LUANN], "", False),

    # Chris listed both round robins with the identical name "Relationship Reset
    # Call (roundrobin)". Suffixed here so the bio and affiliate links stay
    # distinguishable for attribution. Pending his confirmation.
    ("Relationship Reset Call - Bio", "reset-bio", 60, 15,
     [KELSEY, KORAL, LUANN], RESET_DESCRIPTION, True),
    ("Relationship Reset Call - Affiliate", "reset-affiliate", 60, 15,
     [KELSEY, KORAL, LUANN], RESET_DESCRIPTION, True),
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
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    env = load_env(os.path.join(root, ".env"))
    token, loc = env.get("GHL_API_KEY"), env.get("GHL_LOCATION_ID")
    if not token or not loc:
        sys.exit("GHL_API_KEY and GHL_LOCATION_ID must be set in .env")

    status, data = call("GET", f"/calendars/?locationId={loc}", token)
    if status != 200:
        sys.exit(f"Cannot list calendars ({status})")
    existing = {c.get("name", "").lower() for c in data.get("calendars", [])}

    print(f"Existing calendars: {len(existing)}")
    if args.dry_run:
        print("MODE: dry run, nothing will be written")
    print()

    created = skipped = failed = 0
    for name, slug, mins, buf, members, desc, rr in CALENDARS:
        if name.lower() in existing:
            print(f"  SKIP    {name}")
            skipped += 1
            continue
        if args.dry_run:
            kind = "round robin" if rr else "individual"
            print(f"  WOULD   {name}  [{kind}, {mins}min, {buf}min buffer,"
                  f" {len(members)} host(s)]")
            continue

        payload = {
            "locationId": loc,
            "name": name,
            "description": desc,
            "slug": slug,
            "widgetType": "classic",
            "calendarType": "round_robin" if rr else "event",
            "slotDuration": mins,
            "slotDurationUnit": "mins",
            "slotInterval": mins,
            "slotIntervalUnit": "mins",
            "slotBuffer": buf,
            "slotBufferUnit": "mins",
            "autoConfirm": True,
            "allowReschedule": True,
            "allowCancellation": True,
            "isActive": False,  # nothing bookable until real hours are set
            "openHours": PLACEHOLDER_HOURS,
            "teamMembers": [
                {"userId": u, "priority": 1.0} for u in members
            ],
        }
        if rr:
            payload["eventType"] = "RoundRobin_OptimizeForAvailability"

        st, resp = call("POST", "/calendars/", token, payload)
        if st in (200, 201):
            cid = (resp.get("calendar") or {}).get("id", "?")
            print(f"  CREATED {name}   id={cid}")
            created += 1
        else:
            msg = resp.get("message") or json.dumps(resp)[:200]
            print(f"  FAILED  {name} ({st}) {msg}")
            failed += 1

    print(f"\ncreated={created} skipped={skipped} failed={failed}")
    if created:
        print("\nAll created INACTIVE with placeholder Mon-Fri 09:00-17:00 ET.")
        print("Set real availability per host, then activate.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
