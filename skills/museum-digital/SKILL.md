---
name: museum-digital
description: Research museum-digital, the open publication platform for museum objects, through the public API of each instance. Use whenever the user wants to search or look up anything on museum-digital (.de/.org), e.g. find museum objects, get an object's full metadata by ID, inspect museums, collections, series, exhibitions or events, run structured/faceted searches, resolve GND/GeoNames IDs via Beacon, harvest via OAI-PMH, or export LIDO, MODS, TEI, EAD, BibTeX or IIIF. Triggers include "museum-digital", "museumdigital", "nat.museum-digital.de", regional hosts like rlp/berlin/sachsen, "find this painting in German museums", "LIDO export", "OAI", "Beacon GND", "Museumsobjekt suchen", "Objekt-ID nachschlagen", "welche Museen haben X". Each instance has its own API host; default is the aggregator nat.museum-digital.de. Read-only, no auth.
---

# museum-digital

museum-digital is an open platform on which museums publish objects, collections, exhibitions and events. Each **instance** is a separate database with its **own API server** on its own host. The endpoint structure is identical on all instances.

This documents the **public frontend API** (behaviour verified 10/2026). It is **read-only** and needs no login; there are no write endpoints.

> Source: each instance's OpenAPI spec at `https://<host>/openapi` (Swagger UI: `/swagger/`). Handbook: <https://de.handbook.museum-digital.info/>

## Self-improvement
If a run deviates from this skill (an error or field not covered here, a changed UI, you had to improvise, the user corrects the result), finish the task first, then load the `skill-self-improvement` skill and propose an improvement. Don't edit the skill files directly: in Claude apps they are a read-only copy. Typical signals here: a DSL token that no longer filters as described (check `total`), a field missing from a response, an endpoint answering 404 that the OpenAPI spec still lists, the helper failing on a response shape.

## 1. Instances first

**There is no single museum-digital API.** Examples:

| Host | Role |
|---|---|
| `nat.museum-digital.de` | **national aggregator**, merges all German holdings |
| `berlin.museum-digital.de` | regional (Berlin) |
| `rlp.museum-digital.de` | regional (Rhineland-Palatinate) |
| `sachsen.museum-digital.de` | regional (Saxony) |
| `owl.museum-digital.de` | regional (Ostwestfalen-Lippe) |

There are many more regional and thematic instances (`<region>.museum-digital.de`) and international ones (`.org`). `/json/home` returns an instance's current size. Querying the wrong instance gives empty or wrong results.

**Choosing an instance:**
- If the user names an instance/region → use it.
- If **unclear → always the aggregator `nat.museum-digital.de`**; it contains practically everything.
- To restrict to a region, filter on the aggregator with `place:` / `institution:` instead of guessing a regional instance.

The helper accepts short names: `--instance berlin` → `berlin.museum-digital.de`.

## 2. Workflow

1. **Pick the instance** (default `nat`).
2. **Call the API**, ideally via the bundled helper:
   ```bash
   python3 scripts/md_api.py -i nat home
   python3 scripts/md_api.py search "fulltext:Dürer" --limit 10
   python3 scripts/md_api.py object 1857870
   ```
   Every endpoint also works with plain `curl`:
   ```bash
   curl -s "https://nat.museum-digital.de/json/objects?s=fulltext:D%C3%BCrer&gbreitenat=10"
   ```
3. **Interpret** responses with `references/data-model.md` (field meanings, image URLs, licences, events).
4. **Present results** with links `https://<host>/object/<id>` (institution `/institution/<id>`, collection `/collection/<id>`) and the thumbnail URL the helper builds.

**Prefer the helper** (`scripts/md_api.py`): it handles instance resolution, URL encoding, pagination, image URLs and the main endpoints, as CLI **and** importable `Client` class. For rare endpoints use `raw`: `python3 scripts/md_api.py raw /json/list_exhibitions`.

## 3. Object search cheat sheet

`/json/objects?s=…` uses a **structured query DSL**:

| Key | Example | Meaning |
|---|---|---|
| `fulltext:` | `fulltext:Dürer` | full text over all fields |
| `name:` / `desc:` | `name:Vase` | title only / description only |
| `type:` | `type:Gemälde` | object type (name, in the instance language) |
| `mattech:` | `mattech:Öl` | material/technique (name) |
| `place:` | `place:61` | linked place (**ID**, here Berlin) |
| `time:` | `time:3723` | linked time (**ID**) |
| `persinst:` | `persinst:5323` | person/institution (**ID**) |
| `tag:` | `tag:247` | keyword (**ID**) |
| `institution:` | `institution:751` | museum (**ID**) |
| `collection:` | `collection:3` | collection (**ID**) |
| `has_resource` | `has_resource` | **flag without value**: only objects with an image/medium |

- **Combine with spaces** (logical AND): `type:Gemälde place:61`. ⚠️ Tokens glued together without a space are silently ignored. The helper encodes the space.
- ID keys need **numeric IDs**. Get them from the `search-*-by-name` typeahead endpoints or `objects_get_query_string` (plain text → query, e.g. `berlin` → `place:61`).
- `has_*` keys are **flags without value**; appending `:1` disables the filter.
- Without `s` all published objects are listed.
- Paging: `gbreitenat` = hits per page, `startwert` = offset. The total is in the `total` field of every hit.

Full DSL including all `tag_*`/`has_*` keys, negation and query negotiation: **`references/search-syntax.md`**.

## 4. Language (navlang)

Choose the output language via `navlang` (or `Accept-Language`): `ar, cs, de, en, fr, hi, hu, id, it, kn, pl, pt, ru, ta, te, tr, tl, uk`. Use the user's language; the German instances have the richest content in `de`. The helper sets it with `--lang`. Note that type/material values in queries (`type:Gemälde`) are in the data's language, usually German.

## 5. Endpoints and standards

All endpoints with parameters, response shapes and examples are in **`references/endpoints.md`**: objects (search, detail, facets, hits per museum, timeline, query negotiation, batch export), institutions and collections, series, exhibitions and events, cross search, typeahead (name → ID) and the standards beyond JSON: `?output=lido|MODS|TEI|ead|BibTeX` on object pages, OAI-PMH at `/oai`, OpenRefine reconcile, Resolver/Beacon for GND/GeoNames IDs, IIIF. Field meanings and image URLs: **`references/data-model.md`**.

## 6. Pitfalls

- **`/json/home`**: the resources counter is misspelled server-side as `resouces`; read it exactly like that.
- **Mislabelled API docs**: `/json/object/{id}` and `/json/objects` both carry the summary "Returns a basic summary of the database contents…"; they are object detail and object search.
- **Negative search** needs a positive search of the same category first; see `search-syntax.md`.
- **Image URLs**: search hits contain a ready relative `image` path; in object details build `data/{md_subset}/{folder}/{preview}` yourself (the helper does). The `200w_` preview is reliably available.
- **XML/text responses**: `?output=lido`, `/oai`, `/resolver` return no JSON; the helper returns the raw string.
- **Metadata vs image rights** differ: `licence` covers metadata, `object_images[].rights` the images. Respect both when reusing.
