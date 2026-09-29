#!/usr/bin/env python3
"""
check_ref.py - verify that references exist and fetch what they actually say.

Accepts DOIs, ISBNs and URLs (auto-detected) and returns metadata so the claim
can be compared against the real source:
  DOI  -> Crossref (title, authors, container, year, type)   [falls back to doi.org]
  ISBN -> Open Library (title, authors, publisher, year)
  URL  -> HTTP status, final URL, <title>, and Internet Archive snapshot if dead

Usage:
  python3 check_ref.py 10.1038/nature14539 978-3-16-148410-0 https://example.org/x
  python3 check_ref.py --file refs.txt --json
Set CROSSREF_MAILTO to join Crossref's polite pool (optional, not a secret).
"""
import argparse, html, json, os, re, sys, urllib.error, urllib.parse, urllib.request

UA = f"citation-checker-skill/1.0 (mailto:{os.environ.get('CROSSREF_MAILTO', 'unknown')})"
DOI_RE = re.compile(r"(10\.\d{4,9}/[^\s\"<>]+)", re.I)


def get(url, accept="application/json", timeout=20):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": accept})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.status, r.geturl(), r.read()


def isbn_ok(s):
    d = re.sub(r"[^0-9Xx]", "", s)
    if len(d) == 10:
        return sum((10 - i) * (10 if c in "Xx" else int(c)) for i, c in enumerate(d)) % 11 == 0
    if len(d) == 13 and d.isdigit():
        return sum(int(c) * (1 if i % 2 == 0 else 3) for i, c in enumerate(d)) % 10 == 0
    return False


def check_doi(doi):
    doi = doi.rstrip(".,;)")
    try:
        _, _, body = get("https://api.crossref.org/works/" + urllib.parse.quote(doi))
        m = json.loads(body)["message"]
        return {"type": "doi", "id": doi, "exists": True, "source": "crossref",
                "title": (m.get("title") or [None])[0],
                "authors": [f"{a.get('given', '')} {a.get('family', '')}".strip() for a in m.get("author", [])][:10],
                "container": (m.get("container-title") or [None])[0],
                "year": (m.get("issued", {}).get("date-parts") or [[None]])[0][0],
                "publisher": m.get("publisher"), "kind": m.get("type"), "url": m.get("URL")}
    except urllib.error.HTTPError as e:
        if e.code != 404:
            return {"type": "doi", "id": doi, "exists": None, "error": f"crossref HTTP {e.code}"}
    try:  # not in Crossref (e.g. DataCite DOIs): does doi.org resolve it?
        status, final, _ = get("https://doi.org/" + doi, accept="text/html")
        return {"type": "doi", "id": doi, "exists": True, "source": "doi.org", "resolves_to": final}
    except urllib.error.HTTPError as e:
        return {"type": "doi", "id": doi, "exists": False, "error": f"doi.org HTTP {e.code}"}


def check_isbn(raw):
    isbn = re.sub(r"[^0-9Xx]", "", raw)
    res = {"type": "isbn", "id": isbn, "checksum_valid": isbn_ok(isbn)}
    try:
        _, _, body = get(f"https://openlibrary.org/search.json?isbn={isbn}"
                         "&fields=title,author_name,publisher,first_publish_year,number_of_pages_median,key&limit=1")
        docs = json.loads(body).get("docs", [])
    except Exception as e:
        return {**res, "exists": None, "error": str(e)}
    if not docs:
        return {**res, "exists": False, "note": "not in Open Library (does not prove non-existence; try DNB/WorldCat)"}
    d = docs[0]
    return {**res, "exists": True, "source": "openlibrary", "title": d.get("title"),
            "authors": d.get("author_name", []), "publisher": d.get("publisher", [])[:5],
            "year": d.get("first_publish_year"), "pages": d.get("number_of_pages_median"),
            "url": "https://openlibrary.org" + d["key"] if d.get("key") else None}


def check_url(url):
    res = {"type": "url", "id": url}
    try:
        status, final, body = get(url, accept="text/html,*/*", timeout=25)
        t = re.search(rb"<title[^>]*>(.*?)</title>", body[:200000], re.I | re.S)
        res.update(exists=True, status=status, final_url=final,
                   title=html.unescape(t.group(1).decode("utf-8", "ignore").strip()) if t else None,
                   looks_like_search_page=bool(re.search(r"[?&](q|query|search|s)=", final)))
        if "utm_source=chatgpt.com" in url:
            res["warning"] = "chatbot tracking parameter in URL"
        return res
    except urllib.error.HTTPError as e:
        res.update(exists=e.code in (401, 403, 429), status=e.code)
    except Exception as e:
        res.update(exists=False, error=str(e))
    try:
        _, _, body = get("https://archive.org/wayback/available?url=" + urllib.parse.quote(url, safe=""))
        snap = json.loads(body).get("archived_snapshots", {}).get("closest")
        if snap:
            res["archived"] = {"url": snap["url"], "timestamp": snap["timestamp"]}
    except Exception:
        pass
    return res


def detect(ref):
    ref = ref.strip()
    m = DOI_RE.search(ref)
    if m:
        return check_doi(m.group(1))
    if re.match(r"^https?://", ref):
        return check_url(ref)
    if re.fullmatch(r"(?:ISBN[:\s-]*)?[\d\- Xx]{10,17}", ref, re.I):
        return check_isbn(ref)
    return {"type": "unknown", "id": ref, "note": "not a DOI, ISBN or URL; search the title manually"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("refs", nargs="*")
    ap.add_argument("--file")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    refs = list(a.refs) + ([l for l in open(a.file, encoding="utf-8").read().splitlines() if l.strip()] if a.file else [])
    results = [detect(r) for r in refs]
    if a.json:
        print(json.dumps(results, indent=2, ensure_ascii=False)); return
    for r in results:
        flag = {True: "OK  ", False: "DEAD", None: "??  "}.get(r.get("exists"), "??  ")
        print(f"{flag} [{r['type']}] {r['id']}")
        for k in ("title", "authors", "container", "publisher", "year", "final_url", "resolves_to", "status", "archived", "warning", "note", "error"):
            if r.get(k):
                print(f"       {k}: {r[k]}")


if __name__ == "__main__":
    main()
