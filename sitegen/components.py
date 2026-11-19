"""Reusable pieces shared by sections and pages."""
import re

from .content import PROFILE, PROJECT_BY_SLUG, PUB_BY_ID
from .html import ICONS, button, bullets, e, tags

STATUS_LABELS = {"under-review": "Under review", "accepted": "Accepted", "published": "Published"}
TYPE_LABELS = {
    "journal": "Journal papers",
    "conference": "Conference papers",
    "workshop": "Workshop papers",
    "preprint": "Preprints",
    "chapter": "Book chapters",
}
CATEGORY_LABELS = {"research": "Academic research", "industry": "Industry", "independent": "Independent"}


# --------------------------------------------------------------------------
# Publications
# --------------------------------------------------------------------------
def venue_line(pub):
    """Venue text that states the status exactly and never overstates it."""
    status = pub["status"]
    if status == "under-review":
        if PROFILE.get("show_venue_for_under_review", True):
            return "Under review · submitted to %s" % pub["venue"]
        return "Under review"
    parts = [pub["venue"]]
    if pub.get("location"):
        parts.append(pub["location"])
    if pub.get("publisher"):
        parts.append(pub["publisher"])
    line = ", ".join(parts)
    return line + " (accepted)" if status == "accepted" else line


def _bib_author(name):
    parts = name.split()
    return "%s, %s" % (parts[-1], " ".join(parts[:-1])) if len(parts) > 1 else name


def bibtex(pub):
    surname = re.sub(r"[^a-z]", "", pub["authors"][0].split()[-1].lower())
    words = [re.sub(r"[^a-z0-9]", "", w.lower()) for w in pub["title"].split()]
    first = next((w for w in words if len(w) > 3), words[0])
    fields = [("title", "{%s}" % pub["title"]), ("author", " and ".join(_bib_author(a) for a in pub["authors"]))]
    if pub["status"] == "under-review" or pub["type"] == "preprint":
        kind = "unpublished"
        note = "Submitted to %s" % pub["venue"] if PROFILE.get("show_venue_for_under_review", True) else "Under review"
        fields += [("note", note), ("year", str(pub["year"]))]
    else:
        kind = {"journal": "article", "chapter": "incollection"}.get(pub["type"], "inproceedings")
        fields += [("journal" if kind == "article" else "booktitle", pub["venue"]), ("year", str(pub["year"]))]
        for key, name in [("pages", "pages"), ("location", "address"), ("publisher", "publisher"), ("doi", "doi")]:
            if pub.get(key):
                fields.append((name, pub[key]))
        if pub["status"] == "accepted":
            fields.append(("note", "Accepted"))
    body = ",\n".join("  %-9s = {%s}" % (k, v) for k, v in fields)
    return "@%s{%s%s%s,\n%s\n}" % (kind, surname, pub["year"], first, body)


def authors_html(pub):
    me = PROFILE["author_name"]
    return ", ".join("<strong>%s</strong>" % e(a) if a == me else e(a) for a in pub["authors"])


def publication_card(pub, root=""):
    links = []
    for key, label in [("pdf", "PDF"), ("arxiv", "arXiv"), ("code", "Code"), ("project_page", "Project page")]:
        if pub.get(key):
            links.append(button(label, pub[key]))
    if pub.get("doi"):
        links.append(button("DOI", "https://doi.org/" + pub["doi"]))
    if pub.get("url"):
        links.append(button("IEEE Xplore" if "ieeexplore" in pub["url"] else "Publisher", pub["url"]))
    if pub.get("project") in PROJECT_BY_SLUG:
        links.append(button("Project", "%sprojects/%s.html" % (root, pub["project"]), external=False))
    bib = bibtex(pub)
    links.append(
        '<details class="bib"><summary class="button button-ghost">BibTeX</summary>'
        '<div class="bib-box"><pre><code>%s</code></pre>'
        '<button type="button" class="button button-ghost copy" data-copy="%s">%s<span>Copy</span></button></div></details>'
        % (e(bib), e(bib), ICONS["copy"])
    )
    title = e(pub["title"])
    target = pub.get("arxiv") or pub.get("url") or (("https://doi.org/" + pub["doi"]) if pub.get("doi") else None)
    if target:
        title = '<a href="%s" target="_blank" rel="noopener">%s</a>' % (e(target), title)
    return (
        '<article class="card publication-item" id="pub-%s" data-year="%s" data-status="%s" data-type="%s">'
        '<h3 class="publication-title">%s</h3>'
        '<p class="publication-authors">%s</p>'
        '<div class="publication-info"><p class="publication-venue">%s</p>'
        '<div class="publication-links">%s</div></div></article>'
    ) % (e(pub["id"]), e(pub["year"]), e(pub["status"]), e(pub["type"]), title, authors_html(pub), e(venue_line(pub)), "".join(links))


# --------------------------------------------------------------------------
# Projects
# --------------------------------------------------------------------------
def project_card(p, root="", show_result=True):
    pub = PUB_BY_ID.get(p.get("publication") or "")
    venue = '<p class="publication-venue">%s</p>' % e(venue_line(pub)) if pub else ""
    result = ""
    if show_result and p.get("results"):
        result = '<p class="project-result"><strong>Key result.</strong> %s</p>' % e(p["results"][0])
    links = [button("Details", "%sprojects/%s.html" % (root, p["slug"]), external=False)]
    for key, label in [("paper", "Paper"), ("code", "Code"), ("demo", "Demo")]:
        if p["links"].get(key):
            links.append(button(label, p["links"][key]))
    image = ""
    if p.get("image"):
        image = '<img class="project-thumb" src="%s%s" alt="" loading="lazy">' % (root, e(p["image"]))
    return (
        '<article class="card project-item" id="project-%s">%s'
        '<p class="kicker">%s</p>'
        '<h3 class="publication-title"><a href="%sprojects/%s.html">%s</a></h3>'
        '<p class="project-summary">%s</p>%s%s'
        '<div class="publication-info">%s<div class="publication-links">%s</div></div></article>'
    ) % (e(p["slug"]), image, e(p["area"]), root, e(p["slug"]), e(p["title"]), e(p["summary"]), result,
         tags(p.get("methods", [])[:6]), venue, "".join(links))


def gallery(spec, root=""):
    """Photo grid for a {"title", "caption", "images": [{"src", "alt"}]} spec. Each photo opens full size."""
    if not spec or not spec.get("images"):
        return ""
    figures = "".join(
        '<a href="%s%s" target="_blank" rel="noopener"><img src="%s%s" alt="%s" loading="lazy"></a>'
        % (root, e(i["src"]), root, e(i["src"]), e(i.get("alt", "")))
        for i in spec["images"]
    )
    caption = "<figcaption>%s</figcaption>" % e(spec["caption"]) if spec.get("caption") else ""
    return '<h3>%s</h3><figure class="gallery"><div class="gallery-grid">%s</div>%s</figure>' % (
        e(spec.get("title", "Gallery")), figures, caption)


# --------------------------------------------------------------------------
# Timeline (education, experience)
# --------------------------------------------------------------------------
def timeline_item(date, title, lines=(), extra=""):
    """One dated row. `lines` are plain strings; `extra` is ready-made HTML."""
    body = "".join("<p>%s</p>" % e(line) for line in lines if line)
    return (
        '<div class="timeline-item"><div class="timeline-date">%s</div>'
        '<div class="timeline-content"><h3>%s</h3>%s%s</div></div>' % (e(date), e(title), body, extra)
    )


def timeline(items):
    return '<div class="timeline">%s</div>' % "".join(items)


__all__ = [
    "STATUS_LABELS", "TYPE_LABELS", "CATEGORY_LABELS", "venue_line", "bibtex", "authors_html",
    "publication_card", "project_card", "timeline_item", "timeline", "bullets",
]
