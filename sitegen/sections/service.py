"""Service: reviewing and volunteering. Add a group by appending to GROUPS."""
from ..content import PROFILE
from ..html import bullets, e


def render(root):
    groups = [
        ("Reviewing", ["%s. %s" % (s["title"], s["detail"]) for s in PROFILE.get("service") or []]),
        ("Volunteering", PROFILE.get("volunteering") or []),
    ]
    return "".join(
        '<div class="service-group"><h3>%s</h3>%s</div>' % (e(title), bullets(items, root=root))
        for title, items in groups if items
    )
