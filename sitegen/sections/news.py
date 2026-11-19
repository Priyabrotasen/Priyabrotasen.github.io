"""News: dated one-liners from content/news.json. The list scrolls once it gets long."""
from ..content import NEWS
from ..html import ICONS, e, rich

VISIBLE = 6  # items shown before the list becomes scrollable


def render(root):
    if not NEWS:
        return ""
    rows = "".join(
        '<li><span class="news-date">%s</span><span>%s</span></li>' % (e(n["date"]), rich(n["text"], root)) for n in NEWS
    )
    scroll = len(NEWS) > VISIBLE
    hint = '<p class="scroll-hint">%s Scroll for more</p>' % ICONS["arrow"] if scroll else ""
    return '<div class="news-scroll%s"%s><ul class="news-list">%s</ul></div>%s' % (
        " is-scrollable" if scroll else "", ' tabindex="0"' if scroll else "", rows, hint)
