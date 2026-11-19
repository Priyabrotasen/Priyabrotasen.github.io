"""Writes the finished site to dist/."""
import shutil

from .content import ASSETS, CVS, DIST, PROFILE, ROOT
from .pages import all_pages


def _write(path, text):
    target = DIST / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8", newline="\n")


def _bundle_css():
    """Concatenate assets/css/*.css in filename order into one stylesheet."""
    parts = []
    for f in sorted((ASSETS / "css").glob("*.css")):
        parts.append("/* ---- %s ---- */\n%s" % (f.name, f.read_text(encoding="utf-8")))
    return "\n".join(parts)


def main():
    if DIST.exists():
        shutil.rmtree(DIST)
    shutil.copytree(ASSETS, DIST / "assets", ignore=shutil.ignore_patterns("css"))
    _write("assets/styles.css", _bundle_css())
    _write(".nojekyll", "")

    pages = all_pages()
    for path, text in pages.items():
        _write(path, text)

    for kind, spec in (PROFILE.get("cv") or {}).items():
        if kind in CVS:
            (DIST / "cv").mkdir(exist_ok=True)
            shutil.copyfile(ROOT / spec["source"], DIST / "cv" / CVS[kind])

    if PROFILE.get("site_url"):
        base = PROFILE["site_url"].rstrip("/") + "/"
        urls = "".join("<url><loc>%s%s</loc></url>" % (base, "" if p == "index.html" else p) for p in pages if p != "404.html")
        _write("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">%s</urlset>' % urls)
        _write("robots.txt", "User-agent: *\nAllow: /\nSitemap: %ssitemap.xml\n" % base)

    print("Built %d pages into %s" % (len(pages), DIST))
    for kind in ("academic", "professional"):
        if kind not in CVS:
            print("  note: %s CV link is hidden (no file set)" % kind)
    for todo in PROFILE.get("todo", []):
        print("  TODO " + todo)
