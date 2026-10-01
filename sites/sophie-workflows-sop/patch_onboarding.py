# -*- coding: utf-8 -*-
"""One-off patch: add group F (Onboarding) to build.py."""
import io
p = 'build.py'
s = io.open(p, encoding='utf-8').read()

s = s.replace('def wf(group, name, ghl, purpose, starts, flow, steps, tags, team=None, notes=None):\n    WF.append(dict(group=group, name=name, ghl=ghl, purpose=purpose, starts=starts, flow=flow, steps=steps, tags=tags, team=team, notes=notes))',
              'def wf(group, name, ghl, purpose, starts, flow, steps, tags, team=None, notes=None, extra=None):\n    WF.append(dict(group=group, name=name, ghl=ghl, purpose=purpose, starts=starts, flow=flow, steps=steps, tags=tags, team=team, notes=notes, extra=extra))')

newwf = r'''
# ===== F. Onboarding =====
ONB = [
    ("Couples Coaching, men", "client - couples coaching men", "Onboarding Email - (men) Couples"),
    ("Couples Coaching, women", "client - couples coaching women", "Onboarding Email - (women) Couples"),
    ("Couples Coaching VIP, men", "client - vip sophie men", "Onboarding Email - Premium Men Couples"),
    ("Couples Coaching VIP, women", "client - vip sophie women", "Onboarding Email - Premium Women Couples"),
    ("RMM Accelerator, men", "client - rmm accelerator men", "Onboarding Email - RMM Accelerator (men)"),
    ("RMM Accelerator, women", "client - rmm accelerator women", "Onboarding Email - RMM Accelerator (women)"),
    ("RMM standard, men", "client - rmm men", "Onboarding Email - RMM Men"),
    ("RMM standard, women", "client - rmm women", "Onboarding Email - RMM Women"),
    ("RMM Group Only, men", "client - group only men", "Onboarding Email - RMM Group Only (men)"),
    ("RMM Group Only, women", "client - group only women", "Onboarding Email - RMM Group Only (women)"),
    ("RMM Course Only, men", "client - rmm course only men", "Onboarding Email - RMM Course only Men"),
    ("RMM Course Only, women", "client - rmm course only women", "Onboarding Email - RMM Course only Women"),
    ("Self-Paced, men", "client - course only men", "Onboarding Email - RMM Self Paced (Men)"),
    ("Self-Paced, women", "client - course only women", "Onboarding Email - RMM Self Paced (Women)"),
]
onb_table = '<div class="lbl" style="margin-top:14px">Program, tag, workflow</div><table><thead><tr><th>Program purchased</th><th>Tag the closer adds</th><th>Workflow that fires</th></tr></thead><tbody>' + "".join(
    '<tr><td>%s</td><td><code>%s</code></td><td>%s</td></tr>' % (esc(a), esc(b), esc(c)) for a, b, c in ONB) + '</tbody></table>'
wf("F. Onboarding", "Program Onboarding Emails", "14 workflows named Onboarding Email- ...",
   "Sends each new client the welcome email for the exact program they bought, with their Circle community invitation, the app download, and the group call schedule.",
   "The closer adds the program tag at close. Each of the 14 workflows listens for one tag only.",
   [T("Tag added: the program tag", "one workflow per program and gender"), A("Send the onboarding email", "Circle invitation link, app download, first steps, coaching call details for that program"), E()],
   ["One tag, one workflow, one email. There are no waits and no branches.",
    "The closer picks the tag from the reference page rather than typing it, because two tags differ by one word: client - course only is Self-Paced, client - rmm course only is the RMM Course Only program with group calls.",
    "Couples programs: tag the primary contact only. The Circle link in the email works for both partners.",
    "Re-entry is off, so a tag added twice does not send twice."],
   [b for _, b, _ in ONB],
   team="Closers: mark the deal Closed Won, fill Offer Discussed, then add the program tag plus existing client. Copy the tag from onboarding-automations-reference.vercel.app. The full email text for every program is at onboarding-sop-ten.vercel.app.",
   notes="Each onboarding workflow must have exactly one trigger, its tag. A leftover Opportunity Changed trigger on the course-only workflows sent one client two onboarding emails on Sept 4 and is being removed.",
   extra=onb_table)

wf("F. Onboarding", "Client Journey Tracker", "WORKFLOW 2 — A1b Client Journey — 90 Day",
   "Moves the client's card through the Existing Clients pipeline over their 90 days and alerts the client success manager at each milestone.",
   "The closer adds the program tag at close (the same 12 program tags as the onboarding emails).",
   [T("Program tag added"), C("program_start_date on the record?"),
    S(("Empty", "n", [E("Stop")]),
      ("Set", "y", [A("Set csm_email to the CSM"), A("Create the client's card", "Existing Clients pipeline, stage Onboarding"), A("Alert: Day 0, new client assigned"),
                   W("21 days"), A("Stage: Check-In 1"), A("Alert: Week 3 check-in due"),
                   W("21 days"), A("Stage: Check-In 2"), A("Alert: Week 6 check-in due"),
                   W("21 days"), A("Stage: Check-In 3"), A("Alert: Week 9 check-in due"),
                   W("6 days"), A("Stage: Renewal Window"), A("Alert: program expires in 3 weeks"),
                   W("21 days"), A("Stage: Program Complete"), A("Stamp program end date; add tag client - completed"), A("Alert: program ends today"), E()]))],
   ["The card is the team's view of where every client is. The alerts go to the email saved in csm_email, Krissy today.",
    "The clock counts from the day the client entered, so it is correct for clients tagged on close day.",
    "Clients added late do not start over here. They are covered by the Client Check-in Alerts below, which count from the real start date."],
   ["program_start_date field", "csm_email field", "client - completed"])

wf("F. Onboarding", "Client Check-in Alerts", "Client Check-in Alerts (date based)",
   "Reminds the client success manager to check in with each client at week 3, week 6, week 9, the renewal window and program end, timed from that client's real start date.",
   "Every day GHL checks each tagged client's <code>program_start_date</code>. On start date plus 21, 42, 63, 69 or 90 days, that client enters.",
   [T("Start date + 21 / 42 / 63 / 69 / 90 days", "only contacts tagged cs alerts - date based"), C("Which milestone fired?"),
    S(("Week 3", "y", [A("Email + in-app alert to Krissy", "week 3 check-in"), E()]),
      ("Week 6", "y", [A("Email + in-app alert", "week 6 check-in"), E()]),
      ("Week 9", "y", [A("Email + in-app alert", "week 9 check-in"), E()]),
      ("Renewal window", "m", [A("Email + in-app alert", "expires in 3 weeks"), E()]),
      ("Program end", "m", [A("Email + in-app alert", "program ends today"), A("Remove tag: cs alerts - date based"), E()]))],
   ["Nobody is enrolled by hand. The date on the record drives everything, so 47 clients with 47 different start dates each get their own schedule.",
    "A milestone that already passed never fires, so a client added at day 26 gets week 6 next and nothing for week 3.",
    "The 90-day alert removes the tag, which switches the client off.",
    "Each alert carries the client's name, contact details, program, start date and days left."],
   ["cs alerts - date based", "program_start_date field", "csm_email field"],
   team="When a client is added after their start date, set program_start_date to the real date and add the tag cs alerts - date based. Nothing else is needed.")

'''
s = s.replace('# ---------- page ----------', newwf + '# ---------- page ----------')
s = s.replace('GROUPS = ["A. Lead intake", "B. Booked call", "C. Cancel and no-show", "D. Nurture", "E. Closing and clients"]',
              'GROUPS = ["A. Lead intake", "B. Booked call", "C. Cancel and no-show", "D. Nurture", "E. Closing and clients", "F. Onboarding"]')
s = s.replace('    "E. Closing and clients": "What happens when a deal is closed and a lead becomes a client.",\n}',
              '    "E. Closing and clients": "What happens when a deal is closed and a lead becomes a client.",\n    "F. Onboarding": "What the new client receives, and how the team is kept on top of their 90 days.",\n}')
s = s.replace('<div class="lane"><div class="n">5</div><b>Becomes a client</b><ul><li>Closed Won Handoff</li><li>Client Owner Assignment</li><li>Closer Assignment Alert</li><li>Client Exit</li></ul></div>\n</div>',
              '<div class="lane"><div class="n">5</div><b>Becomes a client</b><ul><li>Closed Won Handoff</li><li>Client Owner Assignment</li><li>Closer Assignment Alert</li><li>Client Exit</li></ul></div>\n<div class="lane"><div class="n">6</div><b>Gets onboarded</b><ul><li>Program Onboarding Emails</li><li>Client Journey Tracker</li><li>Client Check-in Alerts</li></ul></div>\n</div>')
s = s.replace('<h2>One lead, five stages</h2>', '<h2>One lead, six stages</h2>').replace('belongs to one of five moments', 'belongs to one of six moments')
s = s.replace("""        parts.append('<div class="lbl" style="margin-top:12px">Flowchart</div><div class="flow">' + render_nodes(w["flow"]) + '</div>')""",
              """        parts.append('<div class="lbl" style="margin-top:12px">Flowchart</div><div class="flow">' + render_nodes(w["flow"]) + '</div>')
        if w.get("extra"): parts.append(w["extra"])""")
io.open(p, 'w', encoding='utf-8').write(s)
print('build.py patched; F group present:', 'F. Onboarding' in s, '| extra hook:', 'w.get("extra")' in s)
