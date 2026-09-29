# museum-digital: endpoint reference

All paths are relative to the instance host, e.g. `https://nat.museum-digital.de` + `/json/home`. `navlang` (output language, see data-model.md) is optional everywhere. `*` = required. All endpoints are **GET** and **read-only**.

Contents:
1. Objects
2. Institutions and their collections
3. Collections
4. Series
5. Exhibitions and events
6. Cross search
7. Typeahead (name → ID)
8. Standards and alternative outputs (LIDO/MODS/TEI/EAD/BibTeX, OAI-PMH, Reconcile, Resolver/Beacon, IIIF)

## 1. Objects

### `/json/objects`: object search
Params: `s`, `gbreitenat` (hits per page), `startwert` (offset), `extendQuery`, `navlang`.
- `s` = structured query DSL (→ `search-syntax.md`). Without `s` = all published objects.
- Response: **flat list** of hits; **total in the `total` field** of each hit.
- Hit fields: `objekt_id`, `objekt_name`, `objekt_inventarnr`, `objekt_erfasst_am`, `institution_id`, `institution_name`, `image` (ready relative path), `image_height`, `total`.

```bash
curl -s "https://nat.museum-digital.de/json/objects?s=fulltext:D%C3%BCrer&gbreitenat=10&startwert=0"
python3 scripts/md_api.py search "fulltext:Dürer" --limit 10 --offset 0
```

### `/json/object/{id}`: object detail
Params: `id*`, `navlang`. (The API doc summary is mislabelled; it returns the full object.) Structure → `data-model.md`.

### `/json/images`: image search
Params: `startAt` (offset), `navlang`. Takes no `s` parameter in the spec; for targeted searches `/json/objects?s=… has_resource` is usually better.

### `/json/object-facet-search/{query}`: facets for a search
Params: `query*` (DSL as **path segment**, URL-encoded), `navlang`.
Response: `{ institutions:[{id,name,count}], persinst:[…], places:[…], times:[…], event_types:[…], tags:[…] }`. Answers "who/where/when/which tags does this result set have?".

```bash
python3 scripts/md_api.py facets "fulltext:vase"
```

### `/json/objects-per-museum`: hits per museum (+ geo)
Params: `s`, `navlang`. Response: list of `{institution_id, institution_name, longitude, latitude, place, count}`. Good for maps and "which museums nearby have this?".

### `/json/objects_activities_in_time`: timeline
Params: `s`, `navlang`. Groups the LIDO events of the hits by time.

### `/json/objects_get_query_string`: query negotiation
Params: `s` (existing query), `extendQuery` (plain text), `navlang`. Translates plain text into DSL and appends it. `extendQuery=berlin` → `{"results":"place:61"}`. Only **recognised** tokens are translated.

### `/export/json/{query}`: batch export
Params: `query*` (DSL as path segment), `limit`, `offset`, `navlang`. For larger metadata dumps; paginate with `limit`/`offset`.

```bash
python3 scripts/md_api.py export "place:61" --limit 100 --offset 0
```

### `/json/objects_last_modified/{ids}`: last modification times
Params: `ids*` (object IDs as path segment). Useful for incremental syncs.

## 2. Institutions and their collections

### `/json/institutions`: list/search museums
Params: `q` (name filter), `navlang`. Hits: `institution_id, institution_name, institution_place, institution_lon, institution_lat, institution_url, institution_image, institution_collections, institution_objects`.

### `/json/institution/{id}`: museum detail
Params: `id*`, `navlang`.

### `/json/collections_by_institution/{id}`
Params: `id*`, `navlang`. All published collections of a museum. Response: **`{results:[{id, name, object_count, superordinate, pos, image_path, image_license, ...}]}`**; the list is under `results` (the helper unwraps it).
```bash
python3 scripts/md_api.py collections 751
```

### `/json/collections_by_institutions` / `…_total`
Params: `q`, `navlang`. Collections grouped by institution / only their total for a search.

## 3. Collections

### `/json/collection/{id}`
Params: `id*`, `navlang`. Fields include `collection_name, collection_description, collection_number_of_objects, collection_institution, collection_supercollections, collection_subcollections, collection_tags` (collections are hierarchical).

## 4. Series

Series are hierarchical object groups (e.g. bundles, work series).

- `/json/series/{id}`: detail (`series_name, series_description, series_institution, series_has_subordinates, superordinate_id, series_objects, contributors, places, times, weblinks`).
- `/json/series-get-subordinates-tree/{id}`: full child hierarchy.
- `/json/series-get-highest-superordinate/{id}`: top parent.

## 5. Exhibitions and events

Both use **Unix timestamps** in `start`/`end`.

### Exhibitions
- `/json/list_exhibitions`: params `institution_id, place, start_before, start_after, end_before, end_after, permanent`. Response `{results:[{exhibition_id, name, description, start, end, institution_id, institution_name, image_path, image_license, permanent, place}]}`.
- `/json/exhibition/{id}`: detail.
- `/json/list_exhibition_places`: places for exhibition search.
- `/json/exhibitions`: **deprecated**, use `list_exhibitions`.

### Events (appointments)
- `/json/list_appointments`: params `institution_id, place, start_before, start_after, end_before, end_after`. Response analogous with `appointment_id`.
- `/json/event/{id}`: event detail.
- `/json/list_appointment_places`: places for event search.
- `/json/events`: **deprecated**, use `list_appointments`.

Events and exhibitions are also available as iCalendar/vCard via content negotiation on the HTML pages.

## 6. Cross search

- `/json/search/{query_string}`: across entities. Response `{results:{institutions:[…], collections:[…], objects:[{id,name,institution_name,summary,image}]}}`. Good as a first question.
- `/json/search_exhibitions_fulltext/{query_string}`
- `/json/search_series_fulltext/{query_string}`

## 7. Typeahead (name → ID)

All: `/json/search-<type>-by-name/{query_string}`, `navlang` optional. Return compact `[{id, value}]` lists, which give you the **IDs** for the DSL (`place:`, `persinst:`, `tag:` …). Types:

`collections`, `event-types`, `exhibitions`, `institutions`, `licenses`, `linked-entries`, `object-types`, `persinst` (actors), `places`, `series`, `tags`, `times`.

`persinst`, `places`, `tags`, `times` also accept `suinin` (only entries linked to at least one object). `object-types` is **not** multilingual.

```bash
curl -s "https://nat.museum-digital.de/json/search-places-by-name/Berlin"
# -> [{"id":61,"value":"Berlin"}, {"id":755,"value":"Berlin-Charlottenburg"}, ...]
```

## 8. Standards and alternative outputs

The HTML object page links further formats via `<link rel="alternate">`; read them if paths differ per instance:

```bash
curl -s "https://nat.museum-digital.de/object/1857870" | grep -oiE '<link[^>]*rel="alternate"[^>]*>'
```

### Alternative object metadata formats
`https://<host>/object/{id}?output=<format>`:

| output | Format |
|---|---|
| `lido` | LIDO XML (museum standard) |
| `MODS` | MODS XML |
| `TEI` | TEI XML |
| `ead` | EAD XML |
| `BibTeX` | BibTeX citation |

```bash
python3 scripts/md_api.py raw "/object/1857870?output=lido"   # XML as raw string
```

### OAI-PMH (harvesting)
`https://<host>/oai`, standard verbs; metadataPrefixes **`lido`** and **`oai_dc`**.
```bash
curl -s "https://nat.museum-digital.de/oai?verb=Identify"
curl -s "https://nat.museum-digital.de/oai?verb=ListMetadataFormats"
curl -s "https://nat.museum-digital.de/oai?verb=ListRecords&metadataPrefix=oai_dc"
```

### Reconcile (OpenRefine)
`https://<host>/reconcile/invno`: reconciliation endpoint matching objects by **inventory number**. Returns an OpenRefine service manifest; view URL template `https://<host>/object/{{id}}`.

### Resolver / Beacon (external IDs)
`https://<host>/resolver` (help). Patterns:
- `…/resolver/{type}`: linked target databases (type ∈ institution, object, actor, place, tag).
- `…/resolver/{type}/{source}`: Beacon concordance museum-digital ↔ target database.
- `…/resolver/{type}/{source}/{source_id}`: redirect to the matching entity.

```
…/resolver/actor/gnd                  # GND concordance (Beacon)
…/resolver/place/geonames/2950159     # -> page for "Berlin"
```
Extra parameters: `?beaconHideLocal=1` (compact Beacon list), `?noReferral=1` (no redirect, target link as plain text).

### IIIF
Presentation API manifest pattern (from the HTML `alternate` links):
```
https://<host>/apis/iiif-presentation/{object_id}/manifest
```
⚠️ **Availability varies per object/instance**; some return 404 ("This resource does not exist"). Read the `<link rel="alternate" type="application/json+ld">` from the object page and use only that. Background: <https://blog.museum-digital.org/2022/04/03/iiif-and-museum-digital/>.

### Other
- **oEmbed**: `https://<host>/oembed/?format=json&url=<object-url>`.
- **iCalendar / vCard** via content negotiation on event/contact pages.
- `/json/contact`: technical/organisational contacts of the instance.
