"""Homepage sections.

Each module in this folder defines one function:

    def render(root: str) -> str

It returns the HTML that goes inside the section (without the <section> tag
or the heading), or "" to skip the section entirely. `root` is the relative
path prefix back to the site root ("" on the homepage).

To add a section:
  1. create sitegen/sections/<name>.py with a render(root) function
  2. add {"module": "<name>", "id": "...", "nav": "...", "title": "..."} to content/site.json
  3. (optional) add styles in assets/css/40-sections.css
"""
from importlib import import_module

from ..content import SITE
from ..html import e


def build_sections(root=""):
    """Render every enabled section. Returns (html, nav) where nav = [(id, label)]."""
    html, nav = [], []
    for spec in SITE["sections"]:
        if not spec.get("enabled", True):
            continue
        inner = import_module("sitegen.sections." + spec["module"]).render(root)
        if not inner:
            continue
        heading = "<h2>%s</h2>" % e(spec["title"]) if spec.get("title") else ""
        html.append('<section id="%s" class="section section-%s">%s%s</section>' % (e(spec["id"]), e(spec["module"]), heading, inner))
        if spec.get("nav"):
            nav.append((spec["id"], spec["nav"]))
    return "\n".join(html), nav
