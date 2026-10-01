# -*- coding: utf-8 -*-
"""ManyChat -> Zapier -> GHL lead magnet + soap opera + long term nurture: detailed build guide PDF (v2)."""
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, ListFlowable, ListItem, PageBreak, KeepTogether, CondPageBreak,
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
OKFILL = colors.HexColor("#EAF5EE")
OK = colors.HexColor("#1D4A33")

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
S("OkNote", fontName="Helvetica", fontSize=9.5, textColor=OK, leading=14,
  leftIndent=8, backColor=OKFILL, borderPadding=6, spaceBefore=2, spaceAfter=8)
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
    while story and isinstance(story[-1], Paragraph) and story[-1].style.name in ("H1", "H2", "XBody"):
        group.insert(0, story.pop())
    story.append(KeepTogether(group))
    story.append(Spacer(1, 4))
def note(txt, warn=False):
    story.append(Paragraph(txt, styles["WarnNote" if warn else "XNote"]))
def verify(txt):
    story.append(Paragraph("<b>Verify before moving on:</b> " + txt, styles["OkNote"]))
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
GATE = C("existing client") + ", " + C("closed-won") + ", " + C("rmm current client")

# ================================================================== HEADER
story.append(Paragraph("FG Funnels  |  Lead Generation", styles["XSub"]))
story.append(Paragraph("ManyChat Lead Magnet &rarr; Soap Opera &rarr; Long Term Nurture", styles["TitleBig"]))
story.append(Paragraph("Detailed build guide for Daniel's Instagram opt-in automation: ManyChat collects the email, Zapier creates the GHL contact, "
                       "GHL sends the Communication Reset, runs the 5-day soap opera, then hands off to long term nurture. "
                       "Clients never enter either sequence and are pulled out the moment they buy.", styles["XSub"]))
story.append(Spacer(1, 4))
rule()

# ================================================================== OVERVIEW
para("How it fits together", "H1")
para("Six pieces. Two are new (the GHL lead magnet workflow and the Zap), two are edits to workflows Daniel already has "
     "(Soap Opera Sequence and Long Term Email Nurture), one is the exit workflow, and one is the ManyChat flow itself. "
     "The lead magnet is delivered twice on purpose: instantly inside the Instagram DM by ManyChat, and by email from GHL as Daniel specified, "
     "because the email is what opens the inbox relationship the soap opera and nurture run on.")
flow([
    "INSTAGRAM (ManyChat)            ZAPIER                    GHL / FG FUNNELS",
    "----------------------------    --------------------      ------------------------------------",
    "Comment / DM keyword",
    "  -> ask for email (validated)",
    "  -> DM: lead magnet link (Instagram)",
    "  -> tag: CR - Email Captured -> New Tagged User",
    "                                  -> Add/Update Contact -> contact created or updated (by email)",
    "                                                    tags: communication reset, lead-instagram",
    "                                                    source: ManyChat - Instagram",
    "                                                                    |",
    "                                                                    v",
    "                                                    WORKFLOW A  ManyChat > Communication Reset",
    "                                                      1. email copy of lead magnet (Daniel's spec)",
    "                                                      2. wait 1 day",
    "                                                      3. client check  --client--> END",
    "                                                      4. add tag: soap opera",
    "                                                                    |",
    "                                                                    v",
    "                                                    WORKFLOW B  Soap Opera Sequence (existing)",
    "                                                      client check --client--> END",
    "                                                      Chapter 1..5, one per day at 11 AM ET",
    "                                                      wait 1 day -> tag: soap opera completed",
    "                                                      client check --not client--> tag: long term nurture",
    "                                                                    |",
    "                                                                    v",
    "                                                    WORKFLOW C  Long Term Email Nurture (Daniel)",
    "                                                      client check -> Daniel's emails",
    "                                                      -> tag: nurture - completed",
    "",
    "ANY TIME the contact is tagged existing client / closed-won:",
    "                                                    WORKFLOW D  Nurture Exit - Client",
    "                                                      remove from A, B and C immediately",
])

para("Why tags drive every hand-off", "H2")
para("Every step passes the baton with a tag, the same pattern as the closer onboarding and the Zapier intake router. "
     "Any future opt-in source (a website form, a Facebook flow, a second lead magnet) plugs in by adding the same tag, "
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

# ================================================================== BEFORE YOU START
para("Before you start", "H1")
para("Access you need open in three tabs", "H2")
steps([
    "<b>FG Funnels</b>: the Sophie Orozco Coaching sub-account, admin role (you already have it).",
    "<b>Zapier</b>: the account that runs the Typeform zaps. It already holds a LeadConnector connection to this sub-account, and the new Zap reuses it.",
    "<b>ManyChat</b>: admin on Sophie's ManyChat account with the <b>Instagram channel connected</b>. The Zapier trigger only appears on the <b>Pro</b> plan. If the account is Free, upgrade first or hand Build F to Daniel.",
])
para("Four habits that prevent the usual mistakes", "H2")
steps([
    "In the GHL workflow builder every trigger and every action has its own <b>Save Trigger</b> / <b>Save Action</b> button at the bottom of the side panel. Click it before closing the panel, then click the top-right <b>Save</b>. Two saves, every time.",
    "Tags are always <b>selected from the dropdown</b>, never typed as new text inside a workflow. Typing creates a second tag with a stray space and nothing fires.",
    "The tag and field pickers cache. If a tag or field you just created is missing from a dropdown, hard-refresh the browser (Ctrl+Shift+R) and reopen the action.",
    "Build everything in <b>Draft</b>. The Publish toggle (top right, next to Test workflow) is flipped only in the go-live order in Part 6.",
    "In an If/Else, several tags inside one <b>Includes</b> box means <i>all of them</i>. To mean <i>any of them</i>, give each tag its own segment (<b>+ Add segment</b>) or switch the connector between rules from AND to OR.",
])

story.append(CondPageBreak(2.4*inch))

# ================================================================== PART 0
para("Part 0 &mdash; Foundations in GHL (15 min)", "H1")
para("A. Create the tag", "H2")
steps([
    "Left sidebar &rarr; <b>Settings</b> (bottom) &rarr; <b>Tags</b>.",
    "Click <b>+ Add Tag</b> (top right).",
    "Name: " + C("communication reset") + ". Click <b>Save</b>. GHL stores it lowercase whatever you type.",
    "In the same list confirm these five already exist by searching each name: " + C("lead-instagram") + ", " + C("soap opera") + ", " +
    C("soap opera completed") + ", " + C("long term nurture") + ", " + C("nurture - completed") + ". All five were present on Sept 12. Do not create duplicates.",
])
para("B. Create the custom field (recommended)", "H2")
steps([
    "<b>Settings</b> &rarr; <b>Custom Fields</b>.",
    "Click <b>+ Add Field</b> &rarr; choose type <b>Single Line</b> &rarr; <b>Next</b>.",
    "Field name: " + C("Instagram Username") + ". Object: <b>Contact</b>. Group/folder: <b>Contact</b> (not Opportunity).",
    "Click <b>Save</b>. The key GHL generates is " + C("contact.instagram_username") + ". Zapier maps the ManyChat username here so the team can find the DM thread from the contact card.",
])
para("C. Create the placeholder email (the email copy Daniel asked for)", "H2")
steps([
    "Left sidebar &rarr; <b>Marketing</b> &rarr; <b>Emails</b> &rarr; tab <b>Templates</b>.",
    "Click <b>+ New</b> &rarr; <b>Blank Template</b> (the drag-and-drop editor opens).",
    "Click the template name at the top left and rename it " + C("ManyChat > Communication Reset (placeholder)") + ".",
    "Subject line (top of the editor): " + C("Your Communication Reset is here, {{contact.first_name}}"),
    "Body: drag one <b>Text</b> block and one <b>Button</b> block. Text: two or three lines from Sophie thanking them for asking. Button label: <b>Get the Communication Reset</b>. Button link: " +
    C("https://sophieorozco.com/communication-reset") + " (placeholder until Daniel sends the real one).",
    "Click <b>Save</b> (top right). Close the editor. The template now appears in the Send Email action's dropdown in Build A.",
])
note("Daniel replaces the copy and the link inside this template before launch. Because Workflow A points at the template, not at the content, nothing in the workflow changes when he does.")
para("D. Check the dedupe setting (30 seconds, no changes expected)", "H2")
steps([
    "<b>Settings</b> &rarr; <b>Business Profile</b> &rarr; scroll to <b>Contact Deduplication Preferences</b>.",
    "<b>Allow Duplicate Contact</b> must be <b>OFF</b>, and <b>Email</b> must be ticked as a match field. Leave the page if it already reads this way.",
])
verify("Settings &rarr; Tags shows " + C("communication reset") + " once. Custom Fields shows Instagram Username under Contact. Marketing &rarr; Emails &rarr; Templates lists the placeholder.")

story.append(CondPageBreak(2.4*inch))

# ================================================================== BUILD A
para("Build A &mdash; Workflow: ManyChat > Communication Reset Lead Magnet (25 min)", "H1")
para("The only new GHL workflow. It sends the freebie to everyone who asks for it, then enrolls non-clients in the soap opera.")
para("A1. Create the workflow", "H2")
steps([
    "Left sidebar &rarr; <b>Automation</b> &rarr; tab <b>Workflows</b>.",
    "Click <b>+ Create Workflow</b> (top right) &rarr; <b>Start from Scratch</b>.",
    "Click the name <i>New Workflow</i> at the top and rename it " + C("ManyChat > Communication Reset Lead Magnet") + ". Press Enter.",
    "Optional: click the folder icon and file it next to the <b>Zapier &gt;</b> workflows so all inbound integrations sit together.",
])
para("A2. The trigger", "H2")
steps([
    "Click <b>Add New Trigger</b>.",
    "In the search box type <i>tag</i> &rarr; choose <b>Contact Tag</b>.",
    "Workflow Trigger Name: leave as <i>Contact Tag</i>.",
    "Click <b>Add filters</b> &rarr; choose <b>Tag added</b> &rarr; in the value box select " + C("communication reset") + " from the dropdown.",
    "Click <b>Save Trigger</b>. There is no second trigger on this workflow.",
])
para("A3. Action 1 &mdash; Send Email (the email copy of the lead magnet)", "H2")
note("Why an email when the chatbot is on Instagram: Daniel's spec reads \"add tag Communication Reset, send email with the lead magnet, enroll in soap opera email series.\" "
     "The lead already received the link in the DM (Build F, Step 3). This email is the first message of the email relationship and confirms the address works. Keep it.")
steps([
    "Click the <b>+</b> under the trigger &rarr; search <i>email</i> &rarr; choose <b>Send Email</b>.",
    "Action Name: " + C("Lead magnet email") + ".",
    "From Name: <b>Sophie Orozco</b>. From Email: the address the Soap Opera Sequence sends from (open that workflow's Chapter 1 action in another tab and copy it, so both land in the same inbox thread).",
    "Templates: choose " + C("ManyChat > Communication Reset (placeholder)") + ". The subject fills in from the template.",
    "Leave attachments empty; the button in the template delivers the file.",
    "Click <b>Save Action</b>.",
])
para("A4. Action 2 &mdash; Wait 1 day", "H2")
steps([
    "Click the <b>+</b> under Action 1 &rarr; search <i>wait</i> &rarr; choose <b>Wait</b>.",
    "Wait type: <b>Time Delay</b>. Wait for: <b>1</b> &rarr; unit <b>Days</b>.",
    "Leave the advanced window options off. Click <b>Save Action</b>.",
])
note("Why a day: the lead magnet gets a full day in the inbox before Chapter 1, the classic soap opera spacing. If Daniel prefers same-day, change this to 2 hours. It is the only number that changes.")
para("A5. Action 3 &mdash; If/Else client check", "H2")
steps([
    "Click the <b>+</b> under the Wait &rarr; search <i>if</i> &rarr; choose <b>If/Else</b>.",
    "Action Name: " + C("Client check") + ".",
    "Branch 1 name: " + C("Is client") + ".",
    "Under Branch 1 click <b>Add condition</b> &rarr; category <b>Contact Details</b> &rarr; field <b>Tags</b> &rarr; operator <b>Includes</b> &rarr; select " + C("existing client") + " only.",
    "Click <b>+ Add segment</b> (below the first rule) &rarr; Contact Details &rarr; Tags &rarr; Includes &rarr; " + C("closed-won") + ". Click <b>+ Add segment</b> again &rarr; Tags &rarr; Includes &rarr; " + C("rmm current client") + ". Segments are OR to each other, so any one of the three tags sends the contact down this branch.",
    "Do not put the three tags into one Includes box. GHL treats several tags in one Includes as <i>all required</i>, and no client carries all three, so the gate would never fire.",
    "Do not add a second branch. GHL adds the <b>None</b> branch by itself; that is the not-a-client path.",
    "Click <b>Save Action</b>. The canvas now shows two paths: <b>Is client</b> on the left and <b>None</b> on the right.",
])
para("A6. Action 4 &mdash; Add Contact Tag (under None only)", "H2")
steps([
    "Click the <b>+</b> under the <b>None</b> path &rarr; search <i>tag</i> &rarr; choose <b>Add Contact Tag</b>.",
    "Tags: select " + C("soap opera") + " from the dropdown. Click <b>Save Action</b>.",
    "Leave the <b>Is client</b> path empty. A client who asked for the freebie gets the freebie and nothing else.",
])
para("A7. Settings", "H2")
steps([
    "Click the <b>Settings</b> tab at the top of the builder.",
    "<b>Allow Re-Entry</b>: OFF. <b>Stop on Response</b>: OFF. <b>Allow Multiple Opportunities</b>: OFF.",
    "<b>Time Window</b>: leave unset. The lead magnet must go out at 2 AM if that is when they asked.",
    "Click <b>Save</b> (top right). Leave the toggle on <b>Draft</b>.",
])
verify("The canvas reads: Contact Tag trigger &rarr; Lead magnet email &rarr; Wait 1 day &rarr; Client check with Is client (empty) and None &rarr; Add Contact Tag soap opera &rarr; End. Settings show Re-Entry OFF.")
note("Why the gate sits after the wait, not at entry: if the lead buys during that first day, the check runs on the tags they have at the moment of enrollment, not the moment they opted in.")
note("Why " + C("existing client") + " is the source of truth: closers add it at every close per the SOP, WF-P1 adds it automatically on Closed Won, and Luann's 73 legacy clients carry it. "
     "Low-ticket buyers (" + C("bought err") + ", " + C("bought magnetic communication") + ") are deliberately not excluded. They are still leads for the programs, which is what the soap opera sells.")

story.append(CondPageBreak(2.4*inch))

# ================================================================== BUILD B
para("Build B &mdash; Edit: Soap Opera Sequence (30 min)", "H1")
para("Daniel's published workflow " + C("Soap Opera Sequence (5-day welcome/re-engagement email series)") +
     ". Do not open or edit the five chapter emails. Four structural edits make it evergreen and hand off to nurture. "
     "Because it is published, every change goes live on <b>Save</b>, so work carefully and in this order.")
para("B1. Read it before touching it (5 min)", "H2")
steps([
    "Automation &rarr; Workflows &rarr; open " + C("Soap Opera Sequence") + ". Click <b>Enrollment History</b> and confirm the last enrollments are dated Aug 17. Nobody is currently inside, so edits cannot strand anyone.",
    "Back on <b>Builder</b>, click the trigger card and write down what it is. Expected: <b>Contact Tag &rarr; Tag added = soap opera</b>. It may instead be empty (bulk-enrollment leftover) or a different tag.",
    "Click each <b>Wait</b> between chapters and confirm it reads <b>Time Delay, 1 Day</b>. The Aug batch timestamps (15:01, 15:08, 15:09, 15:11, 15:13 UTC across five days) say they are relative already. If any Wait is a fixed date, change it to Time Delay 1 Day.",
    "Click <b>Settings</b> &rarr; note the <b>Time Window</b>. Expected 11:00 AM to about 12:00 PM ET, which is why every chapter went at 11 AM. Leave it.",
])
para("B2. The trigger", "H2")
steps([
    "If the trigger is already Contact Tag = " + C("soap opera") + ": nothing to do.",
    "If not: click <b>Add New Trigger</b> &rarr; <b>Contact Tag</b> &rarr; Add filters &rarr; <b>Tag added</b> = " + C("soap opera") + " &rarr; <b>Save Trigger</b>.",
    "If an old trigger exists that Daniel no longer needs (for example a Form Submitted trigger), delete it with the trash icon on its card. Ask Daniel first if unsure; leaving it does no harm as long as B3 is in place.",
])
para("B3. Entry gate: insert the client check above Chapter 1", "H2")
steps([
    "Hover the line between the trigger and the first step (the Wait or Chapter 1) and click the <b>+</b> that appears there.",
    "Search <i>if</i> &rarr; <b>If/Else</b>. Action Name " + C("Client check") + ". Branch 1 name " + C("Is client") + ". Build the condition exactly as in A5: three separate segments, one tag each (" + GATE + "), joined by OR. <b>Save Action</b>.",
    "GHL automatically hangs everything that was below the insertion point under one of the two branches. Look at the canvas: the five chapters must sit under <b>None</b>, and <b>Is client</b> must be empty.",
    "If the chapters landed under <b>Is client</b> instead, click the If/Else, swap the branch condition to <b>Does not include</b> with the same three tags, and rename Branch 1 to " + C("Not a client") + ". Now the chapters are on the correct path and None (the client path) is empty. Same result, no rebuilding.",
    "Click <b>Save</b> (top right).",
])
para("B4. Hand-off at the end", "H2")
steps([
    "Scroll to the Chapter 5 email. Click the <b>+</b> under it &rarr; <b>Wait</b> &rarr; Time Delay, <b>1 Day</b> &rarr; Save Action.",
    "Click the <b>+</b> under that Wait &rarr; <b>Add Contact Tag</b> &rarr; select " + C("soap opera completed") + " &rarr; Save Action. Everyone who finishes gets this, client or not.",
    "Click the <b>+</b> under it &rarr; <b>If/Else</b> &rarr; Action Name " + C("Client check end") + ", Branch 1 " + C("Is client") + ", condition built as in A5: three segments, one tag each (" + GATE + "), OR between them &rarr; Save Action.",
    "Under the <b>None</b> path click <b>+</b> &rarr; <b>Add Contact Tag</b> &rarr; select " + C("long term nurture") + " &rarr; Save Action. This tag starts Workflow C.",
    "Leave <b>Is client</b> empty. Click <b>Save</b> (top right).",
])
para("B5. Settings", "H2")
steps([
    "<b>Settings</b> tab &rarr; <b>Allow Re-Entry</b> OFF &rarr; <b>Save</b>.",
    "The workflow is already Published. Your saves are live. Nothing enrolls until a " + C("soap opera") + " tag is added to someone, which only Workflow A does and only after its own gate.",
])
verify("Enrollment History still shows nobody new. The canvas reads: trigger &rarr; Client check &rarr; (None) Chapter 1 &hellip; Chapter 5 &rarr; Wait 1 day &rarr; tag soap opera completed &rarr; Client check end &rarr; (None) tag long term nurture.")
note("Known behaviour to tell Daniel: the 5,591 contacts from the Aug 17 batch already carry the " + C("soap opera") +
     " tag. If one of them opts in through Instagram, adding a tag they already have fires nothing, so they get the lead magnet and skip the chapters they already received. "
     "They will not reach long term nurture through this path. If Daniel wants that batch nurtured, it is a separate bulk action: "
     "add " + C("long term nurture") + " to the batch minus clients. Not part of this build.", warn=True)

story.append(CondPageBreak(2.4*inch))

# ================================================================== BUILD C
para("Build C &mdash; Edit: Long Term Email Nurture (10 min)", "H1")
para("Daniel's draft (v78, edited Sept 11). Daniel owns the emails and decides when it publishes. This build only sets the entry and the guard rails, and it is safe to do now because the workflow is in Draft.")
steps([
    "Automation &rarr; Workflows &rarr; open " + C("Long Term Email Nurture") + ".",
    "Click the trigger card. Required: <b>Contact Tag &rarr; Tag added = " + C("long term nurture") + "</b>. If it reads anything else, add that trigger (Add New Trigger &rarr; Contact Tag &rarr; Add filters &rarr; Tag added &rarr; select the tag &rarr; Save Trigger) and tell Daniel what you found.",
    "Hover the line between the trigger and the first email, click <b>+</b> &rarr; <b>If/Else</b> &rarr; Action Name " + C("Client check") + ", Branch 1 " + C("Is client") + ", condition built as in A5: three segments, one tag each (" + GATE + "), OR between them &rarr; Save Action.",
    "Confirm Daniel's emails hang under <b>None</b> and <b>Is client</b> is empty. If reversed, use the same swap trick as B3 step 4 (Does not include, rename branch).",
    "Scroll to the last email. Click <b>+</b> under it &rarr; <b>Add Contact Tag</b> &rarr; select " + C("nurture - completed") + " &rarr; Save Action.",
    "<b>Settings</b> tab &rarr; Allow Re-Entry OFF &rarr; <b>Save</b>. Leave on <b>Draft</b>. Daniel flips it to Publish when his copy is final.",
])
verify("Trigger card reads Contact Tag, long term nurture. First step is Client check. Last step adds nurture - completed. Still Draft.")

# ================================================================== BUILD D
para("Build D &mdash; Workflow: Nurture Exit - Client (15 min)", "H1")
para("The guarantee Daniel asked for. The moment anyone becomes a client they are pulled out of all three sequences, mid-chapter or mid-nurture. "
     "Daniel already started this as the draft " + C("Long Term Nurture - Exit") + " (v7). Finish that one rather than creating a second.")
para("D1. Open and rename", "H2")
steps([
    "Automation &rarr; Workflows &rarr; open " + C("Long Term Nurture - Exit") + ".",
    "Click the name at the top &rarr; rename to " + C("Nurture Exit - Client") + " &rarr; Enter.",
    "Look at what Daniel already put on the canvas. Keep anything that matches the steps below; delete (trash icon) anything else, for example a Remove From Workflow that points at a workflow not listed here.",
])
para("D2. Two triggers", "H2")
steps([
    "Trigger 1: click the trigger card (or <b>Add New Trigger</b>) &rarr; <b>Contact Tag</b> &rarr; Add filters &rarr; <b>Tag added</b> = " + C("existing client") + " &rarr; Save Trigger.",
    "Trigger 2: click <b>Add New Trigger</b> next to the first card &rarr; <b>Contact Tag</b> &rarr; Add filters &rarr; <b>Tag added</b> = " + C("closed-won") + " &rarr; Save Trigger.",
    "Both cards now feed the same first action. Either tag fires the exit.",
])
para("D3. Three removals", "H2")
steps([
    "Click <b>+</b> &rarr; search <i>remove</i> &rarr; <b>Remove From Workflow</b> &rarr; Workflow: select " + C("Soap Opera Sequence (5-day welcome/re-engagement email series)") + " &rarr; Save Action.",
    "Click <b>+</b> &rarr; <b>Remove From Workflow</b> &rarr; select " + C("ManyChat > Communication Reset Lead Magnet") + " &rarr; Save Action. If it is not in the dropdown, it is because Workflow A is still Draft; the dropdown lists published workflows only. Come back for this line right after Workflow A is published in Part 6.",
    "Click <b>+</b> &rarr; <b>Remove From Workflow</b> &rarr; select " + C("Long Term Email Nurture") + " &rarr; Save Action. Same rule: add this line once Daniel publishes Workflow C.",
])
para("D4. Settings and publish", "H2")
steps([
    "<b>Settings</b> tab &rarr; <b>Allow Re-Entry ON</b>. A contact can be tagged closed-won and then existing client minutes apart; both events should run the removals.",
    "<b>Save</b> &rarr; flip the toggle to <b>Publish</b> &rarr; Save again. This one goes live first (see go-live order); on its own it only removes people from sequences they should not be in.",
])
verify("Two trigger cards (existing client, closed-won) &rarr; Remove From Workflow x3 (or x1 today plus a reminder to add the other two after A and C publish). Published, Re-Entry ON.")
note("Do not use <b>Stop All Workflows</b> here (it exists both as a GHL action and as a Zapier action). It would also pull the client out of their onboarding, check-in, and continuation workflows. Three explicit removals only.", warn=True)

story.append(CondPageBreak(2.4*inch))

# ================================================================== BUILD E ZAPIER
para("Build E &mdash; Zapier: ManyChat &rarr; GHL (25 min)", "H1")
para("Two steps, one task per lead. Uses the same LeadConnector connection the Typeform zaps already use, so no new FG Funnels authorisation is needed. "
     "Build F (the ManyChat flow and its tag) must exist before step E2.4, because Zapier needs to see the tag in a dropdown.")
para("E1. Create the Zap", "H2")
steps([
    "zapier.com &rarr; left sidebar <b>Zaps</b> &rarr; <b>+ Create</b> &rarr; <b>Zaps</b>.",
    "Click the name <i>Untitled Zap</i> (top left) and rename it " + C("ManyChat -> GHL: Communication Reset") + ".",
])
para("E2. Trigger: ManyChat, New Tagged User", "H2")
steps([
    "Click the <b>Trigger</b> box &rarr; search <i>ManyChat</i> &rarr; select it.",
    "Trigger event: <b>New Tagged User</b> (instant). Click <b>Continue</b>.",
    "Account: <b>Sign in</b> &rarr; a ManyChat window opens &rarr; log in as an admin of Sophie's account &rarr; allow. Click <b>Continue</b>. If Zapier says the plan is not supported, the ManyChat account is not on Pro.",
    "Configure: <b>Tag</b> dropdown &rarr; select " + C("CR - Email Captured") + " (created in F1). Click <b>Continue</b>.",
    "Test: click <b>Test trigger</b>. Zapier looks for a subscriber who already has that tag. If it finds none, run the ManyChat flow once from your own Instagram (F5) so a real record exists, then click <b>Find new records</b> again.",
    "Select the sample record and click <b>Continue with selected record</b>.",
])
para("E3. Action: LeadConnector, Add/Update Contact", "H2")
steps([
    "Click the <b>Action</b> box &rarr; search <i>LeadConnector</i> &rarr; select it.",
    "Action event: <b>Add/Update Contact</b>. Click <b>Continue</b>.",
    "Account: choose the <b>existing</b> Sophie Orozco Coaching connection from the dropdown (the one the Typeform zaps use). Do not click Connect a new account. Click <b>Continue</b>.",
    "Map the fields exactly as the table below. Click into each box and pick the ManyChat value from the <i>Insert Data</i> list, or type the fixed text. Anything not listed stays empty.",
])
table(["LeadConnector field", "Value", "Notes"],
      [["Email", C("Email") + " (from ManyChat)", "Required. This is the dedupe key. Never send the Zap without it."],
       ["First Name", C("First Name") + " (from ManyChat)", ""],
       ["Last Name", C("Last Name") + " (from ManyChat)", "Often empty on Instagram. Fine."],
       ["Tags", C("communication reset, lead-instagram"), "Typed as plain text, comma separated. GHL adds both without removing existing tags."],
       ["Source", C("ManyChat - Instagram"), "Plain text. Shows on the contact card and in reporting."],
       ["Instagram Username (custom field)", C("Ig Username") + " (from ManyChat)", "The field from Part 0B. It appears in the mapping list only after the field exists in GHL. Skip if you skipped 0B."]],
      [1.7*inch, 2.2*inch, 2.6*inch])
steps([
    "Click <b>Continue</b> &rarr; <b>Test step</b>. Zapier sends the sample to GHL.",
    "In GHL search Contacts for the sample email. Confirm: contact exists, tags " + C("communication reset") + " and " + C("lead-instagram") + " are on it, Source reads ManyChat - Instagram, and Automation &rarr; " + C("ManyChat > Communication Reset Lead Magnet") + " &rarr; Enrollment History lists the contact (only once Workflow A is published; while Draft it will not enroll, which is fine for this test).",
    "Back in Zapier click <b>Publish</b>. The Zap is now on.",
], start=5)
note("Watch-out from Zapier's community: some users report Add/Update Contact creating duplicates. In every case Email was unmapped or GHL's duplicate setting was ON. "
     "Part 0D plus the Email mapping above prevents it. Test 4 in Part 6 proves it on this account.", warn=True)
note("No-Zapier alternative for later: ManyChat's External Request node can POST straight to a GHL <b>Inbound Webhook</b> trigger, and once FG Funnels "
     "unlocks the App Marketplace the native ManyChat integration replaces the Zap entirely. Either swap touches only the entry; Workflows A to D stay as built.")

story.append(CondPageBreak(2.4*inch))

# ================================================================== BUILD F MANYCHAT
para("Build F &mdash; ManyChat flow on the Instagram channel (25 min)", "H1")
para("Daniel or whoever runs ManyChat builds this. The whole flow lives on the <b>Instagram</b> channel: the trigger is an Instagram comment or DM, every message is an Instagram DM, "
     "and the person types their email address into that DM. ManyChat's email channel is not used anywhere. The only email in the entire build is the one GHL sends in Build A.")
note("Where the word Email appears below, it is the <b>reply type</b> on a User Input element. That setting tells ManyChat to check that the text typed into the Instagram DM looks like an "
     "email address and to store it in the subscriber's Email field. It does not switch the conversation to email.", warn=True)
para("F0. Confirm the Instagram channel is connected", "H2")
steps([
    "app.manychat.com &rarr; left sidebar <b>Settings</b> &rarr; <b>Instagram</b> (under Channels).",
    "It must show Sophie's handle with a green <b>Connected</b> status. If it shows Connect instead, click it and complete the Meta login. The Instagram account has to be a Business or Creator account linked to the Sophie Orozco Coaching Facebook Page, and DM access must be allowed in Instagram &rarr; Settings &rarr; Messages and story replies &rarr; Connected tools.",
    "Also under Settings &rarr; Instagram, confirm <b>Comment automation</b> permissions are on. Without them the comment trigger in F2 cannot fire.",
])
para("F1. Create the tag", "H2")
steps([
    "Settings &rarr; <b>Tags</b> &rarr; <b>+ New Tag</b> &rarr; name " + C("CR - Email Captured") + " &rarr; Create.",
])
para("F2. Create the automation and its Instagram trigger", "H2")
steps([
    "Left sidebar <b>Automation</b> &rarr; <b>+ New Automation</b> &rarr; <b>Start from scratch</b>. If ManyChat asks which channel the automation is for, choose <b>Instagram</b>.",
    "Click the name at the top left &rarr; rename to " + C("IG DM - Communication Reset") + ".",
    "Click <b>+ New Trigger</b> &rarr; pick the <b>Instagram</b> tab &rarr; <b>User comments on your Post or Reel</b>.",
    "Post: <b>Select specific post</b> &rarr; pick the Communication Reset post (Daniel chooses). Comment contains: <b>specific words</b> &rarr; type " + C("RESET") + " (Daniel chooses the word). Click <b>Continue</b>.",
    "Optional second trigger for people who DM instead of comment: <b>+ New Trigger</b> &rarr; <b>Instagram</b> tab &rarr; <b>User sends a message</b> &rarr; message contains " + C("RESET") + ". Both triggers point at the same first message.",
])
para("F3. The conversation, all Instagram DM blocks", "H2")
steps([
    "<b>Step 1, first DM</b>: click the <b>+</b> after the trigger &rarr; choose <b>Instagram</b> as the channel &rarr; <b>Send Message</b>. Type: <i>Hey {{first_name}}! The Communication Reset is yours. What is the best email to send it to?</i> Use the <b>{{ }}</b> button to insert First Name.",
    "<b>Step 2, capture the email inside the same Instagram block</b>: under the text, click <b>+ Add element</b> (or the + inside the block) &rarr; <b>User Input</b>. Reply type: <b>Email</b>. Save response to: the system field <b>Email</b>. Skip button: <b>OFF</b>. Retry message: <i>That did not look like an email, can you double check it?</i> Retries: 2.",
    "<b>Step 3, deliver the lead magnet in the DM</b>: drag from the User Input's <b>success</b> port &rarr; <b>Instagram</b> &rarr; <b>Send Message</b>. Text: <i>Here is your Communication Reset. I am also emailing you a copy so you can find it later.</i> Then <b>+ Add button</b> &rarr; type <b>Open URL</b> &rarr; label " + C("Open the Communication Reset") + " &rarr; URL " + C("https://sophieorozco.com/communication-reset") + " (same placeholder as Part 0C; Daniel swaps in the real link in both places).",
    "<b>Step 4, the tag that fires the Zap</b>: drag from Step 3 &rarr; <b>Actions</b> &rarr; <b>+ Add Action</b> &rarr; <b>Add Tag</b> &rarr; select " + C("CR - Email Captured") + ".",
    "<b>Failure path</b>: drag from the User Input's <b>retries exhausted</b> port &rarr; <b>Instagram</b> &rarr; <b>Send Message</b>: <i>No problem, DM me your email whenever you are ready and I will send it right over.</i> Connect nothing after it. No tag on this path, ever.",
    "Check every block on the canvas carries the Instagram icon. A block showing a Messenger, WhatsApp, SMS or Email icon is on the wrong channel: delete it and re-add it as Instagram.",
])
para("F4. Publish", "H2")
steps([
    "Click <b>Set Live</b> (top right). The automation is now listening on the post.",
])
para("F5. First live run on Instagram (also creates the sample Zapier needs)", "H2")
steps([
    "From a personal Instagram account, comment " + C("RESET") + " on the chosen post.",
    "Open the DM that arrives from Sophie's account and reply with a test email you control, e.g. " + C("johncaintic01+cr1@gmail.com") + ".",
    "In ManyChat &rarr; <b>Contacts</b> &rarr; open that subscriber &rarr; confirm the channel shows Instagram, the Email field is filled, and the tag " + C("CR - Email Captured") + " is on the record. This is the record Zapier picks up in E2.5.",
])
verify("Subscriber card shows Instagram as the channel, the email, and the tag. Every block on the canvas is an Instagram block. The failure path has no tag action anywhere on it.")
note("Alternative to the tag: the flow can use the <b>Trigger a Zap</b> action instead, with Zapier's <b>New \"Trigger a Zap\" Event</b> trigger. "
     "The tag version is the documented ManyChat and LeadConnector template, leaves a visible marker on the subscriber, and can be re-fired for testing by removing and re-applying the tag. Use the tag.")

story.append(CondPageBreak(2.4*inch))

# ================================================================== PART 6 TEST
para("Part 6 &mdash; Testing (45 min, before anything goes live to real leads)", "H1")
para("For tests 1 and 2 temporarily shorten the two 1-day waits (Build A step A4, Build B step B4.1) to <b>2 minutes</b>, save, then restore them in test 6. "
     "Workflow A must be Published for tests 1 to 5; that is why Build D is published first and Workflow A second.")
table(["#", "Test", "Do this", "Pass when"],
      [["1", "Happy path", "Comment the keyword from a personal IG account. Reply with a fresh test email, e.g. " + C("johncaintic01+cr2@gmail.com") + ".",
        "Within a minute the GHL contact exists with both tags and the source. Lead magnet email arrives. Two minutes later the contact carries " + C("soap opera") +
        " and Soap Opera Sequence &rarr; Enrollment History lists it. Chapter 1 lands at the next 11 AM ET."],
       ["2", "End-of-sequence hand-off", "On the test-1 contact, open Soap Opera Sequence &rarr; Enrollment History &rarr; the contact row &rarr; Execution Logs and watch it step through, or wait the five days.",
        "Contact gets " + C("soap opera completed") + " then " + C("long term nurture") + " and appears in Long Term Email Nurture &rarr; Enrollment History (once C is published)."],
       ["3", "Existing client asks for the freebie", "Open " + C("test test0002") + " (already tagged existing client) &rarr; Tags &rarr; add " + C("communication reset") + " manually.",
        "Lead magnet email is sent. After the wait, no " + C("soap opera") + " tag appears. Execution Logs show Client check took the Is client branch."],
       ["4", "Dedupe", "Run the ManyChat flow again (remove the tag from your subscriber first, then comment again) and enter the email of a contact that already exists in GHL.",
        "The existing record gains the tags. Searching that email in Contacts returns one card, not two."],
       ["5", "Mid-sequence exit", "While the test-1 contact is between chapters, open it &rarr; Tags &rarr; add " + C("existing client") + ".",
        "Nurture Exit - Client &rarr; Enrollment History shows it fired. Soap Opera Sequence &rarr; Enrollment History shows the contact as <b>Removed</b>. No further chapters arrive."],
       ["6", "Restore", "Set both waits back to 1 Day and save. On the test contacts remove " + C("soap opera") + ", " + C("communication reset") + ", " + C("existing client") + " (test-1 contact only).",
        "Both waits read 1 Day. Test contacts carry none of the flow tags."]],
      [0.3*inch, 1.2*inch, 2.5*inch, 2.5*inch])

para("Go-live order", "H2")
steps([
    "Publish Build D (Nurture Exit - Client). Harmless on its own and protects everything after it.",
    "Confirm Build B saves are in place (it is already published).",
    "Publish Workflow A. Go back to Build D and add the Remove From Workflow line for Workflow A (it is now in the dropdown).",
    "Publish the Zap (E3.7) if you have not already. Set the ManyChat automation Live (F4).",
    "Run Part 6.",
    "Build C goes live whenever Daniel finishes the nurture emails. When he publishes it, add its Remove From Workflow line to Build D. Contacts who finished the soap opera before that day hold the " + C("long term nurture") +
    " tag but were never enrolled; on launch day bulk-remove and re-add that tag on them (Contacts &rarr; filter by tag &rarr; select all &rarr; Bulk actions) so the trigger picks them up.",
])

# ================================================================== TIMELINE
para("What one lead experiences", "H1")
table(["When", "What happens", "Where"],
      [["Day 0, minute 0", "Comments RESET on Instagram, types their email into the DM, gets the lead magnet link back in the DM", "ManyChat, Instagram channel"],
       ["Day 0, minute 1", "Contact created, email copy of the Communication Reset arrives", "Zapier &rarr; Workflow A"],
       ["Day 1", "Tagged " + C("soap opera") + " (unless already a client)", "Workflow A"],
       ["Day 1 or 2, 11 AM ET", "Chapter 1 of 5: Before I tell you what happened", "Soap Opera Sequence"],
       ["Next 4 days, 11 AM ET", "Chapters 2 to 5, one per day", "Soap Opera Sequence"],
       ["Day after Chapter 5", "Tagged " + C("soap opera completed") + " and, if still not a client, " + C("long term nurture"), "Soap Opera Sequence"],
       ["From then on", "Daniel's long term nurture emails on his schedule", "Long Term Email Nurture"],
       ["Any moment they buy", "Tagged " + C("existing client") + " by the closer &rarr; removed from all three within seconds", "Nurture Exit - Client"]],
      [1.5*inch, 3.6*inch, 1.4*inch])

# ================================================================== DECISIONS
para("Decisions for Daniel (already answered in this build unless he objects)", "H1")
table(["Question", "Built as"],
      [["Wait between lead magnet and Chapter 1?", "1 day. Change Build A step A4 if he wants same-day."],
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
