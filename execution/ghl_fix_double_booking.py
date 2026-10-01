# -*- coding: utf-8 -*-
"""
Clean up a lead who booked a second call while the first was still live.

    python execution/ghl_fix_double_booking.py --contact <id> --old-appt <apptId> --assign-to "Stephanie Waring" [--apply]

Does, in order (dry run unless --apply):
  1. removes the contact from the booking-triggered sequences (WF-VALUE, SMS - Call Booked Sequence)
  2. sets the old appointment's status to 'invalid' (not cancelled / no-show, which would fire recovery flows).
     Calendly-synced appointments reject this (400); the script says so and you set Invalid in the UI instead.
  3. reassigns the contact and every open opportunity to the named user
Then re-reads everything and prints the after state.
"""
import os, sys, time, argparse, requests
from dotenv import load_dotenv

HERE = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(HERE, "..", ".env"))
K = os.environ["GHL_API_KEY"]; L = os.environ["GHL_LOCATION_ID"]
H = {"Authorization": f"Bearer {K}", "Version": "2021-07-28", "Content-Type": "application/json", "User-Agent": "curl/8.0.1"}
B = "https://services.leadconnectorhq.com"
SEQUENCES = ["WF-VALUE Booked Call Email Sequence", "Call Booked Sequence > SMS"]

ap = argparse.ArgumentParser()
ap.add_argument("--contact", required=True); ap.add_argument("--old-appt", required=True)
ap.add_argument("--assign-to", required=True); ap.add_argument("--apply", action="store_true")
a = ap.parse_args()

def req(m, url, **kw):
    for i in range(6):
        r = requests.request(m, url, headers=H, timeout=60, **kw)
        if r.status_code in (429, 500, 502, 503, 504): time.sleep(1.5 * (i + 1)); continue
        return r
    return r

users = {u["id"]: f"{u.get('firstName','')} {u.get('lastName','')}".strip() for u in req("GET", f"{B}/users/", params={"locationId": L}).json().get("users", [])}
uid = next((k for k, v in users.items() if v.lower() == a.assign_to.lower()), None)
if not uid: sys.exit(f"user {a.assign_to!r} not found; users: {sorted(users.values())}")
wfs = {w["name"]: w["id"] for w in req("GET", f"{B}/workflows/", params={"locationId": L}).json().get("workflows", [])}
wf_ids = [(n, wfs[n]) for n in SEQUENCES if n in wfs]
missing = [n for n in SEQUENCES if n not in wfs]
if missing: sys.exit(f"workflow(s) not found: {missing}")

def state():
    c = req("GET", f"{B}/contacts/{a.contact}").json().get("contact", {})
    appts = req("GET", f"{B}/contacts/{a.contact}/appointments").json().get("events", [])
    opps = req("GET", f"{B}/opportunities/search", params={"location_id": L, "contact_id": a.contact}).json().get("opportunities", [])
    print(f"  contact {c.get('firstNameLowerCase')} {c.get('lastNameLowerCase')} | assigned {users.get(c.get('assignedTo'), c.get('assignedTo'))}")
    for x in appts: print(f"  appt {x['id']} | {x.get('startTime','')[:16]} | {x.get('appointmentStatus')} | {users.get(x.get('assignedUserId'))}")
    for o in opps: print(f"  opp  {o['id']} | {o.get('status')} | assigned {users.get(o.get('assignedTo'))} | stage {o.get('pipelineStageId','')[:8]}")
    return opps

print("BEFORE"); opps = state()
print("\nPLAN")
for n, w in wf_ids: print(f"  remove from workflow: {n}")
print(f"  appointment {a.old_appt} -> status invalid")
print(f"  assign contact + {len([o for o in opps if o.get('status')=='open'])} open opportunit(ies) -> {users[uid]}")
if not a.apply: print("\nDRY RUN, nothing changed."); sys.exit(0)

print("\nAPPLY")
for n, w in wf_ids:
    r = req("DELETE", f"{B}/contacts/{a.contact}/workflow/{w}")
    print(f"  remove from {n}: {r.status_code} {r.text[:80] if r.status_code >= 300 else ''}")
r = req("PUT", f"{B}/calendars/events/appointments/{a.old_appt}", json={"appointmentStatus": "invalid"})
if r.status_code == 400 and "Calendly" in r.text:
    print("  appointment -> invalid: NOT POSSIBLE BY API (Calendly-synced). Do it in the UI: contact record -> Appointments -> the old one -> status Invalid.")
else:
    print(f"  appointment -> invalid: {r.status_code} {r.text[:120] if r.status_code >= 300 else ''}")
r = req("PUT", f"{B}/contacts/{a.contact}", json={"assignedTo": uid})
print(f"  contact -> {users[uid]}: {r.status_code} {r.text[:80] if r.status_code >= 300 else ''}")
for o in opps:
    if o.get("status") != "open": continue
    r = req("PUT", f"{B}/opportunities/{o['id']}", json={"assignedTo": uid})
    print(f"  opportunity {o['id']} -> {users[uid]}: {r.status_code} {r.text[:80] if r.status_code >= 300 else ''}")
time.sleep(2)
print("\nAFTER"); state()
