# -*- coding: utf-8 -*-
"""
Add one tag to a short list of contacts identified by email or by "name:First Last".

    python execution/ghl_add_tag_to_contacts.py "existing client" a@b.com "name:Zamira Jaffer" ...            # dry run
    python execution/ghl_add_tag_to_contacts.py "existing client" a@b.com "name:Zamira Jaffer" ... --apply

Every identifier must resolve to exactly one contact or the run aborts before writing.
Uses POST /contacts/{id}/tags, which appends; existing tags are never touched.
"""
import os, sys, time
import requests
from dotenv import load_dotenv

HERE = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(HERE, "..", ".env"))
K = os.environ["GHL_API_KEY"]; L = os.environ["GHL_LOCATION_ID"]
H = {"Authorization": f"Bearer {K}", "Version": "2021-07-28", "Content-Type": "application/json", "User-Agent": "curl/8.0.1"}
B = "https://services.leadconnectorhq.com"

args = [a for a in sys.argv[1:] if a != "--apply"]; apply = "--apply" in sys.argv
tag, idents = args[0], args[1:]

def req(method, url, **kw):
    for i in range(6):
        r = requests.request(method, url, headers=H, timeout=60, **kw)
        if r.status_code in (429, 500, 502, 503, 504): time.sleep(1.5 * (i + 1)); continue
        return r
    return r

def search(q):
    return req("POST", f"{B}/contacts/search", json={"locationId": L, "query": q, "pageLimit": 20}).json().get("contacts", [])

plan, bad = [], []
for ident in idents:
    if ident.startswith("name:"):
        first, last = ident[5:].strip().split(" ", 1)
        hits = [c for c in search(ident[5:]) if (c.get("firstNameLowerCase") or "") == first.lower() and (c.get("lastNameLowerCase") or "") == last.lower()]
    else:
        hits = [c for c in search(ident) if (c.get("email") or "").lower() == ident.lower()]
    if len(hits) != 1:
        bad.append((ident, len(hits))); continue
    c = hits[0]
    plan.append((c["id"], f"{c.get('firstNameLowerCase')} {c.get('lastNameLowerCase') or ''}".strip(), c.get("email") or "", tag in c.get("tags", [])))
    time.sleep(0.2)

for cid, name, email, has in plan:
    print(f"  {name:22} {email:32} {'already has tag' if has else 'will add'}")
for ident, n in bad: print(f"  ABORT: {ident!r} resolved to {n} contacts")
if bad: sys.exit(1)
if not apply: print("\nDRY RUN, nothing written."); sys.exit(0)

todo = [p for p in plan if not p[3]]
for cid, name, email, _ in todo:
    r = req("POST", f"{B}/contacts/{cid}/tags", json={"tags": [tag]})
    print(f"  {name:22} -> {r.status_code}")
    time.sleep(0.2)

# let the tag-triggered workflow run, then verify owner + csm_email
time.sleep(20)
fields = req("GET", f"{B}/locations/{L}/customFields").json().get("customFields", [])
csm = next((f["id"] for f in fields if f["name"] == "csm_email"), None)
users = {u["id"]: f"{u.get('firstName','')} {u.get('lastName','')}".strip() for u in req("GET", f"{B}/users/", params={"locationId": L}).json().get("users", [])}
print("\nverify (20s after tagging):")
for cid, name, email, _ in plan:
    c = req("GET", f"{B}/contacts/{cid}").json().get("contact", {})
    v = next((cf.get("value") for cf in c.get("customFields", []) if cf["id"] == csm), None)
    print(f"  {name:22} tag={'yes' if tag in c.get('tags', []) else 'NO':3} owner={users.get(c.get('assignedTo'), c.get('assignedTo')) or '-':16} csm_email={v or '-'}")
    time.sleep(0.2)
