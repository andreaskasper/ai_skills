# museum-digital: object search DSL (`s` parameter)

The object search `/json/objects?s=…` (and `/export/json/{query}`, `/json/object-facet-search/{query}`, `/json/objects-per-museum?s=…`) uses a structured query language of `key:value` tokens.

Behaviour verified against `nat.museum-digital.de` (10/2026).

Contents:
- Basic rules
- Keys (identity, content fields, linked entities, tags, flags, rights, alphabetical range)
- Resolving IDs (typeahead, query negotiation)
- Negation
- Checking a query
- Facets for a result set

## Basic rules

1. **One token = `key:value`**, e.g. `place:61`, `fulltext:Dürer`, `type:Gemälde`.
2. **Combine with a space → logical AND.** `type:Gemälde place:61` = paintings **and** place Berlin.
   - ⚠️ Tokens glued together without a space (`place:61institution:751`) do **not** work; the parser can't see the boundary and usually ignores the filter (result = all objects).
   - With plain `curl`, encode the space as `%20`/`+`. The helper (`md_api.py`) does it automatically.
3. **ID-based vs text-based keys:**
   - ID-based (need **numeric IDs**): `place`, `time`, `persinst`, `tag`, `tag_*`, `institution`, `collection`, `series`, `exhibition`, `event`, `id`, `ids`.
   - Text/full-text: `fulltext`, `name`, `desc`, `type`, `mattech`, `invno`, `size`.
   - Get IDs from the `search-*-by-name` typeahead endpoints or `objects_get_query_string` (below).
4. **`has_*` keys are flags WITHOUT a value.** Write `has_resource`, **not** `has_resource:1`; an appended `:1`/`:j` disables the filter.
5. **Without `s`** all published objects are listed.
6. **Hit count** is in the `total` field of every returned object.

## Keys

(Complete list from the OpenAPI `s` description; ID/text notes from tests.)

### Identity / inventory
| Key | Value | Example |
|---|---|---|
| `id` | object ID | `id:1857870` |
| `ids` | several IDs | (list) |
| `invno` | inventory number (text) | `invno:1851/195` |

### Content fields (text)
| Key | Meaning | Example |
|---|---|---|
| `fulltext` | all fields | `fulltext:Dürer` |
| `name` | title only | `name:Vase` |
| `desc` | description only | `desc:Bildnis` |
| `type` | object type | `type:Gemälde` |
| `mattech` | material/technique | `mattech:Kupferstich` |
| `size` | dimensions | |
| `puqi` | data quality index | |
| `aesthetics_score` | aesthetics score | |

### Linked entities (IDs)
| Key | Meaning |
|---|---|
| `place` | linked place |
| `time` | linked time |
| `persinst` | actor (person/institution) |
| `institution` | holding museum |
| `collection` | collection |
| `series` | series |
| `exhibition` | exhibition |
| `event` / `event_type` | event / event type |
| `geo` | geo search |
| `updated_at` | update period |

### Tags (IDs), general and by tag type
`tag` (any relation) and typed variants, all expecting **tag IDs**: `tag_general`, `tag_object_type`, `tag_material`, `tag_technique`, `tag_display_subject`, `tag_taxon`, `tag_mentioned`, `tag_topic`.

`tag_material:13314` only matches objects with tag 13314 as **material** (narrower than `tag:13314`).

### Flags (no value)
`has_resource` (image/medium attached), `has_transcriptions`, `has_image_annotations`, `has_literature`, `has_hyperlink`, `has_publications`, `has_reference`, `has_marking`, `has_event_sources`.

### Rights
`metadata_rights`, `metadata_rights_images`.

### Alphabetical range
`alpha`, `omega` (first/last letter).

## Resolving IDs

### a) Typeahead (name → ID)
```bash
curl -s "https://nat.museum-digital.de/json/search-places-by-name/Berlin"
# [{"id":61,"value":"Berlin"}, ...]   -> place:61
curl -s "https://nat.museum-digital.de/json/search-persinst-by-name/Dürer"
curl -s "https://nat.museum-digital.de/json/search-tags-by-name/Gemälde"
```
Types: `places, persinst, tags, times, collections, institutions, licenses, object-types, series, event-types, linked-entries`. `places/persinst/tags/times` accept `?suinin=1` to return only entries linked to objects.

### b) Query negotiation (plain text → DSL)
```bash
curl -s "https://nat.museum-digital.de/json/objects_get_query_string?extendQuery=berlin"
# {"results":"place:61"}
curl -s "https://nat.museum-digital.de/json/objects_get_query_string?extendQuery=Papier"
# {"results":"tag:3812"}
```
- Translates **recognised single tokens** (often to `tag:`/`place:`).
- With `s=<existing query>` the text is appended.
- ⚠️ Negotiation doesn't always insert the required **space** between tokens; check before reusing the result.
- Helper: `python3 scripts/md_api.py negotiate "berlin"`.

## Negation

The DSL can exclude tokens, but a **positive search of the same category must come first**. Example counts (they grow with the holdings; the arithmetic holds):

**Text category: works with a `-` prefix:**
```
fulltext:Maria                 -> 16,655
fulltext:Maria type:Gemälde    ->    496   (Maria AND painting)
fulltext:Maria -type:Gemälde   -> 16,159   (= 16,655 − 496, exactly excluded)
fulltext:Maria -Gemälde        -> fewer    (full text "Gemälde" excluded)
```

**ID categories (`place`, `tag`, `persinst`, `institution` …):** plain `-place:198` did **not** reliably exclude in tests (returned the full positive set). For ID-based exclusion, determine the complement via **facets** (`object-facet-search`) or set the filter in the HTML frontend and reuse the resulting `s` URL.

**Always check `total`** to confirm the negation had the expected effect.

## Checking a query

Totals change daily, so judge a query by how `total` moves, not by a fixed number:

| Query | Expected `total` |
|---|---|
| `fulltext:Dürer has_resource` | smaller than `fulltext:Dürer` |
| `fulltext:Dürer has_resource:1` | same as `fulltext:Dürer` (the `:1` disables the flag) |
| `type:Gemälde place:61` | smaller than either token alone |
| `place:61 institution:751` | small (Berlin-linked objects in Kunsthalle Bremen) |
| `place:61institution:751` | **all objects**: glued tokens are ignored |
| `place:61 -place:198` | same as `place:61`: ID negation does not work |

## Facets for a result set

`/json/object-facet-search/{query}` returns the most frequent linked institutions, actors, places, times, event types and tags **with counts**, ideal for refining a search iteratively.

```bash
python3 scripts/md_api.py facets "fulltext:vase"
# -> {institutions:[{id,name,count}], persinst:[…], places:[…], times:[…], event_types:[…], tags:[…]}
```
