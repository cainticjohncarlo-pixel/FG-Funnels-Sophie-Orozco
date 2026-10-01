# -*- coding: utf-8 -*-
"""Build guide for the ManyChat 'Communication Reset | New Follower' automation + Zap + GHL handoff.
Writes build/index.html so it deploys at /build on the same Vercel project."""
import html, os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(HERE, "build")
os.makedirs(OUT_DIR, exist_ok=True)
OUT = os.path.join(OUT_DIR, "index.html")
E = html.escape

def cp(val):
    return f'<button class="tagbtn" data-tag="{E(val)}">{E(val)} <span class="ic">copy</span></button>'

def crumbs(*parts):
    return " → ".join(f'<span class="crumb">{E(p)}</span>' for p in parts)

def table(head, rows):
    th = "".join(f"<th>{h}</th>" for h in head)
    trs = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
    return f'<div class="tblwrap"><table><thead><tr>{th}</tr></thead><tbody>{trs}</tbody></table></div>'

def step(n, title, body):
    return f'''
<div class="card" id="s{n}">
  <div class="chead"><div class="num">{n}</div><h3>{title}</h3></div>
  {body}
</div>'''

def part(kicker, title, lead=""):
    return f'<section><div class="kicker">{E(kicker)}</div><h2>{E(title)}</h2>{("<p class=lead>"+lead+"</p>") if lead else ""}'

steps = []

# ---------------------------------------------------------------- PART A: ManyChat
steps.append(part("Part A", "Build the flow in ManyChat", "Seven blocks. Build them in this order and keep the flow unpublished until Part D."))

steps.append(step(1, "Open the new-follower automation", f'''
<p>Go to {crumbs("Automations", "Basic", "Say hi to new followers")}.</p>
<p>Confirm it is available for Sophie's connected Instagram account. Availability depends on Meta's eligibility rules, so if it is not there, stop and flag it.</p>
<p>Set the opening delay to <b>5 minutes</b>, then select {crumbs("⋯", "Switch to Flow Builder")}.</p>
<div class="kv"><span class="k">Name it</span><span>{cp("Communication Reset | New Follower")}</span></div>
<div class="note"><b>Keep it unpublished</b> until every test in Part D passes.</div>
'''))

steps.append(step(2, "Create the two ManyChat tags", f'''
<p>Go to {crumbs("Settings", "Tags")} and create these if they do not exist yet.</p>
{table(["Tag", "What it is for"], [
    [cp("Source_Instagram_Follow"), "Records that the lead came from an Instagram follow"],
    [cp("CR_Email_Confirmed"), "Fires the Zap once the email is confirmed"],
])}
<p class="small">The two GHL tags, <code>communication reset</code> and <code>lead-instagram</code>, are added by the Zap in Part C, not in ManyChat.</p>
'''))

steps.append(step(3, "Welcome Message block", f'''
<div class="kv"><span class="k">Block name</span><span>{cp("Welcome Message")}</span></div>
<p>Paste the welcome message from <a href="../#s2">step 2 on the structure page</a>. Add one button:</p>
<div class="kv"><span class="k">Button</span><span>{cp("Yes, send it over!")}</span><span class="k">Goes to</span><span><b>Check Existing Email</b> (step 4)</span></div>
<p class="small">Leave the no-interaction path empty. Their tap or reply is what opens the 24 hour messaging window for the rest of the conversation.</p>
'''))

steps.append(step(4, "Check Existing Email condition", f'''
<div class="kv"><span class="k">Block name</span><span>{cp("Check Existing Email")}</span></div>
<p>Add a <b>Condition</b> block after the welcome button. Condition: the <b>Email</b> system field has a value.</p>
{table(["Result", "Next block"], [
    ["Email exists", "<b>Confirm Email</b> (step 6)"],
    ["Email is empty", "<b>Collect Email</b> (step 5)"],
])}
<p class="small">Both paths go through confirmation before any tag is applied.</p>
'''))

steps.append(step(5, "Collect Email block", f'''
<div class="kv"><span class="k">Block name</span><span>{cp("Collect Email")}</span></div>
<p>Add an Instagram message, then a <b>Data Collection</b> step inside it. Paste the email question from <a href="../#s3">step 3 on the structure page</a>.</p>
{table(["Setting", "Configuration"], [
    ["Reply type", "Email"],
    ["Save response", "Email system field"],
    ["Invalid response", "Ask them to check and re-enter the address"],
    ["Successful response", "Continue to <b>Confirm Email</b>"],
    ["No response", "End. Do not apply any tag"],
])}
<p class="small">Remove any skip button, or send it to an end with no delivery. Data Collection needs a paid ManyChat plan. The Email reply type checks the address format for you.</p>
'''))

steps.append(step(6, "Confirm Email block and the correction loop", f'''
<div class="kv"><span class="k">Block name</span><span>{cp("Confirm Email")}</span></div>
<p>Add an Instagram message and paste the confirmation text from <a href="../#s4">step 4 on the structure page</a>. Replace the email placeholder with the variable picker → <b>Email</b>.</p>
{table(["Button", "Goes to"], [
    [cp("Yes, that's correct"), "<b>Apply Confirmed Tags</b> (step 7)"],
    [cp("Change my email"), "<b>Collect Email</b> (step 5), then back here to confirm again"],
])}
<div class="note"><b>Tags come only from the Yes button.</b> An address they are still fixing must never start the Zap.</div>
'''))

steps.append(step(7, "Apply Confirmed Tags, then the inbox message", f'''
<div class="kv"><span class="k">Block name</span><span>{cp("Apply Confirmed Tags")}</span></div>
<p>Add an <b>Actions</b> block with these two actions, in this order:</p>
{table(["Order", "Action"], [
    ["1", "Add tag " + cp("Source_Instagram_Follow")],
    ["2", "Add tag " + cp("CR_Email_Confirmed")],
])}
<p>Connect it to one last Instagram message:</p>
<div class="kv"><span class="k">Block name</span><span>{cp("Check Your Inbox")}</span></div>
<p>Use the text-only inbox message from <a href="../#s5">step 5 on the structure page</a>. No button, no course link.</p>
<div class="note"><b>Wording to confirm with Daniel.</b> The tag starts the Zap, it does not confirm GHL has finished sending. "My team just sent it" can land a few seconds before the email does. "It's on its way to your inbox" is the safer wording. Daniel's call.</div>
'''))
steps.append("</section>")

# ---------------------------------------------------------------- PART B: GHL
steps.append(part("Part B", "Check the GHL workflow", "Nothing to build here. Just confirm the existing workflow is ready to receive the tag."))
steps.append(step(8, "Verify 01 - Communication Reset Lead Magnet", f'''
<p>Go to {crumbs("Automation", "Workflows", "01 - Communication Reset Lead Magnet")} and check:</p>
{table(["Check", "Expected"], [
    ["Status", "Published"],
    ["Trigger", "Contact Tag"],
    ["Trigger filter", "Tag added: " + cp("communication reset")],
    ["Email action", "Sends the Communication Reset course"],
    ["Course link in the email", "The correct learner-facing access link"],
])}
<p class="small">Reuse this workflow. If a separate course-delivery workflow was made from earlier instructions, leave it unpublished.</p>
'''))
steps.append("</section>")

# ---------------------------------------------------------------- PART C: Zapier
steps.append(part("Part C", "Build the one Zap", "ManyChat tag in, GHL contact out."))
steps.append(step(9, "ManyChat → GHL | Communication Reset", f'''
<p>In Zapier select {crumbs("Create", "Zap")}.</p>
<div class="kv"><span class="k">Zap name</span><span>{cp("ManyChat → GHL | Communication Reset")}</span></div>
<div class="lbl" style="margin-top:14px">Trigger</div>
{table(["Setting", "Value"], [
    ["App", "ManyChat"],
    ["Event", "New Tagged User"],
    ["Account", "Sophie's ManyChat account"],
    ["Tag", cp("CR_Email_Confirmed")],
])}
<p class="small">Test the trigger with a contact whose email has been saved and confirmed.</p>
<div class="lbl" style="margin-top:14px">Action</div>
<p>App <b>LeadConnector</b>, event <b>Add/Update Contact</b>. Sign in and pick the Sophie Orozco Coaching subaccount. Map:</p>
{table(["LeadConnector field", "ManyChat value"], [
    ["Email", "Email system field"],
    ["First Name", "First name, if available"],
    ["Last Name", "Last name, if available"],
    ["Instagram username, if the field is offered", "Instagram username system field"],
    ["Tags", cp("communication reset,lead-instagram")],
])}
<p class="small">If there is no Instagram username field, put it in <b>Notes</b> as <code>Instagram username: ...</code>. Leave a name field unmapped rather than mapping the wrong thing. Paste both tags into the one comma-separated Tags field.</p>
<div class="note"><b>Testing the action sends a real email.</b> The GHL workflow is live, so use a test inbox you control.</div>
'''))
steps.append("</section>")

# ---------------------------------------------------------------- PART D: Test
steps.append(part("Part D", "Test everything, then publish", "Use Preview → In messengers with a real test contact. ManyChat's visual preview does not run Zaps or validate inputs."))
tests = [
    ("Ignore the welcome message", "No further DM, no course email"),
    ("Tap the button with no saved email", "Email collection appears"),
    ("Enter an invalid email", "Retry prompt appears"),
    ("Tap the button with a saved email", "Confirmation appears straight away"),
    ("Tap Change my email", "New address is collected, then confirmed"),
    ("Tap Yes, that's correct", "Both ManyChat tags are applied"),
    ("Open Zapier history", "LeadConnector action succeeded"),
    ("Open the GHL contact", "Correct email, both GHL tags present"),
    ("Open the GHL workflow history", "Contact entered 01 - Communication Reset Lead Magnet and the email sent"),
    ("Check the test inbox", "Course email arrived and its link works"),
    ("Check Instagram", "Final DM is the inbox message only"),
]
items = "".join(f'<label class="chk"><input type="checkbox" data-k="t{i}"><span><b>{E(a)}</b><em>{E(b)}</em></span></label>' for i, (a, b) in enumerate(tests, 1))
steps.append(step(10, "Run the checklist", f'''
<div class="checks">{items}</div>
<p class="small" style="margin-top:12px">Ticks save in this browser only. When all eleven pass, publish the ManyChat flow and turn the Zap on.</p>
'''))
steps.append("</section>")

body = "".join(steps)

page = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="robots" content="noindex">
<title>Build Guide — Communication Reset | New Follower</title>
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
  .wrap{{max-width:960px;margin:0 auto;padding:0 20px 90px}}
  header.hero{{background:var(--ink);color:#F7F4EE;padding:48px 20px 40px;text-align:center}}
  .hero .brand{{font-family:'Playfair Display',serif;font-size:14px;letter-spacing:.18em;text-transform:uppercase;color:#CDB68A;margin-bottom:12px}}
  .hero h1{{font-family:'Playfair Display',serif;font-size:clamp(28px,5vw,40px);font-weight:600;line-height:1.15;margin-bottom:12px}}
  .hero p{{color:#BFB8AC;max-width:640px;margin:0 auto;font-size:15.5px}}
  .hero a{{color:#CDB68A}}
  section{{margin-top:44px}}
  h2{{font-family:'Playfair Display',serif;font-size:clamp(22px,3.4vw,28px);font-weight:600;margin-bottom:8px}}
  .lead{{color:var(--muted);font-size:15px;margin-bottom:4px}}
  .kicker{{color:var(--terra);font-weight:700;font-size:12.5px;letter-spacing:.14em;text-transform:uppercase;margin-bottom:6px}}
  code{{font-family:ui-monospace,monospace;font-size:12.5px;background:#F4F1EA;border:1px solid var(--line);border-radius:5px;padding:1px 6px}}
  .small{{font-size:14px;color:var(--muted)}}
  .lbl{{font-size:11.5px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:var(--green);margin-bottom:7px}}
  .overview{{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:14px;margin-top:16px}}
  .ov{{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:18px}}
  .ov .n{{display:inline-flex;align-items:center;justify-content:center;width:28px;height:28px;border-radius:50%;background:var(--terra);color:#fff;font-weight:700;font-size:13px;margin-bottom:8px}}
  .ov b{{display:block;margin-bottom:4px;font-size:15px}}
  .ov p{{font-size:13.5px;color:var(--muted)}}
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
  th{{text-align:left;font-size:11.5px;letter-spacing:.08em;text-transform:uppercase;color:var(--green);padding:10px 14px;border-bottom:1px solid var(--line)}}
  td{{padding:9px 14px;border-bottom:1px solid var(--line);vertical-align:middle}}
  tr:last-child td{{border-bottom:none}}
  .note{{background:var(--warn-bg);border-left:4px solid var(--terra);border-radius:0 12px 12px 0;padding:12px 16px;margin:12px 0 4px;font-size:14px;color:var(--warn)}}
  .note b{{color:var(--warn)}}
  .checks{{display:flex;flex-direction:column;gap:8px}}
  .chk{{display:flex;gap:12px;align-items:flex-start;background:#FBF9F5;border:1px solid var(--line);border-radius:10px;padding:10px 14px;cursor:pointer}}
  .chk input{{margin-top:5px;width:16px;height:16px;accent-color:var(--green);flex:none}}
  .chk span{{display:flex;flex-direction:column;font-size:14.5px}}
  .chk em{{font-style:normal;color:var(--muted);font-size:13.5px}}
  .chk:has(input:checked){{background:var(--green-soft);border-color:var(--green)}}
  .chk:has(input:checked) b{{text-decoration:line-through;color:var(--muted)}}
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
  <h1>Build Guide: Communication Reset | New Follower</h1>
  <p>Ten steps to build the ManyChat flow, connect it to GHL with one Zap, and test it before publishing. The messages themselves are on the <a href="../">structure page</a>.</p>
</header>

<div class="wrap">

<section>
  <div class="kicker">The setup</div>
  <h2>Three pieces, one job</h2>
  <div class="overview">
    <div class="ov"><span class="n">A</span><b>ManyChat flow</b><p>Greets the follower, collects and confirms the email, applies two tags, sends one inbox message.</p></div>
    <div class="ov"><span class="n">B</span><b>GHL workflow</b><p>Already published. <code>communication reset</code> tag in, course email out.</p></div>
    <div class="ov"><span class="n">C</span><b>One Zap</b><p>Moves the confirmed contact from ManyChat into GHL with both GHL tags.</p></div>
  </div>
  <div class="note" style="margin-top:16px"><b>The rule that shapes everything:</b> GHL sends the course by email. The Instagram DM never contains the course or its link.</div>
</section>

{body}

<footer>
  <span>Build Guide · Communication Reset | New Follower · Updated Sept 28, 2026</span>
  <span>Maintained by John Carlo Caintic</span>
</footer>

</div>

<div class="toast" id="toast">Copied</div>
<button class="top" id="top">↑ Top</button>

<script>
  const toast = document.getElementById('toast');
  async function copyText(t) {{
    try {{ await navigator.clipboard.writeText(t); }}
    catch (e) {{
      const ta = document.createElement('textarea');
      ta.value = t; document.body.appendChild(ta); ta.select();
      try {{ document.execCommand('copy'); }} catch (err) {{}}
      document.body.removeChild(ta);
    }}
  }}
  document.querySelectorAll('.tagbtn').forEach(btn => {{
    btn.addEventListener('click', async () => {{
      await copyText(btn.dataset.tag);
      btn.classList.add('copied');
      const ic = btn.querySelector('.ic'); const old = ic.textContent; ic.textContent = 'copied ✓';
      toast.textContent = 'Copied: ' + btn.dataset.tag; toast.classList.add('show');
      setTimeout(() => {{ btn.classList.remove('copied'); ic.textContent = old; toast.classList.remove('show'); }}, 1600);
    }});
  }});
  const KEY = 'cr-build-checks';
  let saved = {{}};
  try {{ saved = JSON.parse(localStorage.getItem(KEY) || '{{}}'); }} catch (e) {{ saved = {{}}; }}
  document.querySelectorAll('.chk input').forEach(cb => {{
    cb.checked = !!saved[cb.dataset.k];
    cb.addEventListener('change', () => {{
      saved[cb.dataset.k] = cb.checked;
      try {{ localStorage.setItem(KEY, JSON.stringify(saved)); }} catch (e) {{}}
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
