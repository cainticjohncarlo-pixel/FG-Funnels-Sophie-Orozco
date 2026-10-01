# -*- coding: utf-8 -*-
"""
Set program_start_date on GHL contacts from a roster CSV (date,name,email,note).

Matching: by email when the roster has one (exact, case-insensitive); otherwise by full name.
A row is written only when exactly ONE contact matches. Rows with date=HOLD, no match, or
several matches are reported and skipped. Existing values equal to the roster date are skipped.

Dry run by default:
    python execution/ghl_set_program_start_dates.py execution/roster_krissy_2026-09-12.csv
    python execution/ghl_set_program_start_dates.py execution/roster_krissy_2026-09-12.csv --apply

Every run writes a before-snapshot CSV next to this script for rollback.
Only the one date field is sent in the update body; tags are never sent.
"""
import os, sys, csv, time, argparse, datetime as dt
import requests
from dotenv import load_dotenv

HERE = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(HERE, "..", ".env"))
K = os.environ["GHL_API_KEY"]; L = os.environ["GHL_LOCATION_ID"]
H = {"Authorization": f"Bearer {K}", "Version": "2021-07-28",
     "Content-Type": "application/json", "User-Agent": "curl/8.0.1"}
B = "https://services.leadconnectorhq.com"

ap = argparse.ArgumentParser()
ap.add_argument("roster")
ap.add_argument("--field", default="program_start_date")
ap.add_argument("--apply", action="store_true")
args = ap.parse_args()

def req(method, url, **kw):
    for attempt in range(6):
        r = requests.request(method, url, headers=H, timeout=60, **kw)
        if r.status_code in (429, 500, 502, 503, 504):
            time.sleep(1.5 * (attempt + 1)); continue
        return r
    return r

def search(**body):
    body["locationId"] = L; body.setdefault("pageLimit", 20)
    return req("POST", f"{B}/contacts/search", json=body).json().get("contacts", [])

fields = req("GET", f"{B}/locations/{L}/customFields").json().get("customFields", [])
fid = next((f["id"] for f in fields if f["name"] == args.field), None)
if not fid: sys.exit(f"field {args.field!r} not found")

def cur_val(c):
    v = next((cf.get("value") for cf in c.get("customFields", []) if cf["id"] == fid), None)
    return (str(v)[:10] if v else "")

rows = list(csv.DictReader(open(args.roster, encoding="utf-8")))
plan, held = [], []
for r in rows:
    name, email, date = r["name"].strip(), (r["email"] or "").strip().lower(), r["date"].strip()
    if date == "HOLD":
        held.append((name, "HOLD", r["note"])); continue
    if email:
        hits = [c for c in search(query=email) if (c.get("email") or "").lower() == email]
        how = "email"
    else:
        first, last = name.split(" ", 1)
        hits = [c for c in search(query=name)
                if (c.get("firstNameLowerCase") or "") == first.lower() and (c.get("lastNameLowerCase") or "") == last.lower()]
        how = "name"
    if len(hits) != 1:
        held.append((name, f"{len(hits)} matches by {how}", "; ".join(f"{h.get('firstNameLowerCase')} {h.get('lastNameLowerCase')} <{h.get('email')}>" for h in hits[:4])))
        continue
    c = hits[0]
    plan.append({"id": c["id"], "name": name, "email": c.get("email") or "", "how": how,
                 "client_tag": "existing client" in c.get("tags", []), "before": cur_val(c), "after": date})
    time.sleep(0.2)

stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
snap = os.path.join(HERE, f"program_start_date_before_{stamp}.csv")
with open(snap, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["id", "name", "email", "how", "client_tag", "before", "after"])
    w.writeheader(); w.writerows(plan)

todo = [p for p in plan if p["before"] != p["after"]]
same = [p for p in plan if p["before"] == p["after"]]
print(f"roster rows: {len(rows)} | matched: {len(plan)} | already correct: {len(same)} | to write: {len(todo)} | held: {len(held)}")
print(f"snapshot: {snap}\n")
print(f"{'name':24} {'via':5} {'client':6} {'before':11} -> after")
for p in plan:
    flag = "" if p["before"] != p["after"] else "  (same)"
    print(f"{p['name']:24} {p['how']:5} {'yes' if p['client_tag'] else 'NO':6} {p['before'] or '(empty)':11} -> {p['after']}{flag}")
if held:
    print("\nHELD (not written):")
    for h in held: print(f"  {h[0]:24} {h[1]:22} {h[2][:110]}")
if not args.apply:
    print("\nDRY RUN, nothing written."); sys.exit(0)

ok, fail = 0, []
for p in todo:
    r = req("PUT", f"{B}/contacts/{p['id']}", json={"customFields": [{"id": fid, "field_value": p["after"]}]})
    if r.status_code == 200: ok += 1
    else: fail.append((p["name"], r.status_code, r.text[:120]))
    time.sleep(0.15)
print(f"\nwritten {ok}, failed {len(fail)}")
for f_ in fail: print("  FAIL", f_)
if todo:
    time.sleep(1)
    c = req("GET", f"{B}/contacts/{todo[0]['id']}").json().get("contact", {})
    print(f"verify {todo[0]['name']}: {args.field} = {cur_val(c)!r}")
