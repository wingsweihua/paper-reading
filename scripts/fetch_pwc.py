#!/usr/bin/env python3
"""Fetch latest/trending papers from Papers With Code and write data/pwc.json."""

import json
import os
import re
from datetime import datetime

import requests
from bs4 import BeautifulSoup

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
PWC_URL = "https://paperswithcode.com/latest"
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; PaperSharing/1.0)"}


def fetch_pwc():
    resp = requests.get(PWC_URL, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "lxml")
    items = []
    # Papers are often in links like /paper/slug or /papers/arxiv-id
    for a in soup.select('a[href*="/paper"]'):
        href = a.get("href", "")
        if not href or "/paper/" not in href:
            continue
        if href.startswith("/"):
            link = "https://paperswithcode.com" + href
        else:
            link = href
        title = (a.get_text() or "").strip()
        if not title or len(title) < 10 or title in ("Paper", "Papers", "Subscribe"):
            continue
        items.append({
            "id": link.split("/paper/")[-1].split("?")[0].strip("/") or link,
            "title": title,
            "authors": "",
            "abstract": "",
            "link": link.split("?")[0],
            "source": "pwc",
        })
    # Dedupe by link
    seen = set()
    out = []
    for p in items:
        if p["link"] in seen:
            continue
        seen.add(p["link"])
        out.append(p)
    return out[:60]


def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    try:
        papers = fetch_pwc()
    except Exception as e:
        print(f"PWC fetch failed: {e}, writing empty list")
        papers = []
    out_path = os.path.join(DATA_DIR, "pwc.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(
            {"updated": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"), "papers": papers},
            f, ensure_ascii=False, indent=2,
        )
    print(f"Wrote {len(papers)} papers to {out_path}")


if __name__ == "__main__":
    main()
