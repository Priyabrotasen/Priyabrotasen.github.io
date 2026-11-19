"""Projects that are not academic research (those appear in the Research section).

Industry and independent projects are grouped; a group with no projects is hidden,
so adding a project with "category": "independent" makes that group appear.
"""
from ..components import project_card
from ..content import PROJECTS
from ..html import e

GROUPS = [("industry", None), ("independent", "Independent projects")]


def render(root):
    parts = []
    for category, heading in GROUPS:
        items = [p for p in PROJECTS if p["category"] == category]
        if not items:
            continue
        if heading:
            parts.append('<h3 class="minor-heading">%s</h3>' % e(heading))
        parts.append('<div class="card-list">%s</div>' % "".join(project_card(p, root) for p in items))
    return "".join(parts)
