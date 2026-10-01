# -*- coding: utf-8 -*-
"""Extract the weekly email copy (subject + body text) of the four RMM sequences from sent emails.

Read-only. Scans contacts carrying each sequence's tag, oldest first, and takes the first sent copy
of each week's email until all 12 weeks are filled. Client first names in the greeting are replaced
with {{contact.first_name}}. Output: JSON {sequence_key: {"1": {"subject":..., "body":...}, ...}}.

Usage: python execution/ghl_extract_sequence_emails.py <out.json>
"""
import sys, os, re, json, html, time, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ENV = os.path.join(HERE, "..", ".env")
env = {}
for line in open(ENV, encoding="utf-8"):
    if "=" in line and not line.startswith("#"):
        k, v = line.strip().split("=", 1); env[k] = v.strip().strip('"')
LOC = env["GHL_LOCATION_ID"]
H = {"Authorization": "Bearer " + env["GHL_API_KEY"], "Version": "2021-07-28", "User-Agent": "curl/8.0.1",
     "Accept": "application/json", "Content-Type": "application/json"}
B = "https://services.leadconnectorhq.com"

def get(p):
    r = urllib.request.Request(B + p, headers=H); return json.load(urllib.request.urlopen(r))
def post(p, body):
    r = urllib.request.Request(B + p, headers=H, data=json.dumps(body).encode(), method="POST")
    return json.load(urllib.request.urlopen(r))

MEN = ["The Hardest Lesson Most Men Need to Learn", "Becoming the Man You Want to Be", "Clean Up Your Side of the Street",
       "Say Less, Say It Better", "Letting Go of What You're Carrying", "What she needs might not be what she says",
       "Understanding Her Without Losing Yourself", "What You Reinforce Grows", "Get Clear on Where You're Going",
       "Rebuilding Intimacy and Connection", "Trust, Betrayal, and What Comes Next", "Building What Comes Next"]
WOMEN = ["Starting where you actually are", "This is where things start to shift", "Allowing yourself to want more",
         "Taking a deeper look at your role", "Letting Go of what you have been carrying", "How you communicate changes everything",
         "Stepping into your Queen Energy", "Understanding how he operates", "Rebuilding Trust with yourself and others",
         "Shifting what you focus on", "Letting yourself be closer", "Taking this with you"]

SEQUENCES = {
    "rmm_men":       {"tag": "general- rrm men",     "week_of": lambda s: (MEN.index(s) + 1) if s in MEN else None},
    "rmm_women":     {"tag": "general- rmm women",   "week_of": lambda s: (WOMEN.index(s) + 1) if s in WOMEN else None},
    "checkin_men":   {"tag": "rmm- checkin (men)",   "week_of": lambda s: int(m.group(1)) if (m := re.match(r"^Week (\d+) Check-In$", s)) else None},
    "checkin_women": {"tag": "rmm- checkin (women)", "week_of": lambda s: int(m.group(1)) if (m := re.match(r"^Week (\d+) Check-In$", s)) else None},
}

def html_to_text(body):
    t = re.sub(r"<style.*?</style>", "", body, flags=re.S)
    t = re.sub(r"<head.*?</head>", "", t, flags=re.S)
    # links: keep visible text and url when they differ
    def link(m):
        url = html.unescape(m.group(1)); txt = re.sub(r"<[^>]+>", "", m.group(2)).strip()
        if not txt or txt == url or txt.rstrip("/") == url.rstrip("/"): return url
        return f"{txt} ({url})"
    t = re.sub(r'<a[^>]*href="([^"]+)"[^>]*>(.*?)</a>', link, t, flags=re.S)
    t = re.sub(r"<br\s*/?>", "\n", t)
    t = re.sub(r"</p>|</div>|</li>|</h\d>", "\n", t)
    t = re.sub(r"<li[^>]*>", "- ", t)
    t = re.sub(r"<[^>]+>", "", t)
    t = html.unescape(t)
    t = t.replace("\xa0", " ")
    t = "\n".join(l.rstrip() for l in t.split("\n"))
    t = re.sub(r"\n{3,}", "\n\n", t).strip()
    # drop the unsubscribe footer GHL appends
    t = re.split(r"\n\s*If you no longer wish to receive these emails", t)[0].rstrip()
    return t

def personalise(text, first):
    text = re.sub(r"^(Hi|Hey|Hello)\s+[^,\n]+,", r"\1 {{contact.first_name}},", text)
    if first:
        text = re.sub(r"\b" + re.escape(first) + r"\b", "{{contact.first_name}}", text)
    return text

def messages_for(cid):
    out = []
    for cv in get(f"/conversations/search?locationId={LOC}&contactId={cid}").get("conversations", []):
        last = None
        while True:
            d = get(f"/conversations/{cv['id']}/messages?limit=100" + (f"&lastMessageId={last}" if last else "")).get("messages", {})
            ms = d.get("messages", []); out += ms
            if not d.get("nextPage") or not ms: break
            last = ms[-1]["id"]
    return sorted(out, key=lambda m: m["dateAdded"])

def main(out_path):
    result = {}
    for key, spec in SEQUENCES.items():
        got = {}
        contacts = post("/contacts/search", {"locationId": LOC, "pageLimit": 40,
                        "filters": [{"field": "tags", "operator": "eq", "value": spec["tag"]}],
                        "sort": [{"field": "dateAdded", "direction": "desc"}]}).get("contacts", [])
        # newest contacts first, so each week's copy is the latest version of the live email
        for c in contacts:
            if len(got) == 12: break
            first = (c.get("firstName") or "").split(" ")[0]
            for m in messages_for(c["id"]):
                if m.get("direction") != "outbound" or m.get("messageType") != "TYPE_EMAIL": continue
                subj = ((m.get("meta") or {}).get("email") or {}).get("subject", "") or ""
                wk = spec["week_of"](subj)
                if not wk or wk in got or wk > 12: continue
                eid = ((m.get("meta") or {}).get("email") or {}).get("messageIds", [None])[0]
                if not eid: continue
                try:
                    body = get(f"/conversations/messages/email/{eid}")["emailMessage"].get("body", "")
                except Exception as ex:
                    print("  body fetch failed", key, wk, ex); continue
                got[wk] = {"subject": subj, "body": personalise(html_to_text(body), first),
                           "source": f"{c.get('firstName','')} {c.get('lastName','')}".strip(), "sent": m["dateAdded"][:10]}
                time.sleep(0.05)
            print(f"{key}: {len(got)}/12 after {c.get('firstName')} {c.get('lastName')}")
        result[key] = {str(k): got[k] for k in sorted(got)}
    json.dump(result, open(out_path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for key, weeks in result.items():
        missing = [w for w in range(1, 13) if str(w) not in weeks]
        print(key, "weeks found:", len(weeks), "missing:", missing)

if __name__ == "__main__":
    main(sys.argv[1])
