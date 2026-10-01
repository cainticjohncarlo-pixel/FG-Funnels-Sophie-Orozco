# -*- coding: utf-8 -*-
"""New Client Journey System SOP. Run: python build.py  ->  index.html  ->  vercel deploy --prod --yes"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "sop-lib"))
from sop_lib import page, flow, cp, table, steps, note, workflow_card, E

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "index.html")

# ------------------------------------------------------------------ big picture
big = flow([
    ("T", "Closer moves the card to Closed Won and adds the program tag"),
    ("A", "Onboarding email with the Circle link goes to the client"),
    ("A", "Program start date recorded, session count set, Luann alerted"),
    ("A", "Luann assigns the coach, coach receives the client brief"),
    ("A", "Luann's check-in emails and tasks: day 7, 21, 42, 63, 85, 90"),
    ("A", "Client milestone emails at week 3, 4, 5, 6, 9, 12, per program"),
    ("A", "Every coaching session counted on the record"),
    ("A", "Last session: coach alerted, client told what comes next"),
    ("A", "What-comes-next email offers the continuation programs"),
    ("E", "Continuation Tracker takes over"),
], "The whole journey")

cards = []

# 1 onboarding
cards.append(workflow_card(1, "Onboarding Email- (one per program and gender)", "live",
    "Ten small workflows, one per program. The client's first email, with their Circle community invitation.",
    "The closer adds the program tag to the contact, for example <code>client - rmm accelerator men</code>. Each tag starts its own workflow. Nothing else starts it.",
    ["Closer marks the sale Closed Won and adds the program tag, copied word for word from the <a href='https://client-tagging-sop.vercel.app' target='_blank' rel='noopener'>Client Tagging SOP</a>.",
     "The matching onboarding workflow starts within a minute.",
     "It sends the welcome email for that program, from hello@sophieorozco.com, with the Circle invitation link and the first steps.",
     "The workflow ends. It never sends anything else."],
    "The client hears from us minutes after buying. If the tag is wrong or missing, nothing sends and nobody is alerted, which is why the tagging SOP exists.",
    flow([("T", "Program tag added, e.g. client - rmm accelerator men"), ("A", "Send the program's onboarding email with the Circle link"), ("E", "Done")], "Onboarding Email")))

# 2 closed won setup
cards.append(workflow_card(2, "WF-Closed Won Client Setup", "draft",
    "Stamps the start date, sets the session count, and alerts Luann. Everything later is timed from this date.",
    "The opportunity card is moved to the <b>Closed Won</b> stage of the sales pipeline.",
    ["Sets <code>program_start_date</code> on the contact to today's date.",
     "Sends Luann an internal email: New client, with the client's name and program.",
     "Reads the program and sets <code>Sessions Purchased</code> and <code>Sessions Remaining</code>: 6 for RMM, VIP, Couples and RFB, 12 for RFB 1 Year, 4 for RMM Plus. Programs without 1:1 sessions are left blank.",
     "Later, once the contract templates are loaded: sends the program's agreement for e-signature and files the signed copy on the contact."],
    "One date drives every email and alert that follows, so it is set by the system and never typed by hand.",
    flow([("T", "Card moved to Closed Won"), ("A", "Set program_start_date = today"), ("A", "Email Luann: new client"),
          ("D", "Which program?", [("A", "Sessions Purchased and Remaining = 6, 12 or 4")], [("E", "No session tracking")], "1:1 program", "Group or self-paced"),
          ("E", "Done")], "WF-Closed Won Client Setup")))

# 3 coach handoff
cards.append(workflow_card(3, "WF- Coach Handoff", "draft",
    "The moment Luann assigns a coach, the coach gets the full client brief.",
    "The contact's <b>Assigned User</b> is set or changed. That is Luann picking the coach on the contact record.",
    ["Luann opens the contact and chooses the coach in the Assigned To field.",
     "The workflow sends that coach an internal email: New client assigned to you, with name, email, phone, program, the intake answers, and where the signed agreement lives on the record.",
     "If the client is ever reassigned, the new coach receives the same brief."],
    "Coaches never chase Luann for details. One click on the record is the whole handoff.",
    flow([("T", "Assigned User set on the contact"), ("A", "Email the coach: full client brief"), ("E", "Done")], "WF- Coach Handoff")))

# 4 CS milestone tasks
cards.append(workflow_card(4, "WF-CS Milestone Tasks", "live",
    "Luann's own touchpoints: six emails and six tasks, timed from the day the client became a client.",
    "The tag <code>existing client</code> is added to the contact, which happens for every client at close.",
    ["Day 7: sends the welcome email from luann@sophieorozco.com and creates the task <i>4 - Week 1 welcome</i> for Luann.",
     "Day 21: sends the check-in email and creates <i>4 - Week 3 check-in</i>.",
     "Day 42: sends the halfway email and creates <i>4 - Week 6 progress check-in</i>.",
     "Day 63: sends the graduation call email with the booking link and creates <i>3 - Week 9 schedule graduation call</i>.",
     "Day 85: sends the renewal conversation email and creates <i>1 - Renewal conversation</i>.",
     "Day 90: creates <i>1 - Day 90 review renewal + remove Circle access</i>. No client email, this one is internal."],
    "Luann works one task list, sorted by due date. The number at the front of each task puts renewals above routine check-ins. Every task opens the client's record.",
    flow([("T", "Tag added: existing client"), ("W", "Wait to day 7"), ("A", "Welcome email + task"), ("W", "Wait to day 21"), ("A", "Check-in email + task"),
          ("W", "Wait to day 42"), ("A", "Halfway email + task"), ("W", "Wait to day 63"), ("A", "Graduation call email + task"),
          ("W", "Wait to day 85"), ("A", "Renewal email + task"), ("W", "Wait to day 90"), ("A", "Task: review renewal, Circle access"), ("E", "Done")], "WF-CS Milestone Tasks")))

# 5 accelerator weekly
cards.append(workflow_card(5, "WF-CS Accelerator Weekly", "live",
    "A weekly accountability task for Luann, Accelerator clients only, until the client completes.",
    "The tag <code>client - accelerator men</code> or <code>client - accelerator women</code> is added.",
    ["Waits 7 days.",
     "Creates the task <i>4 - Verify accountability submission</i> for Luann.",
     "Checks for the tag <code>client - completed</code>. If it is there, the loop ends.",
     "If not, goes back to the wait and repeats the following week."],
    "One task a week per Accelerator client, without anyone setting reminders. Adding <code>client - completed</code> at the end of the program stops it.",
    flow([("T", "Tag added: client - accelerator men or women"), ("W", "Wait 7 days"), ("A", "Task for Luann: verify accountability submission"),
          ("D", "Has client - completed?", [("E", "Loop ends")], [("A", "Back to the 7 day wait")], "Yes", "No")], "WF-CS Accelerator Weekly")))

# 6 client check-in alerts
cards.append(workflow_card(6, "Client Check-in Alerts", "live",
    "Date-based alerts to the client's CSM at each milestone, so nothing depends on remembering a calendar.",
    "A milestone day arrives, counted from <code>program_start_date</code>: day 21, 42, 63, 69 or 90. The contact must carry the tag <code>cs alerts - date based</code>.",
    ["On each milestone day the workflow checks which milestone fired.",
     "Sends the milestone email to the address in the contact's <code>csm_email</code> field, and an in-app alert.",
     "On day 90 it also removes the <code>cs alerts - date based</code> tag, so the client drops out of the alert cycle."],
    "The CSM sees a client's milestone on the day it happens, even for clients enrolled months apart.",
    flow([("T", "Day 21, 42, 63, 69 or 90 after program start"), ("D", "Has cs alerts - date based?", [("A", "Email csm_email + in-app alert for that milestone"), ("A", "Day 90: remove the tag")], [("E", "Nothing")], "Yes", "No")], "Client Check-in Alerts")))

# 7 milestone emails (six)
milestone_rows = [
    ["WF- Week 3 Check-In", "Day 21", "Every client", "Check-in"],
    ["WF- Week 4 Next Steps", "Day 28", "RMM Plus only", "What-comes-next, the continuation offer"],
    ["WF- Week 5 Next Steps", "Day 35", "6-session programs: RMM, VIP, Couples, RFB", "What-comes-next, the continuation offer"],
    ["WF- Week 6 Check-In", "Day 42", "All except RMM Plus", "Check-in"],
    ["WF- Week 9 Next Steps", "Day 63", "RFB 1 Year only", "What-comes-next, the continuation offer"],
    ["WF- Week 12 Completion", "Day 84", "RFB 1 Year only", "Completion"],
]
cards.append(workflow_card(7, "WF- Week 3, 4, 5, 6, 9 and 12 (six milestone workflows)", "draft",
    "Emails to the client at the right week of their own program. Six workflows, one email each.",
    "The milestone day arrives, counted from <code>program_start_date</code>. Each workflow also checks the client's program, so only the right people get it.",
    ["The day arrives for that client. A day that already passed when the client entered never fires, so nobody gets a week 3 email in week 10.",
     "The workflow checks the program. If the milestone does not apply, nothing sends.",
     "Check-in and completion emails send once and stop.",
     "The three <b>Next Steps</b> workflows do more: they split by gender, send the continuation offer with five program buttons, tag the contact <code>outreach sent</code>, put a card at <b>Outreach Sent</b> in the Continuation Programs pipeline, wait 5 days, and if the client has not clicked, replied or enrolled, move the card to <b>Needs Follow-Up</b> and create a task for Luann. That part is described in the Continuation Tracker SOP."],
    "Every client gets the same journey, on their own calendar, with the offer arriving exactly when their program is wrapping up.",
    flow([("T", "Milestone day arrives for this client"), ("D", "Does the milestone apply to their program?", [("A", "Send the email from Luann")], [("E", "Nothing sends")], "Yes", "No"),
          ("N", "Next Steps emails continue into the Continuation Tracker")], "The six milestone workflows"),
    table(["Workflow", "When", "Who gets it", "Email"], milestone_rows)))

# 8 session counter
cards.append(workflow_card(8, "WF- Session Counter", "draft",
    "Keeps the session count on the client's record without a spreadsheet.",
    "An appointment on a <b>coaching session calendar</b> is marked <b>Showed</b> or <b>No-Show</b>. Sales and reset-call calendars are excluded.",
    ["Adds 1 to <code>Sessions Used</code>.",
     "Subtracts 1 from <code>Sessions Remaining</code>.",
     "Ends. It runs again on every session, so re-entry is on."],
    "Any coach can open a record and see exactly where the client stands. No-shows count as used, as Chris decided.",
    flow([("T", "Coaching session marked Showed or No-Show"), ("A", "Sessions Used + 1"), ("A", "Sessions Remaining - 1"), ("E", "Done, runs again next session")], "WF- Session Counter")))

# 9 last session alert
cards.append(workflow_card(9, "WF- Last Session Alert", "draft",
    "Warns the coach that the next session is the last, and tells the client what happens next.",
    "The <code>Sessions Remaining</code> field changes on the contact.",
    ["Checks whether Sessions Remaining now equals 1.",
     "If yes, sends the assigned coach an internal notification: this client's final session is next.",
     "Sends the client a short note from Luann so questions about what comes next land in her inbox.",
     "If the number is anything other than 1, nothing happens."],
    "The continuation conversation starts before the last session, not after the client has gone quiet.",
    flow([("T", "Sessions Remaining changed"), ("D", "Is it 1?", [("A", "Notify the coach: final session next"), ("A", "Email the client from Luann")], [("E", "Nothing")], "Yes", "No")], "WF- Last Session Alert")))

# 10 handoff to continuation
cards.append(workflow_card(10, "Hand-off to the Continuation Tracker", "draft",
    "Where this system ends and the next one begins.",
    "Day 77 after <code>program_start_date</code>, handled by <b>WF-CT1 Graduation Entry</b> in the Continuation Tracker.",
    ["The client is tagged <code>graduated</code> and a card is created at <b>Graduated</b> in the Continuation Programs pipeline.",
     "From there the Continuation Tracker records every click, reply, purchase or decline.",
     "See the <a href='https://continuation-tracker-sop.vercel.app' target='_blank' rel='noopener'>Continuation Tracker SOP</a> for that system."],
    "The two systems share one date, one pipeline and one set of tags, so a client never falls between them.",
    flow([("T", "Day 77 after program start"), ("A", "Tag graduated, card at Graduated"), ("E", "Continuation Tracker SOP")], "Hand-off")))

toc = "".join(f'<a href="#wf{i}"><span class="n">{i}</span>{E(n)}</a>' for i, n in enumerate([
    "Onboarding Email", "WF-Closed Won Client Setup", "WF- Coach Handoff", "WF-CS Milestone Tasks", "WF-CS Accelerator Weekly",
    "Client Check-in Alerts", "Six milestone workflows", "WF- Session Counter", "WF- Last Session Alert", "Hand-off to Continuation"], 1))

parts = table(["Name", "Type", "What it is for"], [
    ["<code>program_start_date</code>", "Date field", "The day the client closed. Every email, alert and task is timed from it."],
    ["<code>Sessions Purchased</code>, <code>Sessions Used</code>, <code>Sessions Remaining</code>", "Number fields", "The 1:1 session count. Set at close, moved by the Session Counter."],
    ["<code>csm_email</code>", "Text field", "The CSM's email. Client Check-in Alerts sends the milestone alert there."],
    ["Program tags, e.g. <code>client - rmm accelerator men</code>", "Tags", "Which program and gender. Starts onboarding, decides milestones and the outreach email."],
    ["<code>existing client</code>", "Tag", "Marks a paying client. Starts Luann's milestone tasks and keeps lead automations away."],
    ["<code>cs alerts - date based</code>", "Tag", "Turns on the date-based CSM alerts for that client. Removed on day 90."],
    ["<code>client - completed</code>", "Tag", "Ends the weekly Accelerator accountability loop."],
    ["Assigned User", "Contact field", "The coach. Setting it fires the Coach Handoff."],
])

human = table(["When", "What you do"], [
    ["A sale closes", "Move the card to Closed Won, set Offer Discussed, add the program tag and <code>existing client</code>. Copy the tag from the Client Tagging SOP."],
    ["The new-client alert arrives", "Open the contact and assign the coach. That one click sends the coach their brief."],
    ["A task lands on your list", "Open it, do the touchpoint, mark it complete. The task links to the client."],
    ["A client replies to any email", "Reply like normal email. The conversation is yours from there."],
    ["A session happens", "The coach marks it Showed or No-Show on the calendar. That is the only bookkeeping."],
    ["The last-session alert arrives", "Have the continuation conversation when the moment is right."],
    ["An Accelerator client finishes", "Add <code>client - completed</code>. The weekly task stops."],
    ["You want an email's wording changed", "Send John the new text. It is swapped in minutes."],
])

body = f'''
<section>
  <div class="kicker">Start here</div>
  <h2>What this system is</h2>
  <p class="lead">From the moment a client buys until they finish their program, one system runs their journey: their first email, their start date, their coach handoff, Luann's check-ins, the client's milestone emails, the session count, and the alert before the last session. Everything is timed from each client's own start date, so nothing goes out in batches and nobody gets an email that does not match where they are.</p>
  <p class="lead">Ten pieces, listed below in the order they happen. Each one names the workflow exactly as it appears in GHL, what starts it, what it does step by step, and a flowchart.</p>
  <div class="toc">{toc}</div>
</section>

<section>
  <div class="kicker">The big picture</div>
  <h2>One client, start to finish</h2>
  <div class="two"><div>{big}</div><div>
    <div class="lbl">Three ideas that make it work</div>
    <div class="grid3" style="grid-template-columns:1fr">
      <div class="box"><span class="n">1</span><b>One date</b><p>The start date is stamped once, at Closed Won. Every wait, alert and email counts from it. Nobody types dates.</p></div>
      <div class="box"><span class="n">2</span><b>One tag decides the program</b><p>The program tag says what the client bought and whether they are a man or a woman. Onboarding, milestones and the continuation offer all read it.</p></div>
      <div class="box"><span class="n">3</span><b>People do the human parts only</b><p>Assigning the coach, doing the check-in, having the conversation. The system does the timing, the records and the reminders.</p></div>
    </div>
  </div></div>
</section>

<section>
  <div class="kicker">The workflows</div>
  <h2>Ten pieces, in the order they happen</h2>
  <p class="lead">A green badge means it is running today. A grey badge means it is built in GHL and waiting to be switched on.</p>
  {"".join(cards)}
</section>

<section>
  <div class="kicker">The moving parts</div>
  <h2>Fields and tags the system relies on</h2>
  <p class="lead">Renaming or deleting any of these breaks the journey silently. Ask John before touching them.</p>
  {parts}
</section>

<section>
  <div class="kicker">Your part</div>
  <h2>The only things a person does</h2>
  {human}
  {note("<b>Never add a client into a workflow by hand.</b> The emails are timed from dates. A manual add has no dates and can fire every email at once. <b>Never edit a workflow yourself</b>, one change can affect every enrolled client. <b>Never re-add a tag a client already had</b>, that restarts automations. Message John instead, changes take minutes.", "stop")}
</section>

<section>
  <div class="kicker">Status</div>
  <h2>What is live and what is waiting</h2>
  {table(["Piece", "Status", "What it is waiting on"], [
      ["Onboarding Email (10 workflows)", "Live", ""],
      ["WF-CS Milestone Tasks", "Live since Sept 15", ""],
      ["WF-CS Accelerator Weekly", "Live since Sept 15", ""],
      ["Client Check-in Alerts", "Live since Sept 15", ""],
      ["WF-Closed Won Client Setup", "Built, draft", "Contract templates for the e-signature step, and the one-time start-date set for existing clients"],
      ["WF- Coach Handoff", "Built, draft", "Switch on with Closed Won Client Setup"],
      ["Six milestone workflows", "Built, draft", "The three Next Steps emails need the continuation buttons finished, see the Continuation Tracker SOP"],
      ["WF- Session Counter and WF- Last Session Alert", "Built, draft", "The list of coaching session calendars to include"],
  ])}
</section>
'''

html_out = page("New Client Journey System — SOP", "Sophie Orozco Coaching", "New Client Journey System",
    "How a client is looked after from the day they buy to the day they finish, and which workflow does each part.",
    "Standard Operating Procedure · v2.0 · Sept 30, 2026", body, "New Client Journey System · SOP v2.0 · Sophie Orozco Coaching")
open(OUT, "w", encoding="utf-8").write(html_out)
print("wrote", OUT, len(html_out), "bytes")
