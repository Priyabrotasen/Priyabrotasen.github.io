#!/usr/bin/env python3
"""Build the site:   py build.py      Preview:   py -m http.server 8000 -d dist

All the logic lives in the sitegen/ package; see sitegen/__init__.py for a map.
"""
from sitegen.build import main

if __name__ == "__main__":
    main()
