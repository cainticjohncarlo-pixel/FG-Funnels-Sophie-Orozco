# -*- coding: utf-8 -*-
"""ManyChat automation structure: Communication Reset | New Follower. Builds index.html for Vercel."""
import html, os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "index.html")
E = html.escape

def copybtn(val, label="copy"):
    return f'<button class="tagbtn" data-tag="{E(val)}">{E(val)} <span class="ic">{label}</span></button>'

def bubble(text):
    paras = "".join(f"<p>{E(p)}</p>" for p in text.strip().split("\n\n"))
    return f'''<div class="bubble"><div class="bhead"><span>Message</span><button class="copymsg" data-tag="{E(text.strip())}">copy text</button></div>{paras}</div>'''

WELCOME = """Hey there! Thanks for the follow 💛

Would you like me to send you the Communication Reset? It's a free 3-hour mini-course to help you communicate more effectively with your spouse, especially when things feel distant.

Tap below and I'll send it over 👇"""

COLLECT = """Absolutely! What's the best email address to send your free Communication Reset course to?"""

CONFIRM = """I have your email as [Email]. Is that correct?"""

DELIVER = """Awesome! My team just sent it to your inbox. Take a look and let me know what you think!"""

# ------------------------------------------------------------------ flow diagram (SVG)
def box(x, y, w, h, text, dashed=False, cls="node"):
    lines = text if isinstance(text, list) else [text]
    ty = y + h/2 - (len(lines)-1)*9
    tspans = "".join(f'<tspan x="{x+w/2}" dy="{0 if i==0 else 18}">{E(l)}</tspan>' for i, l in enumerate(lines))
    dash = ' stroke-dasharray="6 4"' if dashed else ""
    return f'<rect class="{cls}" x="{x}" y="{y}" width="{w}" height="{h}" rx="14"{dash}/><text class="ntext" x="{x+w/2}" y="{ty}" text-anchor="middle" dominant-baseline="middle">{tspans}</text>'

def pill(cx, cy, text):
    w = len(text)*7.2 + 26
    return f'<rect class="pill" x="{cx-w/2}" y="{cy-13}" width="{w}" height="26" rx="13"/><text class="ptext" x="{cx}" y="{cy+1}" text-anchor="middle" dominant-baseline="middle">{E(text)}</text>'

def path(d):
    return f'<path class="edge" d="{d}" marker-end="url(#arr)"/>'

svg = f'''
<svg viewBox="0 0 880 540" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Communication Reset new follower flow">
  <defs><marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#6B6459"/></marker></defs>
  {box(110, 20, 220, 58, "New Instagram follower")}
  {box(140, 132, 160, 58, "Welcome DM")}
  {box(470, 132, 160, 58, "Confirm email", dashed=True)}
  {pill(195, 252, "No interaction")}
  {pill(370, 252, "Taps Yes")}
  {pill(478, 252, "Change email")}
  {pill(655, 252, "Yes")}
  {box(95, 340, 200, 58, "Wait for interaction")}
  {box(332, 340, 156, 58, "Collect email")}
  {box(527, 336, 260, 66, ["Tag contact, Zap to GHL,", "GHL sends course email"])}
  {box(527, 458, 260, 58, "DM: check your inbox")}
  {path("M220,78 L220,128")}
  {path("M195,190 L195,235")}
  {path("M195,265 L195,336")}
  {path("M245,190 L245,215 Q245,222 252,222 L363,222 Q370,222 370,229 L370,235")}
  {path("M370,265 L370,336")}
  {path("M410,340 L410,300 Q410,292 418,292 L540,292 Q550,292 550,284 L550,194")}
  {path("M520,190 L520,215 Q520,222 512,222 L486,222 Q478,222 478,229 L478,235")}
  {path("M478,265 L478,300 Q478,308 470,308 L456,308 Q448,308 448,316 L448,336")}
  {path("M600,190 L600,215 Q600,222 608,222 L647,222 Q655,222 655,229 L655,235")}
  {path("M655,265 L655,332")}
  {path("M657,402 L657,454")}
</svg>'''

page = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="robots" content="noindex">
<title>Communication Reset | New Follower — ManyChat Automation</title>
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
  .hero p{{color:#BFB8AC;max-width:620px;margin:0 auto;font-size:15.5px}}
  section{{margin-top:40px}}
  h2{{font-family:'Playfair Display',serif;font-size:clamp(22px,3.4vw,28px);font-weight:600;margin-bottom:12px}}
  .kicker{{color:var(--terra);font-weight:700;font-size:12.5px;letter-spacing:.14em;text-transform:uppercase;margin-bottom:6px}}
  code{{font-family:ui-monospace,monospace;font-size:12.5px;background:#F4F1EA;border:1px solid var(--line);border-radius:5px;padding:1px 6px}}
  .small{{font-size:14px;color:var(--muted)}}
  .lbl{{font-size:11.5px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:var(--green);margin-bottom:7px}}
  .diagram{{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:18px 10px 6px;margin-top:16px}}
  .diagram svg{{width:100%;height:auto;display:block}}
  .node{{fill:#FBF9F5;stroke:var(--green);stroke-width:1.6}}
  .ntext{{font-family:'Inter',sans-serif;font-size:14px;font-weight:600;fill:var(--ink)}}
  .pill{{fill:var(--terra-soft);stroke:var(--terra);stroke-width:1}}
  .ptext{{font-family:'Inter',sans-serif;font-size:12px;font-weight:600;fill:var(--terra)}}
  .edge{{fill:none;stroke:#6B6459;stroke-width:1.4}}
  .legend{{display:flex;gap:18px;flex-wrap:wrap;font-size:13px;color:var(--muted);padding:8px 10px 6px}}
  .legend span::before{{content:"";display:inline-block;width:12px;height:12px;border-radius:4px;margin-right:6px;vertical-align:-1px}}
  .legend .a::before{{background:#FBF9F5;border:1.5px solid var(--green)}}
  .legend .b::before{{background:#FBF9F5;border:1.5px dashed var(--green)}}
  .legend .c::before{{background:var(--terra-soft);border:1px solid var(--terra);border-radius:6px}}
  .card{{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:26px;margin-top:20px;scroll-margin-top:16px}}
  .chead{{display:flex;gap:14px;align-items:center;padding-bottom:14px;border-bottom:1px solid var(--line);margin-bottom:16px}}
  .num{{flex:none;width:34px;height:34px;border-radius:50%;background:var(--green);color:#fff;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:15px}}
  .card h3{{font-family:'Playfair Display',serif;font-size:21px;font-weight:600;line-height:1.25}}
  .card p{{margin-bottom:10px}}
  .card b{{font-weight:600}}
  .crumb{{display:inline-block;background:#F4F1EA;border:1px solid var(--line);border-radius:6px;padding:1px 8px;font-size:14px;font-weight:600;white-space:nowrap}}
  .bubble{{background:var(--ink);color:#F7F4EE;border-radius:16px;padding:14px 18px 8px;margin:12px 0 14px;font-size:15px;line-height:1.6}}
  .bubble p{{margin-bottom:10px}}
  .bhead{{display:flex;justify-content:space-between;align-items:center;font-size:11.5px;letter-spacing:.1em;text-transform:uppercase;color:#CDB68A;margin-bottom:8px}}
  .copymsg{{background:transparent;border:1px solid #6B6459;color:#CDB68A;border-radius:999px;padding:3px 10px;font-size:11.5px;cursor:pointer;font-family:inherit;letter-spacing:.04em;text-transform:none}}
  .copymsg:hover{{border-color:#CDB68A}}
  .kv{{display:grid;grid-template-columns:auto 1fr;gap:6px 14px;align-items:center;margin:8px 0 12px;font-size:14.5px}}
  .kv .k{{color:var(--muted);font-weight:600}}
  .tagbtn{{display:inline-flex;align-items:center;gap:8px;background:#F4F1EA;border:1px solid var(--line);border-radius:8px;padding:7px 12px;font-family:ui-monospace,monospace;font-size:13px;color:var(--ink);cursor:pointer;transition:.15s;text-align:left;margin:2px 6px 2px 0}}
  .tagbtn:hover{{background:var(--terra-soft);border-color:var(--terra)}}
  .tagbtn.copied{{background:var(--green-soft);border-color:var(--green);color:var(--green)}}
  .tagbtn .ic{{opacity:.5;font-size:11.5px}}
  .tblwrap{{overflow-x:auto;background:#FBF9F5;border:1px solid var(--line);border-radius:12px;margin:10px 0 14px}}
  table{{width:100%;border-collapse:collapse;font-size:14px}}
  th{{text-align:left;font-size:11.5px;letter-spacing:.08em;text-transform:uppercase;color:var(--green);padding:10px 14px;border-bottom:1px solid var(--line)}}
  td{{padding:9px 14px;border-bottom:1px solid var(--line);vertical-align:top}}
  tr:last-child td{{border-bottom:none}}
  .note{{background:var(--warn-bg);border-left:4px solid var(--terra);border-radius:0 12px 12px 0;padding:12px 16px;margin:12px 0 4px;font-size:14px;color:var(--warn)}}
  .note b{{color:var(--warn)}}
  .note code{{background:#fff}}
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
  <h1>Communication Reset | New Follower</h1>
  <p>The ManyChat automation that greets a new Instagram follower, collects and confirms their email, hands the contact to GHL for the course email, and tells them in Instagram to check their inbox. The course is never sent in the DM. Name the automation exactly as the title above.</p>
  <p style="margin-top:12px"><a href="build/" style="color:#CDB68A;font-weight:600">Open the step-by-step build guide →</a></p>
</header>

<div class="wrap">

<section>
  <div class="kicker">The structure</div>
  <h2>How the flow moves</h2>
  <div class="diagram">
    {svg}
    <div class="legend"><span class="a">Message or action block</span><span class="b">Confirmation block</span><span class="c">Button or condition</span></div>
  </div>
</section>

<section>
  <div class="kicker">Build it</div>
  <h2>Five steps, in order</h2>

  <div class="card" id="s1">
    <div class="chead"><div class="num">1</div><h3>Set up the new-follower trigger</h3></div>
    <p>In ManyChat, open <span class="crumb">Automations</span> → <span class="crumb">Basic</span> → <span class="crumb">Say hi to new followers</span>, then select <span class="crumb">···</span> → <span class="crumb">Switch to Flow Builder</span> to add the email collection and confirmation steps.</p>
    <p>Set the opening message to send after <b>5 minutes</b>.</p>
    <div class="note"><b>Check eligibility first.</b> This trigger is subject to Meta's account eligibility. Confirm it is available for the connected Instagram account before building the rest.</div>
  </div>

  <div class="card" id="s2">
    <div class="chead"><div class="num">2</div><h3>Send the welcome message</h3></div>
    {bubble(WELCOME)}
    <div class="kv"><span class="k">Button</span><span>{copybtn("Yes, send it over!")}</span></div>
    <p class="small">No interaction: the flow waits. Taps the button: continue to email collection.</p>
  </div>

  <div class="card" id="s3">
    <div class="chead"><div class="num">3</div><h3>Collect their email</h3></div>
    {bubble(COLLECT)}
    <p>Add a <b>Data Collection</b> block with these settings:</p>
    <div class="tblwrap"><table>
      <thead><tr><th>Setting</th><th>Configuration</th></tr></thead>
      <tbody>
        <tr><td>Reply type</td><td>Email</td></tr>
        <tr><td>Save response</td><td>Email system field</td></tr>
        <tr><td>Invalid response</td><td>Ask them to check and re-enter the address</td></tr>
        <tr><td>Successful response</td><td>Continue to email confirmation</td></tr>
      </tbody>
    </table></div>
    <p class="small">ManyChat's Email reply type checks the email's format. The Data Collection block requires a paid plan. If an email is already saved on the contact, route them straight to confirmation.</p>
  </div>

  <div class="card" id="s4">
    <div class="chead"><div class="num">4</div><h3>Confirm the email address</h3></div>
    {bubble(CONFIRM)}
    <p class="small">Replace <code>[Email]</code> using ManyChat's variable picker.</p>
    <div class="tblwrap"><table>
      <thead><tr><th>Button</th><th>Next action</th></tr></thead>
      <tbody>
        <tr><td>{copybtn("Yes, that's correct")}</td><td>Tag the contact and continue to delivery</td></tr>
        <tr><td>{copybtn("Change my email")}</td><td>Return to the email collection block</td></tr>
      </tbody>
    </table></div>
    <div class="lbl">Tags to apply after they confirm</div>
    <div>{copybtn("CR_Email_Confirmed")}{copybtn("Source_Instagram_Follow")}</div>
    <div class="note" style="margin-top:14px"><b>Deliver from the confirmation branch only.</b> An address they are still correcting must not start the course email.</div>
  </div>

  <div class="card" id="s5">
    <div class="chead"><div class="num">5</div><h3>Hand off to GHL for the email, then point them to their inbox</h3></div>
    <p><b>GHL sends the course email, not ManyChat.</b> Saving an email address in ManyChat sends nothing on its own. The <code>CR_Email_Confirmed</code> tag from step 4 is what moves the contact into GHL, through one Zap.</p>
    <div class="tblwrap"><table>
      <thead><tr><th>Zap step</th><th>Setting</th></tr></thead>
      <tbody>
        <tr><td>Trigger</td><td>ManyChat, <b>New Tagged User</b>, tag <code>CR_Email_Confirmed</code></td></tr>
        <tr><td>Action</td><td>LeadConnector, <b>Add/Update Contact</b></td></tr>
        <tr><td>Fields to map</td><td>Email, First name, Last name, Instagram username</td></tr>
        <tr><td>Tags to add</td><td>{copybtn("communication reset")}{copybtn("lead-instagram")}</td></tr>
      </tbody>
    </table></div>
    <p>In GHL the tag <code>communication reset</code> starts <b>01 - Communication Reset Lead Magnet</b>, which is already published and sends the course email. Nothing else to build on the GHL side.</p>
    <p>Right after the tags are applied in ManyChat, send this Instagram message. Text only, no button and no course link:</p>
    {bubble(DELIVER)}
    <div class="note"><b>Never send the course in the DM.</b> The course arrives by email only, from GHL. The Instagram message just points them to their inbox.</div>
  </div>
</section>

<footer>
  <span>Communication Reset | New Follower · ManyChat automation · Updated Sept 28, 2026</span>
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
  document.querySelectorAll('.copymsg').forEach(btn => {{
    btn.addEventListener('click', async () => {{
      await copyText(btn.dataset.tag);
      const old = btn.textContent; btn.textContent = 'copied ✓';
      toast.textContent = 'Message copied'; toast.classList.add('show');
      setTimeout(() => {{ btn.textContent = old; toast.classList.remove('show'); }}, 1600);
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
