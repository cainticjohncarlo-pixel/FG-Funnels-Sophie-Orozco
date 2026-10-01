# -*- coding: utf-8 -*-
"""SOC Staff Hub portal setup, short version."""
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
FLOWFILL = colors.HexColor("#F4F7FA"); OKFILL = colors.HexColor("#EAF5EE"); OK = colors.HexColor("#1D4A33")

styles = getSampleStyleSheet()
def S(name, **kw): styles.add(ParagraphStyle(name, **kw))
S("TitleBig", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=21, textColor=INK, spaceAfter=3, alignment=TA_LEFT, leading=25)
S("XSub", fontName="Helvetica", fontSize=11, textColor=MUTED, spaceAfter=2, leading=15)
S("H1", parent=styles["Heading1"], fontName="Helvetica-Bold", fontSize=13.5, textColor=ACCENT, spaceBefore=14, spaceAfter=5, leading=17, keepWithNext=1)
S("XBody", parent=styles["Normal"], fontName="Helvetica", fontSize=10.5, textColor=INK, spaceAfter=6, leading=15.5)
S("XStep", parent=styles["Normal"], fontName="Helvetica", fontSize=10.5, textColor=INK, leading=15.5, leftIndent=4)
S("OkNote", fontName="Helvetica", fontSize=10, textColor=OK, leading=14.5, leftIndent=8, backColor=OKFILL, borderPadding=6, spaceBefore=2, spaceAfter=8)
S("Flow", fontName="Courier", fontSize=9, textColor=INK, leading=12, backColor=FLOWFILL, borderPadding=8, spaceBefore=4, spaceAfter=10)

story = []
def para(t, st="XBody"): story.append(Paragraph(t, styles[st]))
def steps(items):
    lf = ListFlowable([ListItem(Paragraph(t, styles["XStep"])) for t in items], bulletType="1", bulletFontName="Helvetica-Bold",
                      bulletColor=ACCENT, leftIndent=18, bulletFontSize=10.5)
    group = [lf]
    while story and isinstance(story[-1], Paragraph) and story[-1].style.name in ("H1", "XBody"): group.insert(0, story.pop())
    story.append(KeepTogether(group)); story.append(Spacer(1, 4))
def done(t): story.append(Paragraph("<b>Done when:</b> " + t, styles["OkNote"]))
def table(rows, widths):
    data = [[Paragraph(c, styles["XBody"]) for c in r] for r in rows]
    t = Table(data, colWidths=widths)
    t.setStyle(TableStyle([("GRID", (0,0), (-1,-1), 0.5, RULE), ("BACKGROUND", (0,0), (0,-1), HEADFILL), ("VALIGN", (0,0), (-1,-1), "TOP"),
                           ("LEFTPADDING", (0,0), (-1,-1), 6), ("RIGHTPADDING", (0,0), (-1,-1), 6), ("TOPPADDING", (0,0), (-1,-1), 5), ("BOTTOMPADDING", (0,0), (-1,-1), 5)]))
    story.append(KeepTogether([story.pop(), t]) if story and isinstance(story[-1], Paragraph) and story[-1].style.name == "H1" else t); story.append(Spacer(1, 8))
def block(lines): story.append(KeepTogether(Paragraph("<br/>".join(l.replace(" ", "&nbsp;") for l in lines), styles["Flow"])))
C = lambda s: f"<font face='Courier'>{s}</font>"

# ---------------------------------------------------------------- header
story.append(Paragraph("Sophie Orozco Coaching  |  Internal", styles["XSub"]))
story.append(Paragraph("SOC Staff Hub &mdash; Portal Setup", styles["TitleBig"]))
story.append(Paragraph("Hazel's Part 2, Step 2.1. Build the private portal where new team members log in for onboarding. Five short parts, about 45 minutes.", styles["XSub"]))
story.append(Spacer(1, 4)); story.append(HRFlowable(width="100%", thickness=0.6, color=RULE)); story.append(Spacer(1, 4))

para("The settings to use", "H1")
table([
    ["Portal name", "SOC Staff Hub"],
    ["Domain", "Keep the default one for now"],
    ["Background colour", C("#FCF6EF") + " (Seashell Peach)"],
    ["Button colour", C("#D6938A") + " (My Pink)"],
    ["Font", "Montserrat. If not offered, Livvic. If not offered, leave the default"],
    ["Logo", "SOC logo PNG, plus a square version for the favicon"],
    ["Sign-up", "Off. Staff get in only through the welcome email"],
], [1.7*inch, 4.8*inch])

para("1. Create the portal", "H1")
steps([
    "Go to <b>Sites</b>, then <b>Memberships</b> (in FG Funnels it may be under <b>Client Portal</b>), then <b>Settings</b>.",
    "Name: <b>SOC Staff Hub</b>. Support email: hello@sophieorozco.com.",
    "Leave the domain as the default. Copy that address, staff will log in there.",
    "Save.",
])
done("the default address opens a login page.")

para("2. Brand it", "H1")
steps([
    "In Settings open the branding or theme section.",
    "Upload the SOC logo. Upload the square logo as favicon.",
    "Background " + C("#FCF6EF") + ". Buttons " + C("#D6938A") + ". Font Montserrat.",
    "Save, then open the login page and look at it.",
])
done("the login page shows the SOC logo, peach background and pink button, and nothing from a client site.")

story.append(CondPageBreak(3.2*inch))
para("3. Welcome email", "H1")
steps([
    "In Settings open the email templates. Select the welcome email, the one sent when someone is given access.",
    "Paste the text below. For the button, insert the login link merge field from the picker.",
    "Sender name: <b>Sophie Orozco Coaching</b>. Sender address: the one used on client emails.",
    "Leave the login (magic link) email as it is, only set the same sender.",
    "Save.",
])
block([
    "Subject: Welcome to the SOC team, here's your Staff Hub login",
    "",
    "Hey {{contact.first_name}},",
    "",
    "Welcome aboard. Your onboarding lives in our Staff Hub, and this email",
    "is your key. Click below to set your password and log in.",
    "",
    "[ Set my password and log in ]",
    "",
    "Start with the course called \"00 - Start Here\" and work top to bottom.",
    "Your role course unlocks alongside it. Plan to complete Start Here in",
    "your first two days.",
    "",
    "Questions while you go? Post them in Slack and tag us. See you inside.",
    "",
    "Chris & Sophie",
])

para("4. Test it", "H1")
steps([
    "Make a test contact with an email you control.",
    "Give it access to the portal. The welcome email should arrive.",
    "Click the button. It should open the portal login and let you set a password.",
    "Remove the test contact's access afterwards.",
])
done("the welcome email arrived in the inbox with the right subject and the button worked.")

para("5. Turn off sign-up", "H1")
steps([
    "Open the login page in a private browser window.",
    "If there is any <b>Sign up</b> or <b>Create account</b> link, go back to Settings and switch off self sign-up. If the link comes from a free offer, unpublish that offer.",
    "Reload the page. Only the login form and forgot password should remain.",
])
done("nobody can create an account from the login page.")

para("Custom domain, only if Chris asks for it", "H1")
para("Hazel suggested " + C("team.sophieorozco.com") + " as an option for later. It needs a DNS record on Chris's domain. Skip it for now. If Chris wants it, tell me and I will add it after the portal works on the default address.")

doc = SimpleDocTemplate(OUT, pagesize=letter, leftMargin=0.85*inch, rightMargin=0.85*inch, topMargin=0.8*inch, bottomMargin=0.8*inch,
                        title="SOC Staff Hub Portal Setup", author="John Carlo Caintic")
def footer(canvas, d):
    canvas.saveState(); canvas.setFont("Helvetica", 8); canvas.setFillColor(MUTED)
    canvas.drawString(0.85*inch, 0.5*inch, "SOC Staff Hub  |  Portal Setup  |  Step 2.1")
    canvas.drawRightString(letter[0]-0.85*inch, 0.5*inch, f"Page {d.page}"); canvas.restoreState()
doc.build(story, onFirstPage=footer, onLaterPages=footer)
print("wrote", OUT)
