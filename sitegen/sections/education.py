"""Education: degrees on a timeline. Coursework and online courses are optional (flags in education.json)."""
from ..components import timeline, timeline_item
from ..content import EDUCATION, PROJECT_BY_SLUG
from ..html import bullets, e, tags


def _degree(d, root):
    title = d["degree"] + (" (%s)" % d["note"].lower() if d.get("note") else "")
    lines = ["%s, %s" % (d["institution"], d["location"])]
    if d.get("department"):
        lines.append(d["department"])
    if d.get("lab"):
        lines.append("Lab: " + d["lab"])
    if d.get("advisor"):
        lines.append("Advisor: " + d["advisor"])
    if d.get("specialization"):
        lines.append("Research focus: " + d["specialization"])
    extra = ""
    if d.get("thesis"):
        t = d["thesis"]
        name = e(t["title"])
        if t.get("project") in PROJECT_BY_SLUG:
            name = '<a href="%sprojects/%s.html">%s</a>' % (root, e(t["project"]), name)
        extra += "<p>Thesis: %s</p>" % name
    extra += bullets(d.get("distinctions"), root=root)
    return timeline_item(d["period"], title, lines, extra)


def render(root):
    parts = [timeline([_degree(d, root) for d in EDUCATION["degrees"]])]
    if EDUCATION.get("show_coursework") and EDUCATION.get("coursework"):
        parts.append('<h3 class="minor-heading">Undergraduate coursework</h3>')
        parts.append(tags(EDUCATION["coursework"]))
    online = EDUCATION.get("online_courses") or {}
    if EDUCATION.get("show_online_courses") and online.get("items"):
        parts.append('<h3 class="minor-heading">Online courses (%s)</h3>' % e(online["provider"]))
        parts.append(bullets(online["items"], root=root))
    return "".join(parts)
