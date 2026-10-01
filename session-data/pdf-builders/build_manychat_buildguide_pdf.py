# -*- coding: utf-8 -*-
"""ManyChat -> Zapier -> GHL lead magnet + soap opera + long term nurture: build guide PDF."""
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, ListFlowable, ListItem, PageBreak, KeepTogether,
)

OUT = sys.argv[1]

INK = colors.HexColor("#1A1A1A")
ACCENT = colors.HexColor("#1D4E89")
TEAL = colors.HexColor("#0E7C7B")
MUTED = colors.HexColor("#5F6B7A")
WARN = colors.HexColor("#9A3412")
RULE = colors.HexColor("#D5DAE0")
HEADFILL = colors.HexColor("#EAEFF4")
WARNFILL = colors.HexColor("#FDF3E7")
FLOWFILL = colors.HexColor("#F4F7FA")

styles = getSampleStyleSheet()
def S(name, **kw): styles.add(ParagraphStyle(name, **kw))

S("TitleBig", parent=styles["Title"], fontName="Helvetica-Bold",
  fontSize=21, textColor=INK, spaceAfter=3, alignment=TA_LEFT, leading=25)
S("XSub", fontName="Helvetica", fontSize=11, textColor=MUTED, spaceAfter=2, leading=15)
S("H1", parent=styles["Heading1"], fontName="Helvetica-Bold", fontSize=13.5,
  textColor=ACCENT, spaceBefore=14, spaceAfter=5, leading=17, keepWithNext=1)
S("H2", parent=styles["Heading2"], fontName="Helvetica-Bold", fontSize=11.5,
  textColor=TEAL, spaceBefore=8, spaceAfter=2, leading=14, keepWithNext=1)
S("XBody", parent=styles["Normal"], fontName="Helvetica", fontSize=10,
  textColor=INK, spaceAfter=6, leading=15)
S("XStep", parent=styles["Normal"], fontName="Helvetica", fontSize=10,
  textColor=INK, leading=15, leftIndent=4)
S("XNote", fontName="Helvetica", fontSize=9.5, textColor=MUTED, leading=14,
  leftIndent=8, spaceAfter=8)
S("WarnNote", fontName="Helvetica", fontSize=9.5, textColor=WARN, leading=14,
  leftIndent=8, backColor=WARNFILL, borderPadding=6, spaceBefore=2, spaceAfter=8)
S("Flow", fontName="Courier", fontSize=8.1, textColor=INK, leading=10.8,
  backColor=FLOWFILL, borderPadding=8, spaceBefore=4, spaceAfter=10)

story = []
def rule():
    story.append(Spacer(1, 4)); story.append(HRFlowable(width="100%", thickness=0.6, color=RULE)); story.append(Spacer(1, 4))
def para(txt, st="XBody"): story.append(Paragraph(txt, styles[st]))
def steps(items, start=1):
    lf = ListFlowable(
        [ListItem(Paragraph(t, styles["XStep"]), value=start+i) for i, t in enumerate(items)],
        bulletType="1", bulletFontName="Helvetica-Bold", bulletColor=ACCENT,
        leftIndent=18, bulletFontSize=10, start=start)
    group = [lf]
    # pull the heading (and its intro paragraph) into the same block so a heading never strands at a page foot
    while story and isinstance(story[-1], Paragraph) and story[-1].style.name in ("H1", "H2", "XBody"):
        group.insert(0, story.pop())
    story.append(KeepTogether(group))
    story.append(Spacer(1, 4))
def note(txt, warn=False):
    story.append(Paragraph(txt, styles["WarnNote" if warn else "XNote"]))
def table(header, rows, widths):
    data = [[Paragraph(f"<b>{h}</b>", styles["XBody"]) for h in header]]
    for r in rows:
        data.append([Paragraph(c, styles["XBody"]) for c in r])
    t = Table(data, colWidths=widths, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), HEADFILL),
        ("GRID", (0,0), (-1,-1), 0.5, RULE),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("LEFTPADDING", (0,0), (-1,-1), 6), ("RIGHTPADDING", (0,0), (-1,-1), 6),
        ("TOPPADDING", (0,0), (-1,-1), 5), ("BOTTOMPADDING", (0,0), (-1,-1), 5),
    ]))
    story.append(t); story.append(Spacer(1, 8))
def flow(lines):
    story.append(KeepTogether(Paragraph("<br/>".join(l.replace(" ", "&nbsp;") for l in lines), styles["Flow"])))

C = lambda s: f"<font face='Courier'>{s}</font>"

# ------------------------------------------------------------------ header
story.append(Paragraph("FG Funnels  |  Lead Generation", styles["XSub"]))
story.append(Paragraph("ManyChat Lead Magnet &rarr; Soap Opera &rarr; Long Term Nurture", styles["TitleBig"]))
story.append(Paragraph("Build guide for Daniel's Instagram opt-in automation: ManyChat collects the email, Zapier creates the GHL contact, "
                       "GHL sends the Communication Reset, runs the 5-day soap opera, then hands off to long term nurture. "
                       "Clients never enter either sequence and are pulled out the moment they buy.", styles["XSub"]))
story.append(Spacer(1, 4))
rule()

# ------------------------------------------------------------------ overview
para("How it fits together", "H1")
para("Six pieces. Two are new (the GHL lead magnet workflow and the Zap), two are edits to workflows Daniel already has "
     "(Soap Opera Sequence and Long Term Email Nurture), one is the exit workflow, and one is the ManyChat flow itself.")
flow([
    "INSTAGRAM (ManyChat)            ZAPIER                    GHL / FG FUNNELS",
    "----------------------------    --------------------      ------------------------------------",
    "Comment / DM keyword",
    "  -> ask for email (validated)",
    "  -> tag: CR - Email Captured -> New Tagged User",
    "                                  -> Add/Update Contact -> contact created or updated (by email)",
    "                                                    tags: communication reset, lead-instagram",
    "                                                    source: ManyChat - Instagram",
    "                                                                    |",
    "                                                                    v",
    "                                                    WORKFLOW A  ManyChat > Communication Reset",
    "                                                      1. send lead magnet email (placeholder)",
    "                                                      2. wait 1 day",
    "                                                      3. client check  --yes--> END",
    "                                                      4. add tag: soap opera",
    "                                                                    |",
    "                                                                    v",
    "                                                    WORKFLOW B  Soap Opera Sequence (existing)",
    "                                                      client check --yes--> END",
    "                                                      Chapter 1..5, one per day at 11 AM ET",
    "                                                      wait 1 day -> tag: soap opera completed",
    "                                                      client check --no--> tag: long term nurture",
    "                                                                    |",
    "                                                                    v",
    "                                                    WORKFLOW C  Long Term Email Nurture (Daniel)",
    "                                                      client check -> Daniel's emails",
    "                                                      -> tag: nurture - completed",
    "",
    "ANY TIME the contact is tagged existing client / closed-won:",
    "                                                    WORKFLOW D  Client Exit",
    "                                                      remove from A, B and C immediately",
])

para("Why tags drive every hand-off", "H2")
para("Every step passes the baton with a tag, the same pattern as the closer onboarding and the Zapier intake router. "
     "It means any future opt-in source (a website form, a Facebook flow, a second lead magnet) plugs in by adding the same tag, "
     "and the enrollment history shows exactly why a contact entered each sequence.")

table(["Tag", "Status", "Applied by", "Meaning"],
      [[C("communication reset"), "<b>create</b>", "Zapier", "Requested the Communication Reset. Starts Workflow A. Daniel's chosen name; GHL stores tags lowercase."],
       [C("lead-instagram"), "exists (0 contacts)", "Zapier", "Source marker. Lets Daniel report on IG leads and lets future flows filter on origin."],
       [C("soap opera"), "exists (5,591)", "Workflow A", "Enrolls the contact in the Soap Opera Sequence."],
       [C("soap opera completed"), "exists (0)", "Workflow B", "Reached the end of the 5 chapters, bought or not."],
       [C("long term nurture"), "exists (4 test)", "Workflow B", "Finished the soap opera without buying. Starts Workflow C."],
       [C("nurture - completed"), "exists (1 test)", "Workflow C", "Reached the end of long term nurture."],
       [C("existing client") + " / " + C("closed-won"), "exist", "Closers, WF-P1", "The client marker. Blocks entry to B and C, and fires the exit (D)."]],
      [1.55*inch, 1.0*inch, 0.95*inch, 3.0*inch])

note("What the recon showed: the Soap Opera Sequence ran as a one-time batch on Aug 17 to 21. Every one of the 5,591 tagged contacts "
     "received Chapter 1 at the same minute, including a contact who had just paid. New form leads since then get no chapters. "
     "Builds B and D below turn it into an evergreen per-contact sequence with a purchaser exit, which is what Daniel is asking for.", warn=True)


# ------------------------------------------------------------------ PART 0
para("Part 0 &mdash; Foundations in GHL (15 min)", "H1")
para("A. The tag", "H2")
steps([
    "Settings &rarr; <b>Tags</b> &rarr; <b>+ Add Tag</b> &rarr; " + C("communication reset") + " &rarr; Save",
    "Confirm these already exist (they do as of Sept 12): " + C("lead-instagram") + ", " + C("soap opera") + ", " +
    C("soap opera completed") + ", " + C("long term nurture") + ", " + C("nurture - completed"),
])
para("B. The custom field (recommended)", "H2")
steps([
    "Settings &rarr; <b>Custom Fields</b> &rarr; folder <b>Contact</b> &rarr; <b>+ Add Field</b> &rarr; type <b>Single Line</b> &rarr; name " + C("Instagram Username") + " &rarr; Save",
    "Zapier will write the ManyChat " + C("ig_username") + " here so the team can match a DM conversation to the contact record.",
])
para("C. The placeholder email", "H2")
steps([
    "Marketing &rarr; <b>Emails</b> &rarr; <b>Templates</b> &rarr; <b>+ New</b> &rarr; blank &rarr; name " + C("ManyChat > Communication Reset (placeholder)"),
    "Subject: " + C("Your Communication Reset is here, {{contact.first_name}}"),
    "Body: 2 to 3 lines from Sophie plus one button labelled <b>Get the Communication Reset</b> pointing to " + C("https://sophieorozco.com/communication-reset") +
    " (placeholder). Daniel replaces the copy and link before launch; the workflow does not change.",
    "Save. Use the same From name and address as the Soap Opera Sequence so the inbox thread looks consistent.",
])
para("D. Dedupe setting (check only)", "H2")
steps([
    "Settings &rarr; <b>Business Profile</b> &rarr; <b>Contact Deduplication Preferences</b> &rarr; confirm <b>Allow Duplicate Contact</b> is OFF and the match is by <b>Email</b>.",
    "This is what makes Zapier's Add/Update Contact update an existing lead (or an existing client) instead of creating a second card.",
])

# ------------------------------------------------------------------ BUILD A
para("Build A &mdash; Workflow: ManyChat > Communication Reset Lead Magnet (20 min)", "H1")
para("This is the only new GHL workflow. It sends the freebie to everyone who asks for it, then enrolls non-clients in the soap opera.")
steps([
    "Automation &rarr; <b>Create Workflow</b> &rarr; Start from scratch &rarr; name " + C("ManyChat > Communication Reset Lead Magnet"),
    "<b>Trigger</b>: Contact Tag &rarr; filter <b>Tag added</b> = " + C("communication reset") + ". No second trigger.",
    "<b>Action 1 &mdash; Send Email</b>: template " + C("ManyChat > Communication Reset (placeholder)") + ". From: Sophie's usual sending address.",
    "<b>Action 2 &mdash; Wait</b>: 1 day. Gives the lead magnet a full day in the inbox before Chapter 1. Adjust later if Daniel prefers same-day.",
    "<b>Action 3 &mdash; If/Else</b> named " + C("Client check") + ": Contact Details &rarr; Tags &rarr; <b>Includes</b> (any of) " +
    C("existing client") + ", " + C("closed-won") + ", " + C("rmm current client") + ".",
    "<b>Yes branch</b>: nothing. It ends. A client who asked for the freebie gets the freebie and no sales sequence.",
    "<b>No branch &mdash; Action 4 &mdash; Add Contact Tag</b>: " + C("soap opera") + ". That single tag enrolls them in Build B.",
    "<b>Settings</b>: Allow Re-Entry OFF. Time window: none (the lead magnet should land immediately, day or night).",
    "Save &rarr; keep in <b>Draft</b> until the test in Part 6 passes.",
])
note("Why the gate sits after the wait, not at entry: if the lead buys during that first day, the check runs on the tags they have "
     "at the moment of enrollment, not the moment they opted in.")
note("Why " + C("existing client") + " is the source of truth: closers add it at every close per the SOP, WF-P1 adds it automatically on "
     "Closed Won, and Luann's 73 legacy clients carry it. Low-ticket buyers (" + C("bought err") + ", " + C("bought magnetic communication") +
     ") are deliberately not excluded. They are still leads for the programs, which is what the soap opera sells.")

story.append(PageBreak())

# ------------------------------------------------------------------ BUILD B
para("Build B &mdash; Edit: Soap Opera Sequence (25 min)", "H1")
para("Daniel's published workflow " + C("Soap Opera Sequence (5-day welcome/re-engagement email series)") +
     ". Do not touch the five chapter emails. Four structural edits make it evergreen and hand off to nurture.")
para("B1. Entry", "H2")
steps([
    "Open the workflow &rarr; click the trigger card. Required: <b>Contact Tag</b> &rarr; Tag added = " + C("soap opera") + ".",
    "If the trigger is anything else (a bulk-enrollment leftover, a different tag), add the Contact Tag trigger and leave the old one only if Daniel still needs it.",
    "First action after the trigger: <b>If/Else</b> " + C("Client check") + " with the same three tags as Build A. Yes branch: nothing (ends). Everything else moves under the No branch.",
])
para("B2. Cadence (check only)", "H2")
steps([
    "Between chapters the delays must be <b>Wait 1 day</b> (relative), not a fixed date. The Aug batch timestamps (15:01, 15:08, 15:09, 15:11, 15:13 UTC across five days) say this is already relative.",
    "Workflow Settings &rarr; confirm the send window is <b>11:00 AM ET</b> (the batch went out at 11 AM ET each day). Chapter 1 will land at the next 11 AM after enrollment.",
])
para("B3. Hand-off at the end", "H2")
steps([
    "After the Chapter 5 email add <b>Wait</b>: 1 day.",
    "<b>Add Contact Tag</b>: " + C("soap opera completed") + ".",
    "<b>If/Else</b> " + C("Client check") + " (same three tags).",
    "<b>No branch &mdash; Add Contact Tag</b>: " + C("long term nurture") + ". Yes branch: nothing.",
    "End.",
])
para("B4. Settings", "H2")
steps([
    "Allow Re-Entry: <b>OFF</b>.",
    "Save &rarr; Publish. Existing contacts are unaffected: the Aug batch already exited, and nothing enrolls until a " + C("soap opera") + " tag is added.",
])
note("Known behaviour to tell Daniel: the 5,591 contacts from the Aug 17 batch already carry the " + C("soap opera") +
     " tag. If one of them opts in through Instagram, adding a tag they already have fires nothing, so they get the lead magnet and skip straight past the chapters "
     "they already received. They will not reach long term nurture through this path. If Daniel wants that batch nurtured, it is a separate bulk action: "
     "add " + C("long term nurture") + " to the batch minus clients. Not part of this build.", warn=True)

# ------------------------------------------------------------------ BUILD C
para("Build C &mdash; Edit: Long Term Email Nurture (10 min)", "H1")
para("Daniel's draft (v78, edited Sept 11). Daniel owns the emails. This build only sets the entry and the guard rails.")
steps([
    "Open " + C("Long Term Email Nurture") + " &rarr; trigger must be <b>Contact Tag</b> &rarr; Tag added = " + C("long term nurture") + ". No other trigger.",
    "First action: <b>If/Else</b> " + C("Client check") + " (same three tags). Yes branch: nothing. Daniel's emails sit under No.",
    "Last action after the final email: <b>Add Contact Tag</b> " + C("nurture - completed") + ".",
    "Settings: Allow Re-Entry OFF. Leave in Draft until Daniel finishes the copy, then Publish.",
])

# ------------------------------------------------------------------ BUILD D
para("Build D &mdash; Workflow: Client Exit (15 min)", "H1")
para("The guarantee Daniel asked for. The moment anyone becomes a client they are pulled out of all three sequences, mid-chapter or mid-nurture. "
     "Daniel already started this as the draft " + C("Long Term Nurture - Exit") + " (v7). Finish that one rather than creating a second.")
steps([
    "Open " + C("Long Term Nurture - Exit") + " &rarr; rename to " + C("Nurture Exit - Client") + " so its scope is obvious.",
    "<b>Trigger 1</b>: Contact Tag &rarr; Tag added = " + C("existing client") + ".",
    "<b>Trigger 2</b>: Contact Tag &rarr; Tag added = " + C("closed-won") + ".",
    "<b>Action 1 &mdash; Remove From Workflow</b>: " + C("Soap Opera Sequence (5-day welcome/re-engagement email series)"),
    "<b>Action 2 &mdash; Remove From Workflow</b>: " + C("Long Term Email Nurture"),
    "<b>Action 3 &mdash; Remove From Workflow</b>: " + C("ManyChat > Communication Reset Lead Magnet"),
    "Settings: Allow Re-Entry <b>ON</b> (each trigger event should run it). Save &rarr; Publish.",
])
note("Do not use the Zapier action or GHL action <b>Stop All Workflows</b> here. It would also remove the client from their onboarding, "
     "check-in, and continuation workflows. Three explicit removals only.", warn=True)

story.append(PageBreak())

# ------------------------------------------------------------------ BUILD E ZAPIER
para("Build E &mdash; Zapier: ManyChat &rarr; GHL (20 min)", "H1")
para("Two steps, one task per lead. Uses the same LeadConnector connection the Typeform zaps already use, so no new FG Funnels authorisation is needed.")
para("E1. Trigger", "H2")
steps([
    "Zapier &rarr; <b>Create Zap</b> &rarr; name " + C("ManyChat -> GHL: Communication Reset"),
    "Trigger app <b>ManyChat</b> &rarr; event <b>New Tagged User</b> (instant).",
    "Connect the ManyChat account (Pro plan required). Sign in when prompted.",
    "Tag: " + C("CR - Email Captured") + " (created in Build F). If it is not in the dropdown yet, build F first, then come back.",
    "Test trigger: apply the tag to a test subscriber in ManyChat (your own IG account after running the flow once). Zapier pulls the sample.",
])
para("E2. Action", "H2")
steps([
    "Action app <b>LeadConnector</b> &rarr; event <b>Add/Update Contact</b> &rarr; account: the existing Sophie Orozco Coaching connection.",
    "Map the fields exactly as below. Anything not listed stays empty.",
])
table(["LeadConnector field", "Value from ManyChat", "Notes"],
      [["Email", C("Email"), "Required. This is the dedupe key. Never send the Zap without it."],
       ["First Name", C("First Name"), ""],
       ["Last Name", C("Last Name"), "Often empty on Instagram. Fine."],
       ["Tags", C("communication reset, lead-instagram"), "Typed as plain text, comma separated. GHL adds both without removing existing tags."],
       ["Source", C("ManyChat - Instagram"), "Plain text. Shows on the contact card and in reporting."],
       ["Instagram Username (custom)", C("Ig Username"), "The custom field from Part 0B. Skip if the field was not created."]],
      [1.7*inch, 2.2*inch, 2.6*inch])
steps([
    "Test action &rarr; open the contact in GHL &rarr; confirm the two tags, the source, and that Workflow A shows the contact in its Enrollment History.",
    "Publish the Zap.",
], start=3)
note("Watch-out from Zapier's community: some users report Add/Update Contact creating duplicates. In every case Email was unmapped or GHL's duplicate setting was ON. "
     "Part 0D plus the Email mapping above prevents it. Test 4 in Part 6 proves it on this account.", warn=True)
note("No-Zapier alternative for later: ManyChat's External Request node can POST straight to a GHL <b>Inbound Webhook</b> trigger, and once FG Funnels "
     "unlocks the App Marketplace the native ManyChat integration replaces the Zap entirely. Either swap touches only the entry; Workflows A to D stay as built.")

# ------------------------------------------------------------------ BUILD F MANYCHAT
para("Build F &mdash; ManyChat flow: IG DM &rarr; email capture (20 min)", "H1")
para("Daniel or whoever runs ManyChat builds this. Everything downstream depends on one rule: the tag is applied only after a valid email is captured.")
steps([
    "ManyChat &rarr; Settings &rarr; <b>Tags</b> &rarr; create " + C("CR - Email Captured") + ".",
    "Automation &rarr; <b>New Automation</b> &rarr; name " + C("IG DM - Communication Reset") + ".",
    "<b>Trigger</b>: Instagram &rarr; <b>User comments on your Post or Reel</b> &rarr; select the post &rarr; keyword " + C("RESET") +
    " (Daniel picks the word and the post). Optional second trigger: <b>User sends a message</b> with the same keyword, so a direct DM works too.",
    "<b>Step 1 &mdash; Send Message</b>: a short DM from Sophie. Example: <i>Hey {{first_name}}! The Communication Reset is yours. What is the best email to send it to?</i>",
    "<b>Step 2 &mdash; User Input</b>: reply type <b>Email</b>. Save response to the system field <b>Email</b>. Retry message: <i>That did not look like an email, can you double check it?</i> Limit 2 retries.",
    "<b>Step 3 &mdash; Send Message</b>: <i>Sent! Check your inbox in the next couple of minutes (and the Promotions tab if it hides).</i>",
    "<b>Step 4 &mdash; Action</b>: Add Tag &rarr; " + C("CR - Email Captured") + ". This is the line that fires the Zap.",
    "Wire Step 4 only off the success path of Step 2. The retry-exhausted path goes to a message like <i>No problem, DM me your email whenever you are ready</i> and nothing else.",
    "Set the automation to <b>Active</b>. Comment on the post from a personal account to run the first live test.",
])
note("Alternative to the tag: the flow can use the <b>Trigger a Zap</b> action instead, with Zapier's <b>New \"Trigger a Zap\" Event</b> trigger. "
     "The tag version is the documented ManyChat and LeadConnector template, leaves a visible marker on the subscriber, and can be re-fired for testing by re-applying the tag. Use the tag.")

story.append(PageBreak())

# ------------------------------------------------------------------ PART 6 TEST
para("Part 6 &mdash; Testing (30 min, before anything goes live)", "H1")
para("Run these in order. For tests 1 and 2 shorten the two 1-day waits (Build A action 2, Build B step B3) to 2 minutes, then restore them.")
table(["#", "Test", "Do this", "Pass when"],
      [["1", "Happy path", "Comment the keyword from a personal IG account. Reply with a fresh test email, e.g. " + C("johncaintic01+cr1@gmail.com") + ".",
        "GHL contact appears with both tags and the source. Lead magnet email arrives. After the short wait the contact carries " + C("soap opera") +
        " and shows in the Soap Opera Sequence enrollment history. Chapter 1 lands at the next 11 AM ET."],
       ["2", "End-of-sequence hand-off", "On the test contact from test 1, use the Soap Opera's <b>Test workflow</b> or wait out the chapters.",
        "Contact gets " + C("soap opera completed") + " then " + C("long term nurture") + " and appears in Long Term Email Nurture enrollment history."],
       ["3", "Existing client asks for the freebie", "Add " + C("communication reset") + " manually to " + C("test test0002") + " (already tagged existing client).",
        "Lead magnet email is sent. No " + C("soap opera") + " tag is added. Enrollment history shows the If/Else took the Yes branch."],
       ["4", "Dedupe", "Run the ManyChat flow again using the email of a contact that already exists in GHL.",
        "The existing record gains the tags. Contact count for that email stays at one."],
       ["5", "Mid-sequence exit", "While the test-1 contact is between chapters, add " + C("existing client") + " to it.",
        "Nurture Exit - Client fires. Soap Opera enrollment history shows the contact <b>Removed</b>. No further chapters arrive."],
       ["6", "Restore", "Set both waits back to 1 day. Remove the test tags from the test contacts.", "Waits read 1 day. Test contacts carry no " + C("soap opera") + " tag."]],
      [0.3*inch, 1.2*inch, 2.5*inch, 2.5*inch])

para("Go-live order", "H2")
steps([
    "Publish Build D (exit) first. It is harmless on its own and protects everything after it.",
    "Publish Build B (soap opera edits).",
    "Publish Build A, then the Zap, then set the ManyChat automation to Active.",
    "Build C goes live whenever Daniel finishes the nurture emails. Until then, contacts who finish the soap opera simply hold the " + C("long term nurture") +
    " tag; the trigger picks them up when it is published only if they are tagged after publishing. If Daniel wants the early finishers included, bulk-remove and re-add the tag on launch day.",
])

# ------------------------------------------------------------------ timeline
para("What one lead experiences", "H1")
table(["When", "What happens", "Where"],
      [["Day 0, minute 0", "Comments RESET, gives email in DM", "ManyChat"],
       ["Day 0, minute 1", "Contact created, Communication Reset email arrives", "Zapier &rarr; Workflow A"],
       ["Day 1", "Tagged " + C("soap opera") + " (unless already a client)", "Workflow A"],
       ["Day 1 or 2, 11 AM ET", "Chapter 1 of 5: Before I tell you what happened", "Soap Opera Sequence"],
       ["Next 4 days, 11 AM ET", "Chapters 2 to 5, one per day", "Soap Opera Sequence"],
       ["Day after Chapter 5", "Tagged " + C("soap opera completed") + " and, if still not a client, " + C("long term nurture"), "Soap Opera Sequence"],
       ["From then on", "Daniel's long term nurture emails on his schedule", "Long Term Email Nurture"],
       ["Any moment they buy", "Tagged " + C("existing client") + " by the closer &rarr; removed from all three within seconds", "Nurture Exit - Client"]],
      [1.5*inch, 3.6*inch, 1.4*inch])

# ------------------------------------------------------------------ decisions
para("Decisions for Daniel (already answered in this build unless he objects)", "H1")
table(["Question", "Built as"],
      [["Wait between lead magnet and Chapter 1?", "1 day. Change Build A action 2 if he wants same-day."],
       ["Do low-ticket buyers (bought err, bought magnetic communication) still get nurtured?", "Yes. Only " + C("existing client") + " / " + C("closed-won") + " / " + C("rmm current client") + " are excluded."],
       ["Should the Aug 17 batch of 5,591 be moved into long term nurture?", "Not in this build. Separate bulk action if he wants it."],
       ["Trigger word and post?", "Placeholder " + C("RESET") + ". His call."],
       ["Lead magnet email copy and link?", "Placeholder template in Part 0C. He replaces copy and link; nothing else changes."]],
      [3.4*inch, 3.1*inch])

story.append(Spacer(1, 6))
rule()
para("Prepared by John Carlo Caintic &middot; Sept 12, 2026 &middot; Sources: ManyChat on Zapier (New Tagged User trigger, Pro plan), "
     "LeadConnector on Zapier (Add/Update Contact), live account recon on Sept 12.", "XNote")

doc = SimpleDocTemplate(OUT, pagesize=letter, leftMargin=0.8*inch, rightMargin=0.8*inch,
                        topMargin=0.7*inch, bottomMargin=0.7*inch,
                        title="ManyChat Lead Magnet Build Guide", author="John Carlo Caintic")
doc.build(story)
print("wrote", OUT)
