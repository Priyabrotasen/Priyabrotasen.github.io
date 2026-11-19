"""Loads content/*.json once and exposes it to the rest of the generator."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"
ASSETS = ROOT / "assets"
DIST = ROOT / "dist"


def load(name):
    return json.loads((CONTENT / (name + ".json")).read_text(encoding="utf-8"))


SITE = load("site")
PROFILE = load("profile")
NEWS = load("news")["items"]
PUBS = load("publications")["items"]
PROJECTS = load("projects")["items"]
EXPERIENCE = load("experience")["items"]
EDUCATION = load("education")
RESEARCH = load("research")

PUB_BY_ID = {p["id"]: p for p in PUBS}
PROJECT_BY_SLUG = {p["slug"]: p for p in PROJECTS}


def _cv_files():
    """{kind: published filename} for each CV whose source file exists."""
    out = {}
    for kind, spec in (PROFILE.get("cv") or {}).items():
        if spec and spec.get("source") and (ROOT / spec["source"]).is_file():
            out[kind] = spec.get("publish_as") or Path(spec["source"]).name
    return out


CVS = _cv_files()
