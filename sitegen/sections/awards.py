"""Honors and awards. An item with a `certificate` path gets a Certificate button."""
from ..content import PROFILE
from ..html import certificate_button, e


def render(root):
    awards = PROFILE.get("awards") or []
    if not awards:
        return ""
    rows = "".join(
        "<li>%s, %s (%s)%s</li>" % (e(a["title"]), e(a["org"]), e(a["year"]), certificate_button(a, root)) for a in awards
    )
    return '<ul class="simple-list">%s</ul>' % rows
