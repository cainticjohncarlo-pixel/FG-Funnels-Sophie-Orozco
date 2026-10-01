#!/usr/bin/env python3
"""
Fire a synthetic test lead at the EAI intake webhook, then read back what landed.

Purpose: answer step 1.3 of the build plan - does the intake workflow put the whole
full name into the standard First Name field, leaving Last Name empty? That decides
whether the name-split automation (MAIN column K) is needed at all.

The payload keys mirror the documented schema in the sheet's "custom fields" tab
(name / email / phone / organization / businessWebsite / icp.* / legalConsent.* /
attribution.*), so it exercises the same mapping a real landing-page submission does.

This is a SYNTHETIC payload, not a real form submission. If a field fails to map,
confirm against a real 20-click submission before concluding the mapping is broken.

Safety: the contact uses an example.com address and a 555-01xx reserved fictional
phone number, so no real person can be contacted even if a workflow tries to send.
Everything is tagged ZZ TEST and isTest=true so it is trivially findable.

Usage:
    python execution/ghl_send_test_lead.py --dry-run     # print the payload only
    python execution/ghl_send_test_lead.py               # fire it, then read back
    python execution/ghl_send_test_lead.py --readback    # just re-read, send nothing
    python execution/ghl_send_test_lead.py --cleanup     # delete the ZZ TEST contacts
"""

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request

BASE = "https://services.leadconnectorhq.com"
API_VERSION = "2021-07-28"

WEBHOOK_URL = ("https://services.leadconnectorhq.com/hooks/2SVQD8zlZukMad4n131K"
               "/webhook-trigger/8fa1269e-5e34-49c8-8ca1-62c7c87a1c86")

# Three words on purpose: proves whether a compound surname survives the split.
TEST_NAME = "Maria Clara Santos"
TEST_EMAIL = "zz-test-lead@example.com"
MARKER = "ZZ TEST"

PAYLOAD = {
    "name": TEST_NAME,
    "email": TEST_EMAIL,
    "phone": "+15550100001",              # 555-01xx = reserved fictional range
    "organization": f"{MARKER} Company",
    "businessWebsite": "https://example.com",
    "icp": {"industry": "Dental", "slug": "dental-multi-location"},
    "businessScale": "10-50 employees",
    "currentSoftware": "Spreadsheets",
    "legalConsent": {"version": "v1.0", "capturedAt": "2026-07-31T00:00:00Z"},
    "source": "Website Form",
    "isTest": True,
    "landingRoute": "/zz-test",
    "primaryBottleneck": "Missed inbound leads",
    "desiredOutcome": "Automated lead response",
    "workflowSummary": f"{MARKER} - synthetic payload for schema validation.",
    "leadIntakeBrief": f"{MARKER} lead. Safe to delete. Fired to verify the "
                       "first/last name mapping before building MAIN column K.",
    "submittedAt": "2026-07-31T00:00:00Z",
    "attribution": {
        "landingPage": "https://automation-maven-main.vercel.app/",
        "referrer": "https://example.com/",
        "utm_source": "zz-test",
        "utm_medium": "zz-test",
        "utm_campaign": "zz-test",
        "utm_term": "zz-test",
        "utm_content": "zz-test",
        "gclid": "zz-test-gclid",
        "fbclid": "zz-test-fbclid",
    },
}


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


def api(method, path, token, body=None):
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


def post_webhook(payload):
    data = json.dumps(payload).encode()
    req = urllib.request.Request(WEBHOOK_URL, data=data, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("User-Agent", "curl/8.0.1")
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return resp.status, resp.read().decode()[:300]
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()[:300]


def find_test_contacts(token, loc):
    st, d = api("GET", f"/contacts/?locationId={loc}&limit=100", token)
    if st != 200:
        return st, []
    hits = [c for c in d.get("contacts", [])
            if "zz-test" in (c.get("email") or "").lower()
            or MARKER.lower() in (c.get("companyName") or "").lower()]
    return st, hits


def report(token, loc):
    st, hits = find_test_contacts(token, loc)
    if st != 200:
        print(f"  cannot read contacts ({st})")
        return
    if not hits:
        print("  no test contact found yet")
        return

    for c in hits:
        print(f"\n  contact id : {c.get('id')}")
        print(f"  firstName  : {c.get('firstName')!r}")
        print(f"  lastName   : {c.get('lastName')!r}")
        print(f"  contactName: {c.get('contactName')!r}")
        print(f"  email      : {c.get('email')!r}")
        print(f"  company    : {c.get('companyName')!r}")
        cf = c.get("customFields") or []
        print(f"  custom fields populated: {len(cf)}")

        print("\n  --- ANSWER TO STEP 1.3 ---")
        fn, ln = (c.get("firstName") or ""), (c.get("lastName") or "")
        if fn.strip() == TEST_NAME:
            print("  First Name holds the WHOLE name; Last Name is "
                  f"{'empty' if not ln.strip() else repr(ln)}.")
            print("  -> The split automation (MAIN column K) IS needed.")
        elif fn.strip() == "Maria" and ln.strip() == "Clara Santos":
            print("  GHL already split it correctly, keeping the compound surname.")
            print("  -> Column K is NOT needed. Mark it accordingly.")
        elif fn.strip() == "Maria" and ln.strip() == "Santos":
            print("  GHL split it but DROPPED the middle word ('Clara').")
            print("  -> Column K IS needed; native handling is lossy.")
        else:
            print(f"  Unexpected result: firstName={fn!r} lastName={ln!r}")
            print("  -> Inspect the contact by hand before deciding.")

        st2, od = api("GET",
                      f"/opportunities/search?location_id={loc}&contact_id={c.get('id')}",
                      token)
        if st2 == 200:
            opps = od.get("opportunities", [])
            print(f"\n  opportunities for this contact: {len(opps)}")
            for o in opps:
                print(f"    {o.get('name')!r} stage={o.get('pipelineStageId')} "
                      f"status={o.get('status')}")
        else:
            print(f"\n  opportunity read failed ({st2})")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--readback", action="store_true")
    ap.add_argument("--cleanup", action="store_true")
    ap.add_argument("--name", help="override the test full name")
    ap.add_argument("--email", help="override the test email (use a new one per case)")
    ap.add_argument("--phone", help="override the test phone - MUST differ per case, "
                                    "Find contact matches on phone as well as email")
    args = ap.parse_args()

    if args.name:
        PAYLOAD["name"] = args.name
    if args.email:
        PAYLOAD["email"] = args.email
    if args.phone:
        PAYLOAD["phone"] = args.phone

    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    env = load_env(os.path.join(root, ".env"))
    token, loc = env.get("GHL_EAI_API_KEY"), env.get("GHL_EAI_LOCATION_ID")
    if not token or not loc:
        sys.exit("GHL_EAI_API_KEY and GHL_EAI_LOCATION_ID must be set in .env")

    if args.dry_run:
        print("MODE: dry run, nothing sent\n")
        print(f"POST {WEBHOOK_URL}\n")
        print(json.dumps(PAYLOAD, indent=2))
        return 0

    if args.cleanup:
        st, hits = find_test_contacts(token, loc)
        if not hits:
            print("nothing to clean up")
            return 0
        for c in hits:
            st2, _ = api("DELETE", f"/contacts/{c.get('id')}", token)
            print(f"  deleted {c.get('id')} ({c.get('email')}) -> {st2}")
        return 0

    if not args.readback:
        print(f"POST -> intake webhook  name={PAYLOAD['name']!r} "
              f"email={PAYLOAD['email']!r} phone={PAYLOAD['phone']!r}")
        st, body = post_webhook(PAYLOAD)
        print(f"  HTTP {st}  {body}\n")
        if st not in (200, 201, 202):
            print("  webhook rejected the payload; not reading back")
            return 1
        print("  waiting 12s for the intake workflow to run...")
        time.sleep(12)

    print("\nreading back from the API:")
    report(token, loc)
    print("\nWhen finished, clean up with:")
    print("  python execution/ghl_send_test_lead.py --cleanup")
    return 0


if __name__ == "__main__":
    sys.exit(main())
