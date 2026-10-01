# -*- coding: utf-8 -*-
"""Sophie Orozco Coaching - GHL tag cleanup review list."""
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
STOPFILL = colors.HexColor("#FBE9E7"); STOP = colors.HexColor("#8C2D14")

styles = getSampleStyleSheet()
def S(name, **kw): styles.add(ParagraphStyle(name, **kw))
S("TitleBig", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=20, textColor=INK, spaceAfter=3, alignment=TA_LEFT, leading=24)
S("XSub", fontName="Helvetica", fontSize=10.5, textColor=MUTED, spaceAfter=2, leading=14.5)
S("H1", parent=styles["Heading1"], fontName="Helvetica-Bold", fontSize=13, textColor=ACCENT, spaceBefore=15, spaceAfter=4, leading=16, keepWithNext=1)
S("H2", parent=styles["Heading2"], fontName="Helvetica-Bold", fontSize=11, textColor=TEAL, spaceBefore=9, spaceAfter=2, leading=13.5, keepWithNext=1)
S("XBody", parent=styles["Normal"], fontName="Helvetica", fontSize=10, textColor=INK, spaceAfter=6, leading=14.5)
S("Mono", fontName="Courier", fontSize=9.5, textColor=INK, leading=13.5, leftIndent=10)
S("OkNote", fontName="Helvetica", fontSize=9.5, textColor=OK, leading=13.5, leftIndent=8, backColor=OKFILL, borderPadding=6, spaceBefore=3, spaceAfter=9)
S("WarnNote", fontName="Helvetica", fontSize=9.5, textColor=WARN, leading=13.5, leftIndent=8, backColor=WARNFILL, borderPadding=6, spaceBefore=3, spaceAfter=9)
S("StopNote", fontName="Helvetica", fontSize=9.5, textColor=STOP, leading=13.5, leftIndent=8, backColor=STOPFILL, borderPadding=6, spaceBefore=3, spaceAfter=9)

story = []
def para(t, st="XBody"): story.append(Paragraph(t, styles[st]))
def rule():
    story.append(Spacer(1, 3)); story.append(HRFlowable(width="100%", thickness=0.6, color=RULE)); story.append(Spacer(1, 3))
def note(t, kind="ok"): story.append(Paragraph(t, styles[{"ok":"OkNote","warn":"WarnNote","stop":"StopNote"}[kind]]))
def taglist(tags, cols=2):
    rows = []
    for i in range(0, len(tags), cols):
        chunk = tags[i:i+cols] + [""]*(cols-len(tags[i:i+cols]))
        rows.append([Paragraph(c, styles["Mono"]) if c else Paragraph("", styles["Mono"]) for c in chunk])
    t = Table(rows, colWidths=[3.25*inch]*cols)
    t.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"TOP"),("LEFTPADDING",(0,0),(-1,-1),2),
                           ("RIGHTPADDING",(0,0),(-1,-1),2),("TOPPADDING",(0,0),(-1,-1),1.5),("BOTTOMPADDING",(0,0),(-1,-1),1.5)]))
    story.append(t); story.append(Spacer(1, 7))
def table(header, rows, widths):
    data = [[Paragraph(f"<b>{h}</b>", styles["XBody"]) for h in header]]
    for r in rows:
        data.append([Paragraph(c, styles["Mono"] if c.startswith("client -") or c.startswith("calendly") else styles["XBody"]) for c in r])
    t = Table(data, colWidths=widths, repeatRows=1)
    t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),HEADFILL),("GRID",(0,0),(-1,-1),0.5,RULE),("VALIGN",(0,0),(-1,-1),"TOP"),
                           ("LEFTPADDING",(0,0),(-1,-1),6),("RIGHTPADDING",(0,0),(-1,-1),6),("TOPPADDING",(0,0),(-1,-1),4),("BOTTOMPADDING",(0,0),(-1,-1),4)]))
    story.append(t); story.append(Spacer(1, 8))

# ---------------------------------------------------------------- header
story.append(Paragraph("Sophie Orozco Coaching  |  FG Funnels  |  Internal", styles["XSub"]))
story.append(Paragraph("GHL Tag Cleanup &mdash; Review List", styles["TitleBig"]))
story.append(Spacer(1, 4)); rule()

# ---------------------------------------------------------------- SAFE
para("1. Safe to delete now &mdash; 23 tags", "H1")
para("Obsolete programs, old event tags, unused lead-source tags and leftovers. None of these has a single contact attached.", "XBody")

para("Retired programs whose automations are now unpublished (3)", "H2")
taglist(["client - rmm men", "client - rmm course only men", "client - rmm course only women"])

para("A near-twin of the live Self-Paced tag, never used (1)", "H2")
taglist(["client - self paced"])

para("Event tags, no longer running (5)", "H2")
taglist(["event-clarity-call", "event-get-unstuck-men", "event-get-unstuck-women",
         "event-relationship-reset-men", "event-relationship-reset-women"])

para("Lead-source tags, replaced by the ig/fb tag (4)", "H2")
taglist(["lead-facebook", "lead-instagram", "lead-organic", "lead-referral"])

para("Miscellaneous leftovers (10)", "H2")
taglist(["booked", "cancelled calls", "comparison", "financial",
         "follow-up-needed", "freebies", "magnetic communication- purchased",
         "offer discussed- rmm selfpaced women", "test", "warm leads male"])

# ---------------------------------------------------------------- DO NOT
story.append(CondPageBreak(3*inch))
para("2. Do not delete &mdash; no contacts, but a live automation triggers on them", "H1")
para("These three have zero contacts, so they look deletable. They are not. Each one is the trigger on a published onboarding automation, "
     "and deleting the tag leaves that automation listening for something that no longer exists.", "XBody")
table(["Tag", "Automation that needs it"],
      [["client - couples coaching men", "Onboarding Email- (men) Couples"],
       ["client - couples coaching women", "Onboarding Email- (women) Couples"],
       ["client - rmm self paced men", "Onboarding Email- RMM- SELF PACED (Men)"]],
      [2.5*inch, 4.0*inch])

# ---------------------------------------------------------------- HOLD
para("3. Hold &mdash; reserved for the continuation tracker, 12 tags", "H1")
para("These have no contacts yet because the continuation tracker is still in draft, but they are its working parts. "
     "The four <font face='Courier'>enrolled-</font> tags are triggers on WF-CT3 Continuation Enrolled and the sweep in WF-CT4, "
     "and the eight <font face='Courier'>client -</font> tags are the program tags for the continuation offers Chris confirmed on Sept 11: "
     "RFB, Forge, RMM Plus and Continue RMM. Deleting any of them now would have to be undone when the tracker goes live.", "XBody")
taglist(["enrolled-rfb-6mo", "enrolled-rfb-1yr", "enrolled-forge-6mo", "enrolled-continuermm-6mo",
         "client - continuation rmm men 3mo", "client - continuation rmm men 6mo",
         "client - continuation rmm women 3mo", "client - continuation rmm women 6mo",
         "client - forge", "client - radiant feminine 1 year",
         "client - radiant feminine 1on1", "client - rmm plus"])

# ---------------------------------------------------------------- CHECK
para("4. Check before deleting &mdash; 10 tags", "H1")
para("Zero contacts, but the names suggest an automation adds or removes them somewhere. Workflow contents cannot be read through the API, "
     "so these need a look in the builder first. My expectation is that <font face='Courier'>recovery</font> and "
     "<font face='Courier'>calendly-recovery-stop</font> are used by the cancellation and no-show recovery automations, so leave those two alone "
     "unless you confirm otherwise.", "XBody")
taglist(["application-not-qualified", "application-qualified", "calendly-recovery-stop",
         "communication reset - series completed", "no-show", "onboarding",
         "precall-application", "recovery", "soap opera completed", "welcome email"])

# ---------------------------------------------------------------- CONFUSING
story.append(CondPageBreak(3.4*inch))
para("5. The confusing near-twins &mdash; none of these can be deleted", "H1")
para("These are the tags Chris is thinking of when he says similar and easy to confuse. Every one of them has real clients attached, "
     "so deleting any of them would wipe the record of what those clients bought from 53 client records in total.", "XBody")
table(["Tag", "Real clients", "Easily confused with"],
      [["client - accelerator men", "27", "client - rmm accelerator men"],
       ["client - accelerator women", "14", "client - rmm accelerator women"],
       ["client - course only men", "4", "client - rmm course only men"],
       ["client - course only women", "3", "client - rmm course only women"],
       ["client - couples coaching", "3", "client - couples coaching men / women"],
       ["client - couples coaching vip", "1", "client - vip sophie men / women"],
       ["client - rmm women", "1", "Heather Kauffman, retired program"]],
      [2.3*inch, 1.0*inch, 3.2*inch])
note("<b>The fix for these seven is not deletion.</b> Add each one into the matching onboarding automation as a second accepted tag. "
     "Then whichever name a closer picks, the client is onboarded correctly and the history on their record stays intact. "
     "This is also what would have prevented Brendan Logan from being missed.", "warn")

# ---------------------------------------------------------------- ORDER
para("Order to work through it", "H1")
lf = ListFlowable([ListItem(Paragraph(t, styles["XBody"])) for t in [
    "Delete the 23 in section 1. Settings, then Tags, search each name and delete. No contact or automation is touched.",
    "Leave the three in section 2 and the twelve in section 3 exactly as they are.",
    "Open the automations for the ten in section 4, confirm whether each tag is referenced, then delete only the ones that are not.",
    "Wire the seven in section 5 into their matching onboarding automations as second accepted tags, and leave the tags in place.",
]], bulletType="1", bulletFontName="Helvetica-Bold", bulletColor=ACCENT, leftIndent=18, bulletFontSize=10)
story.append(lf); story.append(Spacer(1, 6))
note("<b>One correction worth passing to Chris.</b> Not every similar-looking tag can be removed. The seven in section 5 carry live client history, "
     "so the clean-up will make the list shorter but those near-twins stay. Wiring them in is what stops them causing problems.", "stop")

doc = SimpleDocTemplate(OUT, pagesize=letter, leftMargin=0.85*inch, rightMargin=0.85*inch, topMargin=0.8*inch, bottomMargin=0.8*inch,
                        title="GHL Tag Cleanup Review List", author="John Carlo Caintic")
def footer(canvas, d):
    canvas.saveState(); canvas.setFont("Helvetica", 8); canvas.setFillColor(MUTED)
    canvas.drawString(0.85*inch, 0.5*inch, "GHL Tag Cleanup  |  Sophie Orozco Coaching  |  22 Sept 2026")
    canvas.drawRightString(letter[0]-0.85*inch, 0.5*inch, f"Page {d.page}")
    canvas.restoreState()
doc.build(story, onFirstPage=footer, onLaterPages=footer)
print("wrote", OUT)
