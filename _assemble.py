# -*- coding: utf-8 -*-
"""Assemble the FG Funnels (Sophie Orozco Coaching) project folder from everything this session produced.
Re-runnable: copies are overwritten, nothing outside this folder is touched. Never prints secrets."""
import os, shutil, glob, json, datetime

ROOT = os.path.dirname(os.path.abspath(__file__))
DL = r"C:\Users\Administrator\Downloads"
ES = os.path.join(DL, "Employee Skills-20260322T140034Z-1-001")
SCR = r"C:\Users\ADMINI~1\AppData\Local\Temp\claude\C--Users-Administrator\e04c35e4-3569-440b-aee1-adafee420c61\scratchpad"
MEM = r"C:\Users\Administrator\.claude\projects\C--\memory"
SKILLS = r"C:\Users\Administrator\.claude\skills"
TRANSCRIPT = r"C:\Users\Administrator\.claude\projects\C--Users-Administrator\e04c35e4-3569-440b-aee1-adafee420c61.jsonl"

def ensure(p): os.makedirs(p, exist_ok=True); return p
def cp(src, dst):
    ensure(os.path.dirname(dst)); shutil.copy2(src, dst); return dst
def cptree(src, dst, skip_ext=(".png",), skip_dirs=("node_modules",)):
    n = 0
    for base, dirs, files in os.walk(src):
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        for f in files:
            if f.lower().endswith(skip_ext): continue
            rel = os.path.relpath(os.path.join(base, f), src)
            cp(os.path.join(base, f), os.path.join(dst, rel)); n += 1
    return n

log = []

# 1. environment ------------------------------------------------------------------
env_src = os.path.join(ES, ".env")
KEEP = ("GHL_API_KEY", "GHL_LOCATION_ID")   # this client's keys only; the shared .env also holds other clients
lines = [l.rstrip("\n") for l in open(env_src, encoding="utf-8") if l.split("=", 1)[0].strip() in KEEP]
open(os.path.join(ROOT, ".env"), "w", encoding="utf-8").write(
    "# FG Funnels / Sophie Orozco Coaching sub-account UXy5gqFd4ZwlDAEsfWHD. Device-local, never share.\n" + "\n".join(lines) + "\n")
keys = list(KEEP)
open(os.path.join(ROOT, ".env.example"), "w", encoding="utf-8").write("".join(f"{k}=\n" for k in keys))
log.append((".env", "copied (values not shown anywhere); .env.example lists the key names: " + ", ".join(keys)))

# 2. execution scripts ----------------------------------------------------------
ex_dst = ensure(os.path.join(ROOT, "execution")); n = 0
for f in sorted(glob.glob(os.path.join(ES, "execution", "ghl_*.py"))):
    name = os.path.basename(f)
    if any(k in name for k in ("eai", "opulent")): continue   # other clients
    cp(f, os.path.join(ex_dst, name)); n += 1
log.append(("execution/", f"{n} GHL scripts (read .env from the folder above them)"))

# 3. sites (Vercel sources, each keeps its .vercel/project.json so deploys hit the same URL) ------
SITES = {
    "client-tagging-sop": "https://client-tagging-sop.vercel.app",
    "manychat-communication-reset": "https://manychat-communication-reset.vercel.app (+ /build)",
    "rmm-catchup-plan": "https://rmm-catchup-plan.vercel.app",
    "client-journey-sop": "https://client-journey-sop.vercel.app",
    "continuation-tracker-sop": "https://continuation-tracker-sop.vercel.app",
    "onboarding-sop": "https://onboarding-sop-ten.vercel.app",
    "onboarding-automations-reference": "https://onboarding-automations-reference.vercel.app",
    "sophie-workflows-sop": "https://sophie-workflows-sop.vercel.app",
    "sop-lib": "(shared generator used by client-journey-sop and continuation-tracker-sop)",
}
site_rows = []
for d, url in SITES.items():
    src = os.path.join(DL, d)
    if not os.path.isdir(src): site_rows.append((d, url, "MISSING")); continue
    n = cptree(src, os.path.join(ROOT, "sites", d))
    site_rows.append((d, url, f"{n} files"))
log.append(("sites/", f"{len(site_rows)} site folders"))

# 4. deliverables -----------------------------------------------------------------
dv = ensure(os.path.join(ROOT, "deliverables")); dv_rows = []
for pat in ["Continuation-Tracker-Completion-Updates.pdf", "GHL-Tag-Cleanup-Review-List.pdf", "SOC-Staff-Hub*.pdf",
            "Catch-Up-Clients.csv", "Catch-Up-Enrollment.csv", "Communication_Reset_ManyChat_Automation.docx",
            "Client-Journey-System-SOP*.pdf", "Continuation-Tracker-System-SOP-Krissy.pdf", "Client Journey System (Krissy)*.pdf",
            "Standard Operating Procedure (SOP)- GHL*.docx", "Client SOP_Journey.docx"]:
    for f in glob.glob(os.path.join(DL, pat)):
        cp(f, os.path.join(dv, os.path.basename(f))); dv_rows.append(os.path.basename(f))
log.append(("deliverables/", f"{len(dv_rows)} files"))

# 5. session data (scratchpad, minus screenshots) ---------------------------------------
sd = ensure(os.path.join(ROOT, "session-data")); n = 0
for f in sorted(glob.glob(os.path.join(SCR, "*"))):
    if os.path.isdir(f) or f.lower().endswith(".png"): continue
    sub = "pdf-builders" if os.path.basename(f).startswith(("build_", "patch_")) else "data"
    cp(f, os.path.join(sd, sub, os.path.basename(f))); n += 1
log.append(("session-data/", f"{n} files: pdf-builders (reportlab scripts) and data (sheets, docs, live-page captures, enrollment logs)"))

# 6. transcript -------------------------------------------------------------------
if os.path.exists(TRANSCRIPT):
    cp(TRANSCRIPT, os.path.join(sd, "transcript", "session-e04c35e4.jsonl"))
    log.append(("session-data/transcript/", "full Claude Code session transcript (jsonl)"))

# 7. memory -----------------------------------------------------------------------
mm = ensure(os.path.join(ROOT, "memory")); mem_files = [
    "project_sophie_orozco_ghl.md", "feedback_team_messages_human_short.md", "feedback_client_email_first_person.md",
    "feedback_outreach_copy_style.md", "feedback_proposal_page_style.md", "feedback_take_initiative_no_repeat_questions.md",
    "feedback_env_secrets_local_only.md", "env_windows_bash_heredoc_limit.md", "user_identity.md"]
for f in mem_files:
    if os.path.exists(os.path.join(MEM, f)): cp(os.path.join(MEM, f), os.path.join(mm, f))
idx = [l for l in open(os.path.join(MEM, "MEMORY.md"), encoding="utf-8") if any(f in l for f in mem_files)]
open(os.path.join(mm, "MEMORY-index-excerpt.md"), "w", encoding="utf-8").write("".join(idx))
log.append(("memory/", f"{len(mem_files)} memory files + the matching MEMORY.md index lines"))

# 8. skills used ------------------------------------------------------------------
sk = ensure(os.path.join(ROOT, "skills"))
for s in ["eod-report"]:
    if os.path.isdir(os.path.join(SKILLS, s)): cptree(os.path.join(SKILLS, s), os.path.join(sk, s), skip_ext=())
log.append(("skills/", "eod-report (the EOD house format used every day)"))

# 9. README -----------------------------------------------------------------------
site_tbl = "\n".join(f"| {d} | {u} | {s} |" for d, u, s in site_rows)
dv_list = "\n".join(f"- {f}" for f in dv_rows)
readme = f"""# FG Funnels: Sophie Orozco Coaching

Self-contained copy of the FG Funnels (GoHighLevel) project for Sophie Orozco Coaching, assembled on {datetime.date.today().isoformat()} from the Claude Code session that ran Sept 23 to Oct 2, 2026. Sub-account `UXy5gqFd4ZwlDAEsfWHD`.

## Folder map

| Folder | What is in it |
|---|---|
| `.env` | API key and location ID for the sub-account. Device-local. Never paste it anywhere. `.env.example` lists the key names only. |
| `execution/` | Deterministic Python scripts that talk to the LeadConnector API. Each reads `../.env`. All are read-only unless the name says otherwise. |
| `sites/` | Source for every Vercel page built for the client. Each folder keeps its `.vercel/project.json`, so `vercel deploy --prod --yes` from inside it updates the same live URL. |
| `deliverables/` | PDFs, CSVs and docs handed to the client or the team. |
| `session-data/` | The working files: PDF builder scripts, downloaded sheets and docs, live-page captures, enrollment logs, and the full session transcript. |
| `memory/` | The persistent memory files for this client plus the working-style feedback that applies to it. |
| `skills/` | The EOD report skill (house format for daily updates). |

## Live pages

| Folder | URL | Copied |
|---|---|---|
{site_tbl}

To change a page: edit `build.py` in its folder, run `python build.py`, then `vercel deploy --prod --yes` from that folder. `client-journey-sop` and `continuation-tracker-sop` import `../sop-lib/sop_lib.py`, so keep `sop-lib` next to them.

## Deliverables
{dv_list}

## Scripts

| Script | Purpose |
|---|---|
| `ghl_extract_sequence_emails.py <out.json>` | Pulls the sent copy of the four RMM sequences, weeks 1 to 12, from conversation history. Feeds the Email copy section of rmm-catchup-plan. |
| `ghl_tag_audit.py`, `ghl_contact_audit.py` | Tag and contact audits (read-only). |
| `ghl_add_tag_to_contacts.py` | Adds one tag to a list of contacts (write; used for the CS alerts roster). |
| `ghl_set_program_start_dates.py`, `ghl_set_csm_email.py` | One-time field sets for the client journey (write). |
| `ghl_fix_double_booking.py`, `ghl_fix_contact_timezones.py` | Targeted fixes (write). |
| `ghl_setup_sophie.py`, `ghl_create_calendars_sophie.py`, `ghl_set_calendar_hours.py` | Original account setup (idempotent). |
| `ghl_location_recon.py`, `ghl_contracts_audit.py`, `ghl_send_test_lead.py` | Recon and test helpers. |

## Tooling the session relied on

- Python 3.12 with `reportlab`, `pypdf`, `PyMuPDF`, `playwright` (Chromium) for PDFs and page screenshots.
- Vercel CLI, logged in to the `cainticjohncarlo-pixels-projects` team.
- LeadConnector API v2021-07-28 with a Private Integration Token, User-Agent `curl/8.0.1`.
- Google Sheets and Docs were read through their `export?format=csv|txt` URLs, no connector needed.
- MCP connectors (Google Drive, Gmail, Calendar, Claude Docs) were available but not used for this client. No plugins specific to this project.

## Where things stand (Oct 2, 2026)

- Catch-up loops live: 62 of 63 clients enrolled at their current week on Sept 30. Alex Baldassari has no GHL record. First loop re-entries land Oct 7.
- Four catch-up workflows published. The client journey (WF-Closed Won Client Setup, six WF- Week workflows, Session Counter, Last Session Alert, Coach Handoff) and the continuation tracker (WF-CT1 to WF-CT4) are built and in draft.
- Koral's Calendly reconnected Sept 25; she is on the round robin calendar.
- Open: women's Week 12 check-in email has never been sent, the live Week 9 check-in bodies say "Week 5", and the men's RMM live sequence still has the day-0 intro that caused the copy shift.

See `memory/project_sophie_orozco_ghl.md` for the full dated history.
"""
open(os.path.join(ROOT, "README.md"), "w", encoding="utf-8").write(readme)

# summary (no secrets)
total = 0; size = 0
for base, dirs, files in os.walk(ROOT):
    for f in files:
        if f == ".env": continue
        total += 1; size += os.path.getsize(os.path.join(base, f))
print("FOLDER:", ROOT)
for k, v in log: print(f"  {k:28} {v}")
for d, u, s in site_rows: print(f"  site {d:34} {s}")
print(f"files: {total + 1}  |  size: {size/1e6:.1f} MB")
