"""Service: reviewing and volunteering. Add a group by appending to `groups`.

A reviewing item with a `certificate` path gets a Certificate button.
"""
from ..content import PROFILE
from ..html import bullets, certificate_button, e


def render(root):
    reviewing = "".join(
        "<li>%s. %s%s</li>" % (e(s["title"]), e(s["detail"]), certificate_button(s, root)) for s in PROFILE.get("service") or []
    )
    groups = [
        ("Reviewing", '<ul class="simple-list">%s</ul>' % reviewing if reviewing else ""),
        ("Volunteering", bullets(PROFILE.get("volunteering") or [], root=root)),
    ]
    return "".join('<div class="service-group"><h3>%s</h3>%s</div>' % (e(title), body) for title, body in groups if body)
