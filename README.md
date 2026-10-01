# FG Funnels: Sophie Orozco Coaching

Self-contained copy of the FG Funnels (GoHighLevel) project for Sophie Orozco Coaching, assembled on 2026-10-02 from the Claude Code session that ran Sept 23 to Oct 2, 2026. Sub-account `UXy5gqFd4ZwlDAEsfWHD`.

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
| client-tagging-sop | https://client-tagging-sop.vercel.app | 6 files |
| manychat-communication-reset | https://manychat-communication-reset.vercel.app (+ /build) | 8 files |
| rmm-catchup-plan | https://rmm-catchup-plan.vercel.app | 7 files |
| client-journey-sop | https://client-journey-sop.vercel.app | 5 files |
| continuation-tracker-sop | https://continuation-tracker-sop.vercel.app | 5 files |
| onboarding-sop | https://onboarding-sop-ten.vercel.app | 7 files |
| onboarding-automations-reference | https://onboarding-automations-reference.vercel.app | 3 files |
| sophie-workflows-sop | https://sophie-workflows-sop.vercel.app | 8 files |
| sop-lib | (shared generator used by client-journey-sop and continuation-tracker-sop) | 2 files |

To change a page: edit `build.py` in its folder, run `python build.py`, then `vercel deploy --prod --yes` from that folder. `client-journey-sop` and `continuation-tracker-sop` import `../sop-lib/sop_lib.py`, so keep `sop-lib` next to them.

## Deliverables
- Continuation-Tracker-Completion-Updates.pdf
- GHL-Tag-Cleanup-Review-List.pdf
- SOC-Staff-Hub-Portal-Setup-Guide.pdf
- Catch-Up-Clients.csv
- Catch-Up-Enrollment.csv
- Communication_Reset_ManyChat_Automation.docx
- Client-Journey-System-SOP-Krissy.pdf
- Client-Journey-System-SOP.pdf
- Continuation-Tracker-System-SOP-Krissy.pdf
- Client Journey System (Krissy) - GHL Workflow SOP.pdf
- Standard Operating Procedure (SOP)- GHL (1).docx
- Standard Operating Procedure (SOP)- GHL.docx
- Client SOP_Journey.docx

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
