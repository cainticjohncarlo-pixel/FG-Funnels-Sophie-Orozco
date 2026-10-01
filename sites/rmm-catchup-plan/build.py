# -*- coding: utf-8 -*-
"""RMM Catch-Up Workflow: setup plan and step-by-step build guide. Writes index.html for Vercel."""
import html, os

import json
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "index.html")
EMAILS = json.load(open(os.path.join(HERE, "emails.json"), encoding="utf-8"))
# Known typos in the live sequences, corrected here so the catch-up sends the right text.
FIXES = {("checkin_men", "9"): ("Week 5 Check-In", "Week 9 Check-In"), ("checkin_women", "9"): ("Week 5 Check-In", "Week 9 Check-In")}
FIXNOTE = {}
for (k, w), (bad, good) in FIXES.items():
    e = EMAILS.get(k, {}).get(w)
    if e and bad in e["body"]:
        e["body"] = e["body"].replace(bad, good)
        FIXNOTE[(k, w)] = f"The live workflow's Week {w} email says \"{bad}\" in the body. Corrected to \"{good}\" here. Fix the live workflow too."
E = html.escape

def cp(val):
    return f'<button class="tagbtn" data-tag="{E(val)}">{E(val)} <span class="ic">copy</span></button>'

def crumbs(*parts):
    return " → ".join(f'<span class="crumb">{E(p)}</span>' for p in parts)

def table(head, rows, cls=""):
    th = "".join(f"<th>{h}</th>" for h in head)
    trs = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
    return f'<div class="tblwrap {cls}"><table><thead><tr>{th}</tr></thead><tbody>{trs}</tbody></table></div>'

def step(n, title, body):
    return f'<div class="card" id="s{n}"><div class="chead"><div class="num">{n}</div><h3>{title}</h3></div>{body}</div>'

def part(kicker, title, lead=""):
    return f'<section><div class="kicker">{E(kicker)}</div><h2>{E(title)}</h2>{("<p class=lead>"+lead+"</p>") if lead else ""}'

MEN = ["The Hardest Lesson Most Men Need to Learn", "Becoming the Man You Want to Be", "Clean Up Your Side of the Street",
       "Say Less, Say It Better", "Letting Go of What You're Carrying", "What she needs might not be what she says",
       "Understanding Her Without Losing Yourself", "What You Reinforce Grows", "Get Clear on Where You're Going",
       "Rebuilding Intimacy and Connection", "Trust, Betrayal, and What Comes Next", "Building What Comes Next"]
WOMEN = ["Starting where you actually are", "This is where things start to shift", "Allowing yourself to want more",
         "Taking a deeper look at your role", "Letting Go of what you have been carrying", "How you communicate changes everything",
         "Stepping into your Queen Energy", "Understanding how he operates", "Rebuilding Trust with yourself and others",
         "Shifting what you focus on", "Letting yourself be closer", "Taking this with you"]

lesson_rows = [[f"<b>{i}</b>", E(m), E(w), f"Week {i} Check-In"] for i, (m, w) in enumerate(zip(MEN, WOMEN), 1)]

week_counts = [("1", 5, "No catch-up. Add the normal tags today."), ("2", 10, "Catch-up"), ("3", 9, "Catch-up"), ("4", 6, "Catch-up"),
               ("5", 7, "Catch-up"), ("6", 8, "Catch-up"), ("7", 12, "Catch-up"), ("8", 3, "Catch-up"), ("9", 3, "Catch-up")]

# ------------------------------------------------------------------ loop diagram
def box(x, y, w, h, lines, dashed=False):
    lines = lines if isinstance(lines, list) else [lines]
    ty = y + h/2 - (len(lines)-1)*8.5
    ts = "".join(f'<tspan x="{x+w/2}" dy="{0 if i==0 else 17}">{E(l)}</tspan>' for i, l in enumerate(lines))
    dash = ' stroke-dasharray="6 4"' if dashed else ""
    return f'<rect class="node" x="{x}" y="{y}" width="{w}" height="{h}" rx="12"{dash}/><text class="ntext" x="{x+w/2}" y="{ty}" text-anchor="middle" dominant-baseline="middle">{ts}</text>'
def pill(cx, cy, t):
    w = len(t)*6.9 + 24
    return f'<rect class="pill" x="{cx-w/2}" y="{cy-12}" width="{w}" height="24" rx="12"/><text class="ptext" x="{cx}" y="{cy+1}" text-anchor="middle" dominant-baseline="middle">{E(t)}</text>'
def path(d, cls="edge"):
    return f'<path class="{cls}" d="{d}" marker-end="url(#arr)"/>'

svg = f'''
<svg viewBox="0 0 900 470" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Catch-up loop">
  <defs><marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#6B6459"/></marker></defs>
  {box(40, 30, 200, 54, ["Tag added", "catchup- rmm (men)"])}
  {box(320, 30, 240, 54, ["If/Else on RMM Week", "branches 1 to 6, none → next"])}
  {box(620, 30, 240, 54, ["If/Else on RMM Week", "branches 7 to 12"])}
  {pill(450, 135, "week = 7")}
  {box(330, 170, 240, 50, "Send lesson 7 email")}
  {box(330, 250, 240, 50, "Wait 7 days")}
  {box(330, 330, 240, 50, "Set RMM Week = 8")}
  {box(330, 410, 240, 50, ["Remove tag, wait 1 min,", "add tag again"])}
  {box(640, 330, 220, 50, ["Branch 12: send lesson 12,", "remove tag, end"], dashed=True)}
  {path("M240,57 L316,57")}
  {path("M560,57 L616,57")}
  {path("M740,84 L740,110 Q740,118 732,118 L470,118 Q460,118 460,126 L460,122")}
  {path("M450,147 L450,166")}
  {path("M450,220 L450,246")}
  {path("M450,300 L450,326")}
  {path("M450,380 L450,406")}
  {path("M330,435 L300,435 Q290,435 290,425 L290,110 Q290,100 300,100 L440,100 Q450,100 450,92 L450,88", "edge loop")}
  <text class="ltext" x="40" y="120">Re-entry: the contact comes</text>
  <text class="ltext" x="40" y="138">back in and lands in the</text>
  <text class="ltext" x="40" y="156">next branch</text>
</svg>'''

steps = []

# ---------------------------------------------------------------- PART A
steps.append(part("Part A", "Prepare, 3 steps", "One field, four tags, and the emails saved as templates so the loop can pick them."))
steps.append(step(1, "Create the two week fields", f'''
<p>Go to {crumbs("Settings", "Custom Fields", "Add Field")} and create both. One drives the RMM loops, the other drives the check-in loops. They are separate so the two loops never overwrite each other's number.</p>
{table(["Setting", "Field 1, for the RMM loops", "Field 2, for the check-in loops"], [
    ["Object", "Contact", "Contact"],
    ["Type", "Number", "Number"],
    ["Name", cp("RMM Week"), cp("Check-In Week")],
    ["Key, fills in by itself", "<code>rmm_week</code>", "<code>checkin_week</code>"],
    ["Folder", "Contact, or wherever program_start_date lives", "Same folder"],
    ["Description", "Current RMM week, 1 to 12. Set at enrollment, moved up by 1 every 7 days by the Catch-Up RMM workflows.", "Current check-in week, 1 to 12. Set at enrollment, moved up by 1 every 7 days by the Catch-Up Check-In workflows."],
])}
<p class="small">Each number decides which branch the contact lands in for its own loop, and moves up by one every 7 days inside that loop.</p>
'''))
steps.append(step(2, "Create the four trigger tags", f'''
<p>Go to {crumbs("Settings", "Tags")} and add these exactly.</p>
{table(["Tag", "Starts"], [
    [cp("catchup- rmm (men)"), "Catch-Up RMM (men)"],
    [cp("catchup- rmm (women)"), "Catch-Up RMM (women)"],
    [cp("catchup- checkin (men)"), "Catch-Up Check-In (men)"],
    [cp("catchup- checkin (women)"), "Catch-Up Check-In (women)"],
])}
<div class="note"><b>Do not reuse the normal tags.</b> <code>general- rrm men</code>, <code>general- rmm women</code> and the two <code>rmm- checkin</code> tags always start at week 1. That is the whole reason the catch-up exists.</div>
'''))
steps.append(step(3, "Know where each week's email text lives", f'''
<p>The four live sequences are plain text typed straight into each Send Email action. There are no templates to pick, so the catch-up branches are built by <b>copying the text out of the live action and pasting it into the new one</b>. Keep both workflows open in two tabs.</p>
{table(["Sequence", "Where the text is"], [
    ["Men's lessons", crumbs("Automation", "Workflows", "GENERAL- RMM Men 12 Weeks with Calls")],
    ["Women's lessons", crumbs("Automation", "Workflows", "RMM Women 12 Weeks with Calls- GENERAL")],
    ["Check-ins", crumbs("Automation", "Workflows", "Check-In Sequence (men)") + " and (women)"],
])}
<p><b>Shortcut:</b> every week's subject and message for all four sequences is already on this page, in the <a href="#emails">Email copy</a> section at the bottom, each with a copy button. Copy from there. The live workflows are the fallback if anything looks off. This map shows which subject belongs to which week:</p>
{table(["Week", "Men's lesson subject", "Women's lesson subject", "Check-in subject"], lesson_rows, "mapTbl")}
<div class="note"><b>Copy each week exactly, do not reuse one email with the week number changed.</b> Every check-in week has its own Typeform link and its own middle line. Week 1 links to <code>form.typeform.com/to/iVaUVrNq</code>, Week 7 to <code>form.typeform.com/to/uA5xMksu</code>, and the women's check-ins use a different set of forms again. Copy each week from the matching gender's workflow, or clients land on the wrong form.</div>
<p class="small">Skip the day 0 emails, the intro and the baseline snapshot. Everyone on the catch-up list is past week 1.</p>
'''))
steps.append("</section>")

# ---------------------------------------------------------------- PART B
steps.append(part("Part B", "Build the first loop, 5 steps", "Build Catch-Up RMM (men) completely, test it, then clone it three times in Part C."))
steps.append(step(4, "Create the first of four workflows", f'''
<p>There will be four workflows in the end, one per sequence and gender. Build the <b>men's RMM</b> one fully in steps 4 to 8, then clone it for the other three in step 9. Do not build the four from scratch.</p>
{table(["Workflow", "Trigger tag", "Emails pasted from", "Built in"], [
    [cp("Catch-Up RMM (men)"), cp("catchup- rmm (men)"), "GENERAL- RMM Men 12 Weeks with Calls", "Steps 4 to 8"],
    [cp("Catch-Up RMM (women)"), cp("catchup- rmm (women)"), "RMM Women 12 Weeks with Calls- GENERAL", "Step 9, clone"],
    [cp("Catch-Up Check-In (men)"), cp("catchup- checkin (men)"), "Check-In Sequence (men)", "Step 9, clone"],
    [cp("Catch-Up Check-In (women)"), cp("catchup- checkin (women)"), "Check-In Sequence (women)", "Step 9, clone"],
])}
<p>Go to {crumbs("Automation", "Workflows", "Create Workflow", "Start from Scratch")}.</p>
<div class="kv"><span class="k">Name</span><span>{cp("Catch-Up RMM (men)")}</span></div>
<p>Open <b>Settings</b> at the top and turn on <b>Allow Re-Entry</b>. Without it the loop stops after the first week.</p>
'''))
steps.append(step(5, "Add the trigger", f'''
{table(["Setting", "Value"], [
    ["Trigger", "Contact Tag"],
    ["Filter", "Tag added"],
    ["Tag", cp("catchup- rmm (men)")],
])}
'''))
steps.append(step(6, "Add two If/Else blocks on RMM Week", f'''
<p>Add an <b>If/Else</b> block named <b>Weeks 1 to 6</b> with six branches. Each branch has one condition:</p>
{table(["Branch", "Condition"], [[f"Week {i}", f"Custom Field <b>RMM Week</b> · Is · <b>{i}</b>"] for i in range(1, 7)])}
<p>On its <b>None</b> path add a second If/Else named <b>Weeks 7 to 12</b> with branches for 7 to 12 the same way.</p>
<p class="small">Two blocks because an If/Else holds at most 10 branches.</p>
'''))
steps.append(step(7, "Fill in every branch, same six actions", f'''
<p><b>Where to connect:</b> under each Week card there is a small <b>+</b> sitting above the grey <b>END</b>. Click that + to add the first action. Each action you save shows a new + under it for the next one. The chain ends at the same END that is already there.</p>
<p>Start with the <b>Week 1</b> card and add these six, in this order. Only the template and the field value change from branch to branch.</p>
{table(["#", "Click + then choose", "In the panel that opens", "Week 1 example"], [
    ["1", "<b>Send Email</b>", "From name <b>Sophie Orozco Coaching</b>, from email <b>hello@sophieorozco.com</b>. Paste this week's subject into Subject and this week's message into the message box, both from the <a href='#emails'>Email copy</a> section below. Keep <code>{{{{contact.first_name}}}}</code> as is. Save.", "<a href='#em-rmm_men-1'>RMM men, Week 1</a>"],
    ["2", "<b>Wait</b>", "Wait type <b>Time Delay</b>. Enter the number and pick Days. Save.", "<b>7</b> Days"],
    ["3", "<b>Update Contact Field</b>", "Field <b>RMM Week</b>. Type the next week's number in the value box. Save.", "RMM Week = <b>2</b>"],
    ["4", "<b>Remove Contact Tag</b>", "Pick the workflow's own trigger tag. Save.", cp("catchup- rmm (men)")],
    ["5", "<b>Wait</b>", "Time Delay, <b>1</b> Minute. This gap lets the remove finish before the add. Save.", "1 Minute"],
    ["6", "<b>Add Contact Tag</b>", "The same trigger tag again. Save.", cp("catchup- rmm (men)")],
])}
<p>Action 6 is what makes it a loop. Adding the tag fires the trigger again, the contact re-enters, and because the field now says 2 they land in the Week 2 card. Nothing needs to be drawn between branches.</p>
<p>Repeat for Week 2 through Week 11, changing two things each time:</p>
{table(["Branch", "Action 1 pastes the live step for", "Action 3 sets RMM Week to"], [[f"Week {i}", f"Week {i}", f"<b>{i+1}</b>"] for i in range(1, 12)])}
<div class="note"><b>Week 12 gets only two actions.</b> Send Email with the live Week 12 text, then Remove Contact Tag. No field update, no add tag. Leave it on END. If you add the tag back, the contact re-enters with RMM Week = 13, matches nothing, and falls into the None path.</div>
<p><b>Both None cards.</b> The None under Weeks 1 to 6 already holds the Weeks 7 to 12 block, which is right. The None under Weeks 7 to 12 only fires if RMM Week is blank or outside 1 to 12. Leave it on END, or add one <b>Send Internal Notification</b> to yourself there so a mis-set field gets noticed.</p>
<p><b>Before you save the workflow:</b> open <b>Settings</b> at the top of the builder and confirm <b>Allow Re-Entry</b> is on. It is off by default, and without it the contact is blocked at action 6 and the loop stops after one week.</p>
'''))
steps.append(step(8, "Test it before cloning", f'''
<p>Temporarily change the 7 day wait in branches 11 and 12 to <b>2 minutes</b>. Then on a test contact:</p>
{table(["Do", "Expect"], [
    ["Set RMM Week to 11, add the tag", "Lesson 11 email arrives right away"],
    ["Wait 3 minutes", "RMM Week reads 12, the tag was removed and re-added"],
    ["Open Enrollment History", "The contact shows two enrollments"],
    ["Check the inbox", "Lesson 12 arrived, tag is gone, no third enrollment"],
])}
<p>Put both waits back to <b>7 days</b> and save. Publish only after that.</p>
'''))
steps.append("</section>")

# ---------------------------------------------------------------- PART C
steps.append(part("Part C", "Clone it three times, 1 step"))
steps.append(step(9, "Clone and swap", f'''
<p>On the workflow list, open the <b>⋯</b> menu on Catch-Up RMM (men) and choose <b>Clone</b>. For each clone change only three things: the name, the trigger tag, and the 12 email texts.</p>
{table(["Clone name", "Trigger tag", "Paste the emails from"], [
    [cp("Catch-Up RMM (women)"), cp("catchup- rmm (women)"), "RMM Women 12 Weeks with Calls- GENERAL, weeks 1 to 12"],
    [cp("Catch-Up Check-In (men)"), cp("catchup- checkin (men)"), "Check-In Sequence (men), weeks 1 to 12"],
    [cp("Catch-Up Check-In (women)"), cp("catchup- checkin (women)"), "Check-In Sequence (women), weeks 1 to 12"],
])}
<p class="small">The remove and add tag actions in every branch must also point at the clone's own tag. Check all 12 branches, it is the easiest thing to miss.</p>
<div class="note"><b>The two check-in clones also switch fields.</b> In both If/Else blocks change every condition from RMM Week to <b>Check-In Week</b>, and in branches 1 to 11 change the Update Contact Field action to set <b>Check-In Week</b>. That is 12 conditions and 11 updates per clone. The RMM women clone keeps RMM Week.</div>
'''))
steps.append("</section>")

# ---------------------------------------------------------------- PART D
steps.append(part("Part D", "Enroll the clients, 3 steps", "The cleaned list with contact IDs is the file Catch-Up-Clients.csv. It says, per client, the week, the gender, and whether they need one sequence or both."))
steps.append(step(10, "Fix the data first", f'''
{table(["Client", "Problem", "Fix"], [
    ["Can (John) Evizi, Alex Baldassari", "Not found in GHL", "Hazel confirms the name or email on their record"],
    ["Melissa Gorsich Reitter, Oli Adams, Steve Piorro, Bjarni Freyr, Jed Padilla, Javier Alcover, Vadim Kuzilov", "No program tag, so no gender", "Hazel or Luann confirms men or women, and the program"],
    ["Kali Piorro, Paul Fluharty", "Tagged couples coaching with no gender", "Confirm men or women"],
    ["Nick Cazel", "Sheet carries Heather Kauffman's email", "Confirm his own email"],
    ["Lacey Williams", "No email on the sheet", "Confirm the email"],
    ["Curtis Spearman", "Listed twice", "Enroll once"],
    ["Shea Fehrenbach, Deborah Mitter", "Hazel flagged wrong tag", "Confirm the program before enrolling"],
])}
'''))
steps.append(step(11, "Confirm the week on enrollment day", f'''
<p>Hazel's weeks were correct on the day she calculated them, Sept 28. The rule is: <b>full weeks since the start date, plus one</b>. A client who started July 29 is in week 9 on Sept 28 and week 10 from Sept 30. Recalculate on the enrollment day itself, never from the sheet's column, or clients who rolled over since receive the week they just finished.</p>
<div class="note"><b>Done Sept 30:</b> 43 clients enrolled at that day's week, women's RMM loop, both check-in loops, and 3 week 1 clients on the normal tags. The 40 men's RMM enrollments wait on the email fix in Catch-Up RMM (men).</div>
{table(["Current week on the sheet", "Clients", "Action"], [[f"Week {w}", str(n), a] for w, n, a in week_counts])}
<p class="small">Week 1 clients get the normal tags from the <a href="https://client-tagging-sop.vercel.app" target="_blank" rel="noopener">Client Tagging SOP</a> instead. Their sequences start at week 1 as designed.</p>
'''))
steps.append(step(12, "Enroll in batches, one week at a time", f'''
<p>Do it by week so a mistake only touches a few people. For each client:</p>
{table(["#", "Action"], [
    ["1", "Open the contact, set <b>RMM Week</b> to the client's current week. If they also need check-ins, set <b>Check-In Week</b> to the same number"],
    ["2", "Add " + cp("catchup- rmm (men)") + " or " + cp("catchup- rmm (women)")],
    ["3", "If the list says they also need check-ins, add " + cp("catchup- checkin (men)") + " or " + cp("catchup- checkin (women)")],
    ["4", "Open Conversations on the contact and confirm the week's email went out"],
])}
<p class="small">Faster path once the first batch checks out: {crumbs("Contacts", "Import")} the CSV, choose <b>update existing contacts by email</b>, map the week column to RMM Week and to Check-In Week, and a tags column to Tags. The import applies the tags, which starts the loops.</p>
<div class="note"><b>The first email sends the moment the tag lands.</b> Enroll during working hours, and if the team wants to keep check-ins on Fridays, enroll on a Friday.</div>
'''))
steps.append("</section>")

# ---------------------------------------------------------------- PART E
steps.append(part("Part E", "Verify after 7 days, 1 step"))
steps.append(step(13, "Spot check three clients", f'''
<p>Pick one client each from an early, middle and late week. On day 8 after enrollment check:</p>
{table(["Check", "Expect"], [
    ["RMM Week, and Check-In Week if enrolled in check-ins", "Each one higher than the day they were enrolled"],
    ["Tags", "The catch-up tag is present again"],
    ["Conversations", "Next week's lesson, and check-in if enrolled, went out on day 7"],
    ["Enrollment History on the workflow", "Two entries for the contact"],
])}
<p>If all three pass, the loop is running for everyone.</p>
'''))
steps.append("</section>")

# ---------------------------------------------------------------- PART F: email copy
GROUPS = [("rmm_men", "RMM lessons, men", "Paste into Catch-Up RMM (men). From GENERAL- RMM Men 12 Weeks with Calls."),
          ("rmm_women", "RMM lessons, women", "Paste into Catch-Up RMM (women). From RMM Women 12 Weeks with Calls- GENERAL."),
          ("checkin_men", "Check-ins, men", "Paste into Catch-Up Check-In (men). From Check-In Sequence (men). Each week has its own Typeform link."),
          ("checkin_women", "Check-ins, women", "Paste into Catch-Up Check-In (women). From Check-In Sequence (women). Each week has its own Typeform link.")]
steps.append('<section id="emails"><div class="kicker">Email copy</div><h2>Every week, ready to paste</h2>'
             '<p class="lead">Taken from the emails these sequences actually sent, with the client\'s name swapped for the merge field. '
             'Copy subject and body straight into the Send Email action of the matching branch.</p>'
             '<div class="jump">' + "".join(f'<a href="#em-{k}">{E(t)}</a>' for k, t, _ in GROUPS) + '</div></section>')
for key, title, lead in GROUPS:
    cards = []
    for wk in range(1, 13):
        e = EMAILS.get(key, {}).get(str(wk))
        if not e:
            cards.append(f'<div class="mailcard" id="em-{key}-{wk}"><div class="mhead"><span class="wk">Week {wk}</span><span class="subj">No sent copy exists yet</span></div>'
                         f'<p class="small" style="padding:12px 16px">Nobody has reached this week in this sequence, so there is no sent email to copy. Open the live workflow, click the Week {wk} step, and copy the subject and message from there.</p></div>')
            continue
        cards.append(f'''<div class="mailcard" id="em-{key}-{wk}">
  <div class="mhead"><span class="wk">Week {wk}</span><span class="subj">{E(e["subject"])}</span><button class="cpy" data-what="subject">copy subject</button></div>
  <div class="mbody"><pre class="mailtxt">{E(e["body"])}</pre><button class="cpy body" data-what="body">copy body</button></div>
  {('<div class="note" style="margin:0 16px 16px">' + E(FIXNOTE[(key, str(wk))]) + '</div>') if (key, str(wk)) in FIXNOTE else ''}
</div>''')
    steps.append(f'<section id="em-{key}" class="emgroup"><h2 class="h2s">{E(title)}</h2><p class="lead">{E(lead)}</p>{"".join(cards)}</section>')

body = "".join(steps)

page = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="robots" content="noindex">
<title>RMM Catch-Up Workflow — Setup Plan</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@500;600&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
  :root{{
    --cream:#F7F4EE; --card:#FFFFFF; --ink:#1E1B16; --muted:#6B6459;
    --terra:#A9502C; --terra-soft:#F3E3DA; --green:#1D4A33; --green-soft:#E4EEE7;
    --gold:#B98A2F; --line:#E4DDD2; --warn-bg:#FBEFE7; --warn:#8C3D14;
  }}
  *{{box-sizing:border-box;margin:0;padding:0}}
  body{{background:var(--cream);color:var(--ink);font-family:'Inter',system-ui,sans-serif;line-height:1.65;font-size:16px}}
  .wrap{{max-width:980px;margin:0 auto;padding:0 20px 90px}}
  header.hero{{background:var(--ink);color:#F7F4EE;padding:48px 20px 40px;text-align:center}}
  .hero .brand{{font-family:'Playfair Display',serif;font-size:14px;letter-spacing:.18em;text-transform:uppercase;color:#CDB68A;margin-bottom:12px}}
  .hero h1{{font-family:'Playfair Display',serif;font-size:clamp(28px,5vw,40px);font-weight:600;line-height:1.15;margin-bottom:12px}}
  .hero p{{color:#BFB8AC;max-width:660px;margin:0 auto;font-size:15.5px}}
  section{{margin-top:44px}}
  h2{{font-family:'Playfair Display',serif;font-size:clamp(22px,3.4vw,28px);font-weight:600;margin-bottom:8px}}
  .lead{{color:var(--muted);font-size:15px;margin-bottom:4px}}
  .kicker{{color:var(--terra);font-weight:700;font-size:12.5px;letter-spacing:.14em;text-transform:uppercase;margin-bottom:6px}}
  code{{font-family:ui-monospace,monospace;font-size:12.5px;background:#F4F1EA;border:1px solid var(--line);border-radius:5px;padding:1px 6px}}
  .small{{font-size:14px;color:var(--muted)}}
  .stats{{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:14px;margin-top:16px}}
  .stat{{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:16px 18px}}
  .stat .v{{font-family:'Playfair Display',serif;font-size:32px;font-weight:600;color:var(--green);line-height:1.1}}
  .stat .l{{font-size:13px;color:var(--muted);margin-top:4px}}
  .why{{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:14px;margin-top:16px}}
  .wbox{{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:18px}}
  .wbox .n{{display:inline-flex;align-items:center;justify-content:center;width:28px;height:28px;border-radius:50%;background:var(--terra);color:#fff;font-weight:700;font-size:13px;margin-bottom:8px}}
  .wbox b{{display:block;margin-bottom:4px;font-size:15px}}
  .wbox p{{font-size:13.5px;color:var(--muted)}}
  .diagram{{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:18px 10px 8px;margin-top:16px}}
  .diagram svg{{width:100%;height:auto;display:block}}
  .node{{fill:#FBF9F5;stroke:var(--green);stroke-width:1.6}}
  .ntext{{font-family:'Inter',sans-serif;font-size:13.5px;font-weight:600;fill:var(--ink)}}
  .ltext{{font-family:'Inter',sans-serif;font-size:12.5px;fill:var(--muted)}}
  .pill{{fill:var(--terra-soft);stroke:var(--terra);stroke-width:1}}
  .ptext{{font-family:'Inter',sans-serif;font-size:12px;font-weight:600;fill:var(--terra)}}
  .edge{{fill:none;stroke:#6B6459;stroke-width:1.4}}
  .loop{{stroke:var(--terra);stroke-dasharray:5 4}}
  .card{{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:26px;margin-top:18px;scroll-margin-top:16px}}
  .chead{{display:flex;gap:14px;align-items:center;padding-bottom:14px;border-bottom:1px solid var(--line);margin-bottom:16px}}
  .num{{flex:none;width:34px;height:34px;border-radius:50%;background:var(--green);color:#fff;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:15px}}
  .card h3{{font-family:'Playfair Display',serif;font-size:21px;font-weight:600;line-height:1.25}}
  .card p{{margin-bottom:10px}}
  .card a{{color:var(--green);font-weight:600}}
  .crumb{{display:inline-block;background:#F4F1EA;border:1px solid var(--line);border-radius:6px;padding:1px 8px;font-size:14px;font-weight:600;white-space:nowrap}}
  .kv{{display:grid;grid-template-columns:auto 1fr;gap:8px 14px;align-items:center;margin:8px 0 12px;font-size:14.5px}}
  .kv .k{{color:var(--muted);font-weight:600;white-space:nowrap}}
  .tagbtn{{display:inline-flex;align-items:center;gap:8px;background:#F4F1EA;border:1px solid var(--line);border-radius:8px;padding:6px 12px;font-family:ui-monospace,monospace;font-size:13px;color:var(--ink);cursor:pointer;transition:.15s;text-align:left;margin:2px 6px 2px 0}}
  .tagbtn:hover{{background:var(--terra-soft);border-color:var(--terra)}}
  .tagbtn.copied{{background:var(--green-soft);border-color:var(--green);color:var(--green)}}
  .tagbtn .ic{{opacity:.5;font-size:11.5px}}
  .tblwrap{{overflow-x:auto;background:#FBF9F5;border:1px solid var(--line);border-radius:12px;margin:8px 0 14px}}
  table{{width:100%;border-collapse:collapse;font-size:14px}}
  th{{text-align:left;font-size:11.5px;letter-spacing:.08em;text-transform:uppercase;color:var(--green);padding:10px 14px;border-bottom:1px solid var(--line);line-height:1.35;vertical-align:bottom}}
  td{{padding:9px 14px;border-bottom:1px solid var(--line);vertical-align:middle}}
  tr:last-child td{{border-bottom:none}}
  .mapTbl td{{font-size:13.5px}}
  .note{{background:var(--warn-bg);border-left:4px solid var(--terra);border-radius:0 12px 12px 0;padding:12px 16px;margin:12px 0 4px;font-size:14px;color:var(--warn)}}
  .note b{{color:var(--warn)}}
  .note code{{background:#fff}}
  .jump{{display:flex;gap:10px;flex-wrap:wrap;margin-top:14px}}
  .jump a{{background:var(--card);border:1px solid var(--line);border-radius:999px;padding:7px 14px;font-size:13.5px;font-weight:600;color:var(--green);text-decoration:none}}
  .jump a:hover{{border-color:var(--terra);color:var(--terra)}}
  .emgroup{{margin-top:36px}}
  .h2s{{font-size:22px}}
  .mailcard{{background:var(--card);border:1px solid var(--line);border-radius:14px;margin-top:14px;overflow:hidden;scroll-margin-top:16px}}
  .mhead{{display:flex;align-items:center;gap:12px;padding:12px 16px;border-bottom:1px solid var(--line);background:#FBF9F5}}
  .mhead .wk{{flex:none;font-size:11.5px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:#fff;background:var(--green);border-radius:999px;padding:3px 10px}}
  .mhead .subj{{flex:1;font-weight:600;font-size:15px}}
  .mbody{{position:relative;padding:14px 16px 16px}}
  .mailtxt{{font-family:'Inter',system-ui,sans-serif;font-size:14.5px;line-height:1.6;white-space:pre-wrap;word-break:break-word;margin:0;max-height:360px;overflow-y:auto;padding-right:110px}}
  .cpy{{flex:none;background:#F4F1EA;border:1px solid var(--line);border-radius:999px;padding:5px 12px;font-size:12.5px;font-weight:600;color:var(--ink);cursor:pointer;font-family:inherit;transition:.15s}}
  .cpy:hover{{background:var(--terra-soft);border-color:var(--terra)}}
  .cpy.done{{background:var(--green-soft);border-color:var(--green);color:var(--green)}}
  .cpy.body{{position:absolute;top:12px;right:16px}}
  footer{{margin-top:60px;padding-top:22px;border-top:1px solid var(--line);color:var(--muted);font-size:13px;display:flex;justify-content:space-between;flex-wrap:wrap;gap:8px}}
  .toast{{position:fixed;bottom:24px;left:50%;transform:translateX(-50%) translateY(80px);background:var(--ink);color:#F7F4EE;padding:11px 20px;border-radius:999px;font-size:14px;transition:.25s;pointer-events:none;opacity:0}}
  .toast.show{{transform:translateX(-50%) translateY(0);opacity:1}}
  .top{{position:fixed;right:20px;bottom:24px;background:var(--ink);color:#F7F4EE;border:none;border-radius:999px;padding:11px 18px;font-size:13px;cursor:pointer;opacity:0;transition:.2s;font-family:inherit}}
  .top.show{{opacity:.92}}
</style>
</head>
<body>

<header class="hero">
  <div class="brand">Sophie Orozco Coaching</div>
  <h1>RMM Catch-Up Workflow: Setup Plan</h1>
  <p>How to put the clients who missed the RMM 12 week emails and the weekly check-ins back on track at the week they are actually in, using four small loop workflows in GHL.</p>
</header>

<div class="wrap">

<section>
  <div class="kicker">The situation</div>
  <h2>Who this is for</h2>
  <p class="lead">From Hazel's list, matched to GHL on Sept 29, 2026.</p>
  <div class="stats">
    <div class="stat"><div class="v">63</div><div class="l">clients on the list, weeks 1 to 9</div></div>
    <div class="stat"><div class="v">63</div><div class="l">missing the RMM 12 week emails</div></div>
    <div class="stat"><div class="v">36</div><div class="l">also missing the weekly check-ins</div></div>
    <div class="stat"><div class="v">11</div><div class="l">need a data fix first (step 10)</div></div>
  </div>
</section>

<section>
  <div class="kicker">Why a normal tag will not do</div>
  <h2>The problem, in three lines</h2>
  <div class="why">
    <div class="wbox"><span class="n">1</span><b>The sequences always start at week 1</b><p>Both published sequences send the day 0 email, then week 1, then one email every 7 days. There is no way to start a contact at week 7.</p></div>
    <div class="wbox"><span class="n">2</span><b>GHL cannot skip steps</b><p>A workflow runs top to bottom. An If/Else branch does not merge back, so "skip the first six weeks" cannot be built inside the existing workflow.</p></div>
    <div class="wbox"><span class="n">3</span><b>So the catch-up loops instead</b><p>A number field says which week the client is in. The workflow sends that week's email, waits 7 days, moves the number up, and re-enters itself.</p></div>
  </div>
</section>

<section>
  <div class="kicker">The design</div>
  <h2>One loop, four copies</h2>
  <p class="lead">Catch-Up RMM (men), Catch-Up RMM (women), Catch-Up Check-In (men), Catch-Up Check-In (women). Same shape, different tag and templates.</p>
  <div class="diagram">{svg}</div>
  {table(["Piece", "What it is"], [
      ["<b>RMM Week</b> and <b>Check-In Week</b>", "Two number fields on the contact, one per loop type. Set once at enrollment, then each loop moves its own field up by one each week. Separate fields so the RMM loop and the check-in loop never overwrite each other."],
      ["<b>Trigger tag</b>", "One per workflow, for example <code>catchup- rmm (men)</code>. Adding it enrolls the contact. The loop removes and re-adds it every 7 days."],
      ["<b>Two If/Else blocks</b>", "Weeks 1 to 6 and weeks 7 to 12, because one If/Else holds at most 10 branches."],
      ["<b>Each branch</b>", "Send that week's email, wait 7 days, set RMM Week to the next number, remove the tag, add it back."],
      ["<b>Allow Re-Entry</b>", "On, in the workflow settings. This is what lets the re-added tag bring the contact back in."],
  ])}
</section>

{body}

<footer>
  <span>RMM Catch-Up Workflow · Setup Plan · Updated Sept 29, 2026</span>
  <span>Maintained by John Carlo Caintic</span>
</footer>

</div>

<div class="toast" id="toast">Copied</div>
<button class="top" id="top">↑ Top</button>

<script>
  const toast = document.getElementById('toast');
  document.querySelectorAll('.tagbtn').forEach(btn => {{
    btn.addEventListener('click', async () => {{
      const t = btn.dataset.tag;
      try {{ await navigator.clipboard.writeText(t); }}
      catch (e) {{ const ta = document.createElement('textarea'); ta.value = t; document.body.appendChild(ta); ta.select(); try {{ document.execCommand('copy'); }} catch (err) {{}} document.body.removeChild(ta); }}
      btn.classList.add('copied');
      const ic = btn.querySelector('.ic'); const old = ic.textContent; ic.textContent = 'copied ✓';
      toast.textContent = 'Copied: ' + t; toast.classList.add('show');
      setTimeout(() => {{ btn.classList.remove('copied'); ic.textContent = old; toast.classList.remove('show'); }}, 1600);
    }});
  }});
  document.querySelectorAll('.cpy').forEach(btn => {{
    btn.addEventListener('click', async () => {{
      const card = btn.closest('.mailcard');
      const t = btn.dataset.what === 'subject' ? card.querySelector('.subj').textContent : card.querySelector('.mailtxt').textContent;
      try {{ await navigator.clipboard.writeText(t); }}
      catch (e) {{ const ta = document.createElement('textarea'); ta.value = t; document.body.appendChild(ta); ta.select(); try {{ document.execCommand('copy'); }} catch (err) {{}} document.body.removeChild(ta); }}
      const old = btn.textContent; btn.textContent = 'copied ✓'; btn.classList.add('done');
      toast.textContent = (btn.dataset.what === 'subject' ? 'Subject' : 'Body') + ' copied'; toast.classList.add('show');
      setTimeout(() => {{ btn.textContent = old; btn.classList.remove('done'); toast.classList.remove('show'); }}, 1600);
    }});
  }});
  const topBtn = document.getElementById('top');
  topBtn.addEventListener('click', () => window.scrollTo({{top:0, behavior:'smooth'}}));
  window.addEventListener('scroll', () => topBtn.classList.toggle('show', window.scrollY > 700));
</script>
</body>
</html>
'''

open(OUT, "w", encoding="utf-8").write(page)
print("wrote", OUT, len(page), "bytes")
