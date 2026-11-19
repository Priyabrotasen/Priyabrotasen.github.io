"""The pages that get written to dist/.

`all_pages()` returns {output path: html}. To add a page, write a function that
returns layout.page(...) and register it in all_pages().
"""
import json

from .components import CATEGORY_LABELS, project_card, publication_card, venue_line
from .content import PROFILE, PROJECTS, PUB_BY_ID
from .html import ICONS, bullets, button, e, paras, tags
from .layout import page
from .sections import build_sections


def home(sections_html, nav):
    aff = PROFILE["affiliation"]
    person = {
        "@context": "https://schema.org",
        "@type": "Person",
        "name": PROFILE["name"],
        "jobTitle": PROFILE["title"],
        "affiliation": {"@type": "CollegeOrUniversity", "name": aff["institution"]},
        "sameAs": [u for u in (PROFILE.get("links") or {}).values() if u],
    }
    if PROFILE.get("site_url"):
        person["url"] = PROFILE["site_url"]
    head = '<script type="application/ld+json">%s</script>' % json.dumps(person).replace("</", "<\\/")
    return page("index.html", PROFILE["name"], PROFILE["intro"], sections_html, nav, home=True, head_extra=head)


def project(p, nav):
    root = "../"
    pub = PUB_BY_ID.get(p.get("publication") or "")
    facts = [("Category", CATEGORY_LABELS[p["category"]]), ("Area", p["area"]), ("Role", p["role"]), ("Status", p["status"])]
    if pub:
        facts.append(("Paper", venue_line(pub)))
    links = "".join(button(label, p["links"][key]) for key, label in
                    [("paper", "Paper"), ("code", "Code"), ("demo", "Demo video")] if p["links"].get(key))
    image = ""
    if p.get("image"):
        image = '<img class="project-figure" src="%s%s" alt="%s">' % (root, e(p["image"]), e(p["title"]))
    results = "<h3>Key results</h3>" + bullets(p["results"]) if p.get("results") else ""
    related = ""
    if pub:
        related = '<h3>Related publication</h3><div class="card-list">%s</div>' % publication_card(pub, root)
    others = [q for q in PROJECTS if q["category"] == p["category"] and q["slug"] != p["slug"]]
    more = ""
    if others:
        more = '<h3>More %s projects</h3><div class="card-list">%s</div>' % (
            e(CATEGORY_LABELS[p["category"]].lower()), "".join(project_card(q, root, show_result=False) for q in others))
    back = "research" if p["category"] == "research" else "projects"
    content = """
<article class="section project-page">
  <a class="back-link" href="../index.html#%(back)s">%(icon)s Back to %(back)s</a>
  <p class="kicker">%(area)s</p>
  <h1>%(title)s</h1>
  <p class="lead">%(summary)s</p>
  %(links)s
  <dl class="facts">%(facts)s</dl>
  %(image)s
  <h3>Overview</h3>%(description)s
  <h3>My contribution</h3>%(contribution)s
  %(results)s
  <h3>Methods and technologies</h3>%(methods)s
  %(related)s
  %(more)s
</article>""" % {
        "back": back, "icon": ICONS["back"], "area": e(p["area"]), "title": e(p["title"]), "summary": e(p["summary"]),
        "links": '<div class="button-row">%s</div>' % links if links else "",
        "facts": "".join("<div><dt>%s</dt><dd>%s</dd></div>" % (e(k), e(v)) for k, v in facts),
        "image": image, "description": paras(p["description"], root), "contribution": bullets(p["contribution"]),
        "results": results, "methods": tags(p["methods"]), "related": related, "more": more,
    }
    return page("projects/%s.html" % p["slug"], p["title"], p["summary"], content, nav)


def not_found(nav):
    content = (
        '<section class="section"><h1>Page not found</h1><p>The link may be out of date.</p>'
        '<div class="button-row"><a class="button button-outline" href="/">Back to the homepage</a></div></section>'
    )
    return page("404.html", "Page not found", "Page not found.", content, nav)


def all_pages():
    sections_html, nav = build_sections("")
    pages = {"index.html": home(sections_html, nav), "404.html": not_found(nav)}
    for p in PROJECTS:
        pages["projects/%s.html" % p["slug"]] = project(p, nav)
    return pages
