#!/usr/bin/env python3
"""
gnd.py - search and resolve GND authority records via lobid-gnd (lobid.org).

The GND (Gemeinsame Normdatei) is the authority file of the German National
Library for persons, corporate bodies, places, subjects, works and events.
lobid-gnd is a free, keyless JSON API run by hbz.

Usage:
  python3 gnd.py search "Albrecht Dürer" --type Person
  python3 gnd.py search "Kinemathek" --type CorporateBody --size 5
  python3 gnd.py get 11852786X                       # full record, condensed
  python3 gnd.py get 11852786X --raw                 # full JSON
  python3 gnd.py match "Fritz Lang" --born 1890      # best candidates for reconciliation
Types: Person, CorporateBody, PlaceOrGeographicName, SubjectHeading, Work,
       ConferenceOrEvent, Family
"""
import argparse, json, re, sys, urllib.parse, urllib.request

BASE = "https://lobid.org/gnd"
UA = "gnd-lookup-skill/1.0"


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def labels(v):
    return [x.get("label") for x in (v or []) if isinstance(x, dict) and x.get("label")]


def links(rec):
    out = {}
    for s in rec.get("sameAs", []) or []:
        abbr = (s.get("collection") or {}).get("abbr")
        if abbr in ("WIKIDATA", "VIAF", "LC", "ISNI", "ORCID", "DNB") or "wikidata.org" in s.get("id", ""):
            out[abbr or "WIKIDATA"] = s.get("id")
    return out


def condense(rec):
    return {
        "gnd": rec.get("gndIdentifier"),
        "uri": rec.get("id"),
        "name": rec.get("preferredName"),
        "types": [t for t in rec.get("type", []) if t != "AuthorityResource"],
        "born": (rec.get("dateOfBirth") or [None])[0],
        "died": (rec.get("dateOfDeath") or [None])[0],
        "place_of_birth": labels(rec.get("placeOfBirth")),
        "professions": list(dict.fromkeys(labels(rec.get("professionOrOccupation"))))[:6],
        "info": (rec.get("biographicalOrHistoricalInformation") or [None])[0],
        "variants": (rec.get("variantName") or [])[:6],
        "links": links(rec),
    }


def search(q, typ=None, size=10, extra_filter=None):
    params = {"q": q, "format": "json", "size": size}
    filters = [f"type:{typ}"] if typ else []
    if extra_filter:
        filters.append(extra_filter)
    if filters:
        params["filter"] = " AND ".join(filters)
    d = fetch(f"{BASE}/search?{urllib.parse.urlencode(params)}")
    return d.get("totalItems", 0), [condense(m) for m in d.get("member", [])]


def get(gnd_id):
    gnd_id = gnd_id.rsplit("/", 1)[-1]
    return fetch(f"{BASE}/{urllib.parse.quote(gnd_id)}.json")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("search"); s.add_argument("q"); s.add_argument("--type"); s.add_argument("--size", type=int, default=10)
    g = sub.add_parser("get"); g.add_argument("id"); g.add_argument("--raw", action="store_true")
    m = sub.add_parser("match"); m.add_argument("name"); m.add_argument("--born"); m.add_argument("--died")
    m.add_argument("--type", default="Person")
    a = ap.parse_args()

    if a.cmd == "search":
        total, hits = search(a.q, a.type, a.size)
        print(json.dumps({"total": total, "hits": hits}, indent=2, ensure_ascii=False))
    elif a.cmd == "get":
        rec = get(a.id)
        print(json.dumps(rec if a.raw else condense(rec), indent=2, ensure_ascii=False))
    elif a.cmd == "match":
        total, hits = search(a.name, a.type, 20)
        def score(h):
            sc = 0
            if a.born and (h["born"] or "").startswith(a.born): sc += 2
            if a.died and (h["died"] or "").startswith(a.died): sc += 2
            if re.sub(r"\W", "", h["name"] or "").lower() in (re.sub(r"\W", "", a.name).lower(),
               re.sub(r"\W", "", ", ".join(reversed(a.name.rsplit(" ", 1)))).lower()): sc += 1
            return sc
        ranked = sorted(hits, key=score, reverse=True)[:5]
        print(json.dumps({"total": total, "candidates": [{**h, "score": score(h)} for h in ranked]}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
