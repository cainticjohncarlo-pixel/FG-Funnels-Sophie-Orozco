# -*- coding: utf-8 -*-
"""Client Tagging SOP: every tag the sales team adds at close, per program, and what each tag starts.
Source of truth: live GHL tag list + workflow triggers (checked 2026-09-26) and Hazel's program list (2026-09-26)."""
import html, os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "index.html")

MEN_RMM   = "general- rrm men"       # spelled with two r's in GHL; the workflow trigger uses this exact tag
WOMEN_RMM = "general- rmm women"
MEN_CHK   = "rmm- checkin (men)"
WOMEN_CHK = "rmm- checkin (women)"
ALWAYS    = "existing client"

# program label, gender, onboarding tag, onboarding workflow, offer discussed, rmm tag (or None), check-in tag (or None)
ROWS = [
    ("Couples Coaching",     "men",   "client - couples coaching men",   "Onboarding Email- (men) Couples",           "Couples Coaching (men)",       MEN_RMM,   None),
    ("Couples Coaching",     "women", "client - couples coaching women", "Onboarding Email- (women) Couples",         "Couples Coaching (women)",     WOMEN_RMM, None),
    ("Couples Coaching VIP", "men",   "client - vip sophie men",         "Onboarding Email- Premium Men Couples",     "Couples Coaching VIP (men)",   MEN_RMM,   None),
    ("Couples Coaching VIP", "women", "client - vip sophie women",       "Onboarding Email- Premium Women Couples",   "Couples Coaching VIP (women)", WOMEN_RMM, None),
    ("RMM Accelerator",      "men",   "client - rmm accelerator men",    "Onboarding Email- RMM Accelerator (men)",   "RMM Accelerator Men",          MEN_RMM,   MEN_CHK),
    ("RMM Accelerator",      "women", "client - rmm accelerator women",  "Onboarding Email- RMM Accelerator(women)",  "RMM Accelerator Women",        WOMEN_RMM, WOMEN_CHK),
    ("RMM Group Only",       "men",   "client - group only men",         "Onboarding Email- RMM Group Only (men)",    "RMM Group Only Men",           MEN_RMM,   None),
    ("RMM Group Only",       "women", "client - group only women",       "Onboarding Email- RMM Group Only (women)",  "RMM Group Only Women",         WOMEN_RMM, None),
    ("Self-Paced",           "men",   "client - rmm self paced men",     "Onboarding Email- RMM- SELF PACED (Men)",   "Self-Paced Lifetime Access",   MEN_RMM,   None),
    ("Self-Paced",           "women", "client - rmm self paced women",   "Onboarding Email- RMM- SELF PACED (Women)", "Self-Paced Lifetime Access",   WOMEN_RMM, None),
]

WRONG = [
    ("client - accelerator men / women", "Looks like the Accelerator tag. Starts nothing. This is what Brendan Logan and Justin Huntington got, and neither received an onboarding email."),
    ("client - couples coaching",        "Missing the gender. Starts nothing."),
    ("client - couples coaching vip",    "Not the VIP tag. The VIP onboarding runs on client - vip sophie men / women."),
    ("client - course only men / women", "Retired program. The automation is unpublished."),
    ("client - rmm course only men / women", "Retired program. The automation is unpublished."),
    ("client - rmm men / women",         "Retired program. The automation is unpublished."),
    ("rmm- checkin",                     "Missing (men) or (women). Starts nothing."),
    ("general- rmm men",                 "Does not exist. The real men's tag is spelled general- rrm men, with two r's."),
]

E = html.escape

def btn(val):
    return f'<button class="tagbtn" data-tag="{E(val)}">{E(val)} <span class="ic">copy</span></button>'

def dash():
    return '<span class="none">none</span>'

# ------------------------------------------------------------------ master table
trs = []
for i, (prog, g, onb, wf, offer, rmm, chk) in enumerate(ROWS, 1):
    trs.append(
        f'<tr><td><a href="#p{i}">{E(prog)}</a><div class="g">{g}</div></td>'
        f'<td><code>{E(onb)}</code></td>'
        f'<td>{("<code>"+E(rmm)+"</code>") if rmm else dash()}</td>'
        f'<td>{("<code>"+E(chk)+"</code>") if chk else dash()}</td>'
        f'<td>{E(offer)}</td></tr>')
master = "".join(trs)

# ------------------------------------------------------------------ per-program cards
cards = []
for i, (prog, g, onb, wf, offer, rmm, chk) in enumerate(ROWS, 1):
    tags = [onb, ALWAYS] + ([rmm] if rmm else []) + ([chk] if chk else [])
    starts = [f"<li><code>{E(onb)}</code> starts <b>{E(wf)}</b>: the onboarding email with the Circle invitation.</li>"]
    if rmm:
        wfn = "GENERAL- RMM Men 12 Weeks with Calls" if g == "men" else "RMM Women 12 Weeks with Calls- GENERAL"
        starts.append(f"<li><code>{E(rmm)}</code> starts <b>{wfn}</b>: the 12 week program email sequence.</li>")
    if chk:
        wfn = "Check-In Sequence (men)" if g == "men" else "Check-In Sequence (women)"
        starts.append(f"<li><code>{E(chk)}</code> starts <b>{wfn}</b>: the snapshot email, then the weekly check-ins.</li>")
    starts.append(f"<li><code>{E(ALWAYS)}</code> marks the record as a client so lead automations leave them alone.</li>")
    cards.append(f'''
<section class="card" id="p{i}">
  <div class="chead">
    <div class="num">{i}</div>
    <div>
      <div class="lbl" style="margin-bottom:2px">Program purchased</div>
      <h3>{E(prog)} <span class="gtag">{g}</span></h3>
    </div>
  </div>
  <div class="cgrid">
    <div>
      <div class="lbl">Tags to add on the contact, all of them</div>
      <div class="taglist">{"".join(btn(t) for t in tags)}</div>
      <div class="lbl" style="margin-top:16px">Offer Discussed on the opportunity</div>
      {btn(offer)}
    </div>
    <div>
      <div class="lbl">What each tag starts</div>
      <ul class="starts">{"".join(starts)}</ul>
    </div>
  </div>
</section>''')

wrong_rows = "".join(f'<tr><td><code class="bad">{E(t)}</code></td><td>{E(why)}</td></tr>' for t, why in WRONG)

page = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="robots" content="noindex">
<title>Client Tagging SOP — Sophie Orozco Coaching</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@500;600&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
  :root{{
    --cream:#F7F4EE; --card:#FFFFFF; --ink:#1E1B16; --muted:#6B6459;
    --terra:#A9502C; --terra-soft:#F3E3DA; --green:#1D4A33; --green-soft:#E4EEE7;
    --gold:#B98A2F; --line:#E4DDD2; --warn-bg:#FBEFE7; --warn:#8C3D14; --bad-bg:#FBE9E7;
  }}
  *{{box-sizing:border-box;margin:0;padding:0}}
  body{{background:var(--cream);color:var(--ink);font-family:'Inter',system-ui,sans-serif;line-height:1.65;font-size:16px}}
  .wrap{{max-width:1000px;margin:0 auto;padding:0 20px 90px}}
  header.hero{{background:var(--ink);color:#F7F4EE;padding:48px 20px 40px;text-align:center}}
  .hero .brand{{font-family:'Playfair Display',serif;font-size:14px;letter-spacing:.18em;text-transform:uppercase;color:#CDB68A;margin-bottom:12px}}
  .hero h1{{font-family:'Playfair Display',serif;font-size:clamp(28px,5vw,40px);font-weight:600;line-height:1.15;margin-bottom:12px}}
  .hero p{{color:#BFB8AC;max-width:640px;margin:0 auto;font-size:15.5px}}
  section{{margin-top:40px}}
  h2{{font-family:'Playfair Display',serif;font-size:clamp(22px,3.4vw,28px);font-weight:600;margin-bottom:12px}}
  .kicker{{color:var(--terra);font-weight:700;font-size:12.5px;letter-spacing:.14em;text-transform:uppercase;margin-bottom:6px}}
  code{{font-family:ui-monospace,monospace;font-size:12.5px;background:#F4F1EA;border:1px solid var(--line);border-radius:5px;padding:1px 6px;white-space:nowrap}}
  code.bad{{background:var(--bad-bg);border-color:#E8C4BC;color:#8C2D14}}
  .steps{{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:14px;margin-top:16px}}
  .step{{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:18px}}
  .step .n{{display:inline-flex;align-items:center;justify-content:center;width:28px;height:28px;border-radius:50%;background:var(--terra);color:#fff;font-weight:700;font-size:13px;margin-bottom:8px}}
  .step b{{display:block;margin-bottom:4px;font-size:15px}}
  .step p{{font-size:13.5px;color:var(--muted)}}
  .tblwrap{{overflow-x:auto;background:var(--card);border:1px solid var(--line);border-radius:14px}}
  table{{width:100%;border-collapse:collapse;font-size:14px}}
  th{{text-align:left;font-size:11.5px;letter-spacing:.08em;text-transform:uppercase;color:var(--green);padding:12px 14px;border-bottom:1px solid var(--line);background:#FBF9F5;line-height:1.35;vertical-align:bottom}}
  td{{padding:10px 14px;border-bottom:1px solid var(--line);vertical-align:top}}
  tr:last-child td{{border-bottom:none}}
  td a{{color:var(--ink);font-weight:600;text-decoration:none}}
  td a:hover{{color:var(--terra)}}
  td .g{{font-size:12px;color:var(--muted);text-transform:capitalize}}
  .none{{color:#B5AEA3;font-size:13px}}
  .auto{{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:14px;margin-top:16px}}
  .abox{{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:18px}}
  .abox h4{{font-size:15px;margin-bottom:4px}}
  .abox .wf{{font-family:ui-monospace,monospace;font-size:12px;color:var(--muted);margin-bottom:8px}}
  .abox p{{font-size:13.5px;color:var(--muted)}}
  .abox .who{{margin-top:10px;font-size:13px}}
  .card{{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:26px;margin-top:20px;scroll-margin-top:16px}}
  .chead{{display:flex;gap:14px;align-items:flex-start;padding-bottom:16px;border-bottom:1px solid var(--line)}}
  .num{{flex:none;width:34px;height:34px;border-radius:50%;background:var(--green);color:#fff;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:15px}}
  .card h3{{font-family:'Playfair Display',serif;font-size:21px;font-weight:600;line-height:1.25}}
  .gtag{{display:inline-block;font-family:'Inter',sans-serif;font-size:12px;font-weight:600;letter-spacing:.08em;text-transform:uppercase;color:var(--terra);background:var(--terra-soft);border-radius:999px;padding:2px 10px;vertical-align:middle;margin-left:6px}}
  .cgrid{{display:grid;grid-template-columns:1.1fr 1fr;gap:24px;margin-top:18px}}
  @media(max-width:760px){{.cgrid{{grid-template-columns:1fr}}}}
  .lbl{{font-size:11.5px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:var(--green);margin-bottom:7px}}
  .small{{font-size:14px;color:var(--muted)}}
  .taglist{{display:flex;flex-direction:column;gap:8px;align-items:flex-start}}
  .tagbtn{{display:inline-flex;align-items:center;gap:8px;background:#F4F1EA;border:1px solid var(--line);border-radius:8px;padding:8px 12px;font-family:ui-monospace,monospace;font-size:13px;color:var(--ink);cursor:pointer;transition:.15s;text-align:left}}
  .tagbtn:hover{{background:var(--terra-soft);border-color:var(--terra)}}
  .tagbtn.copied{{background:var(--green-soft);border-color:var(--green);color:var(--green)}}
  .tagbtn .ic{{opacity:.5;font-size:11.5px}}
  .starts{{list-style:none;display:flex;flex-direction:column;gap:9px;font-size:14px}}
  .starts li{{padding-left:14px;position:relative;color:var(--muted)}}
  .starts li::before{{content:"";position:absolute;left:0;top:10px;width:6px;height:6px;border-radius:50%;background:var(--terra)}}
  .starts b{{color:var(--ink)}}
  .warnbox{{background:var(--warn-bg);border-left:4px solid var(--terra);border-radius:0 12px 12px 0;padding:15px 18px;margin-top:16px}}
  .warnbox b{{color:var(--warn)}}
  .warnbox p{{font-size:14px;color:var(--warn);margin-top:3px}}
  .warnbox code{{background:#fff}}
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
  <h1>Client Tagging SOP</h1>
  <p>Every tag the sales team adds when a client closes, program by program, and the automation each tag starts. Click any value to copy it.</p>
</header>

<div class="wrap">

<section>
  <div class="kicker">At close, in this order</div>
  <h2>How a new client gets set up</h2>
  <div class="steps">
    <div class="step"><span class="n">1</span><b>Close the opportunity</b><p>Move the card to Closed Won and set <b>Offer Discussed</b> to the program's value from the table below.</p></div>
    <div class="step"><span class="n">2</span><b>Add every tag in the client's row</b><p>Find the program and the client's gender in the table, then add each tag shown. Copy them from this page, do not type them.</p></div>
    <div class="step"><span class="n">3</span><b>The tags do the rest</b><p>The onboarding tag sends the welcome email. The RMM tag starts the 12 week emails. The check-in tag starts the weekly check-ins. A missing tag means that automation never runs.</p></div>
  </div>
  <div class="warnbox"><b>Copy each tag word for word.</b>
    <p>An automation only starts when the tag matches exactly, character for character. Several tags look almost identical, so copy from this page instead of typing. A near miss starts nothing and nobody is alerted. One to know: the men's RMM tag is spelled <code>general- rrm men</code>, with two r's. That spelling is what the automation listens for, so use it as is.</p></div>
</section>

<section>
  <div class="kicker">The whole picture</div>
  <h2>Program, tags, Offer Discussed</h2>
  <p class="small" style="margin-bottom:12px">Add <code>existing client</code> to every client as well. It is not repeated in the table.</p>
  <div class="tblwrap"><table>
    <thead><tr><th>Program purchased</th><th>Onboarding tag</th><th>General - RMM Automation Sequence</th><th>Check - In Automation sequence</th><th>Offer Discussed</th></tr></thead>
    <tbody>{master}</tbody>
  </table></div>
</section>

<section>
  <div class="kicker">What runs</div>
  <h2>The three automations behind the tags</h2>
  <div class="auto">
    <div class="abox"><h4>Onboarding email</h4><div class="wf">Onboarding Email- ... (one per program and gender)</div>
      <p>Sends the welcome email with the Circle invitation link the moment the program tag lands. The tag is the only trigger.</p>
      <div class="who"><b>Who gets it:</b> every program.</div></div>
    <div class="abox"><h4>RMM 12 weeks with calls</h4><div class="wf">GENERAL- RMM Men 12 Weeks with Calls<br>RMM Women 12 Weeks with Calls- GENERAL</div>
      <p>The 12 week program email sequence. Starts on <code>{E(MEN_RMM)}</code> or <code>{E(WOMEN_RMM)}</code>.</p>
      <div class="who"><b>Who gets it:</b> Couples Coaching, Couples Coaching VIP, RMM Accelerator, RMM Group Only, Self-Paced. Every program, per Hazel, Sept 30.</div></div>
    <div class="abox"><h4>Check-in sequence</h4><div class="wf">Check-In Sequence (men)<br>Check-In Sequence (women)</div>
      <p>The snapshot email, then the weekly check-ins starting with Week 1. Starts on <code>{E(MEN_CHK)}</code> or <code>{E(WOMEN_CHK)}</code>.</p>
      <div class="who"><b>Who gets it:</b> RMM Accelerator only.</div></div>
  </div>
</section>

<section>
  <div class="kicker">Program by program</div>
  <h2>Copy the tags for the client's program</h2>
  <p class="small">Couples: each partner who has their own contact record gets the tags for their own gender.</p>
  {"".join(cards)}
</section>

<section>
  <div class="kicker">Do not use these</div>
  <h2>Tags that look right and start nothing</h2>
  <p class="small" style="margin-bottom:12px">These exist in the account, some with clients on them from before. None of them starts an automation. If a client has one of these and nothing else, they got no onboarding email.</p>
  <div class="tblwrap"><table>
    <thead><tr><th>Tag</th><th>Why not</th></tr></thead>
    <tbody>{wrong_rows}</tbody>
  </table></div>
</section>

<footer>
  <span>Client Tagging SOP · Sophie Orozco Coaching · Updated Sept 30, 2026</span>
  <span>Maintained by John Carlo Caintic</span>
</footer>

</div>

<div class="toast" id="toast">Copied</div>
<button class="top" id="top">↑ Top</button>

<script>
  const toast = document.getElementById('toast');
  document.querySelectorAll('.tagbtn').forEach(btn => {{
    btn.addEventListener('click', async () => {{
      const tag = btn.dataset.tag;
      try {{ await navigator.clipboard.writeText(tag); }}
      catch (e) {{
        const ta = document.createElement('textarea');
        ta.value = tag; document.body.appendChild(ta); ta.select();
        try {{ document.execCommand('copy'); }} catch (err) {{}}
        document.body.removeChild(ta);
      }}
      btn.classList.add('copied');
      const ic = btn.querySelector('.ic'); const old = ic.textContent; ic.textContent = 'copied ✓';
      toast.textContent = 'Copied: ' + tag; toast.classList.add('show');
      setTimeout(() => {{ btn.classList.remove('copied'); ic.textContent = old; toast.classList.remove('show'); }}, 1600);
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
