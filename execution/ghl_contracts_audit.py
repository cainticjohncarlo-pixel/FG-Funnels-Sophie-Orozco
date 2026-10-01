# -*- coding: utf-8 -*-
"""
Dump every Documents & Contracts record in the sub-account and summarise it.

    python execution/ghl_contracts_audit.py                 # summary + CSV
    python execution/ghl_contracts_audit.py --find morris   # also print full records matching a name/email fragment

Endpoint: GET /proposals/document?locationId&limit<=20&skip=N  (limit above 21 is rejected; offset/page are rejected).
Writes execution/contracts_<stamp>.csv with one row per document.
"""
import os, sys, csv, json, time, argparse, collections, datetime as dt
import requests
from dotenv import load_dotenv

HERE = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(HERE, "..", ".env"))
K = os.environ["GHL_API_KEY"]; L = os.environ["GHL_LOCATION_ID"]
H = {"Authorization": f"Bearer {K}", "Version": "2021-07-28", "User-Agent": "curl/8.0.1"}
B = "https://services.leadconnectorhq.com"

ap = argparse.ArgumentParser(); ap.add_argument("--find", default=None); a = ap.parse_args()

def req(url, **kw):
    for i in range(6):
        r = requests.get(url, headers=H, timeout=40, **kw)
        if r.status_code in (429, 500, 502, 503, 504): time.sleep(1.5 * (i + 1)); continue
        return r
    return r

users = {u["id"]: f"{u.get('firstName','')} {u.get('lastName','')}".strip() for u in req(f"{B}/users/", params={"locationId": L}).json().get("users", [])}
who = lambda uid: users.get(uid, uid or "-")

docs, skip = [], 0
while True:
    j = req(f"{B}/proposals/document", params={"locationId": L, "limit": 20, "skip": skip}).json()
    batch = j.get("documents", []); docs += batch
    if len(batch) < 20: break
    skip += 20; time.sleep(0.25)
print(f"documents fetched: {len(docs)} (api total {j.get('total')})")
if not docs: sys.exit(0)

def row(d):
    rc = (d.get("recipients") or [{}])[0]
    return {"created": d.get("createdAt", "")[:16], "status": d.get("status"), "name": d.get("name"),
            "recipient": f"{rc.get('firstName','')} {rc.get('lastName','')}".strip(), "email": rc.get("email"),
            "contactId": rc.get("id"), "createdBy": who(d.get("createdBy")), "updatedBy": who(d.get("updatedBy")),
            "updated": d.get("updatedAt", "")[:16], "sentAt": (d.get("sentAt") or "")[:16], "value": (d.get("grandTotal") or {}).get("amount"),
            "type": d.get("type"), "id": d.get("_id")}
rows = [row(d) for d in docs]
stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
out = os.path.join(HERE, f"contracts_{stamp}.csv")
with open(out, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
print("csv:", out)

print("\nfields on a document:", sorted(docs[0].keys()))
print("\nstatus counts:", collections.Counter(r["status"] for r in rows).most_common())
print("created by:", collections.Counter(r["createdBy"] for r in rows).most_common())
print("\nunsigned (status not completed/signed) by creator:")
unsigned = [r for r in rows if (r["status"] or "").lower() not in ("completed", "signed", "accepted")]
print(" ", collections.Counter(r["createdBy"] for r in unsigned).most_common())
print("unsigned by month created:", collections.Counter(r["created"][:7] for r in unsigned).most_common())

if a.find:
    print(f"\n=== full records matching {a.find!r} ===")
    for d in docs:
        if a.find.lower() in json.dumps(d).lower():
            d2 = {k: v for k, v in d.items() if k not in ("elements", "pages", "content", "settings", "pdf")}
            print(json.dumps(d2, indent=1, default=str)[:3000]); print("----")
