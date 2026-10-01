#!/usr/bin/env python3
"""
Sophie Orozco - contact list audit.

Answers Chris's question: "I want to see what our total working email contact
list is with duplicates removed."

His rules (2026-07-23):
  - A contact needs an email to count as a real contact. Social media
    conversations without an email are not true contacts.
  - A duplicate is any contact with the same email.

Read-only. Deletes nothing, changes nothing.

Usage:
    python execution/ghl_contact_audit.py
    python execution/ghl_contact_audit.py --dump-duplicates dupes.csv
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
PAGE = 100


def load_env(path):
    env = {}
    if not os.path.exists(path):
        return env
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip()
    return env


def call(token, body, retries=6):
    """GHL returns intermittent 429s and 504s on long paging runs. Back off and
    retry both, rather than losing 19,000 records of progress to one blip."""
    last = None
    for attempt in range(retries):
        req = urllib.request.Request(
            f"{BASE}/contacts/search", data=json.dumps(body).encode(), method="POST"
        )
        req.add_header("Authorization", f"Bearer {token}")
        req.add_header("Version", API_VERSION)
        req.add_header("Accept", "application/json")
        req.add_header("Content-Type", "application/json")
        req.add_header("User-Agent", "curl/8.0.1")  # Cloudflare blocks urllib's default
        try:
            with urllib.request.urlopen(req, timeout=90) as resp:
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            last = e
            if e.code in (429, 500, 502, 503, 504) and attempt < retries - 1:
                wait = min(2 ** attempt, 30)
                print(f"    HTTP {e.code}, retrying in {wait}s"
                      f" (attempt {attempt + 2}/{retries})", flush=True)
                time.sleep(wait)
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dump-duplicates", help="write duplicate groups to a CSV")
    args = ap.parse_args()

    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    env = load_env(os.path.join(root, ".env"))
    token = env.get("GHL_API_KEY")
    loc = env.get("GHL_LOCATION_ID")
    if not token or not loc:
        sys.exit("GHL_API_KEY and GHL_LOCATION_ID must be set in .env")

    by_email = collections.defaultdict(list)
    no_email = 0
    no_email_no_phone = 0
    no_email_has_phone = 0
    total_seen = 0
    reported_total = None
    search_after = None

    print("Paging through contacts...", flush=True)
    while True:
        body = {"locationId": loc, "pageLimit": PAGE}
        if search_after:
            body["searchAfter"] = search_after
        data = call(token, body)
        if reported_total is None:
            reported_total = data.get("total")
            print(f"  API reports {reported_total} total contacts\n", flush=True)

        contacts = data.get("contacts", [])
        if not contacts:
            break

        for c in contacts:
            total_seen += 1
            email = (c.get("email") or "").strip().lower()
            if email:
                by_email[email].append(c)
            else:
                no_email += 1
                if (c.get("phone") or "").strip():
                    no_email_has_phone += 1
                else:
                    no_email_no_phone += 1

        search_after = contacts[-1].get("searchAfter")
        if not search_after:
            break
        if total_seen % 2000 == 0:
            print(f"  {total_seen} scanned...", flush=True)

    unique_emails = len(by_email)
    with_email = sum(len(v) for v in by_email.values())
    dupe_groups = {e: v for e, v in by_email.items() if len(v) > 1}
    dupe_records = sum(len(v) for v in dupe_groups.values())
    removable = dupe_records - len(dupe_groups)

    print("\n" + "=" * 58)
    print("CONTACT AUDIT - Sophie Orozco Coaching")
    print("=" * 58)
    print(f"  Total contacts scanned          {total_seen:>8,}")
    print()
    print("  NOT REAL CONTACTS (no email address)")
    print(f"    No email, no phone            {no_email_no_phone:>8,}")
    print(f"    No email, has phone           {no_email_has_phone:>8,}")
    print(f"    Subtotal                      {no_email:>8,}")
    print()
    print("  EMAIL CONTACTS")
    print(f"    Records with an email         {with_email:>8,}")
    print(f"    Duplicate email groups        {len(dupe_groups):>8,}")
    print(f"    Records inside those groups   {dupe_records:>8,}")
    print(f"    Removable as duplicates       {removable:>8,}")
    print()
    print("  " + "-" * 54)
    print(f"  WORKING EMAIL LIST (deduped)    {unique_emails:>8,}")
    print("  " + "-" * 54)
    if total_seen:
        print(f"  That is {unique_emails/total_seen*100:.1f}% of the current database.")

    worst = sorted(dupe_groups.items(), key=lambda kv: -len(kv[1]))[:10]
    if worst:
        print("\n  Most duplicated addresses:")
        for email, rows in worst:
            print(f"    {len(rows):>3}x  {email}")

    if args.dump_duplicates and dupe_groups:
        with open(args.dump_duplicates, "w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh)
            w.writerow(["email", "count", "contact_id", "first_name", "last_name",
                        "phone", "date_added", "tags"])
            for email, rows in sorted(dupe_groups.items(), key=lambda kv: -len(kv[1])):
                for c in rows:
                    w.writerow([
                        email, len(rows), c.get("id"), c.get("firstName"),
                        c.get("lastName"), c.get("phone"), c.get("dateAdded"),
                        "|".join(c.get("tags") or []),
                    ])
        print(f"\n  Duplicate detail written to {args.dump_duplicates}")

    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
