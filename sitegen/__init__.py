"""Static site generator for the personal site.

Module map (each file is small and independent):

    content.py      loads content/*.json
    html.py         escaping, inline formatting, icons, small HTML helpers
    components.py   reusable pieces: publication card, project card, timeline item
    layout.py       page shell: top nav, sidebar, footer
    sections/       one module per homepage section (ordered by content/site.json)
    pages.py        the pages that get written: home, project detail pages, 404
    build.py        writes everything to dist/
"""
