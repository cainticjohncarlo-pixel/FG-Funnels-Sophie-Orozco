# -*- coding: utf-8 -*-
"""A1b Backfill (date-based) - step-by-step build guide PDF."""
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, ListFlowable, ListItem, KeepTogether, CondPageBreak,
)

OUT = sys.argv[1]
INK = colors.HexColor("#1A1A1A"); ACCENT = colors.HexColor("#1D4E89"); TEAL = colors.HexColor("#0E7C7B")
MUTED = colors.HexColor("#5F6B7A"); WARN = colors.HexColor("#9A3412"); RULE = colors.HexColor("#D5DAE0")
HEADFILL = colors.HexColor("#EAEFF4"); WARNFILL = colors.HexColor("#FDF3E7"); FLOWFILL = colors.HexColor("#F4F7FA")
OKFILL = colors.HexColor("#EAF5EE"); OK = colors.HexColor("#1D4A33")

styles = getSampleStyleSheet()
def S(name, **kw): styles.add(ParagraphStyle(name, **kw))
S("TitleBig", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=21, textColor=INK, spaceAfter=3, alignment=TA_LEFT, leading=25)
S("XSub", fontName="Helvetica", fontSize=11, textColor=MUTED, spaceAfter=2, leading=15)
S("H1", parent=styles["Heading1"], fontName="Helvetica-Bold", fontSize=13.5, textColor=ACCENT, spaceBefore=14, spaceAfter=5, leading=17, keepWithNext=1)
S("H2", parent=styles["Heading2"], fontName="Helvetica-Bold", fontSize=11.5, textColor=TEAL, spaceBefore=8, spaceAfter=2, leading=14, keepWithNext=1)
S("XBody", parent=styles["Normal"], fontName="Helvetica", fontSize=10, textColor=INK, spaceAfter=6, leading=15)
S("XStep", parent=styles["Normal"], fontName="Helvetica", fontSize=10, textColor=INK, leading=15, leftIndent=4)
S("XNote", fontName="Helvetica", fontSize=9.5, textColor=MUTED, leading=14, leftIndent=8, spaceAfter=8)
S("WarnNote", fontName="Helvetica", fontSize=9.5, textColor=WARN, leading=14, leftIndent=8, backColor=WARNFILL, borderPadding=6, spaceBefore=2, spaceAfter=8)
S("OkNote", fontName="Helvetica", fontSize=9.5, textColor=OK, leading=14, leftIndent=8, backColor=OKFILL, borderPadding=6, spaceBefore=2, spaceAfter=8)
S("Flow", fontName="Courier", fontSize=8.1, textColor=INK, leading=10.8, backColor=FLOWFILL, borderPadding=8, spaceBefore=4, spaceAfter=10)

story = []
def rule():
    story.append(Spacer(1, 4)); story.append(HRFlowable(width="100%", thickness=0.6, color=RULE)); story.append(Spacer(1, 4))
def para(txt, st="XBody"): story.append(Paragraph(txt, styles[st]))
def steps(items, start=1):
    lf = ListFlowable([ListItem(Paragraph(t, styles["XStep"]), value=start+i) for i, t in enumerate(items)],
                      bulletType="1", bulletFontName="Helvetica-Bold", bulletColor=ACCENT, leftIndent=18, bulletFontSize=10, start=start)
    group = [lf]
    while story and isinstance(story[-1], Paragraph) and story[-1].style.name in ("H1", "H2", "XBody"):
        group.insert(0, story.pop())
    story.append(KeepTogether(group)); story.append(Spacer(1, 4))
def note(txt, warn=False): story.append(Paragraph(txt, styles["WarnNote" if warn else "XNote"]))
def verify(txt): story.append(Paragraph("<b>Verify before moving on:</b> " + txt, styles["OkNote"]))
def table(header, rows, widths, keep=False):
    data = [[Paragraph(f"<b>{h}</b>", styles["XBody"]) for h in header]] + [[Paragraph(c, styles["XBody"]) for c in r] for r in rows]
    t = Table(data, colWidths=widths, repeatRows=1)
    t.setStyle(TableStyle([("BACKGROUND", (0,0), (-1,0), HEADFILL), ("GRID", (0,0), (-1,-1), 0.5, RULE), ("VALIGN", (0,0), (-1,-1), "TOP"),
                           ("LEFTPADDING", (0,0), (-1,-1), 6), ("RIGHTPADDING", (0,0), (-1,-1), 6), ("TOPPADDING", (0,0), (-1,-1), 5), ("BOTTOMPADDING", (0,0), (-1,-1), 5)]))
    if keep:
        group = [t]
        while story and isinstance(story[-1], Paragraph) and story[-1].style.name in ("H1", "H2", "XBody"):
            group.insert(0, story.pop())
        story.append(KeepTogether(group))
    else:
        story.append(t)
    story.append(Spacer(1, 8))
def flow(lines): story.append(KeepTogether(Paragraph("<br/>".join(l.replace(" ", "&nbsp;") for l in lines), styles["Flow"])))
C = lambda s: f"<font face='Courier'>{s}</font>"
def brk(): story.append(CondPageBreak(2.4*inch))

# ================================================================== HEADER
story.append(Paragraph("FG Funnels  |  Existing Client Touch Point Automation", styles["XSub"]))
story.append(Paragraph("A1b Backfill (date-based) &mdash; Build Guide", styles["TitleBig"]))
story.append(Paragraph("A copy of WORKFLOW 2 whose waits count from each client's program_start_date instead of from enrollment. "
                       "Used once to place 16 roster clients on the correct pipeline stage today, then left running so their remaining milestones fire on the real dates. "
                       "WORKFLOW 2 itself is not touched.", styles["XSub"]))
story.append(Spacer(1, 4)); rule()

para("Why a copy and not an edit", "H1")
para("WORKFLOW 2 has 73 contacts inside it right now: 28 waiting at the first 21-day step and 45 at the second. Its waits are relative "
     "(21 days after the previous step), which is correct for a client enrolled on their close day. It is wrong for a client enrolled weeks later, "
     "because the clock restarts at Onboarding. Changing the wait steps underneath 73 in-flight contacts is not worth the risk, so the copy carries the date-based waits and only the late clients go through it.")
flow([
    "WORKFLOW 2 (live, untouched)               A1b Backfill (date-based) - this build",
    "-------------------------------            ---------------------------------------",
    "12 program-tag triggers                    no triggers (bulk add only)",
    "program_start_date empty? -> END           program_start_date empty? -> END   (kept)",
    "Update contact field                       CHECK: delete if it writes luann@ csm_email",
    "Create/update opportunity                  same",
    "stage Onboarding                           same",
    "notify Day 0                               DELETED",
    "wait 21 days   -> stage Check-In 1         wait until start + 21 d  -> stage Check-In 1",
    "notify Week 3                              kept, sent to csm_email",
    "wait 21 days   -> stage Check-In 2         wait until start + 42 d  -> stage Check-In 2",
    "notify Week 6                              kept, sent to csm_email",
    "wait 21 days   -> stage Check-In 3         wait until start + 63 d  -> stage Check-In 3",
    "notify Week 9                              kept, sent to csm_email",
    "wait 6 days    -> stage Renewal Window     wait until start + 69 d  -> stage Renewal Window",
    "notify Expires in 3 weeks                  kept, sent to csm_email",
    "wait 21 days   -> stage Program Complete   wait until start + 90 d  -> stage Program Complete",
    "end date, tag client - completed,          same",
    "notify Program ends today                  kept, sent to csm_email",
    "",
    "A wait whose date is already past is skipped, so a late client runs",
    "straight to the stage that matches today and waits for the next real date.",
])

# ================================================================== PART 0
para("Part 0 &mdash; Who goes through it (as of Sept 12)", "H1")
para("Every existing-client contact that has a program_start_date and no card in the Existing Clients pipeline, meaning WORKFLOW 2 never processed them. "
     "Ten carry the tag already. Six roster clients have no " + C("existing client") + " tag yet and get it in Part 1. The test contact " + C("test test0001") + " also fits the filter; leave it out.")
table(["Client", "Start date", "Days in", "Stage the card should land on", "Tag status"],
      [["Oli Adams", "Aug 17", "26", "Check-In 1", "tagged"],
       ["Bjarni Freyr", "Aug 17", "26", "Check-In 1", "<b>needs tag</b>"],
       ["Doug Hungate", "Aug 20", "23", "Check-In 1", "tagged"],
       ["Amy Petrikova", "Aug 20", "23", "Check-In 1", "tagged"],
       ["Kirsty Huddart", "Aug 23", "20", "Onboarding (Check-In 1 on Sept 13)", "<b>needs tag</b>"],
       ["Maja Pavlica", "Aug 25", "18", "Onboarding", "tagged"],
       ["Jordan Taylor", "Aug 28", "15", "Onboarding", "tagged"],
       ["Ellen Folkers", "Aug 28", "15", "Onboarding", "<b>needs tag</b>"],
       ["Ryan Garcia", "Aug 31", "12", "Onboarding", "tagged"],
       ["Jed Padilla", "Aug 31", "12", "Onboarding", "<b>needs tag</b>"],
       ["Zamira Jaffer", "Sept 3", "9", "Onboarding", "<b>needs tag</b>"],
       ["Ashley McCarthy", "Sept 5", "7", "Onboarding", "tagged"],
       ["Shawna Fesler", "Sept 7", "5", "Onboarding", "tagged"],
       ["Rebecca Piks", "Sept 7", "5", "Onboarding", "tagged"],
       ["Javier Alcover", "Sept 9", "3", "Onboarding", "tagged"],
       ["Brandon Martin", "Sept 10", "2", "Onboarding", "<b>needs tag</b>"]],
      [1.5*inch, 0.85*inch, 0.65*inch, 2.4*inch, 1.1*inch])
note("Kathleen Weber, Sarah Matts and Rob Deutsch had their start dates corrected today but already have cards and are inside WORKFLOW 2 on its relative clock. Leave them; they are not part of this backfill.")

brk()
# ================================================================== PART 1
para("Part 1 &mdash; Tag the six untagged clients (5 min)", "H1")
steps([
    "Contacts &rarr; search each name: Bjarni Freyr, Kirsty Huddart, Ellen Folkers, Jed Padilla, Zamira Jaffer, Brandon Martin.",
    "Open the record &rarr; <b>Tags</b> box on the left &rarr; type " + C("existing client") + " &rarr; pick it from the dropdown (do not create a new one) &rarr; click away to save.",
    "The tag fires <b>Client Owner Assignment (Krissy)</b>: owner becomes Krissy and " + C("csm_email") + " is set. It also fires Nurture Exit - Client once that is published, which is harmless. Nothing else listens to that tag.",
])
verify("Each of the six shows the tag, Assigned To Krissy Thomas, and csm_email krissy@sophieorozco.com. If you would rather I add the six tags through the API, say so; it is one command.")

# ================================================================== PART 2
para("Part 2 &mdash; Duplicate WORKFLOW 2 (3 min)", "H1")
steps([
    "Automation &rarr; Workflows &rarr; open the folder <b>Existing Client Touch Point Automation</b>.",
    "On the row <b>WORKFLOW 2 &mdash; A1b Client Journey &mdash; 90 Day</b> click the three-dot menu at the far right &rarr; <b>Duplicate</b> (labelled Clone in some builds). Confirm.",
    "GHL creates <i>WORKFLOW 2 &mdash; A1b Client Journey &mdash; 90 Day (copy)</i> in Draft. Open it.",
    "Click the name at the top &rarr; rename to " + C("A1b Backfill (date-based)") + " &rarr; Enter.",
])
verify("The copy shows Draft in the top right and the folder now lists both workflows. WORKFLOW 2 still says Published.")

# ================================================================== PART 3
para("Part 3 &mdash; Remove all twelve triggers (5 min)", "H1")
para("The copy must never enroll anyone on its own. If a trigger stayed, the next close would enter both workflows and get two cards.")
steps([
    "In the copy, click the first <b>Contact Tag</b> trigger card &rarr; click its trash icon &rarr; confirm.",
    "Repeat for all twelve. Work left to right so you do not lose count. The dashed <b>Add new trigger</b> placeholder stays; that is normal.",
    "Click <b>Save</b> (top right). GHL allows a workflow with no trigger; it can only be entered by bulk add or manual add, which is exactly what we want.",
])
verify("The top row of the canvas shows only the Add new trigger placeholder.")

brk()
# ================================================================== PART 4
para("Part 4 &mdash; Check the first Update Contact Field step (2 min)", "H1")
steps([
    "Click the <b>Update contact field</b> card that sits right under the None branch, before Create or update opportunity.",
    "Read which field it writes. If it is " + C("csm_email") + " with Luann's address, click the trash icon and delete it from the copy. Krissy's workflow owns that field now.",
    "If it writes anything else (for example a program status), leave it.",
    "Leave <b>Create or update opportunity</b> and <b>Onboarding</b> as they are. Backfilled clients have no card yet; this is what creates it.",
])
note("If that step did write luann@ into csm_email, it is also the reason Darren Wang and Nick Sincerbox got Luann on Sept 10. Delete the same step in WORKFLOW 2 afterwards (Part 9).", warn=True)

# ================================================================== PART 5
para("Part 5 &mdash; Convert the five waits to date-based (10 min)", "H1")
para("Right now each wait counts 21 days from the previous step. After this change each wait counts from the client's start date instead, "
     "so the numbers must grow: 21, 42, 63, 69 and 90. That is how many days after the start date each stage begins. Do the five cards in order down the canvas.")
def waitblock(title, name, days):
    para(title, "H2")
    steps([
        "Click the card. A panel opens on the right.",
        "In the <b>Action Name</b> box at the top, delete the text and type " + C(name) + ".",
        "Find the dropdown labelled <b>Wait For</b>. It says <i>Time Delay</i>. Click it and choose <b>Event / Appointment Time</b>.",
        "A new dropdown appears for the event. Click it. You will see appointment options and, below them, your date fields. Choose " + C("program_start_date") +
        ". If you only see a <b>Custom Field</b> option, click that first, then choose " + C("program_start_date") + ".",
        "Find the <b>Before / After</b> selector. Set it to <b>After</b>.",
        "In the number box type <b>" + days + "</b>. In the unit dropdown choose <b>Days</b>.",
        "If the panel shows a time-of-day box, set it to <b>9:00 AM</b>. If there is no such box, skip this.",
        "Click <b>Save Action</b> at the bottom of the panel. The card on the canvas now shows the new name.",
    ])
waitblock("Wait 1: the first After 21 Days card, directly below Day 0 (new client assigned)", "Wait until start + 21 days", "21")
waitblock("Wait 2: the After 21 Days card directly below Check-in due (Week 3)", "Wait until start + 42 days", "42")
waitblock("Wait 3: the After 21 Days card directly below Check-in due (Week 6)", "Wait until start + 63 days", "63")
waitblock("Wait 4: the After 6 Days card directly below Check-in due (Week 9)", "Wait until start + 69 days", "69")
waitblock("Wait 5: the After 21 Days card directly below Expires in 3 weeks", "Wait until start + 90 days", "90")
para("Finish Part 5", "H2")
steps([
    "Click <b>Save</b> in the top right corner of the builder.",
    "Read down the canvas. You should see five wait cards named 21, 42, 63, 69, 90 in that order from top to bottom. If any card still says After 21 Days or After 6 Days, you missed one. Go back to it.",
    "Do not click the Publish toggle yet. That comes in Part 7.",
])

brk()
# ================================================================== PART 6
para("Part 6 &mdash; Point every alert at Krissy, delete only Day 0 (8 min)", "H1")
para("The copy has six internal notifications: Day 0 (new client assigned), Check-in due (Week 3), (Week 6), (Week 9), Expires in 3 weeks, and Program ends today. "
     "Krissy must receive them, so they stay. The recipient on each one is what decides whether she does; it is set at the top of the notification panel, above the message text. "
     "Use the csm_email field as the recipient: it reads krissy@sophieorozco.com on all 160 existing clients today and the Client Owner Assignment workflow fills it for every new one, "
     "so if the CSM ever changes you change one value, not six workflows.")
para("A. Delete Day 0 only", "H2")
steps([
    "Click <b>Day 0 (new client assigned)</b> &rarr; trash icon &rarr; confirm. For a client who started weeks ago, a new-client alert today is wrong.",
])
para("B. Set the recipient on each of the remaining five", "H2")
steps([
    "Click <b>Check-in due (Week 3)</b>. Scroll to the <b>top</b> of the panel, above Templates and Message.",
    "<b>Type</b> (or Notification Type): keep <b>Email</b>.",
    "<b>Send To</b>: choose <b>Custom Email</b>.",
    "In the email box click the tag icon (custom values) &rarr; Contact &rarr; " + C("csm_email") + ". The box should now show " + C("{{contact.csm_email}}") + ". Delete any typed address that was there before, for example luann@sophieorozco.com.",
    "Optional but useful: change <b>Type</b> to add an <b>In-app notification</b> as well, Send To <b>User</b> &rarr; Krissy Thomas, so it also pops up inside FG Funnels.",
    "Leave the subject and message as they are. Click <b>Save Action</b>.",
    "Repeat steps 1 to 6 for <b>Check-in due (Week 6)</b>, <b>Check-in due (Week 9)</b>, <b>Expires in 3 weeks</b> and <b>Program ends today</b>.",
    "Click <b>Save</b> (top right).",
])
note("What to expect at enrollment: the four clients already past day 21 (Oli Adams, Bjarni Freyr, Doug Hungate, Amy Petrikova) trigger their Week 3 alert the moment they are added, so Krissy receives four emails within a minute. That is accurate; they are due a check-in. Everyone else alerts on their real dates.")
verify("Open any of the five notifications: Send To reads Custom Email with {{contact.csm_email}}. The canvas reads: condition &rarr; Create or update opportunity &rarr; Onboarding &rarr; wait &rarr; Check-In 1 &rarr; Check-in due (Week 3) &rarr; wait &rarr; Check-In 2 &rarr; Check-in due (Week 6) &rarr; wait &rarr; Check-In 3 &rarr; Check-in due (Week 9) &rarr; wait &rarr; Renewal Window &rarr; Expires in 3 weeks &rarr; wait &rarr; Program Complete &rarr; Update contact field &rarr; Add Tag client - completed &rarr; Program ends today &rarr; END.")

# ================================================================== PART 7
para("Part 7 &mdash; Settings and publish (2 min)", "H1")
steps([
    "<b>Settings</b> tab &rarr; <b>Allow Re-Entry</b> OFF &rarr; <b>Allow Multiple Opportunities</b> OFF &rarr; Time Window none.",
    "<b>Save</b> &rarr; flip the toggle to <b>Publish</b> &rarr; Save again.",
    "Nothing happens yet. With no trigger, the workflow sits idle until Part 8.",
])

brk()
# ================================================================== PART 8
para("Part 8 &mdash; Enroll the 16 (10 min)", "H1")
para("Selecting 16 names by hand inside a 154-row list invites a mis-click. Use a throwaway tag so the filter does the selecting.")
para("A. Mark the 16", "H2")
steps([
    "Settings &rarr; Tags &rarr; + Add Tag &rarr; " + C("backfill - a1b") + " &rarr; Save. No workflow listens to it.",
    "Contacts &rarr; open each of the 16 in the Part 0 table &rarr; add the tag " + C("backfill - a1b") + ". (Or say the word and I apply it to exactly those 16 through the API in one pass.)",
])
para("B. Bulk add", "H2")
steps([
    "Contacts &rarr; <b>Filters</b> &rarr; Tags &rarr; Includes &rarr; " + C("backfill - a1b") + " &rarr; Apply. The count must read <b>16</b>. If it reads more, a wrong contact carries the tag; fix before continuing.",
    "Tick the header checkbox &rarr; <b>Select all 16</b>.",
    "In the action bar above the list click <b>Add to Workflow</b> (the workflow icon).",
    "Workflow: " + C("A1b Backfill (date-based)") + ". Mode: <b>Add all at once</b>. Name the action " + C("A1b backfill Sept 12") + ". Click <b>Add</b>.",
    "Bulk Actions (left menu) &rarr; open the action &rarr; wait for 16 processed, 0 errors.",
])
para("C. Clean up", "H2")
steps([
    "Contacts &rarr; same filter &rarr; Select all &rarr; Bulk Actions &rarr; <b>Remove Tag</b> &rarr; " + C("backfill - a1b") + ". Optional; the tag is harmless either way.",
])

# ================================================================== PART 9
para("Part 9 &mdash; Verify (5 min)", "H1")
steps([
    "Opportunities &rarr; pipeline <b>Existing Clients</b>. Find the 16 cards. Each must sit on the stage from the Part 0 table. Oli Adams, Bjarni Freyr, Doug Hungate and Amy Petrikova on Check-In 1; everyone else on Onboarding.",
    "Open the copy &rarr; <b>Enrollment History</b> &rarr; 16 rows, all Active.",
    "Click Oli Adams' row &rarr; <b>Execution Logs</b>. Expect: the first wait shows <i>Skipped</i> (date in the past), Check-In 1 executed, and the contact is now waiting at the second wait with a release date of Sept 28 (Aug 17 + 42 days).",
    "Click Javier Alcover's row: waiting at the first wait with a release date of Sept 30 (Sept 9 + 21 days).",
])
verify("Sixteen cards on the right stages, sixteen Active enrollments, release dates that equal start date plus 42 or 21 days.")

# ================================================================== PART 10
para("Part 10 &mdash; Three fixes back in WORKFLOW 2 (10 min)", "H1")
steps([
    "If Part 4 found a step writing luann@ into csm_email, open WORKFLOW 2 and delete that same step. It is the source of Luann overwriting Krissy on new closes. Deleting an Update Contact Field step does not affect contacts already waiting further down.",
    "Open each of the six notifications in WORKFLOW 2 (Day 0, Week 3, Week 6, Week 9, Expires in 3 weeks, Program ends today) and set Send To exactly as in Part 6B: Custom Email &rarr; {{contact.csm_email}}. This is why Krissy has not been receiving the 45 Week 3 alerts that already fired; they went to whoever was set there before. Editing a notification step does not disturb the contacts waiting further down.",
    "The first condition sends anyone with an empty program_start_date to END, which is how a client can vanish from tracking when the closer's tag lands a moment before WF-P1 stamps the date. The reliable fix is in <b>WF-P1 Closed Won Handoff</b>: make sure its Update Contact Field for program_start_date sits <i>above</i> the step that adds the program tag, so the date always exists first.",
])
note("From here on: new closes keep flowing through WORKFLOW 2 on close day. Any client who has to be added late, for any reason, goes through the backfill copy instead. Never bulk-add into WORKFLOW 2.", warn=True)

story.append(Spacer(1, 6)); rule()
para("Prepared by John Carlo Caintic &middot; Sept 12, 2026 &middot; Backfill list computed from the live account the same day: existing-client contacts with a program_start_date and no Existing Clients card.", "XNote")

doc = SimpleDocTemplate(OUT, pagesize=letter, leftMargin=0.8*inch, rightMargin=0.8*inch, topMargin=0.7*inch, bottomMargin=0.7*inch,
                        title="A1b Backfill Build Guide", author="John Carlo Caintic")
doc.build(story)
print("wrote", OUT)
