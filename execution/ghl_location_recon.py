#!/usr/bin/env python3
"""
Read-only recon of a GHL sub-account: users, calendars, pipelines + stages, workflows.

Run this before any build so stage names, user IDs and existing assets are known
facts rather than assumptions. Writes nothing.

Credentials come from .env via a prefix, so the same script serves every
sub-account:
    GHL_<PREFIX>_API_KEY / GHL_<PREFIX>_LOCATION_ID
and with no prefix, GHL_API_KEY / GHL_LOCATION_ID.

Usage:
    python execution/ghl_location_recon.py --prefix EAI
    python execution/ghl_location_recon.py --prefix EAI --json .tmp/eai_recon.json
"""

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

BASE = "https://services.leadconnectorhq.com"
API_VERSION = "2021-07-28"


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


def call(path, token):
    req = urllib.request.Request(f"{BASE}{path}", method="GET")
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Version", API_VERSION)
    req.add_header("Accept", "application/json")
    req.add_header("User-Agent", "curl/8.0.1")
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
    except urllib.error.URLError as e:
        return 0, {"error": str(e)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prefix", default="",
                    help="env var prefix, e.g. EAI for GHL_EAI_API_KEY")
    ap.add_argument("--json", help="also dump raw responses to this path")
    args = ap.parse_args()

    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    env = load_env(os.path.join(root, ".env"))
    p = f"{args.prefix.upper()}_" if args.prefix else ""
    token = env.get(f"GHL_{p}API_KEY")
    loc = env.get(f"GHL_{p}LOCATION_ID")
    if not token or not loc:
        sys.exit(f"GHL_{p}API_KEY and GHL_{p}LOCATION_ID must be set in .env")

    q = urllib.parse.urlencode({"locationId": loc})
    endpoints = [
        ("users", f"/users/?{q}"),
        ("calendars", f"/calendars/?{q}"),
        ("pipelines", f"/opportunities/pipelines?{q}"),
        ("workflows", f"/workflows/?{q}"),
        ("customFields", f"/locations/{loc}/customFields"),
    ]

    raw = {}
    print(f"location {loc}\n")

    for label, path in endpoints:
        status, data = call(path, token)
        raw[label] = {"status": status, "data": data}
        if status != 200:
            msg = data.get("message") or data.get("error") or json.dumps(data)[:160]
            print(f"## {label}: HTTP {status} - {msg}")
            print("   (likely a missing scope on the private integration token)\n")
            continue

        if label == "users":
            users = data.get("users", [])
            print(f"## users ({len(users)})")
            for u in users:
                name = f"{u.get('firstName','')} {u.get('lastName','')}".strip() \
                       or u.get("name", "?")
                print(f"   {u.get('id')}  {name}  <{u.get('email','')}>  "
                      f"role={(u.get('roles') or {}).get('role','?')}")

        elif label == "calendars":
            cals = data.get("calendars", [])
            print(f"## calendars ({len(cals)})")
            for c in cals:
                print(f"   {c.get('id')}  {c.get('name')}  "
                      f"active={c.get('isActive')}  type={c.get('calendarType')}")

        elif label == "pipelines":
            pipes = data.get("pipelines", [])
            print(f"## pipelines ({len(pipes)})")
            for pl in pipes:
                print(f"   {pl.get('id')}  {pl.get('name')}")
                for s in pl.get("stages", []):
                    print(f"      - {s.get('name')!r}   id={s.get('id')}")

        elif label == "workflows":
            wfs = data.get("workflows", [])
            print(f"## workflows ({len(wfs)})")
            for w in wfs:
                print(f"   {w.get('id')}  {w.get('name')}  status={w.get('status')}")

        elif label == "customFields":
            cfs = data.get("customFields", [])
            print(f"## custom fields ({len(cfs)})")
            for f in cfs:
                print(f"   [{f.get('model','?')}] {f.get('name')!r}  "
                      f"key={f.get('fieldKey')}  type={f.get('dataType')}")
        print()

    if args.json:
        os.makedirs(os.path.dirname(os.path.abspath(args.json)), exist_ok=True)
        with open(args.json, "w", encoding="utf-8") as fh:
            json.dump(raw, fh, indent=2)
        print(f"raw responses -> {args.json}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
