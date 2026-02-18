#!/usr/bin/env python3
"""Fetch recent ML papers from arXiv (cs.LG, cs.CL, cs.AI, stat.ML) and write data/arxiv.json."""

import json
import os
import xml.etree.ElementTree as ET
from datetime import datetime
from urllib.parse import urlencode, urljoin

import requests

# 分类与数量
CATEGORIES = ["cs.LG", "cs.CL", "cs.AI", "stat.ML"]
MAX_RESULTS = 80
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
ARXiv_API = "http://export.arxiv.org/api/query"


def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    query = " OR ".join(f"cat:{c}" for c in CATEGORIES)
    params = {"search_query": query, "sortBy": "submittedDate", "max_results": MAX_RESULTS}
    resp = requests.get(ARXiv_API, params=params, timeout=30)
    resp.raise_for_status()
    root = ET.fromstring(resp.content)
    ns = {"atom": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}
    items = []
    seen = set()
    for entry in root.findall("atom:entry", ns):
        id_el = entry.find("atom:id", ns)
        if id_el is None or id_el.text is None:
            continue
        # id is like http://arxiv.org/abs/2401.12345
        raw_id = id_el.text.strip()
        short_id = raw_id.split("/abs/")[-1].rstrip("/")
        if short_id in seen:
            continue
        seen.add(short_id)
        title_el = entry.find("atom:title", ns)
        title = (title_el.text or "").replace("\n", " ").strip()
        summary_el = entry.find("atom:summary", ns)
        abstract = (summary_el.text or "").replace("\n", " ").strip()
        authors = []
        for author in entry.findall("atom:author", ns):
            name = author.find("atom:name", ns)
            if name is not None and name.text:
                authors.append(name.text.strip())
        published_el = entry.find("atom:published", ns)
        published = published_el.text if published_el is not None and published_el.text else ""
        link = f"https://arxiv.org/abs/{short_id}"
        items.append({
            "id": short_id,
            "title": title,
            "authors": ", ".join(authors),
            "abstract": abstract,
            "link": link,
            "published": published,
            "source": "arxiv",
        })
    out_path = os.path.join(DATA_DIR, "arxiv.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({"updated": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"), "papers": items}, f, ensure_ascii=False, indent=2)
    print(f"Wrote {len(items)} papers to {out_path}")


if __name__ == "__main__":
    main()
