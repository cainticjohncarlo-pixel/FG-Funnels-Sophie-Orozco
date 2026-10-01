# -*- coding: utf-8 -*-
"""Generate the Sales & Client Automations SOP page (one section + flowchart per workflow)."""
import html, os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "index.html")
esc = html.escape

# ---------- flow DSL ----------
def T(t, s=""): return ("trig", t, s)
def A(t, s=""): return ("act", t, s)
def C(t, s=""): return ("check", t, s)
def H(t, s=""): return ("hand", t, s)
def W(t, s=""): return ("wait", t, s)
def E(t="End"): return ("end", t, "")
def S(*cols): return ("split", cols, "")   # cols: (label, 'y'|'n'|'m', [nodes])

def render_nodes(nodes):
    out = []
    for i, n in enumerate(nodes):
        kind = n[0]
        if i > 0: out.append('<div class="arrow"></div>')
        if kind == "split":
            cols = n[1]
            out.append('<div class="split" style="grid-template-columns:repeat(%d,1fr)">' % len(cols))
            for label, cls, sub in cols:
                out.append('<div class="col"><div class="tag %s">%s</div>%s</div>' % (cls, esc(label), render_nodes(sub)))
            out.append('</div>')
        elif kind == "end":
            out.append('<div class="node end">%s</div>' % esc(n[1]))
        else:
            sub = ('<small>%s</small>' % n[2]) if n[2] else ''
            out.append('<div class="node %s"><b>%s</b>%s</div>' % (kind, esc(n[1]), sub))
    return "".join(out)

# ---------- workflow data ----------
WF = []
def wf(group, name, ghl, purpose, starts, flow, steps, tags, team=None, notes=None, extra=None):
    WF.append(dict(group=group, name=name, ghl=ghl, purpose=purpose, starts=starts, flow=flow, steps=steps, tags=tags, team=team, notes=notes, extra=extra))

# ===== A. Lead intake =====
wf("A. Lead intake", "Form Intake Router", "Zapier > FORM Intake Router",
   "Sorts every completed assessment into the right lane: already booked a call, or still needs to book.",
   "The tag <code>form - completed assessment</code> is added (Zapier adds it when the Typeform assessment is finished).",
   [T("Tag added: form - completed assessment"), W("Wait 2 minutes", "lets the Calendly booking tag land first"),
    A("Remove tag: form - partial"), C("Already booked? Tags includes calendly-appointment-booked"),
    S(("Yes", "y", [A("Call Status = Booked Call"), E()]),
      ("No", "n", [A("Create opportunity", "Main Sales Pipeline (New), stage New Lead (Opt-In)"), A("Call Status = Form Submitted - No Call Booked"), E()]))],
   ["Waits two minutes so a booking made in the same sitting is already tagged.",
    "Clears the partial-form tag, because the form is now complete.",
    "If they booked, the record is marked Booked Call and nothing else happens.",
    "If not, a New Lead card is created in the sales pipeline and Call Status shows the gap for the setters."],
   ["form - completed assessment", "form - partial", "calendly-appointment-booked", "Call Status field"])

wf("A. Lead intake", "Form Abandonment Recovery (email)", "Zapier > Form Abandonment Recovery",
   "Brings back people who started the assessment and stopped.",
   "The tag <code>form - partial</code> is added (Zapier, when someone starts but does not finish).",
   [T("Tag added: form - partial"), W("Wait 1 hour", "time to finish on their own"),
    C("Did they finish? Tags includes form - completed assessment"),
    S(("Yes", "y", [A("Remove tag: form - partial"), E("Stop")]),
      ("No", "n", [H("Add to workflow: Form Abandonment Recovery > SMS"), A("Email: You still with me {{first_name}}?", "Sophie's story, invitation to book a Relationship Reset Call"),
                  C("Goal: appointment confirmed on Relationship Reset Call", "reached at any time"), E("Exit when the goal is met")]))],
   ["One hour of grace. Many people come back and finish on their own.",
    "If they finished, the partial tag is removed and this stops.",
    "If not, the text version starts alongside, and one personal email goes out with the booking link.",
    "The moment they book a Relationship Reset Call, the goal fires and they leave this workflow."],
   ["form - partial", "form - completed assessment"])

wf("A. Lead intake", "Form Abandonment Recovery (text)", "Zapier > Form Abandonment Recovery > SMS",
   "Four texts over four days to the same abandoners, each one checking whether they have booked yet.",
   "Added by the email version above (Add to Workflow). It has no trigger of its own.",
   [T("Added from Form Abandonment Recovery (email)"),
    A("SMS 1", "“I saw that you partially filled out my form... Are you still looking to get some help?”"),
    W("Wait for a reply, up to 1 day", "a staff reply in the conversation notifies the team and skips ahead"),
    C("Booked? tag calendly-appointment-booked"),
    S(("Booked", "y", [E("Stop")]),
      ("Not booked", "n", [A("SMS 2", "“Hey just bumping this last message”"), W("Wait for a reply, up to 1 day"), C("Booked?"),
                          S(("Booked", "y", [E("Stop")]),
                            ("Not booked", "n", [A("SMS 3", "“I know asking for help can be scary... Is that you?”"), W("Wait for a reply, up to 1 day"), C("Booked?"),
                                                S(("Booked", "y", [E("Stop")]), ("Not booked", "n", [A("SMS 4", "“now might not be the right time... my YouTube is a great place to start”"), E()]))]))]))],
   ["Each text is followed by a one-day window. If a team member replies to the lead in the conversation, the team is notified and the flow jumps straight to the next booking check.",
    "Every booking check looks for the Calendly booked tag. Booked means stop, quietly.",
    "SMS 4 is the graceful exit. Nothing follows it."],
   ["calendly-appointment-booked"],
   team="Reply inside the GHL conversation when a lead answers. That reply is what the workflow watches for.")

# ===== B. Booked call =====
wf("B. Booked call", "New Booking Handler", "CAL - Rebooking Recovery Exit",
   "Runs on every Relationship Reset Call booking. Makes sure the contact exists, marks them booked, stops any recovery sequence, sets up the pipeline card, assigns the closer and alerts them.",
   "Calendly sends Invitee Created for the Relationship Reset Call event type (organization scope).",
   [T("Calendly: Invitee Created", "Relationship Reset Call event type"), C("Find contact by the Calendly email"),
    S(("Found", "y", [C("Existing client?"), S(("Client", "n", [E("Nothing further")]), ("Not a client", "y", [A("Update Calendly fields", "event type, host email, event URI, reschedule URL"), H("Continue below")]))]),
      ("Not found", "m", [A("Create contact", "name, email, phone from Calendly"), A("Update Calendly fields"), H("Continue below")])),
    A("Add tag: calendly-appointment-booked"),
    A("Remove from both recovery workflows", "CAL - Canceled Appointment Recovery, CAL - No-Show Recovery (and their text versions)"),
    A("Remove recovery tags", "calendly-canceled-recovery, calendly-no-show-recovery, calendly-recovery-completed, calendly-recovery-stop"),
    C("Opportunity already in the Appointment Booked stage?"),
    S(("Found", "y", [A("Remove the old card")]), ("Not found", "n", [A("Create opportunity in the sales pipeline", "Appointment Booked stage, status open")])),
    A("Assign contact to the host", "the closer whose Calendly was booked"),
    H("Add to Appointment Confirmation and Reminder"), A("Remove from Form Submitted, No Call Booked"),
    A("Notify the closer", "internal email: Appointment Rebooked, recovery sequences stopped"), E()],
   ["Every booking passes through here, first-time or rebooked.",
    "Existing clients are found and left alone. Everyone else is tagged booked and pulled out of any cancel or no-show recovery that was running.",
    "The pipeline gets one fresh card in Appointment Booked; a stale one is removed first.",
    "The contact is assigned to whichever closer's calendar was booked, which also fires the Closer Assignment Alert."],
   ["calendly-appointment-booked", "calendly-canceled-recovery", "calendly-no-show-recovery", "calendly-recovery-completed", "calendly-recovery-stop", "existing client"],
   notes="The opportunity step still points at the old Main Sales Pipeline. It is scheduled to be repointed to Main Sales Pipeline (New), stage Call Booked.")

wf("B. Booked call", "Pre-Call Email Sequence", "WF-VALUE Booked Call Email Sequence",
   "Eleven emails timed back from the appointment that prepare the lead emotionally, set expectations and handle the investment conversation before the call.",
   "An appointment is confirmed on any of the 13 Relationship Reset Call calendars (each closer's Calendly).",
   [T("Appointment confirmed", "any Relationship Reset Call calendar"), A("Add tag: calendly-appointment-booked"),
    A("Create opportunity", "Appointment Booked stage"), A("Email 1: What happens on your call with us", "sent immediately"),
    C("Still inside Book a Call Email?"), S(("Yes", "y", [A("Remove from Book a Call Email")]), ("No", "n", [A("Continue")])),
    W("72 h before"), A("Email 2: try this the next time a fight starts"),
    W("60 h before"), A("Email 3: Three questions to ask before your call"),
    W("48 h before"), A("Email 4: If your spouse has moved out, start here"),
    W("36 h before"), A("Email 5: the investment (we won't dodge this)"),
    W("24 h before"), A("Email 6: Five habits that create distance"),
    W("12 h before"), A("Email 7: Why you feel like roommates"),
    W("6 h before"), A("Email 8: Why 'let me decide after Thursday' costs more"),
    W("3 h before"), A("Email 9: Why explaining your needs one more time isn't going to work"),
    W("1 h before"), A("Email 10: 'I love you, but I'm not in love with you anymore'"),
    W("30 min before"), A("Email 11: Before we talk today"), E()],
   ["Every wait is measured back from the appointment time, not from the booking. A call booked two days out skips the 72-hour email and starts at 48 hours.",
    "A wait whose time has already passed is skipped together with its email, so nothing arrives late.",
    "If the lead was still in the older Book a Call Email flow, it is removed first so the two never overlap."],
   ["calendly-appointment-booked"],
   notes="A lead who books a second call while the first is still live enters again. A once-only gate is planned so a rebook sends only a fresh confirmation.")

wf("B. Booked call", "Booked Call Text Sequence", "Call Booked Sequence > SMS",
   "Six texts from the moment of booking to five minutes before the call: confirmation, resources, reminders and one podcast.",
   "An appointment is confirmed on any of the 13 Relationship Reset Call calendars.",
   [T("Appointment confirmed"), A("SMS 1: confirmation", "call time and date, asks for a YES reply, points to the pre-call page"),
    W("30 seconds"), A("SMS 2: resources are on the way by email"),
    W("24 h before"), A("SMS 3: reminder for tomorrow"),
    W("6 h before"), A("SMS 4: podcast part 1 of 3"),
    W("1 h before"), A("SMS 5: starts in 1 hour, reschedule link"),
    W("5 min before"), A("SMS 6: 5 minutes out"), E()],
   ["The confirmation goes out within seconds of the booking and asks for a YES.",
    "The reminders are tied to the appointment time and adjust if the call moves.",
    "The call time in every text is shown in the timezone saved on the contact record."],
   [],
   team="Setters: set the lead's Timezone on the contact before they book. A record created from Instagram defaults to the setter's own zone, and the texts would show the wrong hour.")

# ===== C. Cancel and no-show =====
wf("C. Cancel and no-show", "Calendly Cancel and No-Show Stage Mover", "WF-P2 Closer Stage Mover (Calendly triggers)",
   "Keeps the pipeline honest. A cancellation or no-show in Calendly moves the lead's card to the matching stage.",
   "Calendly sends Invitee Canceled or Invitee No Show Created (organization scope).",
   [T("Calendly: Invitee Canceled / Invitee No Show Created"), C("Which trigger fired?"),
    S(("No-show", "n", [A("Create or update opportunity", "Main Sales Pipeline (New), stage No-Show"), E()]),
      ("Cancelled", "m", [A("Create or update opportunity", "Main Sales Pipeline (New), stage Cancelled"), E()]),
      ("Anything else", "y", [E("Nothing")]))],
   ["One workflow, two doors. The branch is chosen by which Calendly event arrived.",
    "The card is created if the lead somehow has none, otherwise moved."],
   [])

for kind, ghl, sms, first_email, tag_in, tag_out, taskname in [
    ("Canceled", "CAL - Canceled Appointment Recovery", "Canceled Appointment Recovery > SMS", "Email 1: everything okay? (cancelled version)", "calendly-canceled-recovery", "calendly-no-show-recovery", "Manual Follow-Up - Canceled Appointment"),
    ("No-Show", "CAL - No-Show Recovery", "No-Show Recovery > SMS", "Email 1: everything okay? (no-show version)", "calendly-no-show-recovery", "calendly-canceled-recovery", "Manual Follow-Up - No-Show")]:
    trig = "Calendly: Invitee Canceled" if kind == "Canceled" else "Calendly: Invitee No Show Created"
    wf("C. Cancel and no-show", f"{kind} Recovery (email)", ghl,
       f"A 14-day, five-email attempt to get a {'cancelled' if kind=='Canceled' else 'missed'} call rebooked, ending in a hand-off to the team if it fails.",
       f"{trig.replace('Calendly: ','Calendly sends ')} (organization scope).",
       [T(trig), C("Find contact by the Calendly email"),
        S(("Found", "y", [A("Update Calendly fields")]), ("Not found", "n", [A("Create contact"), A("Update Calendly fields")])),
        W("Wait 15 minutes", "a reschedule arrives as cancel + rebook; the New Booking Handler pulls them out in this window"),
        C("Skip team and clients: tags includes team OR existing client"),
        S(("Team or client", "n", [E("Stop, nothing sent")]),
          ("Lead", "y", [A("Remove from the pre-call sequences", "WF-VALUE, Call Booked Sequence > SMS") if kind == "Canceled" else A("Continue"),
                         H(f"Add to workflow: {sms}"), A(first_email), A("Set the Calendly reschedule URL on the record"),
                         A("Remove tag: calendly-appointment-booked" + ("" if kind == "Canceled" else "; add tag: calendly-no-show-recovery")),
                         C("Old card in the Call Booked stage?"), S(("Found", "y", [A("Remove it")]), ("Not found", "n", [A("Continue")])),
                         W("Wait 30 minutes"), C("Rebooked already? tag calendly-appointment-booked") if kind == "Canceled" else A("Email 2: it's not too late", "Sophie's own story, rebook link"),
                         S(("Rebooked", "y", [A("Remove tag: recovery"), E("Stop")]), ("Not yet", "n", [A(f"Add tag: {tag_in}; remove {tag_out} and calendly-recovery-completed"), A("Email 2: it's not too late", "Sophie's own story, rebook link")])) if kind == "Canceled" else A("Continue"),
                         W("Wait 1 day"), C("Booked?"), S(("Booked", "y", [E("Stop")]), ("Not booked", "n", [A("Email 3: how Bill turned around his marriage")])),
                         W("Wait 2 days"), C("Booked?"), S(("Booked", "y", [E("Stop")]), ("Not booked", "n", [A("Email 4: the stats behind separation")])),
                         W("Wait 2 days"), C("Booked?"), S(("Booked", "y", [E("Stop")]), ("Not booked", "n", [A("Email 5: Resources for {{first_name}}", "soft exit, reply YES if still interested")])),
                         A(f"Task for the owner: {taskname}", "due in 1 day"), A("Internal email to the owner", "sequence finished without a rebook"),
                         A(f"Remove tag: {tag_in}; add tag: calendly-recovery-completed"), E()]))],
       ["The first 15 minutes are a safety window. A reschedule reaches GHL as a cancel plus a new booking, and the New Booking Handler removes the contact before anything sends.",
        "Team members and existing clients are skipped entirely. A coach meeting moved in Calendly no longer triggers a recovery email.",
        f"Five emails over about two weeks, each followed by a booking check. A booking at any point stops the sequence.",
        "If nothing works, the owner gets a task and an email, and the contact is tagged as having completed recovery."],
       [tag_in, "calendly-recovery-completed", "calendly-appointment-booked", "team", "existing client"],
       team="When a lead replies, answer inside the GHL conversation. When the follow-up task appears, call or text them personally.")

    wf("C. Cancel and no-show", f"{kind} Recovery (text)", sms,
       f"Three texts over three days alongside the {kind.lower()} recovery emails.",
       f"{trig.replace('Calendly: ','Calendly sends ')} (organization scope). Also added by the email version.",
       [T(trig), W("Wait 15 minutes"), C("Skip team and clients"),
        S(("Team or client", "n", [E("Stop")]),
          ("Lead", "y", [A("SMS 1", "“it's Sophie. I noticed you cancelled your call”" if kind == "Canceled" else "“it's Sophie. I saw you missed your call”"),
                         W("Wait for a staff reply, up to 1 day", "a reply notifies the team" if kind == "No-Show" else "a reply jumps to the booking check"),
                         C("Booked or rebooked?"), S(("Yes", "y", [E("Stop")]), ("No", "n", [A("SMS 2", "“I know asking for help can feel scary... Were you able to get the help you need?”"),
                                                                                       W("Wait for a staff reply, up to 1 day"), C("Booked or rebooked?"),
                                                                                       S(("Yes", "y", [E("Stop")]), ("No", "n", [A("SMS 3", "“{{first_name}}?”"), E()]))]))]))],
       ["Same 15-minute safety window and the same team and client skip as the email version.",
        "Each text waits a day for a human reply before the next booking check.",
        "The third text is deliberately just their name. It gets replies."],
       ["calendly-appointment-booked", "team", "existing client"])

# ===== D. Nurture =====
wf("D. Nurture", "Soap Opera Sequence", "Soap Opera Sequence (5-day welcome/re-engagement email series)",
   "Five story emails, one per day, that warm a lead up and end with a call to book. Clients are pulled out at every step.",
   "The tag <code>soap opera</code> is added, or the contact is added directly from another workflow (for example the Communication Reset lead magnet).",
   [T("Enters the sequence"), A("Add tag: soap opera"), A("Email 1 of 5: Before I tell you what happened"),
    W("1 day"), C("Existing client?"), S(("Yes", "n", [A("Add tag: long term nurture"), A("Remove from this workflow"), E()]), ("No", "y", [A("Email 2 of 5: The night I stopped chasing")])),
    W("1 day"), C("Existing client?"), S(("Yes", "n", [A("Tag long term nurture, remove"), E()]), ("No", "y", [A("Email 3 of 5: It only takes one")])),
    W("1 day"), C("Existing client?"), S(("Yes", "n", [A("Remove, tag long term nurture"), E()]), ("No", "y", [A("Email 4 of 5: The part I didn't expect")])),
    W("1 day"), C("Existing client?"), S(("Yes", "n", [A("Remove, tag long term nurture"), E()]), ("No", "y", [A("Email 5 of 5: Why I'm telling you this now", "book-a-call close")])),
    H("Add tag: long term nurture"), E()],
   ["One chapter a day at 11 AM ET.",
    "Before every chapter after the first, the workflow asks whether the person became a client. If yes, they leave and go to long-term nurture instead.",
    "Everyone who finishes is handed to Long Term Email Nurture by the tag."],
   ["soap opera", "existing client", "long term nurture"])

wf("D. Nurture", "Long Term Email Nurture", "Long Term Email Nurture",
   "Thirteen daily teaching emails for leads who did not book, each ending with an invitation to apply for the 90 Day Turnaround.",
   "The tag <code>long term nurture</code> is added (by the Soap Opera Sequence).",
   [T("Tag added: long term nurture"), C("Client check: existing client, closed-won or rmm current client"),
    S(("Client", "n", [A("Remove from this workflow"), A("Add tag: nurture - completed"), E()]),
      ("Lead", "y", [A("Email 01: you need to let go"), W("1 day"), A("Email 02: the 7 biggest relationship killers"), W("1 day"), A("Email 03: how to clear resentment"), W("1 day"),
                    A("Email 04: How to stop monitoring"), W("1 day"), A("Email 05: The secret to grounding yourself"), W("1 day"), A("Email 06: why your partner is turning away"), W("1 day"),
                    A("Email 07: are you holding space or holding your breath?"), W("1 day"), A("Email 08: You're not listening"), W("1 day"), A("Email 09: the thing that makes you irresistible"), W("1 day"),
                    A("Email 10: 5 fake ways people build self-esteem"), W("1 day"), A("Email 11: the apology most people get backward"), W("1 day"), A("Email 12: the biggest lie about relationships"), W("1 day"),
                    A("Email 13: the couples who make it and those who don't"), A("Add tag: nurture - completed"), E()]))],
   ["Two client checks at the top. A client is removed and marked completed without receiving anything.",
    "Thirteen emails, one per day, every one pointing to the 90 Day Turnaround application.",
    "The completion tag records that the person reached the end."],
   ["long term nurture", "nurture - completed", "existing client", "closed-won", "rmm current client"])

wf("D. Nurture", "Nurture Exit - Client", "Nurture Exit - Client",
   "The moment someone becomes a client, they are pulled out of the nurture sequences.",
   "The tag <code>existing client</code> or <code>closed-won</code> is added.",
   [T("Tag added: existing client or closed-won"), A("Remove from Soap Opera Sequence"), A("Remove from Long Term Email Nurture"), E()],
   ["No waits, no messages. Removal only.",
    "Runs every time either tag is added, so a client tagged twice is still handled."],
   ["existing client", "closed-won"],
   notes="In the current build the second removal step still points at the Soap Opera Sequence, a duplicate of the first. It should point at Long Term Email Nurture.")

# ===== E. Closing and clients =====
wf("E. Closing and clients", "Closed Won Handoff", "WF-P1 Closed Won Handoff",
   "Turns a closed deal into a client record: the client tag, the weekly check-in tag by program, and a heads-up to Krissy.",
   "A card in Main Sales Pipeline (New) moves to the Closed Won stage.",
   [T("Pipeline stage changed: Closed Won"), A("Add tag: existing client", "this one tag fires Client Owner Assignment, Client Exit and Nurture Exit"),
    C("Which program? reads Offer Discussed"),
    S(("Men's program", "y", [A("Add tag: rmm- checkin (men)"), A("Notify Krissy", "New client closed: name, program"), E()]),
      ("Women's program", "y", [A("Add tag: rmm- checkin (women)"), A("Notify Krissy"), E()]),
      ("Couples, other or empty", "n", [A("Task for the closer", "Check-in tag needed, due in 1 day"), A("Notify Krissy"), E()]))],
   ["The closer moves the card to Closed Won. Everything else here is automatic.",
    "The check-in tag is chosen from Offer Discussed. If that field is empty or says Couples, the closer gets a task to set it by hand.",
    "Krissy is notified in every case."],
   ["existing client", "rmm- checkin (men)", "rmm- checkin (women)", "Offer Discussed field"],
   team="Closers: set Offer Discussed on the contact and add the program tag at close. Both feed the automations downstream.")

wf("E. Closing and clients", "Client Owner Assignment", "Client Owner Assignment (Krissy)",
   "Gives every new client to the client success manager and stamps her email on the record for the check-in alerts.",
   "The tag <code>existing client</code> is added.",
   [T("Tag added: existing client"), A("Assign contact to Krissy", "replaces any previous owner"), A("csm_email = krissy@sophieorozco.com"), E()],
   ["Runs for every client, new or historic, the moment the tag lands.",
    "The csm_email field is what the check-in alert workflows use as the recipient."],
   ["existing client", "csm_email field"])

wf("E. Closing and clients", "Closer Assignment Alert", "Closer Assignment Alert: Internal Notification",
   "Tells a closer the instant a lead is assigned to them, in the app and by email, with the lead's details.",
   "A contact's assigned user changes to one of the closers.",
   [T("Assigned user changed to a closer"), A("In-app notification to that closer", "New lead assigned to you: name, phone, email"), A("Email to that closer", "same details plus source and the next step"), E()],
   ["Assignment usually happens from the New Booking Handler, which assigns the closer whose calendar was booked.",
    "The email tells the closer to read the notes and the last conversation before reaching out, then confirm the next step on the pipeline card."],
   [])

wf("E. Closing and clients", "Client Exit - Leave All Lead Sequences", "Client Exit - Leave All Lead Sequences",
   "Pulls a new client out of every lead-facing sequence at once, so nobody who just bought gets a sales message.",
   "The tag <code>existing client</code> is added.",
   [T("Tag added: existing client"), A("Remove from Zapier > Form Abandonment Recovery"), A("Remove from Zapier > Form Abandonment Recovery > SMS"),
    A("Remove from CAL - Canceled Appointment Recovery"), A("Remove from CAL - No-Show Recovery"), A("Remove from WF-VALUE Booked Call Email Sequence"),
    A("Remove from BOOKED CALL"), A("Remove from Call Booked Sequence > SMS"), A("Remove from Soap Opera Sequence"), E()],
   ["Eight removals, no messages. Together with Nurture Exit - Client it covers every sequence a lead can be in.",
    "This is why the existing client tag has to be added at every close: it is the switch that turns off the sales machine."],
   ["existing client"])


# ===== F. Onboarding =====
ONB = [
    ("Couples Coaching, men", "client - couples coaching men", "Onboarding Email - (men) Couples"),
    ("Couples Coaching, women", "client - couples coaching women", "Onboarding Email - (women) Couples"),
    ("Couples Coaching VIP, men", "client - vip sophie men", "Onboarding Email - Premium Men Couples"),
    ("Couples Coaching VIP, women", "client - vip sophie women", "Onboarding Email - Premium Women Couples"),
    ("RMM Accelerator, men", "client - rmm accelerator men", "Onboarding Email - RMM Accelerator (men)"),
    ("RMM Accelerator, women", "client - rmm accelerator women", "Onboarding Email - RMM Accelerator (women)"),
    ("RMM Group Only, men", "client - group only men", "Onboarding Email - RMM Group Only (men)"),
    ("RMM Group Only, women", "client - group only women", "Onboarding Email - RMM Group Only (women)"),
    ("Self-Paced, men", "client - rmm self paced men", "Onboarding Email - RMM Self Paced (Men)"),
    ("Self-Paced, women", "client - rmm self paced women", "Onboarding Email - RMM Self Paced (Women)"),
]
onb_table = '<div class="lbl" style="margin-top:14px">Program, tag, workflow</div><table><thead><tr><th>Program purchased</th><th>Tag the closer adds</th><th>Workflow that fires</th></tr></thead><tbody>' + "".join(
    '<tr><td>%s</td><td><code>%s</code></td><td>%s</td></tr>' % (esc(a), esc(b), esc(c)) for a, b, c in ONB) + '</tbody></table>'
wf("F. Onboarding", "Program Onboarding Emails", "10 workflows named Onboarding Email- ...",
   "Sends each new client the welcome email for the exact program they bought, with their Circle community invitation, the app download, and the group call schedule.",
   "The closer adds the program tag at close. Each of the 14 workflows listens for one tag only.",
   [T("Tag added: the program tag", "one workflow per program and gender"), A("Send the onboarding email", "Circle invitation link, app download, first steps, coaching call details for that program"), E()],
   ["One tag, one workflow, one email. There are no waits and no branches.",
    "The closer copies the tag from the reference page rather than typing it. Self-Paced is client - rmm self paced, RMM Course Only is client - rmm course only. The older client - course only tags are retired and send nothing.",
    "Couples programs: tag the primary contact only. The Circle link in the email works for both partners.",
    "Re-entry is off, so a tag added twice does not send twice."],
   [b for _, b, _ in ONB],
   team="Closers: mark the deal Closed Won, fill Offer Discussed, then add the program tag plus existing client. Copy the tag from onboarding-automations-reference.vercel.app. The full email text for every program is at onboarding-sop-ten.vercel.app.",
   notes="Each onboarding workflow has exactly one trigger, its tag. Until Sept 17 a second trigger on the Offer Discussed field could also start these workflows, so a close where the tag and Offer Discussed named different programs sent two onboarding emails. That trigger was removed from all 14 workflows on Sept 17, 2026. On Sept 22 four more were retired: RMM standard (men and women), which was never a real program, and RMM Course Only (men and women), whose clients are now tagged as Self-Paced.",
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

# ---------- page ----------
GROUPS = ["A. Lead intake", "B. Booked call", "C. Cancel and no-show", "D. Nurture", "E. Closing and clients", "F. Onboarding"]
GROUP_BLURB = {
    "A. Lead intake": "What happens when someone fills in, or abandons, the assessment.",
    "B. Booked call": "What happens the moment a Relationship Reset Call is booked, up to the call itself.",
    "C. Cancel and no-show": "What happens when a booked call is cancelled or missed.",
    "D. Nurture": "The email sequences for leads who have not booked.",
    "E. Closing and clients": "What happens when a deal is closed and a lead becomes a client.",
    "F. Onboarding": "What the new client receives, and how the team is kept on top of their 90 days.",
}

css = """
:root{--cream:#F7F4EE;--card:#FFFFFF;--ink:#1E1B16;--muted:#6B6459;--terra:#A9502C;--terra-soft:#F3E3DA;--green:#1D4A33;--green-soft:#E4EEE7;--gold:#B98A2F;--line:#E4DDD2;--warn-bg:#FBEFE7;--warn:#8C3D14;}
*{box-sizing:border-box;margin:0;padding:0}
body{background:var(--cream);color:var(--ink);font-family:'Inter',system-ui,sans-serif;line-height:1.6;font-size:15.5px}
.wrap{max-width:960px;margin:0 auto;padding:0 20px 80px}
header.hero{background:var(--ink);color:#F7F4EE;padding:46px 20px 38px;text-align:center}
.hero .brand{font-family:'Playfair Display',serif;font-size:13px;letter-spacing:.18em;text-transform:uppercase;color:#CDB68A;margin-bottom:12px}
.hero h1{font-family:'Playfair Display',serif;font-size:clamp(28px,5vw,40px);font-weight:600;line-height:1.15;margin-bottom:10px}
.hero p{color:#BFB8AC;max-width:640px;margin:0 auto;font-size:15px}
section{margin-top:44px}
.kicker{color:var(--terra);font-weight:700;font-size:12px;letter-spacing:.14em;text-transform:uppercase;margin-bottom:6px}
h2{font-family:'Playfair Display',serif;font-size:clamp(22px,3.4vw,28px);font-weight:600;margin-bottom:8px}
h3{font-family:'Playfair Display',serif;font-size:21px;font-weight:600;line-height:1.25}
.lead{color:var(--muted);font-size:15px;margin-bottom:14px;max-width:760px}
.card{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:22px 24px;margin-top:14px}
.toc{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:10px;margin-top:14px}
.toc a{display:block;background:var(--card);border:1px solid var(--line);border-radius:12px;padding:12px 14px;text-decoration:none;color:var(--ink)}
.toc a:hover{border-color:var(--terra);background:var(--terra-soft)}
.toc a b{display:block;font-size:14.5px}.toc a span{font-size:12px;color:var(--muted);font-family:ui-monospace,monospace}
.lanes{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px;margin-top:14px}
.lane{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:14px 12px}
.lane .n{display:inline-flex;align-items:center;justify-content:center;width:26px;height:26px;border-radius:50%;background:var(--green);color:#fff;font-weight:700;font-size:12px;margin-bottom:8px}
.lane b{display:block;font-size:14px;margin-bottom:6px}
.lane li{font-size:12.5px;color:var(--muted);line-height:1.45;margin-left:14px}
.wfhead{display:flex;gap:14px;align-items:flex-start;padding-bottom:14px;border-bottom:1px solid var(--line);margin-bottom:14px}
.wfnum{flex:none;width:34px;height:34px;border-radius:50%;background:var(--green);color:#fff;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:14px}
.ghl{font-family:ui-monospace,monospace;font-size:12px;color:var(--muted);margin-top:3px}
.meta{font-size:14px;margin-bottom:6px}.meta b{color:var(--green)}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:18px;margin-top:14px}
@media(max-width:700px){.grid2{grid-template-columns:1fr}}
.lbl{font-size:11.5px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:var(--green);margin-bottom:6px}
.steps{list-style:none}.steps li{position:relative;padding-left:22px;margin-bottom:7px;font-size:14px}
.steps li::before{content:"";position:absolute;left:0;top:8px;width:10px;height:10px;border-radius:50%;background:var(--green)}
.chips span{display:inline-block;background:#F4F1EA;border:1px solid var(--line);border-radius:6px;padding:1px 7px;font-family:ui-monospace,monospace;font-size:12px;margin:0 6px 6px 0}
.team{background:var(--green-soft);border-left:4px solid var(--green);border-radius:0 10px 10px 0;padding:10px 14px;font-size:14px;margin-top:12px}
.team b{color:var(--green)}
.warnbox{background:var(--warn-bg);border-left:4px solid var(--terra);border-radius:0 10px 10px 0;padding:10px 14px;font-size:14px;color:var(--warn);margin-top:12px}
.warnbox b{color:var(--warn)}
code{background:#F4F1EA;border:1px solid var(--line);border-radius:6px;padding:1px 6px;font-family:ui-monospace,monospace;font-size:12.5px}
/* flowchart */
.flow{display:flex;flex-direction:column;align-items:stretch;margin-top:12px}
.node{position:relative;background:#FBF9F5;border:1.5px solid var(--line);border-radius:10px;padding:9px 13px;font-size:13.5px;margin:0 auto;width:min(100%,520px)}
.node b{display:block;font-size:13.5px}.node small{display:block;color:var(--muted);font-size:12px;line-height:1.4;margin-top:1px}
.node.trig{border-color:var(--terra);background:var(--terra-soft)}.node.trig b{color:var(--terra)}
.node.check{border-style:dashed;border-color:var(--gold)}
.node.wait{background:#F1EFEA;border-color:#D8D2C6;font-style:italic}
.node.hand{border-color:var(--green);background:var(--green-soft)}.node.hand b{color:var(--green)}
.node.end{background:var(--ink);color:#F7F4EE;border-color:var(--ink);width:min(100%,200px);text-align:center;font-weight:600;font-size:12.5px;padding:6px 12px}
.arrow{width:2px;height:16px;background:var(--line);margin:0 auto;position:relative}
.arrow::after{content:"";position:absolute;left:-4px;bottom:-1px;border-left:5px solid transparent;border-right:5px solid transparent;border-top:6px solid var(--line)}
.split{display:grid;gap:12px;width:100%;margin:0 auto}
.split .col{display:flex;flex-direction:column;align-items:stretch}
.split .tag{font-size:11px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;text-align:center;margin-bottom:5px}
.tag.y{color:var(--green)}.tag.n{color:var(--warn)}.tag.m{color:var(--gold)}
.split .node{width:100%}.split .node.end{width:min(100%,170px)}
@media(max-width:600px){.split{grid-template-columns:1fr !important}}
table{width:100%;border-collapse:collapse;font-size:13.5px;margin-top:10px}
th,td{text-align:left;padding:8px 9px;border-bottom:1px solid var(--line);vertical-align:top}
th{font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:var(--green)}
footer{margin-top:60px;padding-top:20px;border-top:1px solid var(--line);color:var(--muted);font-size:13px;display:flex;justify-content:space-between;flex-wrap:wrap;gap:8px}
.top{position:fixed;right:18px;bottom:22px;background:var(--ink);color:#F7F4EE;border:none;border-radius:999px;padding:10px 16px;font-size:13px;cursor:pointer;opacity:0;transition:.2s;font-family:inherit}
.top.show{opacity:.92}
"""

parts = []
parts.append(f"""<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><meta name="robots" content="noindex">
<title>Sales &amp; Client Automations SOP — Sophie Orozco Coaching</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@500;600&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>{css}</style></head><body>
<header class="hero"><div class="brand">Sophie Orozco Coaching</div><h1>Sales &amp; Client Automations SOP</h1>
<p>How each workflow in FG Funnels works, what starts it, what it sends, and where the team steps in. One page per workflow, with a flowchart.</p></header>
<div class="wrap">""")

# journey map
parts.append("""<section><div class="kicker">The Big Picture</div><h2>One lead, six stages</h2>
<p class="lead">Every automation below belongs to one of six moments in the journey. Read across to see which workflows fire at each one.</p>
<div class="lanes">
<div class="lane"><div class="n">1</div><b>Fills in the assessment</b><ul><li>Form Intake Router</li><li>Form Abandonment Recovery, email and text</li></ul></div>
<div class="lane"><div class="n">2</div><b>Books a call</b><ul><li>New Booking Handler</li><li>Pre-Call Email Sequence</li><li>Booked Call Text Sequence</li></ul></div>
<div class="lane"><div class="n">3</div><b>Cancels or misses it</b><ul><li>Stage Mover</li><li>Canceled Recovery, email and text</li><li>No-Show Recovery, email and text</li></ul></div>
<div class="lane"><div class="n">4</div><b>Does not book</b><ul><li>Soap Opera Sequence</li><li>Long Term Email Nurture</li><li>Nurture Exit - Client</li></ul></div>
<div class="lane"><div class="n">5</div><b>Becomes a client</b><ul><li>Closed Won Handoff</li><li>Client Owner Assignment</li><li>Closer Assignment Alert</li><li>Client Exit</li></ul></div>
<div class="lane"><div class="n">6</div><b>Gets onboarded</b><ul><li>Program Onboarding Emails</li><li>Client Journey Tracker</li><li>Client Check-in Alerts</li></ul></div>
</div>
<div class="team"><b>The one tag that matters most.</b> <code>existing client</code> is the switch. Adding it at close pulls the person out of every lead sequence, assigns them to Krissy, and starts the client check-ins. If it is missing, the sales emails keep going to a paying client.</div>
</section>""")

# contents
parts.append('<section><div class="kicker">Contents</div><h2>The workflows</h2><div class="toc">')
for i, w in enumerate(WF, 1):
    parts.append(f'<a href="#wf{i}"><b>{i}. {esc(w["name"])}</b><span>{esc(w["ghl"])}</span></a>')
parts.append('</div></section>')

# sections
n = 0
for g in GROUPS:
    parts.append(f'<section><div class="kicker">{esc(g)}</div><h2>{esc(g[3:])}</h2><p class="lead">{esc(GROUP_BLURB[g])}</p>')
    for w in [x for x in WF if x["group"] == g]:
        n += 1
        parts.append(f'<div class="card" id="wf{n}"><div class="wfhead"><div class="wfnum">{n}</div><div><h3>{esc(w["name"])}</h3><div class="ghl">GHL workflow: {esc(w["ghl"])}</div></div></div>')
        parts.append(f'<p class="meta"><b>What it does.</b> {esc(w["purpose"])}</p>')
        parts.append(f'<p class="meta"><b>Starts when.</b> {w["starts"]}</p>')
        parts.append('<div class="lbl" style="margin-top:12px">Flowchart</div><div class="flow">' + render_nodes(w["flow"]) + '</div>')
        if w.get("extra"): parts.append(w["extra"])
        parts.append('<div class="grid2"><div><div class="lbl">In plain English</div><ul class="steps">' + "".join(f'<li>{esc(s)}</li>' for s in w["steps"]) + '</ul></div>')
        parts.append('<div><div class="lbl">Tags and fields involved</div><div class="chips">' + ("".join(f'<span>{esc(t)}</span>' for t in w["tags"]) or '<span style="font-family:inherit;border:none;background:none;color:#6B6459">none</span>') + '</div></div></div>')
        if w["team"]: parts.append(f'<div class="team"><b>Where the team steps in.</b> {esc(w["team"])}</div>')
        if w["notes"]: parts.append(f'<div class="warnbox"><b>Known gap.</b> {esc(w["notes"])}</div>')
        parts.append('</div>')
    parts.append('</section>')

# glossary
parts.append("""<section><div class="kicker">Reference</div><h2>Tags the system runs on</h2><div class="card" style="padding-top:8px"><table><thead><tr><th>Tag</th><th>Meaning</th><th>Added by</th></tr></thead><tbody>
<tr><td><code>form - partial</code></td><td>Started the assessment, did not finish</td><td>Zapier</td></tr>
<tr><td><code>form - completed assessment</code></td><td>Finished the assessment</td><td>Zapier</td></tr>
<tr><td><code>calendly-appointment-booked</code></td><td>Has a booked Relationship Reset Call. Every recovery sequence checks for it.</td><td>New Booking Handler, Pre-Call Email Sequence</td></tr>
<tr><td><code>calendly-canceled-recovery</code> / <code>calendly-no-show-recovery</code></td><td>Currently inside a recovery sequence</td><td>Recovery workflows</td></tr>
<tr><td><code>calendly-recovery-completed</code></td><td>Finished a recovery sequence without rebooking</td><td>Recovery workflows</td></tr>
<tr><td><code>soap opera</code></td><td>Went through the five-day series</td><td>Soap Opera Sequence</td></tr>
<tr><td><code>long term nurture</code> / <code>nurture - completed</code></td><td>Entered, then finished, long-term nurture</td><td>Soap Opera Sequence, Long Term Email Nurture</td></tr>
<tr><td><code>existing client</code></td><td>The client switch. Stops all lead sequences, assigns Krissy, starts check-ins.</td><td>Closers at close, Closed Won Handoff</td></tr>
<tr><td><code>closed-won</code></td><td>Deal marked won; second trigger for the nurture exit</td><td>Closers</td></tr>
<tr><td><code>rmm- checkin (men)</code> / <code>(women)</code></td><td>Enrolls the client in the weekly check-in emails</td><td>Closed Won Handoff</td></tr>
<tr><td><code>team</code></td><td>Staff and coaches. Recovery sequences skip anyone with it.</td><td>Set once on every team record</td></tr>
</tbody></table></div></section>""")

parts.append("""<footer><span>Sales &amp; Client Automations SOP · Sophie Orozco Coaching</span><span>Prepared by John Carlo Caintic · from the workflow documentation of Sept 2026</span></footer>
</div><button class="top" id="top">↑ Top</button>
<script>const b=document.getElementById('top');b.addEventListener('click',()=>window.scrollTo({top:0,behavior:'smooth'}));window.addEventListener('scroll',()=>b.classList.toggle('show',window.scrollY>700));</script>
</body></html>""")

open(OUT, "w", encoding="utf-8").write("".join(parts))
print("wrote", OUT, len("".join(parts)), "bytes,", len(WF), "workflows")
