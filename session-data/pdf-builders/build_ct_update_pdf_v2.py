# -*- coding: utf-8 -*-
"""Continuation Tracker - completion updates, step by step."""
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable,
                                ListFlowable, ListItem, KeepTogether, CondPageBreak, PageBreak)

OUT = sys.argv[1]
INK = colors.HexColor("#1A1A1A"); ACCENT = colors.HexColor("#1D4E89"); TEAL = colors.HexColor("#0E7C7B")
MUTED = colors.HexColor("#5F6B7A"); RULE = colors.HexColor("#D5DAE0"); HEADFILL = colors.HexColor("#EAEFF4")
OKFILL = colors.HexColor("#EAF5EE"); OK = colors.HexColor("#1D4A33")
WARNFILL = colors.HexColor("#FDF3E7"); WARN = colors.HexColor("#9A3412"); FLOWFILL = colors.HexColor("#F4F7FA")

styles = getSampleStyleSheet()
def S(name, **kw): styles.add(ParagraphStyle(name, **kw))
S("TitleBig", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=20, textColor=INK, spaceAfter=3, alignment=TA_LEFT, leading=24)
S("XSub", fontName="Helvetica", fontSize=10.5, textColor=MUTED, spaceAfter=2, leading=14.5)
S("H1", parent=styles["Heading1"], fontName="Helvetica-Bold", fontSize=13.5, textColor=ACCENT, spaceBefore=16, spaceAfter=4, leading=17, keepWithNext=1)
S("H2", parent=styles["Heading2"], fontName="Helvetica-Bold", fontSize=11, textColor=TEAL, spaceBefore=10, spaceAfter=2, leading=13.5, keepWithNext=1)
S("XBody", parent=styles["Normal"], fontName="Helvetica", fontSize=10.5, textColor=INK, spaceAfter=6, leading=15)
S("XStep", parent=styles["Normal"], fontName="Helvetica", fontSize=10.5, textColor=INK, leading=15.5, leftIndent=4)
S("Cell", parent=styles["Normal"], fontName="Helvetica", fontSize=9.3, textColor=INK, leading=12.5)
S("CellMono", fontName="Courier-Bold", fontSize=9.6, textColor=INK, leading=12.5)
S("Block", fontName="Courier", fontSize=9.6, textColor=INK, leading=14.5, backColor=FLOWFILL, borderPadding=9, spaceBefore=4, spaceAfter=12, leftIndent=2)
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
def verify(t): story.append(Paragraph("<b>Check before moving on:</b> " + t, styles["OkNote"]))
def warn(t): story.append(Paragraph(t, styles["WarnNote"]))
def block(lines):
    out = []
    for l in lines:
        t = l.replace(" ", "&nbsp;")
        if l.startswith("https://") or l.startswith("ENROLL-") or l.startswith("client - ") or l.startswith("enrolled-") or l.startswith("continuation-"):
            t = "<font face='Courier-Bold' color='#0B2E5C'>" + t + "</font>"
        out.append(t)
    group = [Paragraph("<br/>".join(out), styles["Block"])]
    while story and isinstance(story[-1], Paragraph) and story[-1].style.name in ("H2", "XBody"): group.insert(0, story.pop())
    story.append(KeepTogether(group))
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
C = lambda s: f"<font face='Courier-Bold' size='10' color='#0B2E5C'>{s}</font>"

# ================================================================ header
story.append(Paragraph("Sophie Orozco Coaching  |  FG Funnels  |  Internal", styles["XSub"]))
story.append(Paragraph("Continuation Tracker &mdash; Completion Updates", styles["TitleBig"]))
story.append(Paragraph("Step by step, in the order to do them, to take the continuation tracker from draft to live using the backend "
                       "payment links Chris posted on Sept 11, 2026. Prepared by John Carlo Caintic, Sept 23, 2026.", styles["XSub"]))
story.append(Spacer(1, 4)); rule()

para("Where it stands", "H1")
table(["Piece", "State"], [
    ["Pipeline Continuation Programs, 6 stages", "Built"],
    ["The 11 tags: graduated, outreach sent, continuation-engaged, declined-all, and the 7 enrolled tags", "All present"],
    ["7 Enroll trigger links", "Exist, every one points at a placeholder"],
    ["WF-CT1, WF-CT2, WF-CT3, WF-CT4", "Built, in draft"],
    ["WF-K2b, WF-K2d, WF-K2f outreach emails", "In draft, need the five offers and the buttons"],
], [4.3*inch, 3.0*inch])
para("Six parts below. Parts 1, 2 and 5 are the work. Parts 3 and 4 are a check and a decision. Part 6 proves it. About two hours end to end.")

# ================================================================ PART 1
para("Part 1 &mdash; Point the seven trigger links at the real checkouts (20 min)", "H1")

para("Why this part has to be done, and done first", "H2")
para("A trigger link is a tracked address that GHL owns. When a client clicks it, GHL records the click on that client's record and then "
     "forwards them to the real page. The Enroll buttons in the continuation emails are trigger links for exactly that reason: the click is "
     "the signal that a graduate looked at an offer.")
steps([
    "<b>The click is what starts WF-CT2.</b> WF-CT2 Continuation Engagement listens for clicks on the seven Enroll links. A click adds the tag "
    + C("continuation-engaged") + " and moves the client's card to Call Booked / Reply Received. Without the trigger links, GHL never knows "
    "the client was interested.",
    "<b>The 5-day follow-up depends on it.</b> Five days after the outreach email, the workflow checks for " + C("continuation-engaged")
    + ". If the click was never recorded, an interested client is filed as no response and Luann gets a follow-up task she does not need.",
    "<b>The links exist but go nowhere.</b> All seven were created during the build with placeholders such as " + C("Enroll-RFB-6mo.com")
    + " because the checkout pages were not confirmed yet. Today a click would record an engagement and then land the client on a dead address.",
    "<b>Seven links, not five,</b> even though RFB and Forge share a checkout. Keeping RFB and Forge as separate names means a click tells you "
    "which gender's email the client opened, which is the only attribution the emails have.",
    "<b>Standard link, not installments.</b> The Standard page carries pay in full, split pay, PayPal and buy now pay later on one screen. "
    "The installments page is a separate ThriveCart product for ThrivePay plans only. One button, one page, fewest decisions for the client.",
])
para("How it flows once the links are right", "XBody")
block([
    "Client clicks an Enroll button in the email",
    "        |",
    "        v",
    "link.fgfunnels.com/...   <- the trigger link. GHL records the click,",
    "        |                   adds continuation-engaged, moves the card    (WF-CT2)",
    "        v",
    "sophieorozco.thrivecart.com/...   <- the checkout. The client pays here.",
])

para("The exact links, copied character for character from Chris's doc", "H2")
para("Use the <b>Standard</b> link for the button. The installments link is listed under each one only for the case where Chris wants it as a "
     "second button.")
block([
    "ENROLL-RFB-6mo  and  ENROLL-Forge-6mo                                   $4,997",
    "Standard link, use this for the button:",
    "https://sophieorozco.thrivecart.com/rfb-forge-6-months-standard-link/",
    "ThriveCart installments link, only if a second button is wanted:",
    "https://sophieorozco.thrivecart.com/rfb-forge-6months-installments/",
])
block([
    "ENROLL-RFB-1yr  and  ENROLL-Forge-1yr                                   $8,500",
    "Standard link, use this for the button:",
    "https://sophieorozco.thrivecart.com/rfb-forge-1year-standardlink/",
    "ThriveCart installments link, only if a second button is wanted:",
    "https://sophieorozco.thrivecart.com/rfb-forge-1-year-installments/",
])
block([
    "ENROLL-RMMPlus   (RMM Continuation with Coaching, 4 x 1:1 calls)        $2,997",
    "Standard link, use this for the button:",
    "https://sophieorozco.thrivecart.com/rmm-continuation-plus-coaching-2997-standard-link/",
    "ThriveCart installments link, only if a second button is wanted:",
    "https://sophieorozco.thrivecart.com/rmm-continuation-coaching-2997-installments/",
])
block([
    "ENROLL-ContinueRMM-6mo   (RMM Continuation, 6 months, no coaching)      $2,000",
    "Standard link, use this for the button:",
    "https://sophieorozco.thrivecart.com/2000-rmm-continuation-standard-link/",
    "ThriveCart installments link, only if a second button is wanted:",
    "https://sophieorozco.thrivecart.com/2000-rmm-continuation-installments/",
])
block([
    "ENROLL-ContinueRMM-3mo   (RMM Continuation, 3 months, no coaching)      $1,500",
    "Listed in the doc under \"Thrive Cart Installments Link\":",
    "https://sophieorozco.thrivecart.com/1500-rmm-continuation-3-months-standard-link/",
    "Listed in the doc under \"Standard Link w/ split pay and paypal and BNPL\":",
    "https://sophieorozco.thrivecart.com/1500-rmm-continuation-installments/",
    "The two labels look swapped. Confirm with Chris which is which before pasting.",
])

para("Set up, one link at a time", "H2")
steps([
    "In the left menu click <b>Marketing</b>. Along the top of the Marketing page click the <b>Trigger Links</b> tab. A table lists every "
    "trigger link in the account by name, with its current destination in the Link URL column.",
    "Find the row named " + C("Enroll-RFB-6mo") + ". On the right of that row click the <b>pencil</b> icon. An edit panel opens with two fields: "
    "<b>Name</b> and <b>Link URL</b>.",
    "Do not touch <b>Name</b>. The WF-CT2 trigger and the email buttons find the link by this name, so it must stay exactly as it is.",
    "Click into <b>Link URL</b>. Select everything in it and delete it. The placeholder " + C("Enroll-RFB-6mo.com") + " must be gone completely.",
    "Paste the Standard link for that program from the block above. For " + C("Enroll-RFB-6mo") + " that is "
    + C("https://sophieorozco.thrivecart.com/rfb-forge-6-months-standard-link/") + ". Paste it, do not type it. Check there is no space at "
    "either end and that it starts with https.",
    "Click <b>Save</b>. The row now shows the ThriveCart address in the Link URL column.",
    "Test that one link before doing the rest. On the same row click the <b>copy</b> icon to copy the trigger link's own address, the one on "
    "link.fgfunnels.com. Open a private browser window, paste it, press Enter. It must land on the ThriveCart page showing $4,997. If it lands "
    "anywhere else, the pasted address is wrong: reopen the row and paste again.",
    "Repeat steps 2 to 7 for the remaining six rows, working down the checklist below.",
])
table(["Trigger link name", "Paste the Standard link ending in", "Page should show"], [
    ["Enroll-RFB-6mo", "rfb-forge-6-months-standard-link/", "$4,997"],
    ["Enroll-Forge-6mo", "rfb-forge-6-months-standard-link/", "$4,997"],
    ["Enroll-RFB-1yr", "rfb-forge-1year-standardlink/", "$8,500"],
    ["Enroll-Forge-1yr", "rfb-forge-1year-standardlink/", "$8,500"],
    ["Enroll-RMMPlus", "rmm-continuation-plus-coaching-2997-standard-link/", "$2,997"],
    ["Enroll-ContinueRMM-6mo", "2000-rmm-continuation-standard-link/", "$2,000"],
    ["Enroll-ContinueRMM-3mo", "1500-rmm-continuation-3-months-standard-link/ once Chris confirms", "$1,500"],
], [1.95*inch, 4.25*inch, 1.1*inch], mono_cols=(0,1))
verify("all seven rows in the Trigger Links table show a sophieorozco.thrivecart.com address, none still ends in .com alone, and each "
       "tested link lands on the ThriveCart page with the price in the checklist. Do not start Part 2 until this is true, because the email "
       "buttons in Part 2 point at these same seven links.")
warn("<b>Two things to confirm with Chris before pasting the last one.</b> In his doc the two labels on the 3-month links are reversed: the "
     "\"installments\" label sits on the slug that ends in standard-link. The checklist goes by the slug. And whether the ThrivePay "
     "installments page should be a second button. If yes, add seven more trigger links named the same with an " + C("-Installments")
     + " suffix, pointing at the installments addresses in the blocks above, and add all seven to the click trigger in WF-CT2 in Part 5.")

# ================================================================ PART 2
story.append(CondPageBreak(2.2*inch))
para("Part 2 &mdash; The outreach emails in WF-K2b, WF-K2d and WF-K2f (60 min)", "H1")
para("These three workflows send the what-comes-next email at different points in the program. Each one gets the same rebuild: split by "
     "gender, send the matching email with five buttons, then the four tracking steps. Build it fully in <b>WF-K2b Week 5 Next Steps</b> first, "
     "then repeat in WF-K2d and WF-K2f.")

para("2.1 Split the workflow by gender", "H2")
para("Branch on the program tag rather than Offer Discussed. The tag is on every client record and always carries the gender. Offer Discussed "
     "is often blank on the contact.")
steps([
    "Automation, open <b>WF-K2b Week 5 Next Steps</b>. Find the existing email step, the what-comes-next email.",
    "Click the plus <b>above</b> that email step and add an <b>If/Else</b>. Name it " + C("Women or men") + ".",
    "First branch, name it " + C("Women") + ". Add one condition: Contact Details, Tags, Includes, " + C("client - rmm accelerator women") + ".",
    "Click <b>Add Segment</b> and add the next tag as its own segment. Repeat until all eight tags in the box below are each in their own segment, joined by OR.",
    "Check the connector between every segment reads <b>OR</b>. One box holding several tags means all must match and the branch never fires.",
    "Leave the <b>None</b> branch as the men's path. Every client who is not a woman falls through to it.",
    "Drag the existing email step under the <b>Women</b> branch. Then click the plus under <b>None</b> and add a second <b>Send Email</b> for men.",
    "Click <b>Save Action</b>.",
])
para("The eight women's tags for the Women branch, one segment each", "XBody")
block([
    "client - rmm accelerator women",
    "client - accelerator women",
    "client - group only women",
    "client - rmm self paced women",
    "client - couples coaching women",
    "client - vip sophie women",
    "client - course only women",
    "client - rmm women",
])

para("2.2 The two emails and their five buttons", "H2")
para("The women's email is <b>Let's Keep Going Together</b>. The men's email is <b>Step Into Your Power</b>. Add the five-option block below "
     "to each. Every button must be a trigger link, never a pasted address, or a click will not reach WF-CT2.")
para("Women's email, five options in this order", "XBody")
block([
    "1. Radiant Feminine Blueprint, 6 months        $4,997   button -> Enroll-RFB-6mo",
    "2. Radiant Feminine Blueprint, 1 year          $8,500   button -> Enroll-RFB-1yr",
    "3. RMM Plus Coaching, 6 months                 $2,997   button -> Enroll-RMMPlus",
    "4. Continue with RMM, 6 months                 $2,000   button -> Enroll-ContinueRMM-6mo",
    "5. Continue with RMM, Short Term, 3 months     $1,500   button -> Enroll-ContinueRMM-3mo",
])
para("Men's email, five options in this order", "XBody")
block([
    "1. Forge, 6 months                             $4,997   button -> Enroll-Forge-6mo",
    "2. Forge, 1 year                               $8,500   button -> Enroll-Forge-1yr",
    "3. RMM Plus Coaching, 6 months                 $2,997   button -> Enroll-RMMPlus",
    "4. Continue with RMM, 6 months                 $2,000   button -> Enroll-ContinueRMM-6mo",
    "5. Continue with RMM, Short Term, 3 months     $1,500   button -> Enroll-ContinueRMM-3mo",
])
para("How to attach a trigger link to a button, five times per email", "XBody")
steps([
    "Open the email step, then <b>Edit</b> the email body.",
    "Select the button or the text that should be clickable, for example the line for option 1.",
    "Click the link icon. In the link type dropdown choose <b>Trigger Link</b>, not URL.",
    "Pick the link named in the block above for that option, for example " + C("Enroll-RFB-6mo") + " for the women's option 1.",
    "Apply, then repeat for options 2 to 5. Save the email.",
])
verify("hover each of the five buttons in the preview. Each should show a link.fgfunnels.com address with the trigger link's slug, not a "
       "thrivecart.com address. A thrivecart.com address means the raw URL was pasted and that click will not be tracked.")

para("2.3 The four tracking steps after each email", "H2")
para("Add these under <b>both</b> emails, the women's and the men's, in this order.")
steps([
    "<b>Add Contact Tag</b>: " + C("outreach sent") + ". Save Action.",
    "<b>Create/Update Opportunity</b>: pipeline " + C("Continuation Programs") + ", stage " + C("Outreach Sent") + ", opportunity name "
    + C("{{contact.name}}") + ", status Open. Save Action.",
    "<b>Wait</b>: type <b>Time Delay</b>, 5, unit <b>Days</b>. Not Event / Appointment Time, which skips when there is no appointment. Save Action.",
    "<b>If/Else</b>, name it " + C("Responded or enrolled") + ". One branch named " + C("Yes") + " with eight OR segments, one tag each, "
    "listed in the box below. Leave the Yes branch empty so it ends.",
    "Under the <b>None</b> branch: <b>Create/Update Opportunity</b>, pipeline " + C("Continuation Programs") + ", stage " + C("Needs Follow-Up") + ". Save Action.",
    "Still under None: <b>Add Task</b>. Title " + C("Continuation follow-up: {{contact.name}}") + ". Description "
    + C("No response 5 days after the continuation email.") + " Assign to <b>Luann Hirou</b>. Due in 3 days. Save Action.",
    "Click <b>Save</b> in the top right. Leave the workflow in <b>Draft</b>. Part 5 publishes it.",
])
para("The eight tags for the Yes branch of Responded or enrolled, one segment each", "XBody")
block([
    "enrolled-rfb-6mo",
    "enrolled-rfb-1yr",
    "enrolled-forge-6mo",
    "enrolled-forge-1yr",
    "enrolled-rmmplus",
    "enrolled-continuermm-6mo",
    "enrolled-continuermm-3mo",
    "continuation-engaged",
])
warn("The original build guide assigned that task to Krissy. The client journey now runs to Luann, so every task in these three workflows "
     "goes to her.")
para("2.4 Repeat in the other two", "H2")
steps([
    "Open <b>WF-K2d Week 9 Next Steps</b> and build 2.1 to 2.3 the same way. Save, leave in Draft.",
    "Open <b>WF-K2f Week 4 Next Steps</b> and do the same. Save, leave in Draft.",
])
verify("each of the three workflows shows: If/Else, two email branches, and under each email the tag, the opportunity update, the 5-day wait, "
       "and the responded If/Else with the task under None. Thirty buttons in total across the six emails, each one a trigger link.")

# ================================================================ PART 3
story.append(CondPageBreak(3*inch))
para("Part 3 &mdash; Confirm WF-CT3 values, nothing to change (5 min)", "H1")
steps([
    "Open <b>WF-CT3 Continuation Enrolled</b>.",
    "Check the seven Contact Tag triggers, one per enrolled tag.",
    "Click the If/Else and open each of the seven branches. The opportunity value in each must match this table.",
])
table(["Branch tag", "Opportunity value"], [
    ["enrolled-rfb-6mo", "4997"], ["enrolled-rfb-1yr", "8500"], ["enrolled-forge-6mo", "4997"], ["enrolled-forge-1yr", "8500"],
    ["enrolled-rmmplus", "2997"], ["enrolled-continuermm-6mo", "2000"], ["enrolled-continuermm-3mo", "1500"],
], [3.5*inch, 3.8*inch], mono_cols=(0,))
verify("all seven match. They already match Chris's confirmed pricing, so this should be a look, not an edit. Close without changes.")

# ================================================================ PART 4
para("Part 4 &mdash; Decide who applies the enrolled tag (a decision, not a build)", "H1")
para("RFB and Forge share one checkout, so a ThriveCart purchase cannot tell the two apart on its own. Until that is automated, one person "
     "applies the enrolled tag when a payment is confirmed. WF-CT3 does everything after that: stage, value, done.")
table(["Client bought", "Tag to add on the contact"], [
    ["Radiant Feminine Blueprint, 6 months", "enrolled-rfb-6mo"],
    ["Radiant Feminine Blueprint, 1 year", "enrolled-rfb-1yr"],
    ["Forge, 6 months", "enrolled-forge-6mo"],
    ["Forge, 1 year", "enrolled-forge-1yr"],
    ["RMM Plus Coaching", "enrolled-rmmplus"],
    ["Continue with RMM, 6 months", "enrolled-continuermm-6mo"],
    ["Continue with RMM, 3 months", "enrolled-continuermm-3mo"],
], [3.7*inch, 3.6*inch], mono_cols=(1,))
steps([
    "Agree with Chris who owns this, Luann or Krissy.",
    "That person, on each confirmed payment: open the client's contact, click the plus next to Tags, pick the one tag from the table, done. Nothing else to touch.",
    "Add the table above to their close checklist.",
])

# ================================================================ PART 5
story.append(CondPageBreak(3.5*inch))
para("Part 5 &mdash; Publish, in this order (15 min)", "H1")
steps([
    "Part 1 must be complete. Confirm the seven trigger links carry thrivecart.com addresses.",
    "If Chris wanted the installments buttons, open <b>WF-CT2 Continuation Engagement</b>, click the Trigger Link Clicked trigger, and add the seven "
    + C("-Installments") + " links to its selection. Otherwise skip this step.",
    "Open <b>WF-CT1 Graduation Entry</b>. Settings tab: Allow Re-Entry OFF, Allow Multiple Opportunities OFF. Builder tab: switch the toggle to <b>Publish</b>.",
    "Open <b>WF-CT2 Continuation Engagement</b>. Settings: Allow Re-Entry ON, Allow Multiple Opportunities OFF. Publish.",
    "Open <b>WF-CT3 Continuation Enrolled</b>. Settings: both OFF. Publish.",
    "Open <b>WF-CT4 Continuation Declined</b>. Settings: both OFF. Publish.",
    "Only after Part 2 is finished in all three: publish <b>WF-K2b</b>, <b>WF-K2d</b> and <b>WF-K2f</b>.",
])
verify("in the Automation list, the four WF-CT workflows and the three WF-K2 outreach workflows all show Published. WF-CT1's date trigger only "
       "fires on the exact day, so publishing does not sweep existing clients in.")
warn("<b>Day counts.</b> WF-CT1 fires at program start date plus 77 days and WF-CT4 at plus 90. Both assume a 12-week container. Confirm with "
     "Luann whether any program runs longer, and adjust those two numbers before publishing if so.")

# ================================================================ PART 6
para("Part 6 &mdash; Prove it before the first real graduate (30 min)", "H1")
para("Use a test contact with an email you control. Shorten WF-CT1 to 1 day for the test if you do not want to wait, and set it back to 77 afterwards.")
steps([
    "Give the test contact the tags " + C("existing client") + " and " + C("client - rmm accelerator women") + ", and set program_start_date to 77 days ago.",
    "Wait for WF-CT1. Check: the contact has " + C("graduated") + " and a card sits at <b>Graduated</b> in Continuation Programs.",
    "Add the test contact to <b>WF-K2b</b> by hand from Actions, Add to Workflow. Check: the women's email arrives with five buttons, "
    + C("outreach sent") + " lands, the card moves to <b>Outreach Sent</b>.",
    "From the test inbox click the option 3 button. Check: the ThriveCart page for $2,997 opens, " + C("continuation-engaged") + " is added, "
    "the card moves to <b>Call Booked / Reply Received</b>.",
    "Add the tag " + C("enrolled-rmmplus") + ". Check: the card moves to <b>Enrolled</b> with value 2997.",
    "Remove " + C("enrolled-rmmplus") + " and " + C("continuation-engaged") + ", shorten the 5-day wait to 5 minutes, add the contact to WF-K2b again. "
    "Check: card moves to <b>Needs Follow-Up</b> and a task for Luann appears. Set the wait back to 5 days.",
    "Clean up: remove the test contact from every workflow, clear its tags, delete its card in Continuation Programs.",
])
verify("all six checks passed. The tracker is live and the first real graduate will flow through without anyone touching it.")

doc = SimpleDocTemplate(OUT, pagesize=letter, leftMargin=0.6*inch, rightMargin=0.6*inch, topMargin=0.7*inch, bottomMargin=0.7*inch,
                        title="Continuation Tracker Completion Updates", author="John Carlo Caintic")
def footer(canvas, d):
    canvas.saveState(); canvas.setFont("Helvetica", 8); canvas.setFillColor(MUTED)
    canvas.drawString(0.6*inch, 0.5*inch, "Continuation Tracker  |  Completion Updates  |  Sophie Orozco Coaching")
    canvas.drawRightString(letter[0]-0.6*inch, 0.5*inch, f"Page {d.page}"); canvas.restoreState()
doc.build(story, onFirstPage=footer, onLaterPages=footer)
print("wrote", OUT)
