---
name: avefi
description: Search the AVefi film database (av-efi.net), the German cross-institutional network for audiovisual holdings with persistent film identifiers (PIDs/handles). Use whenever the user wants to search AVefi, look up a film work, manifestation or copy (item), resolve an AVefi handle/PID (21.11155/…), filter holdings by facets (genre, institution, language, sound, colour, year …), or check whether a film exists in AVefi and get its ID. Triggers include "AVefi", "av-efi.net", "AVefi handle", "21.11155/", "is this film in AVefi", "film archives search", "Filmdatenbank abfragen", "AVefi-Werk suchen", "Filmrecherche über Archive hinweg". Read-only public API, no authentication.
---

# AVefi

AVefi ("Automatisiertes Verbundsystem für audiovisuelle Bestände über einheitliche Filmidentifikatoren") links the film holdings of several German institutions (Deutsche Kinemathek, TIB Hannover, GWDG, Filmmuseum Düsseldorf, Haus des Dokumentarfilms and others). Every record gets a persistent ID (PID/handle of the form `21.11155/<UUID>`).

The public frontend API is **read-only** and needs no login (behaviour below verified 10/2026). It is undocumented and can change; if a call fails with 404/422 although it matches this page, re-check the request shape against the site's network traffic.

## Self-improvement
If a run deviates from this skill (an error or field not covered here, a changed UI, you had to improvise, the user corrects the result), finish the task first, then load the `skill-self-improvement` skill and propose an improvement. Don't edit the skill files directly: in Claude apps they are a read-only copy. Typical signals here: a 404/422 for a request built exactly as below, a facet attribute or hit field that is missing or renamed, the bare domain starting to work (or `www` failing), the user rejecting a "match" from recipe 3.

## Host and access

- **Always use `https://www.av-efi.net`.** The bare domain `https://av-efi.net` does not serve the API (503 or no connection).
- The site is a Nuxt/Vue SPA; the HTML contains no data. Use the JSON API below.
- Some sandboxes cannot resolve `av-efi.net`. Then run the request from a browser tab on `https://www.av-efi.net`, e.g. with Claude in Chrome's `mcp__claude-in-chrome__javascript_tool` (recipe 1).

## Data model (3 levels)

| Level | Meaning | Index |
|---|---|---|
| **Work** | the film as an abstract unit | `works` |
| **Manifestation** | a concrete version/release | `manifestations` |
| **Item** | a physical/digital copy | `items` |

For "does this film exist?" use the **`works`** index. `indexName` determines which hits and counters come back.

## Search endpoint

```
POST https://www.av-efi.net/rest/v1/frontend/search
Content-Type: application/json
```

The **body is a JSON array** of query objects (Algolia-style; the backend is Elasticsearch):

```json
[{ "indexName": "works", "params": { "query": "Tamango", "hitsPerPage": 20, "page": 0 } }]
```

- The body must be an array (an object → 422 "valid list") and `params` an object (a string → 422 "valid dictionary").
- `[]` → `{"results":[]}`; empty `params` `{}` → everything (up to `hitsPerPage`, max ~10,000).

| Param | Type | Effect |
|---|---|---|
| `query` | string | full-text search, typo-tolerant (fuzzy); empty = all |
| `hitsPerPage` | int | hits per page; `0` = counts/facets only |
| `page` | int | 0-based; `nbPages` in the response |
| `facets` | string[] | facet attributes to return with counts; `["*"]` → 422, name them |
| `facetFilters` | string[][] | outer array = AND, inner array = OR; format `"<attribute>:<value>"` |

`filters` (Algolia filter string) is **ignored**; `facetFilters` work only on the facet attributes below, anything else (e.g. `objectID`) → **422**. IDs and handles are not full-text searchable either (`query:<UUID>` → 0 hits): to fetch a single record, search by title and match `objectID` in the hits.

### Facet attributes

| Attribute | Example values |
|---|---|
| `has_genre_has_name` | Documentation-Report, Drama, Dokumentation, Amateurfilm |
| `has_form` | Documentary, Short, Feature |
| `has_sound_type` | Silent, Sound |
| `has_colour_type` | Colour, BlackAndWhite, BlackAndWhiteTinted |
| `in_language_code` | ger, eng, fre (ISO 639-2) |
| `has_issuer_name` (holding institution) | Technische Informationsbibliothek (TIB), Filmmuseum der Landeshauptstadt Düsseldorf, Haus des Dokumentarfilms |
| `subjects` | subject headings |
| `creators` | filmmakers |
| `castmembers` | cast |
| `production` | production companies |
| `located_in_has_name` | production country/place |
| `has_duration_has_value` | ISO 8601 duration, e.g. PT01H30M00S |
| `has_format_type` | DVD, … |
| `manifestation_event_type` | ReleaseEvent, BroadcastEvent, TheatricalDistributionEvent |
| `item_element_type` | Positive, DCP, Subtitles |

## Response

```json
{ "results": [ {
  "hits": [ … ],
  "nbHits": 9, "nbWorks": 9, "nbManifestations": 16, "nbItems": 41,
  "page": 0, "nbPages": 1, "hitsPerPage": 20,
  "facets": { "<attribute>": { "<value>": <count> } }
} ] }
```

`nbWorks`, `nbManifestations` and `nbItems` count the matches on each level for the query (example: 9 works, 16 manifestations, 41 items for "Tamango"). `nbHits` and `nbPages` are capped at 10,000, so use the `nb<Level>` counters for totals; `hitsPerPage: 0` returns just the counts.

### Work hit

| Field | Content |
|---|---|
| `objectID` | UUID |
| `handle` | full PID `21.11155/<UUID>` |
| `url` | `https://www.av-efi.net/film/<UUID>` |
| `years` / `production_in_year` | production year(s) |
| `creators`, `subjects`, `manifestations` | linked data |
| `has_record` | structured metadata |

**Title:** `hit.has_record.has_primary_title.has_name`; alternative titles: `hit.has_record.has_alternative_title[].has_name`.

`has_record` also contains `has_subject[]`, `has_form[]`, `same_as[]` (e.g. `avefi:FilmportalResource`, `avefi:GNDResource` → GND/filmportal IDs), `has_event[]` (with `has_activity[]`, e.g. `DirectingActivity` → director, and `located_in[]`), `category`, `described_by`, `type`.

## Detail URLs

- Work page `https://www.av-efi.net/film/<objectID>` redirects to the canonical PID URL `https://www.av-efi.net/res/21.11155/<objectID>`.
- The handle resolves via `https://hdl.handle.net/21.11155/<UUID>`.

## Recipes

### 1. Full-text search from a browser tab

Run in a tab on `https://www.av-efi.net` (relative URL, same origin):

```js
(async()=>{
  const r = await fetch('/rest/v1/frontend/search', {
    method:'POST', headers:{'Content-Type':'application/json'},
    body: JSON.stringify([{ indexName:"works", params:{ query:"Professor Mamlock", hitsPerPage:10 } }])
  });
  const j = await r.json();
  return j.results[0].hits.map(h => ({
    title: h.has_record?.has_primary_title?.has_name,
    year: (h.years||[])[0], id: h.objectID, handle: h.handle, url: h.url
  }));
})()
```

### 2. Facet filter (TIB holdings, silent films only)

```json
[{ "indexName":"works", "params":{
  "query":"", "hitsPerPage":20,
  "facetFilters":[["has_issuer_name:Technische Informationsbibliothek (TIB)"], ["has_sound_type:Silent"]]
}}]
```

### 3. Existence check / exact title match

Search is **fuzzy** and returns near-misses ("Tango-Traum" for "Tamango"). For a reliable "does this work exist?", compare **normalised titles**, don't rely on `nbHits > 0`:

```js
const norm = s => (s||'').toLowerCase()
  .replace(/ß/g,'ss').normalize('NFD').replace(/\p{M}/gu,'')
  .replace(/[.,:;!?"'`´’()\[\]\-–—…]/g,' ').replace(/\s+/g,' ').trim();
// match if norm(primary or alternative title) === norm(searched title)
```

On a title match, `handle`/`objectID` is the AVefi ID. Also compare production year and director to rule out other works with the same title (several "Hamlet"s).

### 4. Direct HTTP (environments with network access)

```bash
curl -s https://www.av-efi.net/rest/v1/frontend/search \
  -H 'Content-Type: application/json' \
  -d '[{"indexName":"works","params":{"query":"Tamango","hitsPerPage":5}}]'
```

Or the bundled helper:
```bash
python3 scripts/avefi_search.py "Professor Mamlock"
python3 scripts/avefi_search.py --index manifestations --hits 20 "Tamango"
python3 scripts/avefi_search.py --match "Alarm im Zirkus"      # exact-title check
```
