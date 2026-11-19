"""Honors and awards."""
from ..content import PROFILE
from ..html import bullets


def render(root):
    awards = PROFILE.get("awards") or []
    if not awards:
        return ""
    return bullets(["%s, %s (%s)" % (a["title"], a["org"], a["year"]) for a in awards], root=root)
