#!/usr/bin/env python3
"""
Sophie Orozco FG Funnels - Build A foundation setup.

Creates the custom fields, control tags and Existing Clients pipeline for the
client touchpoint automation. Idempotent: checks what already exists and skips it,
so re-running is safe.

Deliberately does NOT create:
  - the program_offer dropdown (options depend on the unresolved offer list)
  - the 8 offer tags (exact names pending client confirmation)
Both are held so we don't have to rename assets in an account we are about to audit.

Usage:
    python execution/ghl_setup_sophie.py --dry-run
    python execution/ghl_setup_sophie.py
"""

import argparse
import json
import os
import sys
import urllib.error
import urllib.request

BASE = "https://services.leadconnectorhq.com"
API_VERSION = "2021-07-28"

# ---------------------------------------------------------------- config

# Offers confirmed 90-day by Chris Orozco, 2026-07-22.
# RMM Men and RMM Women were marked RETIRE, so no tags are created for them.
# (3) 1:1 Coaching Calls is held: Chris wants it added to the CRM but did not
# mark it 90-day / not-90-day, and described it as an upsell path.
OFFERS = [
    ("RMM Group Only Men", "client - group only men"),
    ("RMM Group Only Women", "client - group only women"),
    ("RMM VIP Sophie Men", "client - vip sophie men"),
    ("RMM VIP Sophie Women", "client - vip sophie women"),
    ("RMM Course only Men", "client - course only men"),
    ("RMM Course only Women", "client - course only women"),
    ("Couples Coaching", "client - couples coaching"),
    ("Couples Coaching VIP Sophie", "client - couples coaching vip"),
    ("RMM Accelerator Men", "client - accelerator men"),
    ("RMM Accelerator Women", "client - accelerator women"),
]

# Upsell / continuation offers, sent by Chris 2026-07-23.
# His list named items 4/6 and 5/7 identically ("Continuation RMM Men" at both
# 6 months and 3 months), which is not creatable as two tags. The 3mo/6mo
# suffixes below are ours, pending his confirmation. Renaming is cheap.
UPSELL_OFFERS = [
    ("Radiant Feminine Blueprint", "client - radiant feminine"),
    ("Radiant Feminine Blueprint w/ 1:1 Calls", "client - radiant feminine 1on1"),
    ("Forge", "client - forge"),
    ("Continuation RMM Men 6mo", "client - continuation rmm men 6mo"),
    ("Continuation RMM Women 6mo", "client - continuation rmm women 6mo"),
    ("Continuation RMM Men 3mo", "client - continuation rmm men 3mo"),
    ("Continuation RMM Women 3mo", "client - continuation rmm women 3mo"),
]

OFFERS = OFFERS + UPSELL_OFFERS

FIELDS = [
    ("program_start_date", "DATE", "Program start. Set by WF-A1/WF-A2, never by hand."),
    ("program_end_date", "DATE", "Program end, start + 90 days. Long track only."),
    ("csm_email", "TEXT", "CSM notification address. Currently Luann."),
    (
        "program_offer",
        "SINGLE_OPTIONS",
        "What the client actually bought. Distinct from the existing "
        "'Offer Discussed' field, which is what was discussed on the call.",
    ),
]

# Display names double as the dropdown options so Luann's emails read the way
# reps and Luann already talk about the offers.
FIELD_OPTIONS = {"program_offer": [display for display, _ in OFFERS]}

TAGS = [
    "existing client",
    "client - cancelled",
    "client - completed",
] + [tag for _, tag in OFFERS]

PIPELINE_NAME = "Existing Clients"
PIPELINE_STAGES = [
    "Onboarding",
    "Check-In 1",
    "Check-In 2",
    "Check-In 3",
    "Renewal Window",
    "Program Complete",
    "Renewal Conversation",
    "Upsell Nurture",
]

# ---------------------------------------------------------------- helpers


def load_env(path):
    """Minimal .env reader. Avoids a dependency for three values."""
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


def call(method, path, token, body=None):
    url = f"{BASE}{path}"
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Version", API_VERSION)
    req.add_header("Accept", "application/json")
    # Cloudflare in front of the API returns 1010 on urllib's default UA.
    req.add_header("User-Agent", "curl/8.0.1")
    if data:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode()
            return resp.status, (json.loads(raw) if raw else {})
    except urllib.error.HTTPError as e:
        raw = e.read().decode()
        try:
            return e.code, json.loads(raw)
        except json.JSONDecodeError:
            return e.code, {"raw": raw}
    except urllib.error.URLError as e:
        return 0, {"error": str(e)}


def err(payload):
    """Pull something human-readable out of a GHL error body."""
    if isinstance(payload, dict):
        for key in ("message", "error", "msg", "raw"):
            if key in payload:
                v = payload[key]
                return v if isinstance(v, str) else json.dumps(v)
    return json.dumps(payload)[:200]


# ---------------------------------------------------------------- steps


def setup_fields(token, loc, dry):
    print("\n=== CUSTOM FIELDS ===")
    status, data = call("GET", f"/locations/{loc}/customFields", token)
    if status != 200:
        print(f"  ABORT: cannot list fields ({status}) {err(data)}")
        return False
    existing = {f.get("name", "").lower(): f for f in data.get("customFields", [])}

    ok = True
    for name, dtype, note in FIELDS:
        if name.lower() in existing:
            print(f"  SKIP    {name} (already exists)")
            continue
        opts = FIELD_OPTIONS.get(name)
        if dry:
            print(f"  WOULD   {name} [{dtype}]  - {note}")
            for o in opts or []:
                print(f"            option: {o}")
            continue
        payload = {
            "name": name,
            "dataType": dtype,
            "model": "contact",
            "placeholder": "",
        }
        if opts:
            # The create endpoint expects "options"; the read endpoint returns
            # the same data as "picklistOptions". Not a typo.
            payload["options"] = opts
        status, resp = call("POST", f"/locations/{loc}/customFields", token, payload)
        if status in (200, 201):
            fid = (resp.get("customField") or {}).get("id", "?")
            print(f"  CREATED {name} [{dtype}]  id={fid}")
        else:
            print(f"  FAILED  {name} ({status}) {err(resp)}")
            ok = False
    return ok


def setup_tags(token, loc, dry):
    print("\n=== CONTROL TAGS ===")
    status, data = call("GET", f"/locations/{loc}/tags", token)
    if status != 200:
        print(f"  ABORT: cannot list tags ({status}) {err(data)}")
        return False
    existing = {t.get("name", "").lower() for t in data.get("tags", [])}

    ok = True
    for name in TAGS:
        if name.lower() in existing:
            print(f"  SKIP    {name} (already exists)")
            continue
        if dry:
            print(f"  WOULD   {name}")
            continue
        status, resp = call("POST", f"/locations/{loc}/tags", token, {"name": name})
        if status in (200, 201):
            print(f"  CREATED {name}")
        else:
            print(f"  FAILED  {name} ({status}) {err(resp)}")
            ok = False
    return ok


def setup_pipeline(token, loc, dry):
    print("\n=== PIPELINE ===")
    status, data = call("GET", f"/opportunities/pipelines?locationId={loc}", token)
    if status != 200:
        print(f"  ABORT: cannot list pipelines ({status}) {err(data)}")
        return False

    for p in data.get("pipelines", []):
        if p.get("name", "").lower() == PIPELINE_NAME.lower():
            print(f"  SKIP    '{PIPELINE_NAME}' already exists (id={p.get('id')})")
            return True

    if dry:
        print(f"  WOULD   create '{PIPELINE_NAME}' with {len(PIPELINE_STAGES)} stages")
        for i, s in enumerate(PIPELINE_STAGES, 1):
            print(f"            {i}. {s}")
        return True

    status, resp = call(
        "POST",
        "/opportunities/pipelines",
        token,
        {
            "locationId": loc,
            "name": PIPELINE_NAME,
            "stages": [
                {"name": s, "position": i} for i, s in enumerate(PIPELINE_STAGES)
            ],
        },
    )
    if status in (200, 201):
        print(f"  CREATED '{PIPELINE_NAME}'")
        return True

    print(f"  FAILED  ({status}) {err(resp)}")
    print("\n  The GHL API has historically been read-only for pipelines.")
    print("  If this is a 404/405, build it by hand:")
    print("    Opportunities -> Pipelines -> Create Pipeline")
    print(f"    Name: {PIPELINE_NAME}")
    for i, s in enumerate(PIPELINE_STAGES, 1):
        print(f"      {i}. {s}")
    return False


# ---------------------------------------------------------------- main


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="show what would change")
    args = ap.parse_args()

    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    env = load_env(os.path.join(root, ".env"))
    token = env.get("GHL_API_KEY") or os.environ.get("GHL_API_KEY")
    loc = env.get("GHL_LOCATION_ID") or os.environ.get("GHL_LOCATION_ID")

    if not token or not loc:
        sys.exit("GHL_API_KEY and GHL_LOCATION_ID must be set in .env")

    status, data = call("GET", f"/locations/{loc}", token)
    if status != 200:
        sys.exit(f"Cannot reach sub-account ({status}): {err(data)}")
    print(f"Sub-account: {data.get('location', {}).get('name')}  ({loc})")
    if args.dry_run:
        print("MODE: dry run, nothing will be written")

    results = [
        setup_fields(token, loc, args.dry_run),
        setup_tags(token, loc, args.dry_run),
        setup_pipeline(token, loc, args.dry_run),
    ]

    print("\n=== HELD (not created, pending client) ===")
    print("  program_offer dropdown - options depend on the offer list")
    print("  8 offer tags           - exact names pending")
    print("  upsell tags            - 3-month / 6-month list pending")

    print("\nDone." if all(results) else "\nDone with failures - see above.")
    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main())
