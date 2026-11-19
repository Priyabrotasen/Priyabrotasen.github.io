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

## Where things live

| Path | What it is |
| --- | --- |
| `content/profile.json` | Name, title, bios, links, CV files, homepage metrics, skills, awards |
| `content/publications.json` | Every paper: title, authors, venue, status, links |
| `content/projects.json` | Research, industry, and independent projects (each gets its own page) |
| `content/experience.json` | Timeline of roles |
| `content/education.json` | Degrees, coursework, online courses |
| `content/research.json` | Text for the Research page |
| `assets/` | `styles.css`, `site.js`, favicon, and any images you add |
| `build.py` | Templates and the generator |
| `dist/` | Generated output. Do not edit by hand |

## Common edits

- **Add a publication:** copy an object in `publications.json`. `status` is one of
  `under-review`, `accepted`, `published`; `type` is `journal`, `conference`, `workshop`,
  `preprint`, or `chapter`. Filters, BibTeX, and counts update automatically.
- **A paper is accepted or published:** change its `status`, and add `doi`, `url`, `pdf`,
  `arxiv`, or `code` as they become available. Links set to `null` are hidden.
- **Add a project:** append an object to `projects.json`. Use `"category": "independent"`
  for personal projects and that tab appears on the Projects page.
- **Add your photo:** put it in `assets/` and set `"photo": "assets/portrait.jpg"` in `profile.json`.
- **Add GitHub / ORCID:** set the URL in `profile.json` under `links`.
- **Hide submission venues:** set `"show_venue_for_under_review": false` in `profile.json`
  to show papers under review as just "Under review".

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
