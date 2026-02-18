#!/usr/bin/env python3
"""Fetch Daily Papers from Hugging Face (huggingface.co/papers) and write data/hf-papers.json."""

import json
import os
import re
from datetime import datetime
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
# Main site is JS-rendered; mirror returns server-rendered HTML we can parse
HF_PAPERS_URL = "https://api-inference.hf-mirror.com/papers"
HF_BASE = "https://huggingface.co"
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; PaperSharing/1.0)"}
ARXIV_ID_RE = re.compile(r"/papers/(\d{4}\.\d{4,5})")


def _parse_by_regex(html: str):
    """Fallback: extract title and paper id from raw HTML / markdown-like content."""
    items = []
    # Match ### Title followed (eventually) by /papers/NNNN.NNNNN
    title_re = re.compile(r"###\s+(.+?)(?=\n|$)", re.DOTALL)
    id_re = re.compile(r"/papers/(\d{4}\.\d{4,5})")
    pos = 0
    while True:
        m = title_re.search(html, pos)
        if not m:
            break
        title = m.group(1).strip().replace("\n", " ")
        if len(title) < 10 or title in ("Daily", "Weekly", "Monthly"):
            pos = m.end()
            continue
        # Look for paper id in next ~500 chars
        chunk = html[m.end() : m.end() + 500]
        id_m = id_re.search(chunk)
        if id_m:
            paper_id = id_m.group(1)
            link = f"{HF_BASE}/papers/{paper_id}"
            items.append({
                "id": paper_id,
                "title": title,
                "authors": "",
                "abstract": "",
                "link": link,
                "source": "hf",
            })
        pos = m.end()
    return items


def fetch_hf_papers():
    resp = requests.get(HF_PAPERS_URL, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    html = resp.text
    soup = BeautifulSoup(html, "lxml")
    items = []
    for a in soup.select('a[href*="/papers/"]'):
        href = a.get("href", "")
        m = ARXIV_ID_RE.search(href)
        if not m:
            continue
        paper_id = m.group(1)
        if href.startswith("/"):
            link = HF_BASE + href.split("?")[0].split("#")[0]
        else:
            link = href.split("?")[0].split("#")[0]
            if not link.startswith("http"):
                link = urljoin(HF_BASE, link)
        h3 = a.find_previous("h3")
        if not h3:
            continue
        title = (h3.get_text() or "").strip()
        if not title or len(title) < 10 or title in ("Daily", "Weekly", "Monthly", "Subscribe", "Previous"):
            continue
        items.append({
            "id": paper_id,
            "title": title,
            "authors": "",
            "abstract": "",
            "link": link,
            "source": "hf",
        })
    if not items:
        items = _parse_by_regex(html)
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
