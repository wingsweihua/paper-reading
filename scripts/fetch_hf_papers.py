#!/usr/bin/env python3
"""Fetch Daily Papers from Hugging Face (huggingface.co/papers) and write data/hf-papers.json."""

import json
import os
import re
from datetime import datetime

import requests
from bs4 import BeautifulSoup

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
HF_PAPERS_URL = "https://huggingface.co/papers"
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; PaperSharing/1.0)"}


def fetch_hf_papers():
    resp = requests.get(HF_PAPERS_URL, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "lxml")
    items = []
    # Links to paper pages: /papers/2602.14111
    for a in soup.select('a[href*="/papers/"]'):
        href = a.get("href", "")
        if not href or href.count("/papers/") != 1:
            continue
        parts = href.strip("/").split("/papers/")
        if len(parts) != 2:
            continue
        paper_id = parts[1].split("?")[0].strip("/").split("#")[0]
        if not paper_id or not re.match(r"[\w.-]+", paper_id):
            continue
        if href.startswith("/"):
            link = "https://huggingface.co" + href.split("?")[0].split("#")[0]
        else:
            link = href.split("?")[0].split("#")[0]
        title = (a.get_text() or "").strip()
        if not title or len(title) < 5:
            continue
        if title.isdigit() or title in ("Daily", "Weekly", "Monthly", "Subscribe", "Previous"):
            continue
        items.append({
            "id": paper_id,
            "title": title,
            "authors": "",
            "abstract": "",
            "link": link,
            "source": "hf",
        })
    seen = set()
    out = []
    for p in items:
        if p["link"] in seen:
            continue
        if len(p["title"]) < 10:
            continue
        seen.add(p["link"])
        out.append(p)
    return out[:60]


def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    try:
        papers = fetch_hf_papers()
    except Exception as e:
        print(f"HF papers fetch failed: {e}, writing empty list")
        papers = []
    out_path = os.path.join(DATA_DIR, "hf-papers.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(
            {"updated": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"), "papers": papers},
            f, ensure_ascii=False, indent=2,
        )
    print(f"Wrote {len(papers)} papers to {out_path}")


if __name__ == "__main__":
    main()
