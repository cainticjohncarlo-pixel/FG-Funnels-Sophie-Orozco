# -*- coding: utf-8 -*-
"""Continuation Tracker - completion updates (links from Chris's 9.11.26 doc)."""
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable,
                                ListFlowable, ListItem, KeepTogether, CondPageBreak)

OUT = sys.argv[1]
INK = colors.HexColor("#1A1A1A"); ACCENT = colors.HexColor("#1D4E89"); TEAL = colors.HexColor("#0E7C7B")
MUTED = colors.HexColor("#5F6B7A"); RULE = colors.HexColor("#D5DAE0"); HEADFILL = colors.HexColor("#EAEFF4")
OKFILL = colors.HexColor("#EAF5EE"); OK = colors.HexColor("#1D4A33")
WARNFILL = colors.HexColor("#FDF3E7"); WARN = colors.HexColor("#9A3412")

styles = getSampleStyleSheet()
def S(name, **kw): styles.add(ParagraphStyle(name, **kw))
S("TitleBig", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=20, textColor=INK, spaceAfter=3, alignment=TA_LEFT, leading=24)
S("XSub", fontName="Helvetica", fontSize=10.5, textColor=MUTED, spaceAfter=2, leading=14.5)
S("H1", parent=styles["Heading1"], fontName="Helvetica-Bold", fontSize=13, textColor=ACCENT, spaceBefore=15, spaceAfter=4, leading=16, keepWithNext=1)
S("H2", parent=styles["Heading2"], fontName="Helvetica-Bold", fontSize=11, textColor=TEAL, spaceBefore=9, spaceAfter=2, leading=13.5, keepWithNext=1)
S("XBody", parent=styles["Normal"], fontName="Helvetica", fontSize=10, textColor=INK, spaceAfter=6, leading=14.5)
S("XStep", parent=styles["Normal"], fontName="Helvetica", fontSize=10, textColor=INK, leading=14.5, leftIndent=4)
S("Cell", parent=styles["Normal"], fontName="Helvetica", fontSize=9.3, textColor=INK, leading=12.5)
S("CellMono", fontName="Courier", fontSize=8.6, textColor=INK, leading=11.5)
S("OkNote", fontName="Helvetica", fontSize=9.5, textColor=OK, leading=13.5, leftIndent=8, backColor=OKFILL, borderPadding=6, spaceBefore=3, spaceAfter=9)
S("WarnNote", fontName="Helvetica", fontSize=9.5, textColor=WARN, leading=13.5, leftIndent=8, backColor=WARNFILL, borderPadding=6, spaceBefore=3, spaceAfter=9)

story = []
def para(t, st="XBody"): story.append(Paragraph(t, styles[st]))
def rule():
    story.append(Spacer(1, 3)); story.append(HRFlowable(width="100%", thickness=0.6, color=RULE)); story.append(Spacer(1, 3))
def steps(items, start=1):
    lf = ListFlowable([ListItem(Paragraph(t, styles["XStep"]), value=start+i) for i, t in enumerate(items)],
                      bulletType="1", bulletFontName="Helvetica-Bold", bulletColor=ACCENT, leftIndent=18, bulletFontSize=10, start=start)
    group = [lf]
    while story and isinstance(story[-1], Paragraph) and story[-1].style.name in ("H1", "H2", "XBody"): group.insert(0, story.pop())
    story.append(KeepTogether(group)); story.append(Spacer(1, 4))
def note(t, warn=False): story.append(Paragraph(t, styles["WarnNote" if warn else "OkNote"]))
def table(header, rows, widths, mono_cols=()):
    data = [[Paragraph(f"<b>{h}</b>", styles["Cell"]) for h in header]]
    for r in rows:
        data.append([Paragraph(c, styles["CellMono"] if i in mono_cols else styles["Cell"]) for i, c in enumerate(r)])
    t = Table(data, colWidths=widths, repeatRows=1)
    t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),HEADFILL),("GRID",(0,0),(-1,-1),0.5,RULE),("VALIGN",(0,0),(-1,-1),"TOP"),
                           ("LEFTPADDING",(0,0),(-1,-1),5),("RIGHTPADDING",(0,0),(-1,-1),5),("TOPPADDING",(0,0),(-1,-1),4),("BOTTOMPADDING",(0,0),(-1,-1),4)]))
    group = [t]
    while story and isinstance(story[-1], Paragraph) and story[-1].style.name in ("H1", "H2", "XBody"): group.insert(0, story.pop())
    story.append(KeepTogether(group)); story.append(Spacer(1, 8))
C = lambda s: f"<font face='Courier' size='9'>{s}</font>"

# ---------------------------------------------------------------- header
story.append(Paragraph("Sophie Orozco Coaching  |  FG Funnels  |  Internal", styles["XSub"]))
story.append(Paragraph("Continuation Tracker &mdash; Completion Updates", styles["TitleBig"]))
story.append(Paragraph("The remaining changes to take the continuation tracker from draft to live, using the backend payment links Chris "
                       "posted on Sept 11, 2026. Prepared by John Carlo Caintic, Sept 23, 2026.", styles["XSub"]))
story.append(Spacer(1, 4)); rule()

para("Where it stands", "H1")
table(["Piece", "State"], [
    ["Pipeline Continuation Programs, 6 stages", "Built"],
    ["The 11 tags (graduated, outreach sent, continuation-engaged, declined-all, 7 enrolled tags)", "All present"],
    ["7 Enroll trigger links", "Exist, but every one points at a placeholder address"],
    ["WF-CT1 Graduation Entry, WF-CT2 Engagement, WF-CT3 Enrolled, WF-CT4 Declined", "Built, in draft"],
    ["WF-K2b, WF-K2d, WF-K2f outreach emails", "In draft, still need the five offers and the buttons"],
], [3.9*inch, 2.6*inch])
para("Three things remain: the trigger links, the outreach emails, and publishing in the right order. Everything else is done.")

# ---------------------------------------------------------------- 1
para("Update 1 &mdash; Point the trigger links at the real checkouts", "H1")
para("RFB and Forge share one checkout per term, which is why Chris combined them. Use the <b>Standard</b> link for every button: "
     "it carries pay in full, split pay, PayPal and buy now pay later on one page.")
para("Every destination starts with " + C("https://sophieorozco.thrivecart.com/") + " followed by the path in the table.")
table(["Trigger link", "Price", "Path after the base address"], [
    ["Enroll-RFB-6mo and Enroll-Forge-6mo", "$4,997", "rfb-forge-6-months-standard-link/"],
    ["Enroll-RFB-1yr and Enroll-Forge-1yr", "$8,500", "rfb-forge-1year-standardlink/"],
    ["Enroll-RMMPlus", "$2,997", "rmm-continuation-plus-coaching-2997-standard-link/"],
    ["Enroll-ContinueRMM-6mo", "$2,000", "2000-rmm-continuation-standard-link/"],
    ["Enroll-ContinueRMM-3mo", "$1,500", "1500-rmm-continuation-3-months-standard-link/"],
], [1.85*inch, 0.6*inch, 4.05*inch], mono_cols=(2,))
steps([
    "Marketing, then <b>Trigger Links</b>.",
    "Open each Enroll link, replace the placeholder in the destination box with the address above, save.",
    "Keep the RFB and Forge links as separate entries even though the address is the same. A click then still tells you which email the client opened.",
    "Open each saved link once in a private browser window and confirm the ThriveCart page loads with the right price.",
])
note("<b>Two things to confirm with Chris before pasting.</b> In his doc the two labels on the 3-month links are the wrong way round: the "
     "\"installments\" label sits on the slug ending in standard-link. The table above goes by the slug. And whether the ThrivePay "
     "installments page should be a second button. If yes, create seven more trigger links with an -Installments suffix pointing at the "
     "installments addresses in his doc, and add them to the click trigger in WF-CT2.", warn=True)

# ---------------------------------------------------------------- 2
story.append(CondPageBreak(3.5*inch))
para("Update 2 &mdash; The outreach emails in WF-K2b, WF-K2d and WF-K2f", "H1")
para("Each of the three workflows sends the what-comes-next email. Replace its single email step with an If/Else on <b>Offer Discussed</b>: "
     "men's values go to the men's email, women's values to the women's. Each email lists five options, and every button is the trigger link, "
     "never the raw address. That is what makes a click fire WF-CT2.")
table(["Women's email, \"Let's Keep Going Together\"", "Men's email, \"Step Into Your Power\"", "Button"], [
    ["Radiant Feminine Blueprint, 6 months, $4,997", "Forge, 6 months, $4,997", "Enroll-RFB-6mo / Enroll-Forge-6mo"],
    ["Radiant Feminine Blueprint, 1 year, $8,500", "Forge, 1 year, $8,500", "Enroll-RFB-1yr / Enroll-Forge-1yr"],
    ["RMM Plus Coaching, 6 months, $2,997", "same", "Enroll-RMMPlus"],
    ["Continue with RMM, 6 months, $2,000", "same", "Enroll-ContinueRMM-6mo"],
    ["Continue with RMM, Short Term, 3 months, $1,500", "same", "Enroll-ContinueRMM-3mo"],
], [2.35*inch, 2.0*inch, 2.15*inch], mono_cols=(2,))
para("After the email, in both branches, the same four steps from the build guide", "H2")
steps([
    "<b>Add Contact Tag</b>: " + C("outreach sent"),
    "<b>Update Opportunity</b>: pipeline " + C("Continuation Programs") + ", stage " + C("Outreach Sent"),
    "<b>Wait</b>: 5 days, type Time Delay.",
    "<b>If/Else</b>: contact has any of the 7 " + C("enrolled-") + " tags OR " + C("continuation-engaged") + ". Yes branch empty, it ends. "
    "None branch: <b>Update Opportunity</b> to stage " + C("Needs Follow-Up") + ", then <b>Create Task</b> assigned to <b>Luann</b>, "
    "title " + C("Continuation follow-up: {{contact.name}}") + ", due in 3 days.",
])
note("The build guide assigned that task to Krissy. The client journey now runs to Luann, so the task goes to her.")

# ---------------------------------------------------------------- 3
para("Update 3 &mdash; WF-CT3 values, nothing to change", "H1")
para("The opportunity values in WF-CT3 are 4997, 8500, 2997, 2000 and 1500. They match Chris's confirmed pricing exactly. Open it once to "
     "confirm the seven branches are there, then leave it.")

# ---------------------------------------------------------------- 4
para("Update 4 &mdash; Decide who applies the enrolled tag", "H1")
para("Because RFB and Forge share one checkout, a ThriveCart purchase cannot tell the two apart on its own. For now the enrolled tag is "
     "applied by hand when a payment is confirmed, which is the manual path the build guide allows. WF-CT3 does everything after that.")
table(["Client bought", "Tag to apply"], [
    ["Radiant Feminine Blueprint, 6 months", "enrolled-rfb-6mo"],
    ["Radiant Feminine Blueprint, 1 year", "enrolled-rfb-1yr"],
    ["Forge, 6 months", "enrolled-forge-6mo"],
    ["Forge, 1 year", "enrolled-forge-1yr"],
    ["RMM Plus Coaching", "enrolled-rmmplus"],
    ["Continue with RMM, 6 months", "enrolled-continuermm-6mo"],
    ["Continue with RMM, 3 months", "enrolled-continuermm-3mo"],
], [3.3*inch, 3.2*inch], mono_cols=(1,))
para("Name the one person who does this, Luann or Krissy, and add it to their close checklist.")

# ---------------------------------------------------------------- 5
story.append(CondPageBreak(3*inch))
para("Publish order", "H1")
steps([
    "Trigger links first, Update 1.",
    "Publish WF-CT1, WF-CT2, WF-CT3 and WF-CT4. The foundations they need are all in place. WF-CT1's date trigger only fires on the exact day, "
    "so publishing does not sweep existing clients in.",
    "Build the emails, Update 2, then publish WF-K2b, WF-K2d and WF-K2f.",
    "Confirm the day counts with Luann. WF-CT1 fires at start date plus 77 days and WF-CT4 at plus 90, which assumes a 12-week container. "
    "Adjust if any program runs longer.",
])
para("Prove it before the first real graduate", "H2")
steps([
    "Give a test contact " + C("existing client") + " and a program_start_date 77 days ago, or set WF-CT1 to 1 day temporarily. "
    "Verify: " + C("graduated") + " tag and a card at Graduated.",
    "Run it through the outreach email. Verify " + C("outreach sent") + " lands and the card moves.",
    "Click one Enroll button from the test inbox. Verify the ThriveCart page opens, " + C("continuation-engaged") + " is added and the card moves to Call Booked / Reply Received.",
    "Add " + C("enrolled-rmmplus") + ". Verify the card moves to Enrolled with value 2997.",
    "Remove the enrolled tag and let the 5-day wait pass, or shorten it. Verify Needs Follow-Up and Luann's task.",
    "Clean up: remove the test contact from every workflow, clear its tags, delete the test card.",
])

doc = SimpleDocTemplate(OUT, pagesize=letter, leftMargin=0.8*inch, rightMargin=0.8*inch, topMargin=0.75*inch, bottomMargin=0.75*inch,
                        title="Continuation Tracker Completion Updates", author="John Carlo Caintic")
def footer(canvas, d):
    canvas.saveState(); canvas.setFont("Helvetica", 8); canvas.setFillColor(MUTED)
    canvas.drawString(0.8*inch, 0.5*inch, "Continuation Tracker  |  Completion Updates  |  Sophie Orozco Coaching")
    canvas.drawRightString(letter[0]-0.8*inch, 0.5*inch, f"Page {d.page}"); canvas.restoreState()
doc.build(story, onFirstPage=footer, onLaterPages=footer)
print("wrote", OUT)
