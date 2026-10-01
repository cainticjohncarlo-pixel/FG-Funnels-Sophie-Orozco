# -*- coding: utf-8 -*-
"""
Set the csm_email custom field on every contact carrying a tag (default: existing client).

Dry run by default. Nothing is written unless --apply is passed.

    python execution/ghl_set_csm_email.py                       # dry run, target krissy@sophieorozco.com
    python execution/ghl_set_csm_email.py --apply               # write
    python execution/ghl_set_csm_email.py --target luann@sophieorozco.com --apply   # roll back

Writes a before-snapshot CSV next to this script on every run (dry or apply) so a rollback is one command.
Only the csm_email field is sent in the update body. Tags are never sent (a PUT with tags replaces them).
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
ap.add_argument("--tag", default="existing client")
ap.add_argument("--field", default="csm_email")
ap.add_argument("--target", default="krissy@sophieorozco.com")
ap.add_argument("--apply", action="store_true", help="actually write; default is dry run")
args = ap.parse_args()

def req(method, url, **kw):
    for attempt in range(6):
        r = requests.request(method, url, headers=H, timeout=60, **kw)
        if r.status_code in (429, 500, 502, 503, 504):
            time.sleep(1.5 * (attempt + 1)); continue
        return r
    return r

# 1. field id
fields = req("GET", f"{B}/locations/{L}/customFields").json().get("customFields", [])
fid = next((f["id"] for f in fields if f["name"] == args.field), None)
if not fid:
    sys.exit(f"custom field {args.field!r} not found")

# 2. contacts with the tag
contacts, page = [], 1
body = {"locationId": L, "pageLimit": 100,
        "filters": [{"field": "tags", "operator": "eq", "value": args.tag}],
        "sort": [{"field": "dateAdded", "direction": "asc"}]}
while True:
    body["page"] = page
    j = req("POST", f"{B}/contacts/search", json=body).json()
    cs = j.get("contacts", []); contacts += cs
    if len(cs) < 100: break
    page += 1

# 3. classify + snapshot
stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
snap = os.path.join(HERE, f"csm_email_before_{stamp}.csv")
todo, same = [], []
with open(snap, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["contactId", "name", "email", f"{args.field}_before"])
    for c in contacts:
        cur = next((cf.get("value") for cf in c.get("customFields", []) if cf["id"] == fid), None) or ""
        name = f"{c.get('firstNameLowerCase') or ''} {c.get('lastNameLowerCase') or ''}".strip()
        w.writerow([c["id"], name, c.get("email") or "", cur])
        (same if cur == args.target else todo).append((c["id"], name, cur))

print(f"tag {args.tag!r}: {len(contacts)} contacts | field {args.field!r} -> {args.target!r}")
print(f"  already set : {len(same)}")
print(f"  to update   : {len(todo)}  (from empty: {sum(1 for t in todo if not t[2])}, "
      f"from other value: {sum(1 for t in todo if t[2])})")
print(f"  snapshot    : {snap}")
if not args.apply:
    print("\nDRY RUN. First 10 that would change:")
    for cid, name, cur in todo[:10]: print(f"    {name:28} {cur or '(empty)':28} -> {args.target}")
    sys.exit(0)

# 4. write
ok, fail = 0, []
for i, (cid, name, cur) in enumerate(todo, 1):
    r = req("PUT", f"{B}/contacts/{cid}", json={"customFields": [{"id": fid, "field_value": args.target}]})
    if r.status_code == 200: ok += 1
    else: fail.append((name, r.status_code, r.text[:120]))
    if i % 25 == 0: print(f"  {i}/{len(todo)} ...")
    time.sleep(0.15)
print(f"\nupdated {ok}, failed {len(fail)}")
for f_ in fail: print("  FAIL", f_)

# 5. verify a sample
time.sleep(1)
c = req("GET", f"{B}/contacts/{todo[0][0]}").json().get("contact", {}) if todo else {}
val = next((cf.get("value") for cf in c.get("customFields", []) if cf["id"] == fid), None)
print(f"verify {todo[0][1] if todo else '-'}: {args.field} = {val!r}")
