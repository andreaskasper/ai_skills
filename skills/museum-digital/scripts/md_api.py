#!/usr/bin/env python3
"""
md_api.py - small, robust client for the museum-digital frontend API.

museum-digital is multi-instance: EVERY instance has its OWN API server on its
own host (e.g. nat.museum-digital.de, berlin.museum-digital.de, ...).
The endpoint structure is the same on all instances.

Default instance (if none given or unclear): nat.museum-digital.de,
the national aggregator that merges all regional holdings.

The API is READ-ONLY and needs no login. There are no write endpoints.

CLI usage:
  python md_api.py home [--instance berlin]
  python md_api.py search "fulltext:Dürer" [--instance nat] [--limit 10] [--offset 0] [--lang de]
  python md_api.py object 1857870 [--instance nat] [--lang de]
  python md_api.py negotiate "berlin vase"            # plain text -> query string
  python md_api.py institutions "Kunsthalle Bremen"
  python md_api.py institution 751
  python md_api.py collections 751                    # collections of a museum
  python md_api.py facets "fulltext:vase"             # facets for a search
  python md_api.py per-museum "fulltext:vase"         # hits per museum (+ geo)
  python md_api.py export "place:61" --limit 100 --offset 0   # batch export
  python md_api.py raw /json/home                     # fetch any endpoint raw

Library usage:
  from md_api import Client
  c = Client("nat")
  hits, total = c.search_objects("fulltext:Dürer", limit=5)
  obj = c.get_object(1857870)
  url = c.image_url_from_hit(hits[0])
"""
import argparse
import json
import sys
import urllib.parse
import urllib.request

DEFAULT_INSTANCE = "nat.museum-digital.de"
TIMEOUT = 40


def resolve_instance(instance: str | None) -> str:
    """Accepts short names ('berlin'), full hosts ('berlin.museum-digital.de'),
    URLs, or None -> default aggregator. Always returns a bare host."""
    if not instance:
        return DEFAULT_INSTANCE
    instance = instance.strip().rstrip("/")
    # full URL -> extract host
    if instance.startswith("http://") or instance.startswith("https://"):
        instance = urllib.parse.urlparse(instance).netloc
    # already a host?
    if "." in instance:
        return instance
    # short name like 'berlin' / 'rlp' / 'nat'
    return f"{instance}.museum-digital.de"


class Client:
    def __init__(self, instance: str | None = None, lang: str | None = None):
        self.host = resolve_instance(instance)
        self.base = f"https://{self.host}"
        self.lang = lang  # default navlang for all calls

    # ---- low level -------------------------------------------------------
    def _url(self, path: str, params: dict | None = None) -> str:
        if not path.startswith("/"):
            path = "/" + path
        url = self.base + path
        params = {k: v for k, v in (params or {}).items() if v is not None}
        if self.lang and "navlang" not in params:
            params["navlang"] = self.lang
        if params:
            url += "?" + urllib.parse.urlencode(params)
        return url

    def get(self, path: str, params: dict | None = None):
        """GET a path and return parsed JSON (or raw text for XML endpoints).
        Note: the query for /json/objects is NOT a path segment but ?s=..."""
        url = self._url(path, params)
        req = urllib.request.Request(url, headers={
            "Accept": "application/json",
            "User-Agent": "md_api.py (museum-digital skill)",
        })
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            raw = r.read().decode("utf-8")
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            # some endpoints (oai, resolver, ?output=lido) return XML/text
            return raw

    @staticmethod
    def _enc_path(value: str) -> str:
        """URL-encode a value used as a PATH segment
        (e.g. the query in /json/search/{query_string})."""
        return urllib.parse.quote(str(value), safe="")

    # ---- high level ------------------------------------------------------
    def home(self):
        """Instance overview (counters, last_update, popular). Note: the key
        'resouces' is misspelled server-side (sic)."""
        return self.get("/json/home")

    def search_objects(self, s: str | None = None, limit: int = 20,
                       offset: int = 0, lang: str | None = None):
        """Object search. 's' is the structured query (see search-syntax.md),
        e.g. 'fulltext:Dürer', 'type:Gemälde', 'place:61 institution:751'
        (tokens separated by spaces). Returns (hits, total)."""
        data = self.get("/json/objects", {
            "s": s, "gbreitenat": limit, "startwert": offset, "navlang": lang,
        })
        hits = data if isinstance(data, list) else []
        total = hits[0].get("total") if hits else 0
        return hits, total

    def get_object(self, object_id: int, lang: str | None = None):
        return self.get(f"/json/object/{int(object_id)}", {"navlang": lang})

    def negotiate_query(self, freetext: str, base_query: str | None = None,
                        lang: str | None = None) -> str:
        """Translate plain text into a query string ('berlin' -> 'place:61'),
        optionally appended to an existing query."""
        data = self.get("/json/objects_get_query_string", {
            "s": base_query, "extendQuery": freetext, "navlang": lang,
        })
        return data.get("results", "") if isinstance(data, dict) else str(data)

    def facets(self, query: str, lang: str | None = None):
        """Facets (institutions, persinst, places, times, event_types, tags)
        for a search. 'query' is used as a path segment."""
        return self.get(f"/json/object-facet-search/{self._enc_path(query)}",
                        {"navlang": lang})

    def objects_per_museum(self, s: str, lang: str | None = None):
        """Hit count per institution plus its coordinates."""
        return self.get("/json/objects-per-museum", {"s": s, "navlang": lang})

    def institutions(self, q: str | None = None, lang: str | None = None):
        return self.get("/json/institutions", {"q": q, "navlang": lang})

    def institution(self, inst_id: int, lang: str | None = None):
        return self.get(f"/json/institution/{int(inst_id)}", {"navlang": lang})

    def collections_by_institution(self, inst_id: int, lang: str | None = None):
        """Collections of a museum; unwraps the list from {results:[...]}."""
        data = self.get(f"/json/collections_by_institution/{int(inst_id)}", {"navlang": lang})
        return data.get("results", []) if isinstance(data, dict) else data

    def collection(self, coll_id: int, lang: str | None = None):
        return self.get(f"/json/collection/{int(coll_id)}", {"navlang": lang})

    def series(self, series_id: int, lang: str | None = None):
        return self.get(f"/json/series/{int(series_id)}", {"navlang": lang})

    def general_search(self, query: str, lang: str | None = None):
        """Cross-entity search -> {results:{institutions,collections,objects}}."""
        return self.get(f"/json/search/{self._enc_path(query)}", {"navlang": lang})

    def export(self, query: str, limit: int = 100, offset: int = 0,
               lang: str | None = None):
        """Batch export of object metadata for a query (path segment)."""
        return self.get(f"/export/json/{self._enc_path(query)}", {
            "limit": limit, "offset": offset, "navlang": lang,
        })

    # ---- image URLs -------------------------------------------------------
    def image_url_from_hit(self, hit: dict) -> str | None:
        """Search hits carry a ready relative 'image' path; prefix the host."""
        rel = hit.get("image")
        if not rel:
            return None
        return f"{self.base}/{rel.lstrip('/')}"

    def image_url_from_detail(self, img: dict, subset: str) -> str | None:
        """Build the 200w thumbnail URL from /json/object/{id} -> object_images[].
        Scheme: {base}/data/{subset}/{folder}/{preview}."""
        folder = img.get("folder")
        preview = img.get("preview")
        if not (folder and preview):
            return None
        return f"{self.base}/data/{subset}/{folder}/{preview}"

    # ---- alternative outputs & standards --------------------------------
    def object_alternate(self, object_id: int, output: str):
        """Alternative object output; output in {lido, ead, MODS, TEI, BibTeX}."""
        return self.get(f"/object/{int(object_id)}", {"output": output})

    def oai(self, verb: str = "Identify", **params):
        """OAI-PMH (XML). verb e.g. Identify, ListMetadataFormats,
        ListRecords (metadataPrefix=lido|oai_dc), GetRecord."""
        return self.get("/oai", {"verb": verb, **params})


def _print(obj):
    if isinstance(obj, (dict, list)):
        print(json.dumps(obj, ensure_ascii=False, indent=2))
    else:
        print(obj)


def main(argv=None):
    # Global flags (--instance/--lang) work before AND after the subcommand
    # via a shared parent parser.
    common = argparse.ArgumentParser(add_help=False)
    # default=SUPPRESS: an omitted flag doesn't overwrite a value parsed
    # before the subcommand.
    common.add_argument("--instance", "-i", default=argparse.SUPPRESS,
                        help="instance: short name (berlin), host or URL. Default: nat (aggregator)")
    common.add_argument("--lang", "-l", default=argparse.SUPPRESS, help="navlang, e.g. de / en")

    p = argparse.ArgumentParser(description="museum-digital API client", parents=[common])
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("home", parents=[common])

    sp = sub.add_parser("search", parents=[common]); sp.add_argument("query")
    sp.add_argument("--limit", type=int, default=10); sp.add_argument("--offset", type=int, default=0)

    sp = sub.add_parser("object", parents=[common]); sp.add_argument("id", type=int)
    sp = sub.add_parser("negotiate", parents=[common]); sp.add_argument("text"); sp.add_argument("--base", default=None)
    sp = sub.add_parser("institutions", parents=[common]); sp.add_argument("query", nargs="?", default=None)
    sp = sub.add_parser("institution", parents=[common]); sp.add_argument("id", type=int)
    sp = sub.add_parser("collections", parents=[common]); sp.add_argument("institution_id", type=int)
    sp = sub.add_parser("collection", parents=[common]); sp.add_argument("id", type=int)
    sp = sub.add_parser("series", parents=[common]); sp.add_argument("id", type=int)
    sp = sub.add_parser("general", parents=[common]); sp.add_argument("query")
    sp = sub.add_parser("facets", parents=[common]); sp.add_argument("query")
    sp = sub.add_parser("per-museum", parents=[common]); sp.add_argument("query")
    sp = sub.add_parser("export", parents=[common]); sp.add_argument("query")
    sp.add_argument("--limit", type=int, default=100); sp.add_argument("--offset", type=int, default=0)
    sp = sub.add_parser("raw", parents=[common]); sp.add_argument("path")

    args = p.parse_args(argv)
    c = Client(getattr(args, "instance", None), getattr(args, "lang", None))

    if args.cmd == "home":
        _print(c.home())
    elif args.cmd == "search":
        hits, total = c.search_objects(args.query, args.limit, args.offset)
        out = [{
            "id": h.get("objekt_id"),
            "name": h.get("objekt_name"),
            "inv": h.get("objekt_inventarnr"),
            "institution": h.get("institution_name"),
            "url": f"{c.base}/object/{h.get('objekt_id')}",
            "image": c.image_url_from_hit(h),
        } for h in hits]
        _print({"instance": c.host, "total": total, "shown": len(out), "hits": out})
    elif args.cmd == "object":
        _print(c.get_object(args.id))
    elif args.cmd == "negotiate":
        _print(c.negotiate_query(args.text, args.base))
    elif args.cmd == "institutions":
        _print(c.institutions(args.query))
    elif args.cmd == "institution":
        _print(c.institution(args.id))
    elif args.cmd == "collections":
        _print(c.collections_by_institution(args.institution_id))
    elif args.cmd == "collection":
        _print(c.collection(args.id))
    elif args.cmd == "series":
        _print(c.series(args.id))
    elif args.cmd == "general":
        _print(c.general_search(args.query))
    elif args.cmd == "facets":
        _print(c.facets(args.query))
    elif args.cmd == "per-museum":
        _print(c.objects_per_museum(args.query))
    elif args.cmd == "export":
        _print(c.export(args.query, args.limit, args.offset))
    elif args.cmd == "raw":
        _print(c.get(args.path))


if __name__ == "__main__":
    try:
        main()
    except urllib.error.HTTPError as e:
        print(f"HTTP {e.code}: {e.reason} ({e.url})", file=sys.stderr); sys.exit(1)
    except urllib.error.URLError as e:
        print(f"Network error: {e.reason}", file=sys.stderr); sys.exit(1)
