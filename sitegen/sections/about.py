"""About: optional callout, positioning line, biography, interests, headline numbers."""
from ..content import CVS, PROFILE
from ..html import ICONS, button, e, paras, rich, tags


def render(root):
    parts = []
    if PROFILE.get("callout"):
        parts.append('<div class="callout">%s<p>%s</p></div>' % (ICONS["info"], rich(PROFILE["callout"], root)))
    if PROFILE.get("positioning"):
        parts.append('<p class="lead">%s</p>' % rich(PROFILE["positioning"], root))
    parts.append(paras(PROFILE["bio_long"], root))

    if PROFILE.get("interests"):
        parts.append('<h3 class="minor-heading">Research interests</h3>')
        parts.append(tags([i["title"] for i in PROFILE["interests"]], "tags tags-lg"))

    if PROFILE.get("metrics"):
        cells = "".join(
            '<div class="metric"><dt>%s</dt><dd class="metric-value">%s</dd><dd class="metric-detail">%s</dd></div>'
            % (e(m["label"]), e(m["value"]), e(m["detail"]))
            for m in PROFILE["metrics"]
        )
        parts.append('<dl class="metrics">%s</dl>' % cells)

    buttons = []
    if "academic" in CVS:
        buttons.append(button("Academic CV", root + "cv/" + CVS["academic"], icon=ICONS["file"], cls="button button-outline"))
    if "professional" in CVS:
        buttons.append(button("Professional CV", root + "cv/" + CVS["professional"], icon=ICONS["file"], cls="button button-outline"))
    if PROFILE.get("email"):
        buttons.append(button("Email me", "mailto:" + PROFILE["email"], external=False, icon=ICONS["mail"], cls="button button-outline"))
    if buttons:
        parts.append('<div class="button-row">%s</div>' % "".join(buttons))
    return '<div class="about-content">%s</div>' % "".join(parts)
