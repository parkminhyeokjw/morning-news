import urllib.request, urllib.parse, xml.etree.ElementTree as ET, html, os, datetime, json, re

FEEDS = [
    ("CNBC 톱뉴스", "https://www.cnbc.com/id/100003114/device/rss/rss.html"),
    ("CNBC 경제", "https://www.cnbc.com/id/20910258/device/rss/rss.html"),
    ("WSJ 마켓", "https://feeds.content.dowjones.io/public/rss/RSSMarketsMain"),
    ("WSJ 세계", "https://feeds.content.dowjones.io/public/rss/RSSWorldNews"),
    ("연합뉴스 경제", "https://www.yna.co.kr/rss/economy.xml"),
    ("한국경제", "https://www.hankyung.com/feed/economy"),
    ("연합뉴스 주요", "https://www.yna.co.kr/rss/news.xml"),
]
N = 6

def clean(x):
    x = re.sub(r"<[^>]+>", " ", html.unescape(x or ""))
    return re.sub(r"\s+", " ", x).strip()

def tr(text):
    if not text or re.search(r"[가-힣]", text):
        return text
    try:
        u = "https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl=ko&dt=t&q=" + urllib.parse.quote(text)
        req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=20) as r:
            return "".join(p[0] for p in json.loads(r.read())[0] if p[0])
    except Exception as e:
        print("TR FAIL", e)
        return text

def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=20) as r:
        root = ET.fromstring(r.read())
    out = []
    for it in root.iter("item"):
        t = (it.findtext("title") or "").strip()
        l = (it.findtext("link") or "").strip()
        d = clean(it.findtext("description"))
        if len(d) > 280:
            d = d[:280].rsplit(" ", 1)[0] + "…"
        if d == t or d.startswith(t):
            d = ""
        if t and l:
            out.append((tr(t), l, tr(d)))
        if len(out) >= N:
            break
    return out

sections = []
for name, url in FEEDS:
    try:
        items = fetch(url)
    except Exception as e:
        print("FAIL", name, e)
        items = []
    if items:
        sections.append((name, items))

kst = datetime.datetime.utcnow() + datetime.timedelta(hours=9)
date = kst.strftime("%Y-%m-%d (%a) %H:%M KST")

body = ""
for name, items in sections:
    body += f"<section><h2>{html.escape(name)}</h2><ul>"
    for t, l, d in items:
        body += f'<li><a href="{html.escape(l)}" target="_blank" rel="noopener">{html.escape(t)}</a>' + (f'<p>{html.escape(d)}</p>' if d else '') + '</li>'
    body += "</ul></section>"

page = f"""<!doctype html><html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>아침 뉴스</title><link rel="manifest" href="manifest.json">
<meta name="theme-color" content="#0f172a">
<style>
:root{{--bg:#f8fafc;--fg:#0f172a;--card:#fff;--mut:#64748b;--ac:#2563eb}}
@media(prefers-color-scheme:dark){{:root{{--bg:#0f172a;--fg:#e2e8f0;--card:#1e293b;--mut:#94a3b8;--ac:#60a5fa}}}}
body{{margin:0;background:var(--bg);color:var(--fg);font:16px/1.5 system-ui,'Malgun Gothic',sans-serif}}
main{{max-width:720px;margin:0 auto;padding:16px}}
h1{{font-size:22px;margin:8px 0 2px}} .d{{color:var(--mut);font-size:13px;margin-bottom:12px}}
section{{background:var(--card);border-radius:12px;padding:12px 16px;margin:12px 0}}
h2{{font-size:15px;margin:0 0 6px;color:var(--ac)}}
ul{{margin:0;padding-left:18px}} li{{margin:10px 0}} li p{{margin:2px 0 0;color:var(--mut);font-size:14px}}
a{{color:var(--fg);text-decoration:none}} a:visited{{color:var(--mut)}}
</style></head><body><main>
<h1>☀️ 아침 경제·주요뉴스</h1><div class="d">{date} 업데이트</div>{body}
</main></body></html>"""

os.makedirs("docs", exist_ok=True)
open("docs/index.html", "w", encoding="utf-8").write(page)
open("docs/manifest.json", "w", encoding="utf-8").write(json.dumps({
    "name": "아침 뉴스", "short_name": "아침뉴스", "start_url": ".", "display": "standalone",
    "background_color": "#0f172a", "theme_color": "#0f172a",
    "icons": [{"src": "icon.svg", "sizes": "any", "type": "image/svg+xml"}]}))
open("docs/icon.svg", "w", encoding="utf-8").write('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><rect width="100" height="100" rx="20" fill="#0f172a"/><text x="50" y="68" font-size="56" text-anchor="middle">☀️</text></svg>')

# push message: top headline of first 3 sections
lines = [f"• {items[0][0]}" for _, items in sections[:4]]
open("push.txt", "w", encoding="utf-8").write("\n".join(lines))
print("OK", len(sections), "sections")
