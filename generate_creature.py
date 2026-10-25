import os, sys, json, math, random, hashlib, collections, urllib.request
from xml.sax.saxutils import escape

USER = (sys.argv[1] if len(sys.argv) > 1 else os.environ.get("GH_USER", "")).strip()
TOKEN = os.environ.get("GITHUB_TOKEN")
if not USER:
    sys.exit("Usage: python generate_creature.py <github-username>")

def api(path):
    req = urllib.request.Request("https://api.github.com" + path, headers={"User-Agent": "creature-bot", "Accept": "application/vnd.github+json"})
    if TOKEN:
        req.add_header("Authorization", "Bearer " + TOKEN)
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r)

try:
    user = api("/users/" + USER)
    repos = [r for r in api("/users/%s/repos?per_page=100&type=owner" % USER) if not r.get("fork")]
except Exception as e:
    print("GitHub API problem, drawing a hatchling:", e)
    user, repos = {"followers": 0}, []

langs = collections.Counter(r["language"] for r in repos if r.get("language"))
stars = sum(r.get("stargazers_count", 0) for r in repos)
n = len(repos)
top = langs.most_common(1)[0][0] if langs else "curiosity"

COLORS = {"Python": "#3572A5", "JavaScript": "#e6c619", "TypeScript": "#3178c6", "Java": "#b07219", "C++": "#f34b7d", "C": "#7a7a7a", "Go": "#00ADD8", "Rust": "#dea584", "HTML": "#e34c26", "CSS": "#8a63d2", "Jupyter Notebook": "#DA5B0B", "Shell": "#89e051"}
rng = random.Random(int(hashlib.md5(USER.lower().encode()).hexdigest(), 16))
base = COLORS.get(top) or "#%02x%02x%02x" % tuple(rng.randint(90, 230) for _ in range(3))
accent = "#c9a96e"
def mix(a, b, t):
    a = [int(a[i:i + 2], 16) for i in (1, 3, 5)]; b = [int(b[i:i + 2], 16) for i in (1, 3, 5)]
    return "#%02x%02x%02x" % tuple(int(x * (1 - t) + y * t) for x, y in zip(a, b))
base = mix(base, "#d9bf86", 0.4)
stage = "Hatchling" if n < 5 else "Explorer" if n < 15 else "Architect"

cx, cy = 190, 160
r = 62 + min(n, 30) * 1.3
pts = []
for i in range(12):
    a = i * math.pi / 6
    rr = r + rng.uniform(-9, 9)
    pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a) * 0.9))
mid = lambda p, q: ((p[0] + q[0]) / 2, (p[1] + q[1]) / 2)
m0 = mid(pts[-1], pts[0])
d = "M%.1f %.1f " % m0
for i, p in enumerate(pts):
    m = mid(p, pts[(i + 1) % 12])
    d += "Q%.1f %.1f %.1f %.1f " % (p[0], p[1], m[0], m[1])
d += "Z"

eyes = min(max(len(langs), 1), 5)
eye_svg = ""
for i in range(eyes):
    ex = cx + (i - (eyes - 1) / 2) * 26
    eye_svg += '<ellipse class="eye" cx="%.1f" cy="%.1f" rx="7" ry="9" fill="#fff"/><circle cx="%.1f" cy="%.1f" r="3.5" fill="#1a1030"/>' % (ex, cy - 10, ex + 1.5, cy - 8)

orbs = ""
k = min(stars, 12)
for i in range(k):
    a = i * 2 * math.pi / max(k, 1)
    orbs += '<circle cx="%.1f" cy="%.1f" r="6" fill="%s"/>' % (cx + (r + 38) * math.cos(a), cy + (r + 38) * 0.9 * math.sin(a), accent)

feet = '<ellipse cx="%d" cy="%.1f" rx="16" ry="9" fill="%s"/><ellipse cx="%d" cy="%.1f" rx="16" ry="9" fill="%s"/>' % (cx - 28, cy + r * 0.9 + 4, base, cx + 28, cy + r * 0.9 + 4, base)
ant = '<path d="M%d %.1f Q%d %.1f %d %.1f" stroke="%s" stroke-width="4" fill="none" stroke-linecap="round"/><circle cx="%d" cy="%.1f" r="7" fill="%s"/>' % (cx, cy - r * 0.9 + 4, cx + 14, cy - r * 0.9 - 30, cx + 6, cy - r * 0.9 - 44, base, cx + 6, cy - r * 0.9 - 46, accent)

food = ", ".join(l for l, _ in langs.most_common(2)) or "ideas"
lines = [("My code creature", "t"), ("@" + USER, "m"), ("Stage: %s" % stage, "s"), ("Repos eaten: %d" % n, "s"), ("Favorite food: %s" % food, "s"), ("Stars collected: %d" % stars, "s"), ("It grows when I ship code.", "m")]
txt = ""
for i, (t, c) in enumerate(lines):
    txt += '<text class="%s" x="400" y="%d">%s</text>' % (c, 92 + i * 30, escape(t))

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="760" height="320" viewBox="0 0 760 320" role="img" aria-label="A creature generated from {escape(USER)}'s GitHub activity">
<style>
text{{font-family:-apple-system,Segoe UI,Helvetica,Arial,sans-serif;fill:#a9c3b8}}
.t{{font-family:Georgia,'Times New Roman',serif;font-size:24px;font-style:italic;fill:#f3e3b8}}.s{{font-size:17px}}.m{{font-size:14px;fill:#c9a96e;letter-spacing:1px}}
.bob{{animation:bob 3s ease-in-out infinite}}
@keyframes bob{{50%{{transform:translateY(-8px)}}}}
.orbit{{transform-origin:{cx}px {cy}px;animation:spin 18s linear infinite}}
@keyframes spin{{to{{transform:rotate(360deg)}}}}
.eye{{transform-box:fill-box;transform-origin:center;animation:blink 4.5s infinite}}
@keyframes blink{{0%,94%,100%{{transform:scaleY(1)}}97%{{transform:scaleY(.1)}}}}
</style>
<rect width="760" height="320" rx="16" fill="#0a1c17"/>
<g class="orbit">{orbs}</g>
<g class="bob">{feet}{ant}<path d="{d}" fill="{base}"/>{eye_svg}<path d="M{cx-16} {cy+22} Q{cx} {cy+38} {cx+16} {cy+22}" fill="none" stroke="#1a1030" stroke-width="4" stroke-linecap="round"/></g>
{txt}
</svg>'''
open("creature.svg", "w", encoding="utf-8").write(svg)
print("creature.svg written:", stage, n, "repos,", stars, "stars, top:", top)
