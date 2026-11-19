#!/usr/bin/env python3
"""Static site generator for the personal site.

Reads content/*.json, writes a complete static site to dist/.
Standard library only:   py build.py     (or: python build.py)
Preview locally:         py -m http.server 8000 -d dist
"""
import html
import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CONTENT = ROOT / "content"
ASSETS = ROOT / "assets"
DIST = ROOT / "dist"


def load(name):
    return json.loads((CONTENT / (name + ".json")).read_text(encoding="utf-8"))


def e(value):
    return html.escape(str(value), quote=True)


PROFILE = load("profile")
PUBS = load("publications")["items"]
PROJECTS = load("projects")["items"]
EXPERIENCE = load("experience")["items"]
EDUCATION = load("education")
RESEARCH = load("research")

PUB_BY_ID = {p["id"]: p for p in PUBS}
PROJECT_BY_SLUG = {p["slug"]: p for p in PROJECTS}

NAV = [
    ("index.html", "Home"),
    ("about.html", "About"),
    ("research.html", "Research"),
    ("publications.html", "Publications"),
    ("projects.html", "Projects"),
    ("experience.html", "Experience"),
    ("education.html", "Education"),
]

TYPE_LABELS = {
    "journal": "Journal paper",
    "conference": "Conference paper",
    "workshop": "Workshop paper",
    "preprint": "Preprint",
    "chapter": "Book chapter",
}
STATUS_LABELS = {
    "under-review": "Under review",
    "accepted": "Accepted",
    "published": "Published",
}
CATEGORY_LABELS = {
    "research": "Academic research",
    "industry": "Industry",
    "independent": "Independent",
}

# --------------------------------------------------------------------------
# Icons (inline SVG, decorative)
# --------------------------------------------------------------------------
def icon(path, size=16):
    return (
        '<svg class="icon" width="%d" height="%d" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">%s</svg>'
        % (size, size, path)
    )


I_ARROW = icon('<path d="M5 12h14M13 6l6 6-6 6"/>')
I_EXT = icon('<path d="M7 17 17 7M8 7h9v9"/>', 14)
I_DOWN = icon('<path d="M12 4v12M6 11l6 6 6-6M5 20h14"/>')
I_MAIL = icon('<rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/>')
I_SUN = icon('<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/>', 18)
I_MOON = icon('<path d="M20 14.5A8.5 8.5 0 0 1 9.5 4a7 7 0 1 0 10.5 10.5z"/>', 18)
I_MENU = icon('<path d="M4 7h16M4 12h16M4 17h16"/>', 20)
I_CLOSE = icon('<path d="M6 6l12 12M18 6 6 18"/>', 20)
I_COPY = icon('<rect x="9" y="9" width="11" height="11" rx="2"/><path d="M5 15V6a2 2 0 0 1 2-2h9"/>', 14)


# --------------------------------------------------------------------------
# Profile links (only shown when a real URL / file exists)
# --------------------------------------------------------------------------
def cv_files():
    """Return {kind: published filename} for CV files that exist on disk."""
    out = {}
    for kind, spec in (PROFILE.get("cv") or {}).items():
        if spec and spec.get("source") and (ROOT / spec["source"]).is_file():
            out[kind] = spec.get("publish_as") or Path(spec["source"]).name
    return out


CVS = cv_files()


def profile_links(root):
    """List of (label, href, external?, icon) for every link that is valid."""
    links = []
    if "academic" in CVS:
        links.append(("Academic CV", root + "cv/" + CVS["academic"], False, I_DOWN))
    if "professional" in CVS:
        links.append(("Professional CV", root + "cv/" + CVS["professional"], False, I_DOWN))
    labels = [("scholar", "Google Scholar"), ("github", "GitHub"), ("linkedin", "LinkedIn"), ("orcid", "ORCID")]
    for key, label in labels:
        url = (PROFILE.get("links") or {}).get(key)
        if url and url.startswith("http"):
            links.append((label, url, True, I_EXT))
    if PROFILE.get("email"):
        links.append(("Email", "mailto:" + PROFILE["email"], False, I_MAIL))
    return links


def link_row(root, cls="link-row"):
    items = []
    for label, href, external, ico in profile_links(root):
        attrs = ' target="_blank" rel="noopener me"' if external else ""
        items.append('<li><a href="%s"%s>%s<span>%s</span></a></li>' % (e(href), attrs, ico, e(label)))
    return '<ul class="%s">%s</ul>' % (cls, "".join(items))


# --------------------------------------------------------------------------
# Small building blocks
# --------------------------------------------------------------------------
def chips(items, cls="chips"):
    if not items:
        return ""
    return '<ul class="%s">%s</ul>' % (cls, "".join("<li>%s</li>" % e(i) for i in items))


def bullets(items, cls="bullets"):
    if not items:
        return ""
    return '<ul class="%s">%s</ul>' % (cls, "".join("<li>%s</li>" % e(i) for i in items))


def paras(items):
    return "".join("<p>%s</p>" % e(p) for p in items)


def sec_head(num, title, link=None, hid=None):
    more = ""
    if link:
        more = '<a class="sec-more" href="%s">%s %s</a>' % (e(link[0]), e(link[1]), I_ARROW)
    id_attr = ' id="%s"' % hid if hid else ""
    return (
        '<header class="sec-head"><span class="sec-num" aria-hidden="true">%s</span>'
        "<h2%s>%s</h2>%s</header>" % (e(num), id_attr, e(title), more)
    )


def page_head(eyebrow, title, lede=None):
    lede_html = '<p class="lede">%s</p>' % e(lede) if lede else ""
    return (
        '<header class="page-head rise"><p class="eyebrow">%s</p><h1>%s</h1>%s</header>'
        % (e(eyebrow), e(title), lede_html)
    )


# --------------------------------------------------------------------------
# Publications
# --------------------------------------------------------------------------
def venue_line(pub):
    """Human-readable venue line that never overstates the status."""
    status = pub["status"]
    if status == "under-review":
        if PROFILE.get("show_venue_for_under_review", True):
            return "Submitted to %s" % pub["venue"]
        return "Under review"
    parts = [pub["venue"]]
    if pub.get("location"):
        parts.append(pub["location"])
    if pub.get("publisher"):
        parts.append(pub["publisher"])
    return " · ".join(parts)


def bib_author(name):
    parts = name.split()
    return "%s, %s" % (parts[-1], " ".join(parts[:-1])) if len(parts) > 1 else name


def bibtex(pub):
    surname = re.sub(r"[^a-z]", "", pub["authors"][0].split()[-1].lower())
    words = [re.sub(r"[^a-z0-9]", "", w.lower()) for w in pub["title"].split()]
    first = next((w for w in words if len(w) > 3), words[0])
    key = "%s%s%s" % (surname, pub["year"], first)
    fields = [
        ("title", "{%s}" % pub["title"]),
        ("author", " and ".join(bib_author(a) for a in pub["authors"])),
    ]
    status = pub["status"]
    if status == "under-review" or pub["type"] == "preprint":
        kind = "unpublished"
        fields.append(("note", venue_line(pub)))
        fields.append(("year", str(pub["year"])))
    else:
        kind = {"journal": "article", "chapter": "incollection"}.get(pub["type"], "inproceedings")
        fields.append(("journal" if kind == "article" else "booktitle", pub["venue"]))
        fields.append(("year", str(pub["year"])))
        if pub.get("location"):
            fields.append(("address", pub["location"]))
        if pub.get("publisher"):
            fields.append(("publisher", pub["publisher"]))
        if pub.get("doi"):
            fields.append(("doi", pub["doi"]))
        if status == "accepted":
            fields.append(("note", "Accepted"))
    body = ",\n".join("  %-9s = {%s}" % (k, v) for k, v in fields)
    return "@%s{%s,\n%s\n}" % (kind, key, body)


def authors_html(pub):
    me = PROFILE["author_name"]
    out = []
    for a in pub["authors"]:
        out.append('<strong class="me">%s</strong>' % e(a) if a == me else e(a))
    return ", ".join(out)


def pub_item(pub, root, tag="li"):
    links = []
    if pub.get("doi"):
        links.append(("DOI", "https://doi.org/" + pub["doi"]))
    for key, label in [("url", "Publisher page"), ("pdf", "PDF"), ("arxiv", "arXiv"), ("code", "Code"), ("project_page", "Project page")]:
        if pub.get(key):
            links.append((label, pub[key]))
    link_html = "".join(
        '<a class="pill" href="%s" target="_blank" rel="noopener">%s %s</a>' % (e(h), e(l), I_EXT) for l, h in links
    )
    if pub.get("project") in PROJECT_BY_SLUG:
        link_html += '<a class="pill" href="%sprojects/%s.html">Project details %s</a>' % (root, e(pub["project"]), I_ARROW)
    bib = bibtex(pub)
    bib_html = (
        '<details class="bib"><summary class="pill">BibTeX</summary>'
        '<div class="bib-box"><pre><code>%s</code></pre>'
        '<button type="button" class="copy" data-copy="%s">%s<span>Copy</span></button></div></details>'
        % (e(bib), e(bib), I_COPY)
    )
    return (
        '<%(tag)s class="pub" id="%(id)s" data-year="%(year)s" data-type="%(type)s" data-status="%(status)s">'
        '<div class="pub-meta"><span class="badge badge-%(status)s">%(status_label)s</span>'
        '<span class="mono">%(type_label)s · %(year)s</span></div>'
        '<h3 class="pub-title">%(title)s</h3>'
        '<p class="pub-authors">%(authors)s</p>'
        '<p class="pub-venue">%(venue)s</p>'
        '<div class="pub-links">%(links)s%(bib)s</div>'
        "</%(tag)s>"
    ) % {
        "tag": tag,
        "id": e(pub["id"]),
        "year": e(pub["year"]),
        "type": e(pub["type"]),
        "status": e(pub["status"]),
        "status_label": e(STATUS_LABELS[pub["status"]]),
        "type_label": e(TYPE_LABELS[pub["type"]]),
        "title": e(pub["title"]),
        "authors": authors_html(pub),
        "venue": e(venue_line(pub)),
        "links": link_html,
        "bib": bib_html,
    }


# --------------------------------------------------------------------------
# Projects
# --------------------------------------------------------------------------
def project_card(p, root, show_results=1):
    results = ""
    if show_results and p.get("results"):
        results = '<p class="card-result">%s</p>' % e(p["results"][0])
    return (
        '<article class="card project-card" data-category="%(cat)s">'
        '<p class="card-kicker"><span>%(area)s</span></p>'
        '<h3><a class="stretched" href="%(root)sprojects/%(slug)s.html">%(title)s</a></h3>'
        '<p class="card-text">%(summary)s</p>%(results)s'
        "%(chips)s"
        '<p class="card-foot"><span class="status">%(status)s</span><span class="go" aria-hidden="true">%(arrow)s</span></p>'
        "</article>"
    ) % {
        "cat": e(p["category"]),
        "area": e(p["area"]),
        "root": root,
        "slug": e(p["slug"]),
        "title": e(p["title"]),
        "summary": e(p["summary"]),
        "results": results,
        "chips": chips(p.get("methods", [])[:5]),
        "status": e(p["status"]),
        "arrow": I_ARROW,
    }


# --------------------------------------------------------------------------
# Layout
# --------------------------------------------------------------------------
THEME_SCRIPT = (
    "(function(){try{var t=localStorage.getItem('theme');"
    "if(t==='light'||t==='dark'){document.documentElement.setAttribute('data-theme',t);}}catch(e){}})();"
)


def layout(path, title, description, body, active=None, extra_head=""):
    depth = path.count("/")
    root = "../" * depth
    active = active or path
    full_title = title if path == "index.html" else "%s · %s" % (title, PROFILE["name"])
    nav_items = []
    for href, label in NAV:
        cur = ' aria-current="page"' if href == active else ""
        nav_items.append('<li><a href="%s%s"%s>%s</a></li>' % (root, href, cur, e(label)))
    canonical = ""
    if PROFILE.get("site_url"):
        url = PROFILE["site_url"].rstrip("/") + "/" + ("" if path == "index.html" else path)
        canonical = '<link rel="canonical" href="%s"><meta property="og:url" content="%s">' % (e(url), e(url))
    year_note = "Built from content/*.json with build.py."
    return """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>%(title)s</title>
<meta name="description" content="%(desc)s">
<meta name="author" content="%(name)s">
<meta property="og:type" content="website">
<meta property="og:title" content="%(title)s">
<meta property="og:description" content="%(desc)s">
<meta name="twitter:card" content="summary">
%(canonical)s
<meta name="theme-color" content="#f9f7f2" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#0e1312" media="(prefers-color-scheme: dark)">
<link rel="icon" href="%(root)sassets/favicon.svg" type="image/svg+xml">
<script>%(theme)s</script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@400;500;600&family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;1,6..72,400&display=swap" rel="stylesheet">
<link rel="stylesheet" href="%(root)sassets/styles.css">
%(extra_head)s
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="site-header">
  <div class="wrap header-inner">
    <a class="brand" href="%(root)sindex.html"><span class="brand-mark" aria-hidden="true">%(initials)s</span><span>%(name)s</span></a>
    <nav id="site-nav" class="site-nav" aria-label="Primary"><ul>%(nav)s</ul></nav>
    <div class="header-tools">
      <button type="button" class="icon-btn" id="theme-toggle" aria-label="Switch colour theme">
        <span class="when-light">%(moon)s</span><span class="when-dark">%(sun)s</span>
      </button>
      <button type="button" class="icon-btn nav-toggle" id="nav-toggle" aria-label="Menu" aria-expanded="false" aria-controls="site-nav">
        <span class="when-closed">%(menu)s</span><span class="when-open">%(close)s</span>
      </button>
    </div>
  </div>
</header>
<main id="main">
%(body)s
</main>
<footer class="site-footer">
  <div class="wrap footer-inner">
    <div>
      <p class="footer-name">%(name)s</p>
      <p class="footer-sub">%(role)s · %(inst)s</p>
    </div>
    %(links)s
  </div>
  <div class="wrap footer-base"><p>© %(name)s. %(year_note)s</p></div>
</footer>
<script src="%(root)sassets/site.js" defer></script>
</body>
</html>
""" % {
        "title": e(full_title),
        "desc": e(description),
        "name": e(PROFILE["name"]),
        "initials": e(PROFILE["initials"]),
        "canonical": canonical,
        "root": root,
        "theme": THEME_SCRIPT,
        "extra_head": extra_head,
        "nav": "".join(nav_items),
        "moon": I_MOON,
        "sun": I_SUN,
        "menu": I_MENU,
        "close": I_CLOSE,
        "body": body,
        "role": e(PROFILE["title"]),
        "inst": e(PROFILE["affiliation"]["institution"]),
        "links": link_row(root, "footer-links"),
        "year_note": e(year_note),
    }


def contact_cta(root):
    email = PROFILE["email"]
    return """
<section class="wrap section">
  <div class="cta">
    <div>
      <p class="eyebrow">Contact and collaboration</p>
      <h2>Working on vision systems, world models, or evaluation that has to survive deployment?</h2>
      <p>I am glad to hear from researchers, collaborators, and teams with related problems.</p>
    </div>
    <div class="cta-actions">
      <a class="btn btn-primary" href="mailto:%(email)s">%(mail)s<span>%(email)s</span></a>
      %(links)s
    </div>
  </div>
</section>""" % {"email": e(email), "mail": I_MAIL, "links": link_row(root, "link-row link-row-small")}


# --------------------------------------------------------------------------
# Pages
# --------------------------------------------------------------------------
def portrait(root):
    if PROFILE.get("photo"):
        alt = "Placeholder portrait" if "placeholder" in PROFILE["photo"] else "Portrait of " + PROFILE["name"]
        return '<img class="portrait-img" src="%s%s" alt="%s" width="400" height="500">' % (root, e(PROFILE["photo"]), e(alt))
    return (
        '<div class="portrait-ph" role="img" aria-label="Portrait placeholder">'
        '<span class="portrait-initials" aria-hidden="true">%s</span>'
        '<span class="portrait-note">Photo placeholder</span></div>' % e(PROFILE["initials"])
    )


def page_home():
    root = ""
    aff = PROFILE["affiliation"]
    metrics = "".join(
        '<div class="metric"><dt>%s</dt><dd><span class="metric-value">%s</span><span class="metric-detail">%s</span></dd></div>'
        % (e(m["label"]), e(m["value"]), e(m["detail"]))
        for m in PROFILE["metrics"]
    )
    interests = "".join(
        '<li><span class="idx" aria-hidden="true">%02d</span><div><h3>%s</h3><p>%s</p></div></li>'
        % (i + 1, e(it["title"]), e(it["text"]))
        for i, it in enumerate(PROFILE["interests"])
    )
    featured = "".join(project_card(p, root) for p in PROJECTS if p.get("featured"))
    selected = "".join(pub_item(p, root) for p in PUBS if p.get("selected"))
    highlights = "".join(
        "<li><h3>%s</h3><p>%s</p></li>" % (e(h["title"]), e(h["text"])) for h in PROFILE["professional_highlights"]
    )
    person = {
        "@context": "https://schema.org",
        "@type": "Person",
        "name": PROFILE["name"],
        "jobTitle": PROFILE["title"],
        "affiliation": {"@type": "CollegeOrUniversity", "name": aff["institution"]},
        "sameAs": [u for u in (PROFILE.get("links") or {}).values() if u],
    }
    body = """
<section class="wrap hero">
  <div class="hero-text rise">
    <p class="eyebrow"><span class="dot" aria-hidden="true"></span>%(title)s · %(inst)s</p>
    <h1>%(name)s</h1>
    <p class="hero-lede">%(positioning)s</p>
    <p class="hero-intro">%(intro)s</p>
    <div class="hero-actions">
      <a class="btn btn-primary" href="research.html"><span>Explore research</span>%(arrow)s</a>
      <a class="btn" href="publications.html"><span>Publications</span></a>
      <a class="btn" href="experience.html"><span>Experience</span></a>
    </div>
    %(links)s
  </div>
  <figure class="portrait rise rise-2">
    %(portrait)s
    <figcaption><span>%(inst)s</span><span>%(loc)s</span></figcaption>
  </figure>
</section>

<section class="wrap" aria-label="Selected results">
  <dl class="metrics">%(metrics)s</dl>
</section>

<section class="wrap section" aria-labelledby="h-interests">
  %(h1)s
  <ol class="interest-grid">%(interests)s</ol>
</section>

<section class="wrap section" aria-labelledby="h-featured">
  %(h2)s
  <div class="card-grid card-grid-3">%(featured)s</div>
</section>

<section class="wrap section" aria-labelledby="h-pubs">
  %(h3)s
  <ul class="pub-list">%(selected)s</ul>
</section>

<section class="wrap section" aria-labelledby="h-pro">
  %(h4)s
  <ul class="highlight-grid">%(highlights)s</ul>
</section>
%(cta)s
""" % {
        "title": e(PROFILE["title"]),
        "inst": e(aff["institution"]),
        "loc": e(aff["location"]),
        "name": e(PROFILE["name"]),
        "positioning": e(PROFILE["positioning"]),
        "intro": e(PROFILE["intro"]),
        "arrow": I_ARROW,
        "links": link_row(root),
        "portrait": portrait(root),
        "metrics": metrics,
        "h1": sec_head("01", "Research interests", ("research.html", "Research overview"), "h-interests"),
        "interests": interests,
        "h2": sec_head("02", "Featured research", ("projects.html", "All projects"), "h-featured"),
        "featured": featured,
        "h3": sec_head("03", "Selected publications", ("publications.html", "All %d publications" % len(PUBS)), "h-pubs"),
        "selected": selected,
        "h4": sec_head("04", "From eight years in industry", ("experience.html", "Full experience"), "h-pro"),
        "highlights": highlights,
        "cta": contact_cta(root),
    }
    head = '<script type="application/ld+json">%s</script>' % json.dumps(person).replace("</", "<\\/")
    desc = "%s is a doctoral researcher in AI and computer vision at %s, with eight years of production software engineering experience." % (
        PROFILE["name"], aff["institution"])
    return layout("index.html", "%s · %s" % (PROFILE["name"], PROFILE["title"]), desc, body, extra_head=head)


def page_about():
    root = ""
    skills = "".join(
        '<div class="skill-group"><h3>%s</h3>%s</div>' % (e(g["group"]), chips(g["items"])) for g in PROFILE["skills"]
    )
    trajectory = [(x["period"], x["title"], x["text"]) for x in PROFILE["trajectory"]]
    traj = "".join(
        '<li><span class="mono">%s</span><div><h3>%s</h3><p>%s</p></div></li>' % (e(a), e(b), e(c)) for a, b, c in trajectory
    )
    recog = "".join(
        "<li><h3>%s</h3><p>%s, %s</p></li>" % (e(a["title"]), e(a["org"]), e(a["year"])) for a in PROFILE["awards"]
    ) + "".join("<li><h3>%s</h3><p>%s</p></li>" % (e(s["title"]), e(s["detail"])) for s in PROFILE["service"])
    body = """
<div class="wrap">
  %(head)s
  <div class="about-grid">
    <div class="prose">
      %(bio)s
    </div>
    <aside class="aside">
      <div class="aside-block">
        <h2 class="aside-title">Short bio</h2>
        <p class="short-bio" id="short-bio">%(short)s</p>
        <button type="button" class="copy" data-copy="%(short)s">%(copy)s<span>Copy short bio</span></button>
      </div>
      <div class="aside-block">
        <h2 class="aside-title">Find me</h2>
        %(links)s
      </div>
    </aside>
  </div>
</div>

<section class="wrap section" aria-labelledby="h-traj">
  %(h1)s
  <ol class="trajectory">%(traj)s</ol>
</section>

<section class="wrap section" aria-labelledby="h-skills">
  %(h2)s
  <div class="skill-grid">%(skills)s</div>
</section>

<section class="wrap section" aria-labelledby="h-recog">
  %(h3)s
  <ul class="highlight-grid">%(recog)s</ul>
  <h3 class="sub-title">Volunteering</h3>
  %(vol)s
</section>
%(cta)s
""" % {
        "head": page_head("About", "From shipping enterprise software to researching vision systems that act", PROFILE["intro"]),
        "bio": paras(PROFILE["bio_long"]),
        "short": e(PROFILE["bio_short"]),
        "copy": I_COPY,
        "links": link_row(root, "link-row link-row-stack"),
        "h1": sec_head("01", "Career trajectory", ("experience.html", "Detailed experience"), "h-traj"),
        "traj": traj,
        "h2": sec_head("02", "Technical expertise", None, "h-skills"),
        "skills": skills,
        "h3": sec_head("03", "Recognition and service", None, "h-recog"),
        "recog": recog,
        "vol": bullets(PROFILE["volunteering"]),
        "cta": contact_cta(root),
    }
    return layout("about.html", "About", PROFILE["bio_short"][:155].rsplit(" ", 1)[0] + "…", body)


def research_card(p, root):
    pub = PUB_BY_ID.get(p.get("publication") or "")
    links = []
    if p["links"].get("paper"):
        links.append('<a class="pill" href="%s" target="_blank" rel="noopener">Paper %s</a>' % (e(p["links"]["paper"]), I_EXT))
    if p["links"].get("code"):
        links.append('<a class="pill" href="%s" target="_blank" rel="noopener">Code %s</a>' % (e(p["links"]["code"]), I_EXT))
    if p["links"].get("demo"):
        links.append('<a class="pill" href="%s" target="_blank" rel="noopener">Demo video %s</a>' % (e(p["links"]["demo"]), I_EXT))
    links.append('<a class="pill" href="%sprojects/%s.html">Full project page %s</a>' % (root, e(p["slug"]), I_ARROW))
    image = ""
    if p.get("image"):
        image = '<img class="rc-image" src="%s%s" alt="%s" loading="lazy">' % (root, e(p["image"]), e(p["title"]))
    venue = ""
    if pub:
        venue = '<p class="rc-venue"><span class="badge badge-%s">%s</span><span>%s</span></p>' % (
            e(pub["status"]), e(STATUS_LABELS[pub["status"]]), e(venue_line(pub)))
    return """
<article class="research-card" id="%(slug)s">
  <div class="rc-main">
    <p class="card-kicker"><span>%(area)s</span></p>
    <h3>%(title)s</h3>
    %(venue)s
    %(image)s
    <p>%(summary)s</p>
    <h4>My contribution</h4>
    <p class="rc-role">%(role)s</p>
    %(contribution)s
    <div class="pub-links">%(links)s</div>
  </div>
  <div class="rc-side">
    <h4>Key results</h4>
    %(results)s
    <h4>Methods and technologies</h4>
    %(methods)s
    <p class="rc-status"><span class="mono">Status</span> %(status)s</p>
  </div>
</article>""" % {
        "slug": e(p["slug"]),
        "area": e(p["area"]),
        "title": e(p["title"]),
        "venue": venue,
        "image": image,
        "summary": e(p["summary"]),
        "role": e(p["role"]),
        "contribution": bullets(p["contribution"]),
        "links": "".join(links),
        "results": bullets(p["results"], "bullets results"),
        "methods": chips(p["methods"]),
        "status": e(p["status"]),
    }


def page_research():
    root = ""
    areas = "".join(
        '<li><span class="idx" aria-hidden="true">%02d</span><div><h3>%s</h3><p>%s</p></div></li>'
        % (i + 1, e(a["title"]), e(a["text"]))
        for i, a in enumerate(RESEARCH["areas"])
    )
    method = "".join(
        '<li><span class="step" aria-hidden="true">%d</span><h3>%s</h3><p>%s</p></li>' % (i + 1, e(m["title"]), e(m["text"]))
        for i, m in enumerate(RESEARCH["methodology"])
    )
    cards = "".join(research_card(p, root) for p in PROJECTS if p["category"] == "research")
    research_skills = [g for g in PROFILE["skills"] if g["group"] in (
        "Production computer vision", "Model evaluation and error analysis", "Datasets and annotation quality",
        "Python and ML frameworks", "Experiment design and validation")]
    skills = "".join('<div class="skill-group"><h3>%s</h3>%s</div>' % (e(g["group"]), chips(g["items"])) for g in research_skills)
    body = """
<div class="wrap">%(head)s</div>

<section class="wrap section section-tight" aria-labelledby="h-areas">
  %(h1)s
  <ol class="interest-grid">%(areas)s</ol>
</section>

<section class="wrap section" aria-labelledby="h-dir">
  %(h2)s
  <div class="two-col">
    <div>%(directions)s</div>
    <div class="note-box"><h3>Selected achievements</h3>%(achievements)s</div>
  </div>
</section>

<section class="wrap section" aria-labelledby="h-proj">
  %(h3)s
  <div class="research-list">%(cards)s</div>
</section>

<section class="wrap section" aria-labelledby="h-method">
  %(h4)s
  <ol class="method-grid">%(method)s</ol>
</section>

<section class="wrap section" aria-labelledby="h-rskills">
  %(h5)s
  <div class="skill-grid">%(skills)s</div>
</section>
%(cta)s
""" % {
        "head": page_head("Research", "Learned perception for systems that act", RESEARCH["lede"]),
        "h1": sec_head("01", "Research areas", None, "h-areas"),
        "areas": areas,
        "h2": sec_head("02", "Current directions", None, "h-dir"),
        "directions": bullets(RESEARCH["directions"], "bullets bullets-lg"),
        "achievements": bullets(RESEARCH["achievements"]),
        "h3": sec_head("03", "Research projects", ("publications.html", "Publications"), "h-proj"),
        "cards": cards,
        "h4": sec_head("04", "How I work", None, "h-method"),
        "method": method,
        "h5": sec_head("05", "Relevant technical expertise", None, "h-rskills"),
        "skills": skills,
        "cta": contact_cta(root),
    }
    return layout("research.html", "Research", RESEARCH["lede"][:155].rsplit(" ", 1)[0] + "…", body)


def filter_group(name, label, options):
    """options: list of (value, label, count). Rendered only when there is a real choice."""
    btns = ['<button type="button" class="chip-btn" data-value="" aria-pressed="true">All</button>']
    for value, text, count in options:
        btns.append(
            '<button type="button" class="chip-btn" data-value="%s" aria-pressed="false">%s <span class="count">%d</span></button>'
            % (e(value), e(text), count)
        )
    return '<div class="filter-group" role="group" aria-label="Filter by %s" data-filter="%s"><span class="filter-label">%s</span>%s</div>' % (
        e(label.lower()), e(name), e(label), "".join(btns))


def page_publications():
    root = ""
    years = sorted({p["year"] for p in PUBS}, reverse=True)
    groups = ""
    for y in years:
        items = "".join(pub_item(p, root) for p in PUBS if p["year"] == y)
        groups += '<section class="pub-year" data-year-group="%d"><h2 class="year-head">%d</h2><ul class="pub-list">%s</ul></section>' % (y, y, items)
    count = lambda key, val: sum(1 for p in PUBS if p[key] == val)
    filters = filter_group("year", "Year", [(y, y, count("year", y)) for y in years])
    types = [t for t in TYPE_LABELS if count("type", t)]
    filters += filter_group("type", "Category", [(t, TYPE_LABELS[t] + "s", count("type", t)) for t in types])
    statuses = [s for s in STATUS_LABELS if count("status", s)]
    filters += filter_group("status", "Status", [(s, STATUS_LABELS[s], count("status", s)) for s in statuses])
    first = sum(1 for p in PUBS if p["authors"][0] == PROFILE["author_name"])
    lede = "%d papers, %d as first author. Each entry shows its exact status: under review, accepted, or published." % (len(PUBS), first)
    scholar = (PROFILE.get("links") or {}).get("scholar")
    scholar_html = ""
    if scholar:
        scholar_html = '<p class="pub-note">Citation data lives on <a href="%s" target="_blank" rel="noopener">Google Scholar</a>. Papers under review are not yet publicly available; please email for a copy.</p>' % e(scholar)
    body = """
<div class="wrap">
  %(head)s
  %(scholar)s
  <div class="filters" id="pub-filters">%(filters)s</div>
  <p class="result-count mono" id="pub-count" aria-live="polite">Showing %(n)d of %(n)d</p>
  <div id="pub-groups">%(groups)s</div>
  <p class="empty" id="pub-empty" hidden>No publications match these filters. <button type="button" class="link-btn" id="pub-reset">Clear filters</button></p>
</div>
%(cta)s
""" % {
        "head": page_head("Publications", "Papers and submissions", lede),
        "scholar": scholar_html,
        "filters": filters,
        "n": len(PUBS),
        "groups": groups,
        "cta": contact_cta(root),
    }
    return layout("publications.html", "Publications", "Publications by %s: conference papers and submissions in computer vision, world models, and calibration." % PROFILE["name"], body)


def page_projects():
    root = ""
    cats = [c for c in CATEGORY_LABELS if any(p["category"] == c for p in PROJECTS)]
    tabs = ['<button type="button" class="chip-btn" data-value="" aria-pressed="true">All <span class="count">%d</span></button>' % len(PROJECTS)]
    for c in cats:
        n = sum(1 for p in PROJECTS if p["category"] == c)
        tabs.append('<button type="button" class="chip-btn" data-value="%s" aria-pressed="false">%s <span class="count">%d</span></button>' % (c, e(CATEGORY_LABELS[c]), n))
    groups = ""
    for c in cats:
        cards = "".join(project_card(p, root) for p in PROJECTS if p["category"] == c)
        groups += '<section class="project-group" data-category-group="%s"><h2 class="year-head">%s</h2><div class="card-grid card-grid-2">%s</div></section>' % (
            c, e(CATEGORY_LABELS[c] + " projects"), cards)
    body = """
<div class="wrap">
  %(head)s
  <div class="filters"><div class="filter-group" role="group" aria-label="Filter by category" id="project-filter"><span class="filter-label">Category</span>%(tabs)s</div></div>
  %(groups)s
</div>
%(cta)s
""" % {
        "head": page_head("Projects", "Research systems and production software",
                          "Academic research projects from my Ph.D. and undergraduate thesis, alongside industry systems delivered at BJIT Ltd."),
        "tabs": "".join(tabs),
        "groups": groups,
        "cta": contact_cta(root),
    }
    return layout("projects.html", "Projects", "Research and industry projects by %s: digital twins, video world models, benchmarks, RAG, secure APIs, and PLM integrations." % PROFILE["name"], body)


def page_project(p):
    root = "../"
    pub = PUB_BY_ID.get(p.get("publication") or "")
    facts = [("Category", CATEGORY_LABELS[p["category"]]), ("Area", p["area"]), ("Role", p["role"]), ("Status", p["status"])]
    if pub:
        facts.append(("Paper", "%s (%s)" % (venue_line(pub), STATUS_LABELS[pub["status"]].lower()) if pub["status"] != "under-review" else venue_line(pub)))
    facts_html = "".join("<div><dt>%s</dt><dd>%s</dd></div>" % (e(k), e(v)) for k, v in facts)
    links = []
    for key, label in [("paper", "Paper"), ("code", "Code repository"), ("demo", "Demo video")]:
        if p["links"].get(key):
            links.append('<a class="btn" href="%s" target="_blank" rel="noopener"><span>%s</span>%s</a>' % (e(p["links"][key]), label, I_EXT))
    links_html = '<div class="hero-actions">%s</div>' % "".join(links) if links else ""
    image = ""
    if p.get("image"):
        image = '<figure class="project-figure"><img src="%s%s" alt="%s"></figure>' % (root, e(p["image"]), e(p["title"]))
    results = ""
    if p.get("results"):
        results = "<h2>Key results</h2>" + bullets(p["results"], "bullets results")
    pub_html = ""
    if pub:
        pub_html = '<section class="section section-tight"><h2 class="plain-h2">Related publication</h2><div class="pub-list">%s</div></section>' % pub_item(pub, root, "div")
    same = [q for q in PROJECTS if q["category"] == p["category"] and q["slug"] != p["slug"]][:2]
    more = ""
    if same:
        more = '<section class="section section-tight"><h2 class="plain-h2">More %s projects</h2><div class="card-grid card-grid-2">%s</div></section>' % (
            e(CATEGORY_LABELS[p["category"]].lower()), "".join(project_card(q, root, 0) for q in same))
    body = """
<div class="wrap">
  <nav class="crumbs" aria-label="Breadcrumb"><a href="../projects.html">Projects</a><span aria-hidden="true">/</span><span>%(cat)s</span></nav>
  <header class="page-head rise"><p class="eyebrow">%(area)s</p><h1>%(title)s</h1><p class="lede">%(summary)s</p>%(links)s</header>
  <dl class="facts">%(facts)s</dl>
  %(image)s
  <div class="detail-grid">
    <div class="prose">
      <h2>Overview</h2>
      %(description)s
      <h2>My contribution</h2>
      %(contribution)s
      %(results)s
    </div>
    <aside class="aside">
      <div class="aside-block"><h2 class="aside-title">Methods and technologies</h2>%(methods)s</div>
    </aside>
  </div>
  %(pub)s
  %(more)s
</div>
%(cta)s
""" % {
        "cat": e(CATEGORY_LABELS[p["category"]]),
        "area": e(p["area"]),
        "title": e(p["title"]),
        "summary": e(p["summary"]),
        "links": links_html,
        "facts": facts_html,
        "image": image,
        "description": paras(p["description"]),
        "contribution": bullets(p["contribution"]),
        "results": results,
        "methods": chips(p["methods"]),
        "pub": pub_html,
        "more": more,
        "cta": contact_cta(root),
    }
    return layout("projects/%s.html" % p["slug"], p["title"], p["summary"], body, active="projects.html")


def page_experience():
    root = ""
    entries = ""
    for x in EXPERIENCE:
        roles = "".join(
            '<li><span class="role-title">%s</span><span class="mono">%s</span></li>' % (e(r["title"]), e(r["period"])) for r in x["roles"]
        )
        streams = ""
        for w in x.get("workstreams", []):
            link = ""
            if w.get("project") in PROJECT_BY_SLUG:
                link = '<a class="pill" href="projects/%s.html">Project details %s</a>' % (e(w["project"]), I_ARROW)
            streams += '<div class="stream"><h4>%s</h4>%s%s%s</div>' % (e(w["title"]), bullets(w["bullets"]), chips(w.get("tech")), link)
        if streams:
            streams = '<div class="streams">%s</div>' % streams
        full = '<p class="org-full">%s</p>' % e(x["org_full"]) if x.get("org_full") else ""
        now = '<span class="badge badge-accepted">Current</span>' if x.get("current") else ""
        entries += """
<li class="tl-item">
  <div class="tl-when"><span class="mono">%(period)s</span><span class="tl-kind">%(kind)s</span></div>
  <div class="tl-body">
    <h2>%(org)s %(now)s</h2>
    %(full)s
    <p class="tl-loc">%(loc)s</p>
    <ul class="roles">%(roles)s</ul>
    %(bullets)s
    %(tech)s
    %(streams)s
  </div>
</li>""" % {
            "period": e(x["period"]),
            "kind": "Research" if x["kind"] == "research" else "Industry",
            "org": e(x["org"]),
            "now": now,
            "full": full,
            "loc": e(x["location"]),
            "roles": roles,
            "bullets": bullets(x["bullets"]),
            "tech": chips(x.get("tech")),
            "streams": streams,
        }
    body = """
<div class="wrap">
  %(head)s
  <ol class="timeline">%(entries)s</ol>
</div>
%(cta)s
""" % {
        "head": page_head("Experience", "Research and industry, on one timeline",
                          "Doctoral research at Kennesaw State University since 2025, after eight years and two promotions at BJIT Ltd."),
        "entries": entries,
        "cta": contact_cta(root),
    }
    return layout("experience.html", "Experience", "Professional timeline of %s: doctoral researcher at Kennesaw State University and former Principal Software Engineer at BJIT Ltd." % PROFILE["name"], body)


def page_education():
    root = ""
    cards = ""
    for d in EDUCATION["degrees"]:
        rows = []
        if d.get("department"):
            rows.append(("Department", e(d["department"])))
        if d.get("lab"):
            rows.append(("Lab", e(d["lab"])))
        if d.get("advisor"):
            rows.append(("Advisor", e(d["advisor"])))
        if d.get("specialization"):
            rows.append(("Research focus", e(d["specialization"])))
        if d.get("thesis"):
            t = d["thesis"]
            title = e(t["title"])
            if t.get("project") in PROJECT_BY_SLUG:
                title = '<a href="projects/%s.html">%s</a>' % (e(t["project"]), title)
            rows.append(("Thesis", title))
        rows_html = "".join("<div><dt>%s</dt><dd>%s</dd></div>" % (k, v) for k, v in rows)
        note = ' <span class="badge badge-accepted">%s</span>' % e(d["note"]) if d.get("note") else ""
        dist = ""
        if d.get("distinctions"):
            dist = "<h3>Distinctions</h3>" + bullets(d["distinctions"])
        cards += """
<article class="degree">
  <div class="degree-when"><span class="mono">%(period)s</span></div>
  <div class="degree-body">
    <h2>%(degree)s%(note)s</h2>
    <p class="degree-inst">%(inst)s · %(loc)s</p>
    <dl class="facts facts-plain">%(rows)s</dl>
    %(dist)s
  </div>
</article>""" % {
            "period": e(d["period"]),
            "degree": e(d["degree"]),
            "note": note,
            "inst": e(d["institution"]),
            "loc": e(d["location"]),
            "rows": rows_html,
            "dist": dist,
        }
    oc = EDUCATION["online_courses"]
    body = """
<div class="wrap">
  %(head)s
  <div class="degrees">%(cards)s</div>
</div>
<section class="wrap section" aria-labelledby="h-course">
  %(h1)s
  %(coursework)s
</section>
<section class="wrap section" aria-labelledby="h-online">
  %(h2)s
  %(online)s
</section>
%(cta)s
""" % {
        "head": page_head("Education", "Academic qualifications",
                          "A Ph.D. in progress at Kennesaw State University, built on a B.Sc. in Computer Science and Engineering from KUET."),
        "cards": cards,
        "h1": sec_head("01", "Undergraduate coursework", None, "h-course"),
        "coursework": chips(EDUCATION["coursework"], "chips chips-lg"),
        "h2": sec_head("02", "Online courses · %s" % oc["provider"], None, "h-online"),
        "online": bullets(oc["items"], "bullets bullets-lg"),
        "cta": contact_cta(root),
    }
    return layout("education.html", "Education", "Education of %s: Ph.D. in Computer Science (in progress) at Kennesaw State University; B.Sc. in CSE from KUET." % PROFILE["name"], body)


def page_404():
    body = """
<div class="wrap">
  <header class="page-head"><p class="eyebrow">404</p><h1>This page does not exist</h1>
  <p class="lede">The link may be out of date.</p>
  <div class="hero-actions"><a class="btn btn-primary" href="index.html"><span>Back to the homepage</span></a></div></header>
</div>"""
    return layout("404.html", "Page not found", "Page not found.", body, active="none")


# --------------------------------------------------------------------------
# Build
# --------------------------------------------------------------------------
def write(path, text):
    target = DIST / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8", newline="\n")


def main():
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir()
    shutil.copytree(ASSETS, DIST / "assets")
    (DIST / ".nojekyll").write_text("", encoding="utf-8")

    pages = {
        "index.html": page_home(),
        "about.html": page_about(),
        "research.html": page_research(),
        "publications.html": page_publications(),
        "projects.html": page_projects(),
        "experience.html": page_experience(),
        "education.html": page_education(),
        "404.html": page_404(),
    }
    for p in PROJECTS:
        pages["projects/%s.html" % p["slug"]] = page_project(p)
    for path, text in pages.items():
        write(path, text)

    for kind, spec in (PROFILE.get("cv") or {}).items():
        if kind in CVS:
            (DIST / "cv").mkdir(exist_ok=True)
            shutil.copyfile(ROOT / spec["source"], DIST / "cv" / CVS[kind])

    if PROFILE.get("site_url"):
        base = PROFILE["site_url"].rstrip("/") + "/"
        urls = "".join("<url><loc>%s%s</loc></url>" % (base, "" if p == "index.html" else p) for p in pages if p != "404.html")
        write("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">%s</urlset>' % urls)
        write("robots.txt", "User-agent: *\nAllow: /\nSitemap: %ssitemap.xml\n" % base)

    print("Built %d pages into %s" % (len(pages), DIST))
    for kind in ("academic", "professional"):
        if kind not in CVS:
            print("  note: %s CV file not found; its link is hidden" % kind)
    for t in PROFILE.get("todo", []):
        print("  TODO " + t)


if __name__ == "__main__":
    sys.exit(main())
