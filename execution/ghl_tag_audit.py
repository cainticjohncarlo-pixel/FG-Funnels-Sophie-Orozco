#!/usr/bin/env python3
"""
Sophie Orozco - tag usage audit.

Counts how many contacts carry each tag, so junk tags can be identified with
evidence rather than by eye. Feeds the "Clean Up Contact List" task.

Read-only. Deletes nothing.

Usage:
    python execution/ghl_tag_audit.py
    python execution/ghl_tag_audit.py --csv .tmp/tag-usage.csv
"""

import argparse
import collections
import csv
import json
import os
import sys
import time
import urllib.error
import urllib.request

BASE = "https://services.leadconnectorhq.com"
API_VERSION = "2021-07-28"

# Tags we created for the Existing Client build. Excluded from junk suggestions.
OURS_PREFIX = ("client - ",)
OURS_EXACT = {"existing client"}


def load_env(path):
    env = {}
    if os.path.exists(path):
        for line in open(path, encoding="utf-8"):
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip()
    return env


def request(method, url, token, body=None, retries=6):
    last = None
    for attempt in range(retries):
        data = json.dumps(body).encode() if body is not None else None
        req = urllib.request.Request(url, data=data, method=method)
        req.add_header("Authorization", f"Bearer {token}")
        req.add_header("Version", API_VERSION)
        req.add_header("Accept", "application/json")
        req.add_header("User-Agent", "curl/8.0.1")
        if data:
            req.add_header("Content-Type", "application/json")
        try:
            with urllib.request.urlopen(req, timeout=90) as resp:
                return json.loads(resp.read().decode() or "{}")
        except urllib.error.HTTPError as e:
            last = e
            if e.code in (429, 500, 502, 503, 504) and attempt < retries - 1:
                time.sleep(min(2 ** attempt, 30))
                continue
            raise
        except urllib.error.URLError as e:
            last = e
            if attempt < retries - 1:
                time.sleep(min(2 ** attempt, 30))
                continue
            raise
    if last:
        raise last
    return {}


def normalise(tag):
    """Collapse a tag to a comparison key so near-duplicates group together."""
    t = tag.lower().strip()
    for ch in "-_;:()/":
        t = t.replace(ch, " ")
    t = " ".join(t.split())
    # crude singular/variant folding for the obvious pairs in this account
    t = t.replace("womens", "women").replace("mens", "men")
    t = t.replace("female", "women").replace("male", "men")
    t = t.replace(" email", "").replace("attendance", "show")
    return t


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", help="write full tag usage table to CSV")
    args = ap.parse_args()

    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    env = load_env(os.path.join(root, ".env"))
    token, loc = env.get("GHL_API_KEY"), env.get("GHL_LOCATION_ID")
    if not token or not loc:
        sys.exit("GHL_API_KEY and GHL_LOCATION_ID must be set in .env")

    # every tag defined in the account
    d = request("GET", f"{BASE}/locations/{loc}/tags", token)
    defined = sorted(t["name"] for t in d.get("tags", []))
    print(f"Tags defined in account: {len(defined)}")

    # count usage across all contacts
    print("Scanning contacts for tag usage...", flush=True)
    usage = collections.Counter()
    seen = 0
    search_after = None
    while True:
        body = {"locationId": loc, "pageLimit": 100}
        if search_after:
            body["searchAfter"] = search_after
        data = request("POST", f"{BASE}/contacts/search", token, body)
        contacts = data.get("contacts", [])
        if not contacts:
            break
        for c in contacts:
            seen += 1
            for t in (c.get("tags") or []):
                usage[t] += 1
        search_after = contacts[-1].get("searchAfter")
        if not search_after:
            break
        if seen % 5000 == 0:
            print(f"  {seen} scanned...", flush=True)

    print(f"  {seen} contacts scanned\n")

    unused = [t for t in defined if usage.get(t, 0) == 0]
    used = [(t, usage[t]) for t in defined if usage.get(t, 0) > 0]
    used.sort(key=lambda kv: -kv[1])

    print("=" * 62)
    print("TAG USAGE AUDIT")
    print("=" * 62)
    print(f"  Defined tags        {len(defined):>5}")
    print(f"  In use              {len(used):>5}")
    print(f"  Zero contacts       {len(unused):>5}   <- junk candidates")
    print()

    print("-- UNUSED TAGS (0 contacts) --")
    for t in unused:
        ours = t in OURS_EXACT or t.startswith(OURS_PREFIX)
        print(f"    {t}" + ("   [ours, keep]" if ours else ""))

    print("\n-- NEAR-DUPLICATE GROUPS --")
    groups = collections.defaultdict(list)
    for t in defined:
        groups[normalise(t)].append(t)
    dupes = {k: v for k, v in groups.items() if len(v) > 1}
    if not dupes:
        print("    none found")
    for key, members in sorted(dupes.items()):
        print(f"    [{key}]")
        for m in sorted(members, key=lambda x: -usage.get(x, 0)):
            print(f"       {usage.get(m,0):>6}  {m}")

    print("\n-- TOP 25 BY USAGE --")
    for t, n in used[:25]:
        print(f"    {n:>6}  {t}")

    if args.csv:
        os.makedirs(os.path.dirname(args.csv), exist_ok=True)
        with open(args.csv, "w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh)
            w.writerow(["tag", "contacts", "status", "decision"])
            for t in defined:
                n = usage.get(t, 0)
                if t in OURS_EXACT or t.startswith(OURS_PREFIX):
                    st = "new build - keep"
                elif n == 0:
                    st = "UNUSED"
                else:
                    st = "in use"
                w.writerow([t, n, st, ""])
        print(f"\nWrote {args.csv} - send this to Chris to mark keep/merge/delete")

    return 0


if __name__ == "__main__":
    sys.exit(main())
