#!/usr/bin/env python3
"""
update_scholar.py — refresh scholar_data.json from Google Scholar.

What it updates automatically:
  - citations (total), h-index, i10-index
  - rolling "since" citations (last 5 calendar years)
  - citations_by_year histogram
  - selected_works: per-paper citation counts for the "Selected works"
    cards on the homepage (matched to Scholar by title)

What it deliberately preserves (not on Scholar):
  - funding, patents, graduates, publications headline, publications_by_year
  - the "over 90 publications / 3,600 citations" narrative line (hand-written)

Design notes:
  - Google Scholar has no public API and actively blocks scrapers. This uses
    the `scholarly` package, which works most of the time but WILL fail
    intermittently. On any failure the script leaves scholar_data.json
    untouched and exits 0, so the site keeps showing the last good values.
  - selected_works values are only overwritten when a confident title match
    is found; otherwise the previous (hand-set) value is preserved, so a
    bad scrape can never blank out a card.
  - Run from anywhere; paths are resolved relative to this file.

Usage:   python3 scripts/update_scholar.py
Requires: pip install scholarly
"""
import json, os, re, sys, datetime

SCHOLAR_ID = "gHTr6DoAAAAJ"   # M. Asif Khan (https://bit.ly/khanam)

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.abspath(os.path.join(HERE, "..", "scholar_data.json"))

# Homepage "Selected works" cards -> distinctive Scholar title fragment.
# When several Scholar entries match a fragment (e.g. a paper + its erratum),
# the one with the most citations wins.
SELECTED_WORKS = {
    "venom-tft":           "three finger toxins",
    "wes-bigdata":         "whole exome sequencing and big data",
    "antimic":             "antimic a database of antimicrobial",
    "flua-conserved":      "evolutionarily conserved protein sequences of influenza",
    "dengue-cytokine":     "cytokine expression profile of dengue",
    "encyclopedia":        "encyclopedia of bioinformatics and computational biology",
    "multipred":           "multipred",
    "dengue-conservation": "conservation and variability of dengue virus proteins",
}


def norm(s):
    return re.sub(r"[^a-z0-9]+", " ", (s or "").lower()).strip()


def load_existing():
    with open(DATA, encoding="utf-8") as f:
        return json.load(f)


def fetch():
    from scholarly import scholarly
    author = scholarly.search_author_id(SCHOLAR_ID)
    author = scholarly.fill(author, sections=["indices", "counts", "publications"])
    return author


def main():
    data = load_existing()
    try:
        a = fetch()
    except Exception as e:
        print(f"[warn] Scholar fetch failed ({e}); leaving scholar_data.json unchanged.")
        return 0

    m = data.setdefault("metrics", {})
    now = datetime.date.today()

    # Headline indices
    if a.get("citedby") is not None:
        m["citations"] = int(a["citedby"])
    if a.get("citedby5y") is not None:
        m["citations_since_2021"] = int(a["citedby5y"])   # rolling last 5y
        m["citations_since_year"] = now.year - 5
    if a.get("hindex") is not None:
        m["hindex"] = int(a["hindex"])
    if a.get("i10index") is not None:
        m["i10"] = int(a["i10index"])

    # Citations-by-year histogram
    cpy = a.get("cites_per_year") or {}
    if cpy:
        years = sorted(int(y) for y in cpy.keys())
        labels, vals = [], []
        for y in years:
            label = f"{y}*" if y == now.year else str(y)   # mark partial current year
            labels.append(label)
            vals.append(int(cpy[y]))
        data["citations_by_year"] = {"years": labels, "values": vals}

    # Per-paper citations for the "Selected works" cards.
    # Preserve prior values; only overwrite on a confident title match.
    pubs = a.get("publications") or []
    title_cites = []
    for p in pubs:
        t = norm((p.get("bib") or {}).get("title", ""))
        c = p.get("num_citations")
        if t and c is not None:
            title_cites.append((t, int(c)))
    sw = data.setdefault("selected_works", {})
    matched = 0
    for key, frag in SELECTED_WORKS.items():
        f = norm(frag)
        cands = [c for (t, c) in title_cites if f in t]
        if cands:
            sw[key] = max(cands)
            matched += 1

    data["as_of"] = now.isoformat()
    data["source"] = "Google Scholar (https://bit.ly/khanam)"

    with open(DATA, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"[ok] Updated {os.path.basename(DATA)} — "
          f"{m.get('citations')} citations, h-index {m.get('hindex')}, "
          f"i10 {m.get('i10')}, {matched}/{len(SELECTED_WORKS)} selected works, "
          f"as of {data['as_of']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
