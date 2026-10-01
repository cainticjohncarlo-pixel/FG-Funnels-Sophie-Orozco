# -*- coding: utf-8 -*-
"""SOC Staff Hub portal setup guide (Hazel's Part 2, Step 2.1) as a PDF."""
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
S("Flow", fontName="Courier", fontSize=8.6, textColor=INK, leading=11.5, backColor=FLOWFILL, borderPadding=8, spaceBefore=4, spaceAfter=10)

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
def bullets(items):
    lf = ListFlowable([ListItem(Paragraph(t, styles["XStep"])) for t in items], bulletType="bullet", start="•",
                      bulletColor=ACCENT, leftIndent=16, bulletFontSize=10)
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
def block(lines): story.append(KeepTogether(Paragraph("<br/>".join(l.replace(" ", "&nbsp;") for l in lines), styles["Flow"])))
C = lambda s: f"<font face='Courier'>{s}</font>"
def brk(): story.append(CondPageBreak(2.4*inch))

# ================================================================== HEADER
story.append(Paragraph("Sophie Orozco Coaching  |  FG Funnels  |  Internal", styles["XSub"]))
story.append(Paragraph("SOC Staff Hub &mdash; Portal Setup Guide", styles["TitleBig"]))
story.append(Paragraph("Build steps for Part 2, Step 2.1 of Hazel's staff onboarding plan: create the membership portal, brand it, set the domain, "
                       "load the welcome and login emails, and lock it to grant-only access. Prepared by John Carlo Caintic, September 18, 2026.",
                       styles["XSub"]))
story.append(Spacer(1, 4)); rule()

# ================================================================== SCOPE
para("What this step delivers", "H1")
para("A private membership portal named SOC Staff Hub where new team members log in, read the 00 - Start Here course and their role course. "
     "Nothing in this step touches the client-facing course portal or any client domain. Courses, roles and access grants come in the later steps of Part 2.")
table(["Setting", "Value"], [
    ["Portal name", "SOC Staff Hub"],
    ["Domain to start", "The default membership domain FG Funnels assigns"],
    ["Custom domain, optional, later", C("team.sophieorozco.com")],
    ["Background colour", "Seashell Peach, " + C("#FCF6EF")],
    ["Accent and button colour", "My Pink, " + C("#D6938A")],
    ["Font", "Montserrat, then Livvic, then the theme default"],
    ["Logo", "SOC logo, PNG with transparent background, plus a square version for the favicon"],
    ["Access", "Grant-only. No public signup, no free offer checkout"],
], [1.9*inch, 4.6*inch], keep=True)

para("Before you start", "H1")
bullets([
    "SOC logo files: the horizontal PNG for the header and a square PNG for the favicon.",
    "The colour codes above, ready to paste.",
    "The support address staff should reply to. Use hello@sophieorozco.com unless Chris names another.",
    "Chris's answer on the custom domain. " + C("team.sophieorozco.com") + " needs a DNS record on his domain, so it can wait until the portal works on the default address.",
    "About 45 minutes, most of it spent on the two email tests.",
])

# ================================================================== A
brk()
para("A. Create the portal shell", "H1")
steps([
    "In the sub-account open <b>Sites</b>, then <b>Memberships</b>. In FG Funnels this can sit under <b>Client Portal</b>. Open <b>Settings</b>.",
    "In the site details section set the name to <b>SOC Staff Hub</b>.",
    "Set the support email to the address agreed with Chris.",
    "Leave the default membership domain as it is for now. Copy the full address into your notes, staff will log in there.",
    "Save.",
])
verify("the settings page shows SOC Staff Hub as the name and the default domain opens a login page in a private browser window.")

# ================================================================== B
para("B. Branding", "H1")
steps([
    "In the same Settings area open the branding or theme section.",
    "Upload the SOC logo for the header and the square logo as the favicon.",
    "Set the background colour to " + C("#FCF6EF") + " and the accent or button colour to " + C("#D6938A") + ". Keep the text colour dark so the peach background stays readable.",
    "Set the font to Montserrat where a font picker exists. If it is not offered, use Livvic. If neither is offered, keep the theme default and move on. This portal is internal.",
    "Open the login page preview and check the logo, the peach background and the pink buttons.",
    "Look for anything left over from a client site: a client logo, a client colour, a welcome line meant for clients. Remove it.",
    "Save.",
])
note("Keep the design plain. Hazel's brief is one logo, two colours and one font. Do not add banners, images or copy beyond that.")
verify("the login page in a private window shows the SOC logo, peach background, pink buttons and the portal name in the browser tab.")

# ================================================================== C
brk()
para("C. Domain", "H1")
para("Start on the default domain. Move to the custom domain only after Chris approves it and after the emails in section D are tested, so the links in those emails are tested once on the final address.", "XBody")
steps([
    "Default domain: nothing to do beyond noting the address from step A.",
    "Custom domain, when approved: open the custom domain section and enter " + C("team.sophieorozco.com") + ".",
    "Copy the CNAME target the screen shows.",
    "In the DNS host for sophieorozco.com add a CNAME record: host " + C("team") + ", target the value copied in the previous step. Chris or whoever holds the domain login does this if you do not have access.",
    "Wait for the domain check to pass. This can take up to an hour.",
    "Set " + C("team.sophieorozco.com") + " as the portal domain and save.",
    "Open the new address in a private window and confirm the branded login page loads over https.",
])
note("Do not attach any domain or path already used by client-facing pages or the client course portal. A shared path would expose staff material on a client address.", warn=True)

# ================================================================== D
para("D. Email templates", "H1")
para("Two templates matter here: the welcome email sent when a staff member is granted access, and the magic link or login email sent when they ask to log in. Both live in the email settings of the membership site.", "XBody")
para("D1. Welcome email", "H2")
steps([
    "Open the email settings and select the welcome or access-granted template.",
    "Replace the subject and body with the draft below. Keep the first-name merge field. For the button, insert the platform's login link merge field from the merge field picker, the entry named login link, magic link or set password link depending on the editor.",
    "Set the sender name to <b>Sophie Orozco Coaching</b> and the sender address to the one already used on client emails, so the message lands in the inbox rather than spam.",
    "Save the template.",
])
block([
    "Subject: Welcome to the SOC team, here's your Staff Hub login",
    "",
    "Hey {{contact.first_name}},",
    "",
    "Welcome aboard. Your onboarding lives in our Staff Hub, and this email",
    "is your key. Click below to set your password and log in.",
    "",
    "[ Set my password and log in ]   <- login link merge field",
    "",
    "Start with the course called \"00 - Start Here\" and work top to bottom.",
    "Your role course unlocks alongside it. Plan to complete Start Here in",
    "your first two days.",
    "",
    "Questions while you go? Post them in Slack and tag us. See you inside.",
    "",
    "Chris & Sophie",
])
para("D2. Magic link or login email", "H2")
steps([
    "Select the login or magic link template.",
    "Keep the platform wording. Apply the same sender name and address, the SOC logo and the peach background where the editor allows.",
    "Save the template.",
])
para("D3. Test both", "H2")
steps([
    "Create a test contact with an email you control, for example your own address with a plus tag.",
    "Grant that contact access to the portal by hand, or send the welcome email from the template's test option if one exists.",
    "Open the welcome email. Check the subject, the sender name, the first name, and that the button opens the portal login on the right domain.",
    "From the login page request a magic link for the test contact. Check it arrives and logs in.",
    "Remove the test contact's access when done, or keep it as the standing test account and note it for Hazel.",
])
verify("both test emails arrived in the inbox, not spam, with the SOC sender name, and both links opened the portal.")

# ================================================================== E
brk()
para("E. Grant-only access", "H1")
para("Staff must only get in through an access grant or the welcome email. There must be no way to create an account from the login page.", "XBody")
steps([
    "Open the portal login page in a private browser window.",
    "Look for any link or button that says Sign up, Create account, Register or Get access.",
    "If one is present, go back to the portal settings and switch off self-registration or public signup.",
    "If the link comes from a published free offer or a checkout page attached to the portal, unpublish that offer. A free offer with a public checkout is a signup path even when the login page hides it.",
    "Reload the login page in the private window. Only the login form and the forgot-password link should remain.",
])
note("If the platform has no switch and the signup link persists, stop and flag it to Hazel and me before granting anyone access. Do not work around it with a hidden page.", warn=True)

# ================================================================== F
para("F. Hand-off checklist", "H1")
para("Tick every line before telling Hazel the portal is ready.", "XBody")
table(["Check", "How to confirm"], [
    ["Portal name is SOC Staff Hub", "Browser tab and header on the login page"],
    ["Branding applied", "SOC logo, favicon, peach background, pink buttons, no client leftovers"],
    ["Domain", "Default domain working. Custom domain either pending Chris or verified over https"],
    ["Welcome email", "Test received with the right subject, sender and a working login button"],
    ["Magic link email", "Test received and logs in"],
    ["No public signup", "Login page in a private window shows only the login form and forgot password"],
    ["No client crossover", "Nothing on the portal points at a client-facing domain, page or course"],
    ["Notes for Hazel", "Default login address, custom domain status, test account details"],
], [2.1*inch, 4.4*inch], keep=True)

para("What comes next", "H1")
para("The remaining steps of Part 2 cover the courses, the 00 - Start Here content, role courses and the access grants for each team member. "
     "This guide will be extended in the same format when those steps are in.", "XBody")

doc = SimpleDocTemplate(OUT, pagesize=letter, leftMargin=0.85*inch, rightMargin=0.85*inch, topMargin=0.8*inch, bottomMargin=0.8*inch,
                        title="SOC Staff Hub Portal Setup Guide", author="John Carlo Caintic")
def footer(canvas, d):
    canvas.saveState(); canvas.setFont("Helvetica", 8); canvas.setFillColor(MUTED)
    canvas.drawString(0.85*inch, 0.5*inch, "SOC Staff Hub  |  Portal Setup Guide  |  Step 2.1")
    canvas.drawRightString(letter[0]-0.85*inch, 0.5*inch, f"Page {d.page}")
    canvas.restoreState()
doc.build(story, onFirstPage=footer, onLaterPages=footer)
print("wrote", OUT)
