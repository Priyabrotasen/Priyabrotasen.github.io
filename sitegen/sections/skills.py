"""Technical skills, grouped."""
from ..content import PROFILE
from ..html import e, tags


def render(root):
    groups = PROFILE.get("skills") or []
    if not groups:
        return ""
    rows = "".join('<div class="skill-row"><h3>%s</h3>%s</div>' % (e(g["group"]), tags(g["items"])) for g in groups)
    return '<div class="skill-list">%s</div>' % rows
