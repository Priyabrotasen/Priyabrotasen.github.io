"""Escaping, inline formatting, icons, and small HTML helpers."""
import html
import re


def e(value):
    """Escape text for safe use in HTML."""
    return html.escape(str(value), quote=True)


_LINK = re.compile(r"\[([^\]]+)\]\(([^)\s]+)\)")
_BOLD = re.compile(r"\*\*(.+?)\*\*")
_ITALIC = re.compile(r"\*(.+?)\*")


def rich(text, root=""):
    """Escape text, then apply [label](url), **bold** and *italic*.

    Relative URLs are prefixed with `root` so they work from sub-pages.
    """
    def link(m):
        label, url = m.group(1), m.group(2)
        if url.startswith(("http://", "https://")):
            return '<a href="%s" target="_blank" rel="noopener">%s</a>' % (url, label)
        if url.startswith(("mailto:", "#")):
            return '<a href="%s">%s</a>' % (url, label)
        return '<a href="%s%s">%s</a>' % (root, url, label)

    out = _LINK.sub(link, e(text))
    out = _BOLD.sub(r"<strong>\1</strong>", out)
    return _ITALIC.sub(r"<em>\1</em>", out)


def paras(items, root=""):
    return "".join("<p>%s</p>" % rich(p, root) for p in items)


def tags(items, cls="tags"):
    if not items:
        return ""
    return '<ul class="%s">%s</ul>' % (cls, "".join("<li>%s</li>" % e(i) for i in items))


def bullets(items, cls="simple-list", root=""):
    if not items:
        return ""
    return '<ul class="%s">%s</ul>' % (cls, "".join("<li>%s</li>" % rich(i, root) for i in items))


def button(label, href, external=True, icon=None, cls="button"):
    attrs = ' target="_blank" rel="noopener"' if external else ""
    return '<a class="%s" href="%s"%s>%s%s</a>' % (cls, e(href), attrs, icon or "", e(label))



def certificate_button(item, root=""):
    """A small 'Certificate' button for an item that has a `certificate` path, else ""."""
    if not item.get("certificate"):
        return ""
    return ' <a class="button button-ghost button-inline" href="%s%s" target="_blank" rel="noopener">Certificate</a>' % (root, e(item["certificate"]))

# --------------------------------------------------------------------------
# Icons: inline SVG, decorative. Add a new one by adding a path here.
# --------------------------------------------------------------------------
def _svg(path, size=16):
    return (
        '<svg class="icon" width="%d" height="%d" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">%s</svg>' % (size, size, path)
    )


ICONS = {
    "file": _svg('<path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z"/><path d="M14 3v5h5M9 13h6M9 17h6"/>'),
    "scholar": _svg('<path d="M22 10 12 5 2 10l10 5 10-5z"/><path d="M6 12v5c3 2 9 2 12 0v-5"/>'),
    "mail": _svg('<rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/>'),
    "github": _svg('<path d="M9 19c-5 1.5-5-2.5-7-3m14 6v-3.87a3.37 3.37 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 9 18.13V22"/>'),
    "linkedin": _svg('<rect x="3" y="3" width="18" height="18" rx="3"/><path d="M8 11v6M8 7.5v.01M12 17v-3.5a2 2 0 0 1 4 0V17M12 11v6"/>'),
    "orcid": _svg('<circle cx="12" cy="12" r="9"/><path d="M9 10v6M9 7.5v.01M12.5 16v-6h1.5a3 3 0 0 1 0 6z"/>'),
    "pin": _svg('<path d="M12 21s-6-5.3-6-10a6 6 0 0 1 12 0c0 4.7-6 10-6 10z"/><circle cx="12" cy="11" r="2"/>'),
    "arrow": _svg('<path d="M5 12h14M13 6l6 6-6 6"/>', 14),
    "back": _svg('<path d="M19 12H5M11 6l-6 6 6 6"/>', 14),
    "sun": _svg('<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/>', 18),
    "moon": _svg('<path d="M20 14.5A8.5 8.5 0 0 1 9.5 4a7 7 0 1 0 10.5 10.5z"/>', 18),
    "copy": _svg('<rect x="9" y="9" width="11" height="11" rx="2"/><path d="M5 15V6a2 2 0 0 1 2-2h9"/>', 14),
    "info": _svg('<circle cx="12" cy="12" r="9"/><path d="M12 11v5M12 7.5v.01"/>', 18),
}
