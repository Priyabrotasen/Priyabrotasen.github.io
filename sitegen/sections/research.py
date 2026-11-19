"""Research: overview, one card per academic research project, current directions."""
from ..components import project_card
from ..content import PROJECTS, RESEARCH
from ..html import bullets, rich


def render(root):
    projects = [p for p in PROJECTS if p["category"] == "research"]
    if not projects and not RESEARCH.get("lede"):
        return ""
    parts = []
    if RESEARCH.get("lede"):
        parts.append('<p class="section-intro">%s</p>' % rich(RESEARCH["lede"], root))
    parts.append('<div class="card-list">%s</div>' % "".join(project_card(p, root) for p in projects))
    if RESEARCH.get("directions"):
        parts.append('<h3 class="minor-heading">Current directions</h3>')
        parts.append(bullets(RESEARCH["directions"], root=root))
    return "".join(parts)
