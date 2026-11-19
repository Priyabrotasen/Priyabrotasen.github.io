"""Page shell shared by every page: top nav, sidebar, footer."""
from datetime import date

from .content import CVS, PROFILE
from .html import ICONS, e

THEME_SCRIPT = (
    "(function(){try{var t=localStorage.getItem('theme');"
    "if(t==='light'||t==='dark'){document.documentElement.setAttribute('data-theme',t);}}catch(e){}})();"
)


def profile_links(root):
    """(label, href, external, icon) for every link that is actually available."""
    out = []
    if "academic" in CVS:
        out.append(("Academic CV", root + "cv/" + CVS["academic"], True, ICONS["file"]))
    if "professional" in CVS:
        out.append(("Professional CV", root + "cv/" + CVS["professional"], True, ICONS["file"]))
    links = PROFILE.get("links") or {}
    for key, label, icon in [("scholar", "Google Scholar", "scholar"), ("github", "GitHub", "github"),
                             ("linkedin", "LinkedIn", "linkedin"), ("orcid", "ORCID", "orcid")]:
        url = links.get(key)
        if url and url.startswith("http"):
            out.append((label, url, True, ICONS[icon]))
    return out


def sidebar(root, home):
    aff = PROFILE["affiliation"]
    name_tag = "h1" if home else "p"
    if PROFILE.get("photo"):
        alt = "Placeholder portrait" if "placeholder" in PROFILE["photo"] else PROFILE["name"]
        photo = '<img class="profile-image" src="%s%s" alt="%s" width="400" height="500">' % (root, e(PROFILE["photo"]), e(alt))
    else:
        photo = '<div class="profile-image profile-initials" aria-hidden="true">%s</div>' % e(PROFILE["initials"])
    items = []
    if PROFILE.get("email"):
        items.append('<li><a href="mailto:%s">%s<span>%s</span></a></li>' % (e(PROFILE["email"]), ICONS["mail"], e(PROFILE["email"])))
    for label, href, external, icon in profile_links(root):
        attrs = ' target="_blank" rel="noopener me"' if external else ""
        items.append('<li><a href="%s"%s>%s<span>%s</span></a></li>' % (e(href), attrs, icon, e(label)))
    where = [aff.get("unit"), aff["institution"]]
    return (
        '<aside class="sidebar">'
        '<%(t)s class="sidebar-name"><a href="%(root)sindex.html">%(name)s</a></%(t)s>'
        '<p class="sidebar-role">%(role)s</p>%(photo)s'
        '<p class="sidebar-affiliation">%(where)s</p>'
        '<ul class="sidebar-links">%(links)s</ul></aside>'
    ) % {
        "t": name_tag, "root": root, "name": e(PROFILE["name"]), "role": e(PROFILE["title"]), "photo": photo,
        "where": "<br>".join(e(w) for w in where if w), "links": "".join(items),
    }


def page(path, title, description, content, nav, home=False, head_extra=""):
    """Wrap `content` in the full HTML document.

    path  output path relative to dist/ (used to work out relative links)
    nav   list of (section id, label) for the top bar
    """
    root = "../" * path.count("/")
    prefix = "" if home else root + "index.html"
    nav_html = "".join('<a href="%s#%s">%s</a>' % (prefix, e(i), e(label)) for i, label in nav)
    canonical = ""
    if PROFILE.get("site_url"):
        url = PROFILE["site_url"].rstrip("/") + "/" + ("" if home else path)
        canonical = '<link rel="canonical" href="%s">\n<meta property="og:url" content="%s">' % (e(url), e(url))
    full_title = title if home else "%s · %s" % (title, PROFILE["name"])
    return """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>%(title)s</title>
<meta name="description" content="%(desc)s">
<meta name="author" content="%(name)s">
<meta property="og:type" content="profile">
<meta property="og:title" content="%(title)s">
<meta property="og:description" content="%(desc)s">
<meta name="twitter:card" content="summary">
%(canonical)s
<link rel="icon" href="%(root)sassets/favicon.svg" type="image/svg+xml">
<script>%(theme)s</script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="%(root)sassets/styles.css">
%(head_extra)s
</head>
<body%(body_attr)s>
<a class="skip" href="#main">Skip to content</a>
<nav class="navbar" aria-label="Primary">
  <div class="container nav-content">
    <div class="nav-links" id="nav-links">%(nav)s</div>
    <button type="button" id="theme-toggle" class="icon-button" aria-label="Switch colour theme">
      <span class="when-light">%(moon)s</span><span class="when-dark">%(sun)s</span>
    </button>
  </div>
</nav>
<div class="container page-layout">
  %(sidebar)s
  <main id="main" class="page-content">
%(content)s
    <footer class="footer"><p>© %(year)s %(name)s · Last updated: %(updated)s</p></footer>
  </main>
</div>
<script src="%(root)sassets/site.js" defer></script>
</body>
</html>
""" % {
        "title": e(full_title), "desc": e(description), "name": e(PROFILE["name"]), "canonical": canonical,
        "root": root, "theme": THEME_SCRIPT, "head_extra": head_extra,
        "body_attr": ' data-page="home"' if home else "",
        "nav": nav_html, "moon": ICONS["moon"], "sun": ICONS["sun"],
        "sidebar": sidebar(root, home), "content": content,
        "year": date.today().year, "updated": date.today().strftime("%B %Y"),
    }
