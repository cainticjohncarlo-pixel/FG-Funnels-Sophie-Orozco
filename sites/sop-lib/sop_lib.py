# -*- coding: utf-8 -*-
"""Shared generator for the Sophie Orozco Coaching SOP pages: house CSS, page shell, and a simple
vertical flowchart renderer (SVG). Import from a build.py and call page(...)."""
import html

E = html.escape

# ------------------------------------------------------------------ flowchart
# items: list of tuples
#   ('T', text)                       trigger, dark
#   ('A', text)                       action, white with green border
#   ('W', text)                       wait, soft green
#   ('D', question, yes_items, no_items[, yes_label, no_label])   decision, two branches
#   ('E', text)                       end marker
#   ('N', text)                       small note under the previous node
W = 560; NODE_W = 330; LINE = 18

def _wrap(text, max_chars=36):
    words = text.split(); lines = []; cur = ""
    for w in words:
        if len(cur) + len(w) + 1 > max_chars and cur:
            lines.append(cur); cur = w
        else:
            cur = (cur + " " + w).strip()
    if cur: lines.append(cur)
    return lines[:3]

def _node(kind, text, cx, y, w=NODE_W):
    lines = _wrap(text, 34 if w >= 300 else 24)
    h = 22 + LINE * len(lines)
    cls = {"T": "n-t", "A": "n-a", "W": "n-w", "E": "n-e", "D": "n-d"}[kind]
    rx = 14 if kind != "E" else 16
    ty = y + h / 2 - (len(lines) - 1) * LINE / 2
    ts = "".join(f'<tspan x="{cx}" dy="{0 if i == 0 else LINE}">{E(l)}</tspan>' for i, l in enumerate(lines))
    svg = f'<rect class="{cls}" x="{cx - w/2}" y="{y}" width="{w}" height="{h}" rx="{rx}"/>' \
          f'<text class="{cls}-t" x="{cx}" y="{ty}" text-anchor="middle" dominant-baseline="middle">{ts}</text>'
    return svg, h

def _arrow(x1, y1, x2, y2):
    if x1 == x2:
        return f'<path class="edge" d="M{x1},{y1} L{x2},{y2}" marker-end="url(#arr)"/>'
    my = y1 + 14
    return f'<path class="edge" d="M{x1},{y1} L{x1},{my} L{x2},{my} L{x2},{y2}" marker-end="url(#arr)"/>'

def _label(x, y, text, cls="lbl-yes"):
    w = len(text) * 6.6 + 18
    return f'<rect class="{cls}" x="{x - w/2}" y="{y - 11}" width="{w}" height="22" rx="11"/>' \
           f'<text class="{cls}-t" x="{x}" y="{y + 1}" text-anchor="middle" dominant-baseline="middle">{E(text)}</text>'

def flow(items, title=None):
    """Render a vertical flowchart. Returns an HTML string with the SVG inside a .diagram box."""
    parts = []; y = 16; cx = W / 2; GAP = 22
    prev_bottom = None; prev_x = cx
    pending_joins = []   # (x, y) ends of branches to join into the next centre node

    def column(seq, colx, starty, colw):
        """render a linear sequence in a column, return (bottom_y, svg)"""
        out = []; yy = starty; bottom = None; px = colx
        for it in seq:
            kind = it[0]
            if kind == "N":
                out.append(f'<text class="note-t" x="{colx}" y="{yy + 6}" text-anchor="middle">{E(it[1])}</text>'); yy += 20; continue
            svg, h = _node(kind, it[1], colx, yy, colw)
            if bottom is not None: out.append(_arrow(px, bottom, colx, yy))
            out.append(svg); bottom = yy + h; yy = bottom + GAP; px = colx
        return bottom, "".join(out)

    for it in items:
        kind = it[0]
        if kind == "N":
            parts.append(f'<text class="note-t" x="{cx}" y="{y + 6}" text-anchor="middle">{E(it[1])}</text>'); y += 20; continue
        if kind == "D":
            q, yes_items, no_items = it[1], it[2], it[3]
            yl = it[4] if len(it) > 4 else "Yes"; nl = it[5] if len(it) > 5 else "No"
            svg, h = _node("D", q, cx, y, 320)
            if pending_joins:
                for (jx, jy) in pending_joins: parts.append(_arrow(jx, jy, cx, y))
                pending_joins = []
            elif prev_bottom is not None:
                parts.append(_arrow(prev_x, prev_bottom, cx, y))
            parts.append(svg); dbot = y + h
            lx, rx_ = W * 0.26, W * 0.74; colw = 250
            by = dbot + 46
            parts.append(_arrow(cx - 60, dbot, lx, by)); parts.append(_label(lx, dbot + 24, yl, "lbl-yes"))
            parts.append(_arrow(cx + 60, dbot, rx_, by)); parts.append(_label(rx_, dbot + 24, nl, "lbl-no"))
            lb, lsvg = column(yes_items, lx, by, colw); rb, rsvg = column(no_items, rx_, by, colw)
            parts.append(lsvg); parts.append(rsvg)
            pending_joins = [(lx, lb), (rx_, rb)] if (lb and rb) else []
            y = max(lb or by, rb or by) + GAP + 10; prev_bottom = None
            continue
        svg, h = _node(kind, it[1], cx, y)
        if pending_joins:
            for (jx, jy) in pending_joins: parts.append(_arrow(jx, jy, cx, y))
            pending_joins = []
        elif prev_bottom is not None:
            parts.append(_arrow(prev_x, prev_bottom, cx, y))
        parts.append(svg); prev_bottom = y + h; prev_x = cx; y = prev_bottom + GAP
    height = y + 6
    head = f'<div class="dtitle">{E(title)}</div>' if title else ""
    return f'''<div class="diagram">{head}<svg viewBox="0 0 {W} {height}" xmlns="http://www.w3.org/2000/svg" role="img">
<defs><marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#6B6459"/></marker></defs>
{"".join(parts)}</svg></div>'''

# ------------------------------------------------------------------ building blocks
def cp(val):
    return f'<button class="tagbtn" data-tag="{E(val)}">{E(val)} <span class="ic">copy</span></button>'

def table(head, rows, cls=""):
    th = "".join(f"<th>{h}</th>" for h in head)
    trs = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
    return f'<div class="tblwrap {cls}"><table><thead><tr>{th}</tr></thead><tbody>{trs}</tbody></table></div>'

def steps(items):
    return '<ol class="steps">' + "".join(f"<li>{s}</li>" for s in items) + "</ol>"

def note(text, kind="warn"):
    return f'<div class="note {kind}">{text}</div>'

def badge(status):
    m = {"live": ("Live", "b-live"), "draft": ("Built, not switched on", "b-draft"), "partial": ("Partly live", "b-part")}
    t, c = m.get(status, (status, "b-draft"))
    return f'<span class="badge {c}">{t}</span>'

def workflow_card(num, name, status, one_liner, trigger, step_list, means, flowchart, extra=""):
    return f'''
<section class="card" id="wf{num}">
  <div class="chead"><div class="num">{num}</div><div>
    <div class="lbl">Workflow name in GHL</div>
    <h3>{E(name)} {badge(status)}</h3>
    <p class="one">{one_liner}</p></div></div>
  <div class="two">
    <div>
      <div class="lbl">What starts it</div>
      <p>{trigger}</p>
      <div class="lbl" style="margin-top:14px">What it does, step by step</div>
      {steps(step_list)}
      <div class="lbl" style="margin-top:14px">What it means for the team</div>
      <p>{means}</p>
      {extra}
    </div>
    <div>{flowchart}</div>
  </div>
</section>'''

CSS = '''
  :root{--cream:#F7F4EE;--card:#FFFFFF;--ink:#1E1B16;--muted:#6B6459;--terra:#A9502C;--terra-soft:#F3E3DA;--green:#1D4A33;--green-soft:#E4EEE7;--gold:#B98A2F;--line:#E4DDD2;--warn-bg:#FBEFE7;--warn:#8C3D14;--stop-bg:#FBE9E7;--stop:#8C2D14}
  *{box-sizing:border-box;margin:0;padding:0}
  body{background:var(--cream);color:var(--ink);font-family:'Inter',system-ui,sans-serif;line-height:1.65;font-size:16px}
  .wrap{max-width:1060px;margin:0 auto;padding:0 20px 90px}
  header.hero{background:var(--ink);color:#F7F4EE;padding:48px 20px 40px;text-align:center}
  .hero .brand{font-family:'Playfair Display',serif;font-size:14px;letter-spacing:.18em;text-transform:uppercase;color:#CDB68A;margin-bottom:12px}
  .hero h1{font-family:'Playfair Display',serif;font-size:clamp(28px,5vw,42px);font-weight:600;line-height:1.15;margin-bottom:12px}
  .hero p{color:#BFB8AC;max-width:680px;margin:0 auto;font-size:15.5px}
  .hero .ver{margin-top:14px;font-size:12.5px;color:#CDB68A;letter-spacing:.08em;text-transform:uppercase}
  section{margin-top:44px}
  h2{font-family:'Playfair Display',serif;font-size:clamp(22px,3.4vw,30px);font-weight:600;margin-bottom:10px}
  .lead{color:var(--muted);font-size:15.5px;margin-bottom:6px;max-width:820px}
  .kicker{color:var(--terra);font-weight:700;font-size:12.5px;letter-spacing:.14em;text-transform:uppercase;margin-bottom:6px}
  code{font-family:ui-monospace,monospace;font-size:12.5px;background:#F4F1EA;border:1px solid var(--line);border-radius:5px;padding:1px 6px}
  .small{font-size:14px;color:var(--muted)}
  .lbl{font-size:11.5px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:var(--green);margin-bottom:7px}
  .toc{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:10px;margin-top:14px}
  .toc a{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:12px 14px;color:var(--ink);text-decoration:none;font-size:14px;display:flex;gap:10px;align-items:center}
  .toc a:hover{border-color:var(--terra)}
  .toc .n{flex:none;width:26px;height:26px;border-radius:50%;background:var(--green);color:#fff;font-weight:700;font-size:12.5px;display:flex;align-items:center;justify-content:center}
  .card{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:26px;margin-top:20px;scroll-margin-top:16px}
  .chead{display:flex;gap:14px;align-items:flex-start;padding-bottom:14px;border-bottom:1px solid var(--line);margin-bottom:18px}
  .num{flex:none;width:36px;height:36px;border-radius:50%;background:var(--green);color:#fff;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:15px}
  .card h3{font-family:'Playfair Display',serif;font-size:22px;font-weight:600;line-height:1.25;display:flex;flex-wrap:wrap;gap:10px;align-items:center}
  .one{color:var(--muted);font-size:15px;margin-top:4px}
  .badge{font-family:'Inter',sans-serif;font-size:11.5px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;border-radius:999px;padding:3px 10px}
  .b-live{background:var(--green-soft);color:var(--green)}
  .b-draft{background:#F1EDE4;color:#6B6459}
  .b-part{background:var(--terra-soft);color:var(--terra)}
  .two{display:grid;grid-template-columns:1fr 1fr;gap:26px;align-items:start}
  @media(max-width:860px){.two{grid-template-columns:1fr}}
  .card p{margin-bottom:8px;font-size:15px}
  .steps{padding-left:22px;display:flex;flex-direction:column;gap:7px;font-size:15px}
  .steps li::marker{color:var(--terra);font-weight:700}
  .diagram{background:#FBF9F5;border:1px solid var(--line);border-radius:14px;padding:12px 8px 6px}
  .diagram svg{width:100%;height:auto;display:block}
  .dtitle{font-size:11.5px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:var(--muted);padding:2px 8px 8px}
  .n-t{fill:var(--ink);stroke:none}.n-t-t{fill:#F7F4EE;font-family:'Inter',sans-serif;font-size:14.5px;font-weight:600}
  .n-a{fill:#fff;stroke:var(--green);stroke-width:1.6}.n-a-t{fill:var(--ink);font-family:'Inter',sans-serif;font-size:14.5px;font-weight:500}
  .n-w{fill:var(--green-soft);stroke:var(--green);stroke-width:1.2}.n-w-t{fill:var(--green);font-family:'Inter',sans-serif;font-size:14.5px;font-weight:600}
  .n-d{fill:var(--terra-soft);stroke:var(--terra);stroke-width:1.4}.n-d-t{fill:var(--terra);font-family:'Inter',sans-serif;font-size:14.5px;font-weight:700}
  .n-e{fill:#EDE9E1;stroke:none}.n-e-t{fill:var(--muted);font-family:'Inter',sans-serif;font-size:12.5px;font-weight:600}
  .lbl-yes{fill:var(--green-soft);stroke:var(--green);stroke-width:1}.lbl-yes-t{fill:var(--green);font-family:'Inter',sans-serif;font-size:11.5px;font-weight:700}
  .lbl-no{fill:#F1EDE4;stroke:#B5AEA3;stroke-width:1}.lbl-no-t{fill:var(--muted);font-family:'Inter',sans-serif;font-size:11.5px;font-weight:700}
  .note-t{fill:var(--muted);font-family:'Inter',sans-serif;font-size:12px;font-style:italic}
  .edge{fill:none;stroke:#6B6459;stroke-width:1.4}
  .tblwrap{overflow-x:auto;background:#FBF9F5;border:1px solid var(--line);border-radius:12px;margin:8px 0 14px}
  table{width:100%;border-collapse:collapse;font-size:14px}
  th{text-align:left;font-size:11.5px;letter-spacing:.08em;text-transform:uppercase;color:var(--green);padding:10px 14px;border-bottom:1px solid var(--line);line-height:1.35;vertical-align:bottom}
  td{padding:9px 14px;border-bottom:1px solid var(--line);vertical-align:top}
  tr:last-child td{border-bottom:none}
  .note{border-left:4px solid var(--terra);border-radius:0 12px 12px 0;padding:12px 16px;margin:12px 0 6px;font-size:14px}
  .note.warn{background:var(--warn-bg);color:var(--warn)}.note.warn b{color:var(--warn)}
  .note.stop{background:var(--stop-bg);color:var(--stop);border-color:var(--stop)}.note.stop b{color:var(--stop)}
  .note.ok{background:var(--green-soft);color:var(--green);border-color:var(--green)}.note.ok b{color:var(--green)}
  .note code{background:#fff}
  .tagbtn{display:inline-flex;align-items:center;gap:8px;background:#F4F1EA;border:1px solid var(--line);border-radius:8px;padding:5px 11px;font-family:ui-monospace,monospace;font-size:12.5px;color:var(--ink);cursor:pointer;transition:.15s;text-align:left;margin:2px 6px 2px 0}
  .tagbtn:hover{background:var(--terra-soft);border-color:var(--terra)}
  .tagbtn.copied{background:var(--green-soft);border-color:var(--green);color:var(--green)}
  .tagbtn .ic{opacity:.5;font-size:11px}
  .grid3{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:14px;margin-top:14px}
  .box{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:18px}
  .box .n{display:inline-flex;align-items:center;justify-content:center;width:28px;height:28px;border-radius:50%;background:var(--terra);color:#fff;font-weight:700;font-size:13px;margin-bottom:8px}
  .box b{display:block;margin-bottom:4px;font-size:15px}
  .box p{font-size:13.5px;color:var(--muted)}
  footer{margin-top:60px;padding-top:22px;border-top:1px solid var(--line);color:var(--muted);font-size:13px;display:flex;justify-content:space-between;flex-wrap:wrap;gap:8px}
  .toast{position:fixed;bottom:24px;left:50%;transform:translateX(-50%) translateY(80px);background:var(--ink);color:#F7F4EE;padding:11px 20px;border-radius:999px;font-size:14px;transition:.25s;pointer-events:none;opacity:0}
  .toast.show{transform:translateX(-50%) translateY(0);opacity:1}
  .top{position:fixed;right:20px;bottom:24px;background:var(--ink);color:#F7F4EE;border:none;border-radius:999px;padding:11px 18px;font-size:13px;cursor:pointer;opacity:0;transition:.2s;font-family:inherit}
  .top.show{opacity:.92}
'''

JS = '''
  const toast = document.getElementById('toast');
  document.querySelectorAll('.tagbtn').forEach(btn => {
    btn.addEventListener('click', async () => {
      const t = btn.dataset.tag;
      try { await navigator.clipboard.writeText(t); }
      catch (e) { const ta = document.createElement('textarea'); ta.value = t; document.body.appendChild(ta); ta.select(); try { document.execCommand('copy'); } catch (err) {} document.body.removeChild(ta); }
      btn.classList.add('copied'); const ic = btn.querySelector('.ic'); const old = ic.textContent; ic.textContent = 'copied ✓';
      toast.textContent = 'Copied: ' + t; toast.classList.add('show');
      setTimeout(() => { btn.classList.remove('copied'); ic.textContent = old; toast.classList.remove('show'); }, 1600);
    });
  });
  const topBtn = document.getElementById('top');
  topBtn.addEventListener('click', () => window.scrollTo({top:0, behavior:'smooth'}));
  window.addEventListener('scroll', () => topBtn.classList.toggle('show', window.scrollY > 700));
'''

def page(title, brand_line, h1, intro, version, body, footer_left):
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="robots" content="noindex">
<title>{E(title)}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@500;600&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>{CSS}</style>
</head>
<body>
<header class="hero">
  <div class="brand">{E(brand_line)}</div>
  <h1>{E(h1)}</h1>
  <p>{intro}</p>
  <div class="ver">{E(version)}</div>
</header>
<div class="wrap">
{body}
<footer><span>{E(footer_left)}</span><span>Maintained by John Carlo Caintic</span></footer>
</div>
<div class="toast" id="toast">Copied</div>
<button class="top" id="top">↑ Top</button>
<script>{JS}</script>
</body>
</html>'''
