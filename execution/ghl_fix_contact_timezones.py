# -*- coding: utf-8 -*-
"""
Find contacts with an upcoming appointment whose timezone looks wrong for their US phone area code, and fix it.

    python execution/ghl_fix_contact_timezones.py            # dry run
    python execution/ghl_fix_contact_timezones.py --apply    # write

Why: contacts created by hand inherit the creating user's browser timezone (Luann is Pacific), and
appointment merge fields in texts/emails render in the contact's timezone. A New Jersey lead booked
for 2 PM ET then gets a text saying 11 AM.

Only US numbers with an unambiguous area code are changed. Split-timezone area codes are listed, not changed.
"""
import os, sys, time, argparse, datetime as dt, requests
from dotenv import load_dotenv

HERE = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(HERE, "..", ".env"))
K = os.environ["GHL_API_KEY"]; L = os.environ["GHL_LOCATION_ID"]
H = {"Authorization": f"Bearer {K}", "Version": "2021-07-28", "Content-Type": "application/json", "User-Agent": "curl/8.0.1"}
B = "https://services.leadconnectorhq.com"
ap = argparse.ArgumentParser(); ap.add_argument("--apply", action="store_true"); ap.add_argument("--days", type=int, default=30); a = ap.parse_args()

ET = "America/New_York"; CT = "America/Chicago"; MT = "America/Denver"; PT = "America/Los_Angeles"; AZ = "America/Phoenix"; HI = "Pacific/Honolulu"; AK = "America/Anchorage"
AREA = {}
def add(tz, codes):
    for c in codes.split(): AREA[c] = tz
add(ET, "201 202 203 207 212 215 216 220 223 229 234 239 240 267 272 276 302 304 305 315 321 330 331 332 339 347 351 352 386 401 404 407 410 412 413 434 440 443 445 470 475 478 484 508 513 516 517 518 540 551 561 570 571 585 586 603 607 609 610 614 616 617 631 646 667 678 680 681 703 704 706 716 717 718 724 727 732 740 743 754 757 762 770 772 774 781 786 802 803 804 810 813 814 828 843 845 848 856 857 859 860 862 864 878 904 906 908 910 912 914 917 919 929 934 937 941 947 954 959 973 978 980 984 989")
add(CT, "205 210 214 217 218 224 225 228 251 254 256 262 269 281 309 312 314 316 317 319 320 325 331 334 337 361 405 409 414 417 430 432 469 479 501 502 504 507 512 515 563 573 574 601 608 612 618 630 636 641 651 660 662 682 708 712 713 715 731 737 763 769 773 779 785 806 812 815 816 817 819 830 832 847 848 850 856 870 872 901 903 913 918 920 936 940 945 952 956 972 979 985")
add(MT, "208 303 307 385 406 435 505 575 719 720 801 970 986")
add(PT, "206 209 213 253 279 310 323 341 360 408 415 424 442 458 503 509 510 530 559 562 619 626 628 650 657 661 669 702 707 714 725 747 760 775 805 818 820 831 858 909 916 925 949 951 971")
add(AZ, "480 520 602 623 928"); add(HI, "808"); add(AK, "907")
SPLIT = {"812", "819", "850", "856", "848", "331"}   # codes that straddle zones or were listed twice; never auto-change

def req(m, url, **kw):
    for i in range(6):
        try:
            r = requests.request(m, url, headers=H, timeout=40, **kw)
        except requests.exceptions.RequestException:
            time.sleep(2 * (i + 1)); continue
        if r.status_code in (429, 500, 502, 503, 504): time.sleep(1.5 * (i + 1)); continue
        return r
    raise SystemExit(f"gave up on {m} {url}")

users = {u["id"]: f"{u.get('firstName','')} {u.get('lastName','')}".strip() for u in req("GET", f"{B}/users/", params={"locationId": L}).json().get("users", [])}
now = dt.datetime.now(dt.timezone.utc); horizon = now + dt.timedelta(days=a.days)

# contacts with a booking tag added in the last 45 days (cheap superset), then check for a future appointment
since = (now - dt.timedelta(days=45)).strftime("%Y-%m-%dT00:00:00Z")
cands, page = [], 1
while True:
    j = req("POST", f"{B}/contacts/search", json={"locationId": L, "pageLimit": 100, "page": page,
            "filters": [{"field": "dateAdded", "operator": "range", "value": {"gte": since}}],
            "sort": [{"field": "dateAdded", "direction": "desc"}]}).json()
    cs = j.get("contacts", []); cands += [c for c in cs if c.get("phone")]
    if len(cs) < 100 or page >= 10: break
    page += 1

rows = []
for c in cands:
    ev = req("GET", f"{B}/contacts/{c['id']}/appointments").json().get("events", [])
    fut = [e for e in ev if e.get("appointmentStatus") in ("confirmed", "new") and e.get("startTime", "") >= now.strftime("%Y-%m-%dT%H:%M")]
    if not fut: continue
    phone = (c.get("phone") or "").replace("+", "")
    code = phone[1:4] if phone.startswith("1") and len(phone) == 11 else None
    should = AREA.get(code) if code and code not in SPLIT else None
    rows.append({"id": c["id"], "name": f"{c.get('firstNameLowerCase')} {c.get('lastNameLowerCase') or ''}".strip(), "phone": c.get("phone"),
                 "code": code, "tz": c.get("timezone") or "(none)", "should": should, "owner": users.get(c.get("assignedTo"), "-"),
                 "appt": sorted(fut, key=lambda e: e["startTime"])[0]["startTime"][:16]})
    time.sleep(0.2)

fix = [r for r in rows if r["should"] and r["tz"] != r["should"]]
hold = [r for r in rows if not r["should"]]
ok = [r for r in rows if r["should"] and r["tz"] == r["should"]]
print(f"contacts with an upcoming call and a phone number: {len(rows)} | already right: {len(ok)} | to fix: {len(fix)} | cannot place from area code: {len(hold)}\n")
print(f"{'name':24} {'phone':14} {'now':22} -> {'should':20} {'owner':16} next call")
for r in fix: print(f"{r['name']:24} {r['phone']:14} {r['tz']:22} -> {r['should']:20} {r['owner']:16} {r['appt']}")
if hold:
    print("\nnot changed (non-US number or split area code):")
    for r in hold: print(f"  {r['name']:24} {r['phone']:14} tz={r['tz']} owner={r['owner']} next call {r['appt']}")
if not a.apply: print("\nDRY RUN, nothing written."); sys.exit(0)
print()
for r in fix:
    resp = req("PUT", f"{B}/contacts/{r['id']}", json={"timezone": r["should"]})
    print(f"  {r['name']:24} -> {r['should']}: {resp.status_code}")
    time.sleep(0.15)
