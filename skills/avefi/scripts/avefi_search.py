#!/usr/bin/env python3
"""
AVefi search & exact-title matching helper.

Works in environments with direct network access to www.av-efi.net.
If your sandbox cannot resolve av-efi.net, run the equivalent fetch()
from a browser tab on https://www.av-efi.net instead (see SKILL.md).

Usage:
    python3 avefi_search.py "Professor Mamlock"
    python3 avefi_search.py --index works --hits 20 "Tamango"
    python3 avefi_search.py --match "Alarm im Zirkus"   # exact-title check
"""
import argparse, json, sys, unicodedata, urllib.request

ENDPOINT = "https://www.av-efi.net/rest/v1/frontend/search"


def search(query, index="works", hits_per_page=20, page=0, facet_filters=None):
    params = {"query": query, "hitsPerPage": hits_per_page, "page": page}
    if facet_filters:
        params["facetFilters"] = facet_filters
    body = [{"indexName": index, "params": params}]
    req = urllib.request.Request(
        ENDPOINT, data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)["results"][0]


def title_of(hit):
    rec = hit.get("has_record", {}) or {}
    pt = (rec.get("has_primary_title") or {}).get("has_name")
    alts = [a.get("has_name") for a in (rec.get("has_alternative_title") or []) if a.get("has_name")]
    return pt, alts


def norm(s):
    s = (s or "").lower().replace("ß", "ss")
    s = "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")
    for ch in '.,:;!?"\'`´’()[]-–—…':
        s = s.replace(ch, " ")
    return " ".join(s.split())


def simplify(hit):
    pt, alts = title_of(hit)
    return {
        "title": pt, "alt_titles": alts,
        "year": (hit.get("years") or [None])[0],
        "objectID": hit.get("objectID"),
        "handle": hit.get("handle"),
        "url": hit.get("url"),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("query")
    ap.add_argument("--index", default="works", choices=["works", "manifestations", "items"])
    ap.add_argument("--hits", type=int, default=20)
    ap.add_argument("--match", action="store_true",
                    help="only report an exact normalized title match")
    args = ap.parse_args()

    res = search(args.query, index=args.index, hits_per_page=args.hits)

    if args.match:
        target = norm(args.query)
        for h in res.get("hits", []):
            pt, alts = title_of(h)
            if any(norm(t) == target for t in [pt, *alts] if t):
                print(json.dumps({"match": True, **simplify(h)}, ensure_ascii=False, indent=2))
                return
        print(json.dumps({"match": False, "nbHits": res.get("nbHits", 0)}, ensure_ascii=False))
        return

    print(json.dumps({
        "nbHits": res.get("nbHits"),
        "nbWorks": res.get("nbWorks"),
        "hits": [simplify(h) for h in res.get("hits", [])],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
