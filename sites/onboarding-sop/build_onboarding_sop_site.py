# -*- coding: utf-8 -*-
"""Build the per-workflow Onboarding SOP site from the Google Doc export."""
import re, html, os, json

SRC = "tag_doc.txt"
OUT_DIR = "onboarding-sop"
os.makedirs(OUT_DIR, exist_ok=True)

doc = open(SRC, encoding="utf-8").read()

# workflow name -> (program label, tag, gender-ish order)
WF = [
    ("Onboarding Email- (men) Couples",           "Couples Coaching — men",        "client - couples coaching men"),
    ("Onboarding Email- (women) Couples",         "Couples Coaching — women",      "client - couples coaching women"),
    ("Onboarding Email- Premium Men Couples",     "Couples Coaching VIP — men",    "client - vip sophie men"),
    ("Onboarding Email- Premium Women Couples",   "Couples Coaching VIP — women",  "client - vip sophie women"),
    ("Onboarding Email- RMM Accelerator (men)",   "RMM Accelerator — men",         "client - rmm accelerator men"),
    ("Onboarding Email- RMM Accelerator (women)", "RMM Accelerator — women",       "client - rmm accelerator women"),
    ("Onboarding Email- RMM Men",                 "RMM standard — men",            "client - rmm men"),
    ("Onboarding Email- RMM Women",               "RMM standard — women",          "client - rmm women"),
    ("Onboarding Email- RMM Group Only (men)",    "RMM Group Only — men",          "client - group only men"),
    ("Onboarding Email- RMM Group Only (women)",  "RMM Group Only — women",        "client - group only women"),
    ("Onboarding Email- RMM Course only Men",     "RMM Course Only — men",         "client - rmm course only men"),
    ("Onboarding Email- RMM Course only Women",   "RMM Course Only — women",       "client - rmm course only women"),
    ("Onboarding Email- RMM- SELF PACED (Men)",    "Self-Paced — men",              "client - rmm self paced men"),
    ("Onboarding Email- RMM- SELF PACED (Women)",  "Self-Paced — women",            "client - rmm self paced women"),
]

# --- locate each workflow's CONTENT section (the 2nd+ occurrence, after the audit table)
positions = [(m.start(), m.group(0).strip()) for m in re.finditer(r'Onboarding Email-[^\n]*', doc)]
content_start = {}
for pos, name in positions:
    if pos < 2900:   # skip the audit table at the top
        continue
    nm = name.strip()
    if nm not in content_start:
        content_start[nm] = pos

# boundaries come from EVERY workflow in the doc, so an unlisted one never bleeds into its neighbour
all_starts = sorted(content_start.values())
sections = {}
for w in WF:
    pos = content_start.get(w[0])
    if pos is None:
        continue
    later = [p for p in all_starts if p > pos]
    end = later[0] if later else len(doc)
    sections[w[0]] = doc[pos:end]

# ---- second source: the RMM- SELF PACED Google Doc (tabs: Womens, Mens)
SP_SRC = "selfpaced_doc.txt"
EMOJI = {":tada:": "🎉", ":link:": "🔗", ":love_letter:": "💌", ":e-mail:": "📧"}
def _sp_section(tab_text):
    NL = chr(10)
    lines = [l.strip() for l in tab_text.split(NL)]
    lines = [l for l in lines if l]
    subj = ""; body = []
    for l in lines:
        if l.startswith("Subject:"):
            subj = l[len("Subject:"):].strip()
        elif subj:
            body.append(l)
    for k, v in EMOJI.items():
        subj = subj.replace(k, v)
    # renumber every list so it restarts at 1 (the doc export continued numbering across tabs)
    fixed = []; n = 0
    for l in body:
        for k, v in EMOJI.items():
            l = l.replace(k, v)
        m = re.match(r"([0-9]+)[.] (.*)", l)
        if m:
            n += 1; fixed.append(f"{n}. {m.group(2)}")
        else:
            n = 0; fixed.append(l)
    # consecutive list lines share one paragraph; everything else is its own paragraph
    paras = []; cur = []
    for l in fixed:
        is_item = bool(re.match(r"[0-9]+[.] ", l)) or l.startswith("💌")
        if is_item:
            cur.append(l)
        else:
            if cur: paras.append(NL.join(cur)); cur = []
            paras.append(l)
    if cur: paras.append(NL.join(cur))
    return "Subject line: " + subj + NL + NL + (NL + NL).join(paras)

if os.path.exists(SP_SRC):
    sp = open(SP_SRC, encoding="utf-8").read().lstrip(chr(65279))
    wi = sp.index("Womens"); mi = sp.index("Mens")
    sections["Onboarding Email- RMM- SELF PACED (Women)"] = _sp_section(sp[wi:mi])
    sections["Onboarding Email- RMM- SELF PACED (Men)"]   = _sp_section(sp[mi:])

def parse(sec):
    """Pull subject + body out of one section."""
    subj = ""
    m = re.search(r'Subject line:\s*(.+)', sec)
    if m:
        subj = m.group(1).strip()
    # body starts at the first "Hi {{" or after the subject line
    bm = re.search(r'(Hi \{\{contact\.first_name\}\},.*)', sec, re.S)
    body = bm.group(1) if bm else sec
    # tidy: collapse 3+ newlines, strip trailing workflow-name noise
    body = re.sub(r'\n{3,}', '\n\n', body).strip()
    return subj, body

def body_html(body):
    """Turn the plain body into readable HTML with links + headings."""
    out = []
    for para in body.split("\n\n"):
        p = para.strip()
        if not p:
            continue
        esc = html.escape(p)
        esc = re.sub(r'(https?://[^\s<]+)', r'<a href="\1" target="_blank" rel="noopener">\1</a>', esc)
        esc = esc.replace("{{contact.first_name}}", '<span class="mf">{{contact.first_name}}</span>')
        if re.match(r'^Step \d+:', p) or p.startswith("What to Expect") or p.startswith("Support") \
           or p.startswith("Office Hours") or p.startswith("One Final Reminder") or p.startswith("Session Recordings") or p.startswith("Having Trouble"):
            out.append(f'<h4>{esc}</h4>')
        else:
            esc = esc.replace("\n", "<br>")
            out.append(f'<p>{esc}</p>')
    return "\n".join(out)

cards = []
nav = []
for i, (wf, program, tag) in enumerate(WF, 1):
    sec = sections.get(wf, "")
    subj, body = parse(sec)
    anchor = "wf" + str(i)
    nav.append(f'<a href="#{anchor}"><span class="nprog">{html.escape(program)}</span>'
               f'<span class="ntag">{html.escape(tag)}</span></a>')
    cards.append(f'''
<section class="wfcard" id="{anchor}">
  <div class="wfhead">
    <div class="wfnum">{i}</div>
    <div>
      <h3>{html.escape(program)}</h3>
      <div class="wfname">{html.escape(wf)}</div>
    </div>
  </div>
  <div class="wfgrid">
    <div class="wfcell">
      <div class="lbl">Tag the sales team applies</div>
      <button class="tagbtn" data-tag="{html.escape(tag)}">{html.escape(tag)} <span class="ic">copy</span></button>
      <div class="lbl" style="margin-top:16px">Plus, always</div>
      <button class="tagbtn" data-tag="existing client">existing client <span class="ic">copy</span></button>
    </div>
    <div class="wfcell">
      <div class="lbl">What happens</div>
      <p class="small">Adding the tag starts <b>{html.escape(wf)}</b>, which sends the onboarding email below with the client's Circle invitation.</p>
    </div>
  </div>
  <div class="mail">
    <div class="mailhead">Onboarding email sent by this automation</div>
    <div class="subj"><span>Subject:</span> {html.escape(subj) if subj else "(no subject captured)"}</div>
    <div class="mailbody">
      {body_html(body) if body else '<p class="small">Email content not captured in the source document.</p>'}
    </div>
  </div>
</section>''')

page = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="robots" content="noindex">
<title>Onboarding SOP by Program — Sophie Orozco Coaching</title>
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
  .wrap{{max-width:900px;margin:0 auto;padding:0 20px 90px}}
  header.hero{{background:var(--ink);color:#F7F4EE;padding:48px 20px 40px;text-align:center}}
  .hero .brand{{font-family:'Playfair Display',serif;font-size:14px;letter-spacing:.18em;text-transform:uppercase;color:#CDB68A;margin-bottom:12px}}
  .hero h1{{font-family:'Playfair Display',serif;font-size:clamp(28px,5vw,40px);font-weight:600;line-height:1.15;margin-bottom:12px}}
  .hero p{{color:#BFB8AC;max-width:560px;margin:0 auto;font-size:15.5px}}
  section{{margin-top:40px}}
  h2{{font-family:'Playfair Display',serif;font-size:clamp(22px,3.4vw,28px);font-weight:600;margin-bottom:12px}}
  .kicker{{color:var(--terra);font-weight:700;font-size:12.5px;letter-spacing:.14em;text-transform:uppercase;margin-bottom:6px}}
  /* steps */
  .steps{{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:14px;margin-top:16px}}
  .step{{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:18px}}
  .step .n{{display:inline-flex;align-items:center;justify-content:center;width:28px;height:28px;border-radius:50%;background:var(--terra);color:#fff;font-weight:700;font-size:13px;margin-bottom:8px}}
  .step b{{display:block;margin-bottom:4px;font-size:15px}}
  .step p{{font-size:13.5px;color:var(--muted)}}
  /* nav */
  .navgrid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:10px;margin-top:16px}}
  .navgrid a{{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:13px 15px;text-decoration:none;color:var(--ink);transition:.15s;display:block}}
  .navgrid a:hover{{border-color:var(--terra);background:var(--terra-soft)}}
  .nprog{{display:block;font-weight:600;font-size:14.5px;margin-bottom:3px}}
  .ntag{{display:block;font-family:ui-monospace,monospace;font-size:11.5px;color:var(--muted)}}
  /* workflow cards */
  .wfcard{{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:26px;margin-top:20px;scroll-margin-top:16px}}
  .wfhead{{display:flex;gap:14px;align-items:flex-start;padding-bottom:16px;border-bottom:1px solid var(--line)}}
  .wfnum{{flex:none;width:34px;height:34px;border-radius:50%;background:var(--green);color:#fff;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:15px}}
  .wfcard h3{{font-family:'Playfair Display',serif;font-size:21px;font-weight:600;line-height:1.25}}
  .wfname{{font-family:ui-monospace,monospace;font-size:12px;color:var(--muted);margin-top:3px}}
  .wfgrid{{display:grid;grid-template-columns:1fr 1fr;gap:22px;margin-top:18px}}
  @media(max-width:640px){{.wfgrid{{grid-template-columns:1fr}}}}
  .lbl{{font-size:11.5px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:var(--green);margin-bottom:7px}}
  .small{{font-size:14px;color:var(--muted)}}
  .tagbtn{{display:inline-flex;align-items:center;gap:8px;background:#F4F1EA;border:1px solid var(--line);border-radius:8px;padding:8px 12px;font-family:ui-monospace,monospace;font-size:13px;color:var(--ink);cursor:pointer;transition:.15s;text-align:left}}
  .tagbtn:hover{{background:var(--terra-soft);border-color:var(--terra)}}
  .tagbtn.copied{{background:var(--green-soft);border-color:var(--green);color:var(--green)}}
  .tagbtn .ic{{opacity:.5;font-size:11.5px}}
  /* email block */
  .mail{{margin-top:20px;border:1px solid var(--line);border-radius:12px;overflow:hidden}}
  .mailhead{{background:var(--green);color:#EAF2EC;font-size:12px;font-weight:600;letter-spacing:.08em;text-transform:uppercase;padding:10px 16px}}
  .subj{{background:#FBF9F5;padding:12px 16px;border-bottom:1px solid var(--line);font-weight:600;font-size:14.5px}}
  .subj span{{color:var(--muted);font-weight:500;margin-right:6px}}
  .mailbody{{padding:18px 16px;font-size:14.5px;max-height:420px;overflow-y:auto}}
  .mailbody p{{margin-bottom:11px}}
  .mailbody h4{{font-size:14.5px;font-weight:700;color:var(--terra);margin:16px 0 7px}}
  .mailbody a{{color:var(--green);word-break:break-all}}
  .mf{{background:var(--terra-soft);color:var(--terra);border-radius:4px;padding:1px 5px;font-family:ui-monospace,monospace;font-size:12.5px}}
  .warnbox{{background:var(--warn-bg);border-left:4px solid var(--terra);border-radius:0 12px 12px 0;padding:15px 18px;margin-top:16px}}
  .warnbox b{{color:var(--warn)}}
  .warnbox p{{font-size:14px;color:var(--warn);margin-top:3px}}
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
  <h1>Onboarding SOP by Program</h1>
  <p>Every program, its tag, and the exact onboarding email the client receives. Click any tag to copy it.</p>
</header>

<div class="wrap">

{"".join(cards)}

<footer>
  <span>Onboarding SOP by Program · Sophie Orozco Coaching</span>
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

open(os.path.join(OUT_DIR, "index.html"), "w", encoding="utf-8").write(page)
print("wrote", os.path.join(OUT_DIR, "index.html"), len(page), "bytes")
for wf, program, tag in WF:
    sec = sections.get(wf, "")
    s, b = parse(sec)
    print(f"  {'OK ' if b else 'EMPTY'} {program:32} subj={s[:44]!r}")
