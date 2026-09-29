---
name: museum-digital
description: Research museum-digital, the open publication platform for museum objects, through the public API of each instance. Use whenever the user wants to search or look up anything on museum-digital (.de/.org): find museum objects, get an object's full metadata by ID, inspect museums, collections, series, exhibitions or events, run structured/faceted searches, resolve GND/GeoNames IDs via Beacon, harvest via OAI-PMH, or export LIDO, MODS, TEI, EAD, BibTeX or IIIF. Triggers include "museum-digital", "nat.museum-digital.de", regional hosts like rlp/berlin/sachsen, "find this painting in German museums", "LIDO export", "OAI", "Museumsobjekt suchen", "welche Museen haben X". Every instance has its OWN API host; default is the aggregator nat.museum-digital.de. Read-only, no auth.
---

# museum-digital

museum-digital is an open platform on which museums publish objects, collections, exhibitions and events. Each **instance** is a separate database with its **own API server** on its own host. The endpoint structure is identical on all instances.

This documents the **public frontend API** (verified 06/2026). It is **read-only** and needs no login; there are no write endpoints.

> Source: each instance's OpenAPI spec at `https://<host>/openapi` (Swagger UI: `/swagger/`). Handbook: <https://de.handbook.museum-digital.info/>

## 1. Instances first

**There is no single museum-digital API.** Examples:

| Host | Role | Size (06/2026) |
|---|---|---|
| `nat.museum-digital.de` | **national aggregator**, merges all German holdings | ~1,050 museums, ~850,000 objects |
| `berlin.museum-digital.de` | regional (Berlin) | ~48 museums |
| `rlp.museum-digital.de` | regional (Rhineland-Palatinate) | ~98 museums |
| `sachsen.museum-digital.de` | regional (Saxony) | ~132 museums |
| `owl.museum-digital.de` | regional (Ostwestfalen-Lippe) | ~33 museums |

There are many more regional and thematic instances (`<region>.museum-digital.de`) and international ones (`.org`).

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

## 5. Endpoint map

Parameters and response shapes in **`references/endpoints.md`**.

- **Objects**: `/json/objects` (search), `/json/object/{id}` (detail), `/json/images`, `/json/object-facet-search/{q}` (facets), `/json/objects-per-museum` (hits per museum + geo), `/json/objects_activities_in_time` (timeline), `/json/objects_get_query_string` (query negotiation), `/export/json/{query}` (batch), `/json/objects_last_modified/{ids}`.
- **Institutions**: `/json/institutions`, `/json/institution/{id}`, `/json/collections_by_institution[s]`.
- **Collections**: `/json/collection/{id}`.
- **Series**: `/json/series/{id}`, `/json/series-get-subordinates-tree/{id}`, `/json/series-get-highest-superordinate/{id}`.
- **Exhibitions & events**: `/json/list_exhibitions`, `/json/exhibition/{id}`, `/json/list_appointments`, `/json/event/{id}` (`start`/`end` are Unix timestamps).
- **Cross search**: `/json/search/{q}` (institutions + collections + objects), `/json/search_exhibitions_fulltext/{q}`, `/json/search_series_fulltext/{q}`.
- **Typeahead** (name → ID): `/json/search-{places|persinst|tags|times|collections|institutions|licenses|object-types|series|event-types|linked-entries}-by-name/{q}`.
- **Meta**: `/json/home` (instance statistics), `/json/contact`.

### Standards and alternative outputs

- **Object formats**: `https://<host>/object/{id}?output=<format>` with `lido`, `MODS`, `TEI`, `ead`, `BibTeX`. They are also listed in the `<link rel="alternate">` tags of the HTML object page.
- **OAI-PMH**: `https://<host>/oai` (metadataPrefix `lido` or `oai_dc`).
- **Reconcile (OpenRefine)** by inventory number: `https://<host>/reconcile/invno`.
- **Resolver / Beacon** for external IDs: `https://<host>/resolver/{type}/{source}/{id}` (e.g. `…/place/geonames/2950159` → Berlin; `…/actor/gnd` → GND concordance).
- **IIIF**: manifest URL per object in the HTML `alternate` links; availability varies. Background: <https://blog.museum-digital.org/2022/04/03/iiif-and-museum-digital/>.

## 6. Pitfalls

- **Wrong instance** → empty or wrong results. When in doubt use `nat`.
- **`/json/home`**: the resources counter is misspelled server-side as `resouces`; read it exactly like that.
- **Mislabelled API docs**: `/json/object/{id}` and `/json/objects` both carry the summary "Returns a basic summary of the database contents…"; they are object detail and object search.
- **Negative search** needs a positive search of the same category first; see `search-syntax.md`.
- **Query negotiation** only translates **recognised** single tokens (`berlin` → `place:61`).
- **Image URLs**: search hits contain a ready relative `image` path; in object details build `data/{md_subset}/{folder}/{preview}` yourself (the helper does). The `200w_` preview is reliably available.
- **XML/text responses**: `?output=lido`, `/oai`, `/resolver` return no JSON; the helper returns the raw string.
- **Metadata vs image rights** differ: `licence` covers metadata, `object_images[].rights` the images. Respect both when reusing.

## 7. Reference files

- `references/endpoints.md`: all endpoints, parameters, responses, example calls.
- `references/search-syntax.md`: the `s` query DSL in detail.
- `references/data-model.md`: field meanings, image URL scheme, licence fields, event model, navlang.
- `scripts/md_api.py`: reusable client (CLI + `Client` class).
