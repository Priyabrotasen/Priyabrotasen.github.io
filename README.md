# Priyabrota Sen: personal website

A static academic and professional portfolio. No Node, no dependencies: one Python script
turns the JSON files in `content/` into a finished site in `dist/`.

## Build and preview

```
py build.py
py -m http.server 8000 -d dist
```

Then open http://localhost:8000. (Use `python` instead of `py` on macOS/Linux.)
Run `py build.py` again after every content change. It also prints the open TODO list.

## How the code is organised

The site is one scrolling homepage (sidebar + sections) plus a detail page per project.

| Path | What it is |
| --- | --- |
| `content/site.json` | **The ordered list of homepage sections.** Reorder, hide, or add sections here |
| `content/profile.json` | Name, title, bio, links, photo, CV files, headline numbers, skills, awards, service |
| `content/news.json` | News items |
| `content/publications.json` | Every paper: title, authors, venue, status, links |
| `content/projects.json` | Research, industry, and independent projects (each gets its own page) |
| `content/experience.json`, `education.json`, `research.json` | Timeline entries and research text |
| `sitegen/sections/` | **One small Python file per homepage section** |
| `sitegen/components.py` | Shared pieces: publication card, project card, timeline row |
| `sitegen/layout.py` | Page shell: top nav, sidebar, footer |
| `sitegen/pages.py` | Which pages get written (home, project pages, 404) |
| `sitegen/html.py` | Escaping, `[link](url)` / `**bold**` formatting, icons |
| `assets/css/` | Stylesheets, bundled in filename order. `00-tokens.css` holds colours, fonts, sizes |
| `assets/site.js` | Theme toggle, nav highlighting, filters, copy buttons |
| `dist/` | Generated output. Do not edit by hand |

## Improving the site step by step

Most changes touch one file.

- **Change text or add an entry:** edit the matching file in `content/`. No code changes.
- **Reorder or hide a section:** move its line in `content/site.json`, or add `"enabled": false`.
- **Add a new section** (for example Talks or Teaching):
  1. Create `sitegen/sections/talks.py` with one function, `render(root)`, that returns HTML
     (or `""` to hide the section when there is nothing to show). Copy `awards.py` as a starting point.
  2. Add `{ "module": "talks", "id": "talks", "nav": "Talks", "title": "Invited Talks" }` to `content/site.json`.
  3. If it needs its own styling, add rules at the bottom of `assets/css/40-sections.css`.
- **Change colours or fonts:** edit `assets/css/00-tokens.css`.
- **Change how every publication or project card looks:** edit one function in `sitegen/components.py`.
- **Add a new page:** write a function in `sitegen/pages.py` and register it in `all_pages()`.
- **Add a sidebar link type:** add it to `profile_links()` in `sitegen/layout.py` and an icon in `sitegen/html.py`.

## Common content edits

- **Add a publication:** copy an object in `publications.json`. `status` is `under-review`,
  `accepted`, or `published`; `type` is `journal`, `conference`, `workshop`, `preprint`, or `chapter`.
  Filters and BibTeX update automatically. Links set to `null` are hidden.
- **Add news:** add `{ "date": "Dec 2026", "text": "..." }` at the top of `news.json`.
- **Add a project:** append an object to `projects.json`. `"category": "independent"` makes an
  "Independent projects" group appear.
- **Add your photo:** put it in `assets/` and set `"photo": "assets/portrait.jpg"` in `profile.json`.
- **Add a highlighted note** (for example "open to internships"): set `callout` in `profile.json`.
- **Hide submission venues:** set `"show_venue_for_under_review": false` in `profile.json`.

## Deploy

The site is plain static files with relative links, so any static host works.

- **GitHub Pages:** push this folder to a GitHub repository, then in
  Settings → Pages set Source to "GitHub Actions". The included workflow
  (`.github/workflows/deploy.yml`) builds and publishes on every push to `main`.
- **Netlify / Cloudflare Pages / Vercel:** build command `python build.py`, output directory `dist`.
- **University web space:** run the build and upload the contents of `dist/`.

After you know the final address, set `site_url` in `profile.json` so the build also
writes `sitemap.xml`, `robots.txt`, and canonical URLs.

## CV downloads

The CV links are currently hidden, and the original PDFs are kept out of the repository
(see `.gitignore`) because they contain phone numbers and referee contact details.
To publish a CV, save a web-safe PDF in the project root under a new filename, set
`cv.academic.source` or `cv.professional.source` in `profile.json` to that filename, and rebuild.
