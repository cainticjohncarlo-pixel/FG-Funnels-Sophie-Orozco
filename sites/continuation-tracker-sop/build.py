# -*- coding: utf-8 -*-
"""Continuation Tracker System SOP. Run: python build.py  ->  index.html  ->  vercel deploy --prod --yes"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "sop-lib"))
from sop_lib import page, flow, cp, table, steps, note, workflow_card, E

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "index.html")

big = flow([
    ("T", "Day 77 after the client's program start date"),
    ("A", "WF-CT1: tag graduated, card created at Graduated"),
    ("A", "Next Steps email: five program buttons, card moves to Outreach Sent"),
    ("W", "Wait 5 days"),
    ("D", "Did they click, reply or book?",
        [("A", "WF-CT2: tag continuation-engaged, card to Call Booked / Reply Received"), ("A", "Luann has the conversation")],
        [("A", "Card to Needs Follow-Up, task for Luann")], "Yes", "No"),
    ("D", "Did they buy?",
        [("A", "Enrolled tag added, WF-CT3 puts the card at Enrolled with the price")],
        [("A", "Day 90: WF-CT4 tags declined-all, card to Declined")], "Yes", "No, by day 90"),
], "The whole tracker")

cards = []

cards.append(workflow_card(1, "WF-CT1 Graduation Entry", "draft",
    "Puts every finishing client on the board one week before their program ends.",
    "Day 77 after <code>program_start_date</code>, for contacts carrying the tag <code>existing client</code>. Leads never enter.",
    ["The day arrives for that client.",
     "Adds the tag <code>graduated</code> to the contact.",
     "Creates a card for the client in the <b>Continuation Programs</b> pipeline at the <b>Graduated</b> stage, status Open.",
     "Ends. Re-entry is off, so a client is only ever entered once."],
    "Luann can see everyone who is about to finish, in one column, before anyone has to remember.",
    flow([("T", "Day 77 after program start, has existing client"), ("A", "Add tag graduated"), ("A", "Create card at Graduated"), ("E", "Done")], "WF-CT1 Graduation Entry")))

cards.append(workflow_card(2, "WF- Week 4, Week 5 and Week 9 Next Steps (the outreach)", "draft",
    "The what-comes-next email is the offer. It lives in the Client Journey milestone workflows and reports back to this pipeline.",
    "The milestone day arrives: day 28 for RMM Plus, day 35 for the 6-session programs, day 63 for RFB 1 Year.",
    ["Checks the program tag to decide men or women.",
     "Women receive <b>Let's Keep Going Together</b>. Men receive <b>Step Into Your Power</b>. Each email has five buttons, one per continuation program, and every button is a tracked link.",
     "Adds the tag <code>outreach sent</code>.",
     "Creates or updates the client's card at <b>Outreach Sent</b>.",
     "Waits 5 days.",
     "Checks for any enrolled tag or <code>continuation-engaged</code>. If found, ends, the client responded.",
     "If not, moves the card to <b>Needs Follow-Up</b> and creates the task <i>Continuation follow-up</i> for Luann, due in 3 days."],
    "Every graduate gets the offer at the right week, and anyone who goes quiet becomes a task for Luann five days later.",
    flow([("T", "Milestone day for a Next Steps email"), ("D", "Woman or man?", [("A", "Send Let's Keep Going Together, five buttons")], [("A", "Send Step Into Your Power, five buttons")], "Woman", "Man"),
          ("A", "Tag outreach sent, card to Outreach Sent"), ("W", "Wait 5 days"),
          ("D", "Clicked, replied or enrolled?", [("E", "Ends")], [("A", "Card to Needs Follow-Up, task for Luann")], "Yes", "No")], "The outreach steps"),
    table(["Button", "Program", "Price", "Tracked link"], [
        ["Women 1", "Radiant Feminine Blueprint, 6 months", "$4,997", "<code>Enroll-RFB-6mo</code>"],
        ["Women 2", "Radiant Feminine Blueprint, 1 year", "$8,500", "<code>Enroll-RFB-1yr</code>"],
        ["Men 1", "Forge, 6 months", "$4,997", "<code>Enroll-Forge-6mo</code>"],
        ["Men 2", "Forge, 1 year", "$8,500", "<code>Enroll-Forge-1yr</code>"],
        ["Both 3", "RMM Plus Coaching, 6 months", "$2,997", "<code>Enroll-RMMPlus</code>"],
        ["Both 4", "Continue with RMM, 6 months", "$2,000", "<code>Enroll-ContinueRMM-6mo</code>"],
        ["Both 5", "Continue with RMM, 3 months", "$1,500", "<code>Enroll-ContinueRMM-3mo</code>"],
    ])))

cards.append(workflow_card(3, "WF-CT2 Continuation Engagement", "draft",
    "Notices interest. A click, a reply or a booking moves the card so Luann reaches out while it is warm.",
    "Any one of three things: the client clicks one of the seven Enroll links, replies to the email, or books an appointment.",
    ["Checks the contact has the tag <code>outreach sent</code>. Anyone without it is not in the continuation flow, so their clicks, replies and bookings are ignored.",
     "Adds the tag <code>continuation-engaged</code>.",
     "Moves the card to <b>Call Booked / Reply Received</b>.",
     "Ends. Re-entry is on, so a second click or reply is fine, it just lands on the same stage."],
    "The Call Booked / Reply Received column is Luann's warm list. Nobody has to watch an inbox for clicks.",
    flow([("T", "Enroll link clicked, or reply, or appointment booked"), ("D", "Has outreach sent?", [("A", "Tag continuation-engaged"), ("A", "Card to Call Booked / Reply Received")], [("E", "Ignored")], "Yes", "No")], "WF-CT2 Continuation Engagement")))

cards.append(workflow_card(4, "WF-CT3 Continuation Enrolled", "draft",
    "One tag records the sale, the program and the price on the pipeline.",
    "One of the seven <code>enrolled-…</code> tags is added to the contact. Seven triggers, one per tag.",
    ["Reads which enrolled tag arrived.",
     "Moves the card to <b>Enrolled</b>.",
     "Sets the card's value to that program's price from the table.",
     "Ends."],
    "The revenue board fills itself. Whoever confirms a payment adds one tag and is done.",
    flow([("T", "An enrolled- tag added"), ("A", "Identify the program from the tag"), ("A", "Card to Enrolled"), ("A", "Set the value to the price"), ("E", "Done")], "WF-CT3 Continuation Enrolled"),
    table(["Client bought", "Tag to add", "Value recorded"], [
        ["Radiant Feminine Blueprint, 6 months", cp("enrolled-rfb-6mo"), "$4,997"],
        ["Radiant Feminine Blueprint, 1 year", cp("enrolled-rfb-1yr"), "$8,500"],
        ["Forge, 6 months", cp("enrolled-forge-6mo"), "$4,997"],
        ["Forge, 1 year", cp("enrolled-forge-1yr"), "$8,500"],
        ["RMM Plus Coaching", cp("enrolled-rmmplus"), "$2,997"],
        ["Continue with RMM, 6 months", cp("enrolled-continuermm-6mo"), "$2,000"],
        ["Continue with RMM, 3 months", cp("enrolled-continuermm-3mo"), "$1,500"],
    ])))

cards.append(workflow_card(5, "WF-CT4 Continuation Declined", "draft",
    "The sweep. Anyone who graduated and never enrolled is moved to Declined for a personal follow-up.",
    "Day 90 after <code>program_start_date</code>, for contacts carrying the tag <code>graduated</code>.",
    ["Checks for any of the seven enrolled tags.",
     "If one is there, the client enrolled. Ends, nothing changes.",
     "If none, adds the tag <code>declined-all</code> and moves the card to <b>Declined</b>."],
    "The Declined column is the list to call. Nobody who bought ever lands there.",
    flow([("T", "Day 90 after program start, has graduated"), ("D", "Any enrolled- tag?", [("E", "Ends, they enrolled")], [("A", "Tag declined-all, card to Declined")], "Yes", "No")], "WF-CT4 Continuation Declined")))

toc = "".join(f'<a href="#wf{i}"><span class="n">{i}</span>{E(n)}</a>' for i, n in enumerate([
    "WF-CT1 Graduation Entry", "Next Steps outreach", "WF-CT2 Continuation Engagement", "WF-CT3 Continuation Enrolled", "WF-CT4 Continuation Declined"], 1))

parts = table(["Piece", "Name in GHL", "What it is for"], [
    ["Pipeline", "<b>Continuation Programs</b>", "Six stages: Graduated, Outreach Sent, Call Booked / Reply Received, Needs Follow-Up, Enrolled, Declined. One card per graduate, moved by the workflows."],
    ["Date field", "<code>program_start_date</code>", "Set at Closed Won by the Client Journey System. Days 28, 35, 63, 77 and 90 all count from it."],
    ["Tag", "<code>existing client</code>", "Only clients enter WF-CT1."],
    ["Tag", "<code>graduated</code>", "Added by WF-CT1. Lets WF-CT4 find the graduates."],
    ["Tag", "<code>outreach sent</code>", "Added when the offer email goes out. The gate WF-CT2 checks."],
    ["Tag", "<code>continuation-engaged</code>", "Added by WF-CT2 on a click, reply or booking. Stops the 5-day follow-up task."],
    ["Tags", "<code>enrolled-rfb-6mo</code> and the other six", "Which program was bought. Starts WF-CT3 and stops WF-CT4."],
    ["Tag", "<code>declined-all</code>", "Added by WF-CT4. Declined every option."],
    ["Trigger links", "<code>Enroll-RFB-6mo</code> and the other six, plus seven <code>-installments</code> twins", "Tracked links behind the email buttons, pointing at the ThriveCart checkouts. A click is what WF-CT2 sees."],
    ["Emails", "Let's Keep Going Together, Step Into Your Power", "The women's and men's offer emails inside the three Next Steps workflows."],
])

human = table(["When", "What you do"], [
    ["A card lands in Call Booked / Reply Received", "The client clicked, replied or booked. Reach out while the interest is warm."],
    ["A Continuation follow-up task appears", "Five days passed with no response. Make the personal touch, then complete the task."],
    ["A client buys a continuation program", "Open their contact and add the one matching <code>enrolled-…</code> tag from the table in workflow 4. The pipeline does the rest."],
    ["A card lands in Declined", "Ninety days passed with no enrollment. This is the personal follow-up list."],
])

body = f'''
<section>
  <div class="kicker">Start here</div>
  <h2>What this system is</h2>
  <p class="lead">When a client reaches the end of their program, this system offers them the next one and keeps score. It puts every graduate on one pipeline board, sends the offer at the right week, notices who clicks or replies, records who buys and for how much, and lists who declined. Nothing here needs a spreadsheet, and the only human step is adding one tag when a payment is confirmed.</p>
  <p class="lead">Five pieces, listed in the order they happen. Each one names the workflow as it appears in GHL, what starts it, what it does step by step, and a flowchart.</p>
  <div class="toc">{toc}</div>
</section>

<section>
  <div class="kicker">The big picture</div>
  <h2>From graduation to the next program</h2>
  <div class="two"><div>{big}</div><div>
    <div class="lbl">The board Luann watches</div>
    {table(["Stage", "Who is in it"], [
        ["Graduated", "Finishing in a week, offer not sent yet"],
        ["Outreach Sent", "Offer email delivered, waiting"],
        ["Call Booked / Reply Received", "Clicked, replied or booked. Warm."],
        ["Needs Follow-Up", "Five days, no response. Task created."],
        ["Enrolled", "Bought, with the price on the card"],
        ["Declined", "Ninety days, no purchase"],
    ])}
    <div class="grid3" style="grid-template-columns:1fr">
      <div class="box"><span class="n">1</span><b>Same start date as the Client Journey</b><p>Day 77 and day 90 count from the date stamped at Closed Won. No second calendar.</p></div>
      <div class="box"><span class="n">2</span><b>Buttons are tracked links</b><p>Every Enroll button is a GHL trigger link. That is how a click in an inbox becomes a card move on the board.</p></div>
    </div>
  </div></div>
</section>

<section>
  <div class="kicker">The workflows</div>
  <h2>Five pieces, in the order they happen</h2>
  <p class="lead">All five are built in GHL. They switch on together once the Next Steps emails are finished, see the status at the bottom.</p>
  {"".join(cards)}
</section>

<section>
  <div class="kicker">The moving parts</div>
  <h2>Pipeline, tags, links and emails the system relies on</h2>
  <p class="lead">Renaming or deleting any of these breaks the tracker silently. Ask John before touching them.</p>
  {parts}
</section>

<section>
  <div class="kicker">Your part</div>
  <h2>The only things a person does</h2>
  {human}
  {note("<b>Who adds the enrolled tag.</b> RFB and Forge share one checkout, so the payment alone cannot tell them apart. Until that is automated, one person, Luann or Krissy as Chris decides, adds the tag when a payment is confirmed. That is the whole manual step.", "warn")}
</section>

<section>
  <div class="kicker">Status</div>
  <h2>What is done and what switches it on</h2>
  {table(["Piece", "Status", "Note"], [
      ["Continuation Programs pipeline, six stages", "Done", ""],
      ["Eleven tags", "Done", ""],
      ["Seven Enroll trigger links plus seven installment twins", "Done", "All point at the ThriveCart checkouts"],
      ["WF-CT1, WF-CT2, WF-CT3, WF-CT4", "Built, draft", "Publish in that order once the outreach emails are ready"],
      ["Next Steps outreach emails, five buttons each", "In progress", "Buttons wired to the trigger links, then the tracking steps under each email"],
      ["Day counts 77 and 90", "Set", "Assume a 12-week program. Adjust before publishing if any program runs longer"],
  ])}
  {note("<b>Before the first real graduate:</b> a test contact runs the whole path once, graduation, email, click, enrolled tag, follow-up task, declined sweep. Only then do the four WF-CT workflows go live.", "ok")}
</section>
'''

html_out = page("Continuation Tracker System — SOP", "Sophie Orozco Coaching", "Continuation Tracker System",
    "How a client moves from the end of their program to the next one: five workflows, one pipeline board, and one tag when they buy.",
    "Standard Operating Procedure · v2.0 · Sept 30, 2026", body, "Continuation Tracker System · SOP v2.0 · Sophie Orozco Coaching")
open(OUT, "w", encoding="utf-8").write(html_out)
print("wrote", OUT, len(html_out), "bytes")
