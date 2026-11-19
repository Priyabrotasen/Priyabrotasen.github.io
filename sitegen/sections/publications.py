"""Publications: filterable list (year, category, status) with BibTeX for each entry."""
from ..components import STATUS_LABELS, TYPE_LABELS, publication_card
from ..content import PROFILE, PUBS
from ..html import e


def _filter(name, label, options):
    """A row of filter buttons. Hidden when there is only one option to choose."""
    if len(options) < 2:
        return ""
    btns = ['<button type="button" class="chip" data-value="" aria-pressed="true">All</button>']
    for value, text, count in options:
        btns.append('<button type="button" class="chip" data-value="%s" aria-pressed="false">%s <span>%d</span></button>'
                    % (e(value), e(text), count))
    return '<div class="filter-group" role="group" aria-label="Filter by %s" data-filter="%s"><span class="filter-label">%s</span>%s</div>' % (
        e(label.lower()), e(name), e(label), "".join(btns))


def render(root):
    if not PUBS:
        return ""
    count = lambda key, val: sum(1 for p in PUBS if p[key] == val)
    years = sorted({p["year"] for p in PUBS}, reverse=True)
    filters = (
        _filter("year", "Year", [(y, y, count("year", y)) for y in years])
        + _filter("type", "Category", [(t, TYPE_LABELS[t], count("type", t)) for t in TYPE_LABELS if count("type", t)])
        + _filter("status", "Status", [(s, STATUS_LABELS[s], count("status", s)) for s in STATUS_LABELS if count("status", s)])
    )
    note = ""
    scholar = (PROFILE.get("links") or {}).get("scholar")
    if scholar:
        note = '<p class="section-intro">Also on <a href="%s" target="_blank" rel="noopener">Google Scholar</a>.</p>' % e(scholar)
    cards = "".join(publication_card(p, root) for p in PUBS)
    return (
        '%s<div class="filters" id="pub-filters">%s</div>'
        '<p class="result-count" id="pub-count" aria-live="polite">Showing %d of %d</p>'
        '<div class="card-list publications-list" id="pub-list">%s</div>'
        '<p class="empty" id="pub-empty" hidden>No publications match these filters. '
        '<button type="button" class="link-button" id="pub-reset">Clear filters</button></p>'
    ) % (note, filters, len(PUBS), len(PUBS), cards)
