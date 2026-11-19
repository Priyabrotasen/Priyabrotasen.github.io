"""Experience: research and industry roles on one timeline."""
from ..components import timeline, timeline_item
from ..content import EXPERIENCE, PROJECT_BY_SLUG
from ..html import bullets, e, tags


def _entry(x, root):
    roles = x["roles"]
    if len(roles) == 1:
        title = roles[0]["title"]
        extra = ""
    else:
        title = "%s → %s" % (roles[-1]["title"], roles[0]["title"])
        extra = '<ul class="role-list">%s</ul>' % "".join(
            "<li><span>%s</span><span>%s</span></li>" % (e(r["title"]), e(r["period"])) for r in roles)
    org = ", ".join(v for v in [x.get("org_full"), x["org"], x["location"]] if v)
    extra += bullets(x["bullets"], root=root)
    for w in x.get("workstreams", []):
        link = ""
        if w.get("project") in PROJECT_BY_SLUG:
            link = ' <a class="inline-link" href="%sprojects/%s.html">Details</a>' % (root, e(w["project"]))
        extra += '<div class="workstream"><h4>%s%s</h4>%s%s</div>' % (
            e(w["title"]), link, bullets(w["bullets"], root=root), tags(w.get("tech")))
    extra += tags(x.get("tech"))
    return timeline_item(x["period"], title, [org], extra)


def render(root):
    if not EXPERIENCE:
        return ""
    return timeline([_entry(x, root) for x in EXPERIENCE])
