# museum-digital: data model and response structures

Field meanings of the main JSON responses, image URL scheme, licence fields and the event model. Verified against `nat.museum-digital.de` (06/2026). Some field names are German (`objekt_*`); they are listed as the API returns them.

## navlang (output language)

`?navlang=<code>` (or `Accept-Language`): `ar, cs, de, en, fr, hi, hu, id, it, kn, pl, pt, ru, ta, te, tr, tl, uk`. The `expected_language`/`langs` field shows which languages an object actually has.

## Object search hits (`/json/objects`, flat list)

| Field | Meaning |
|---|---|
| `objekt_id` | object ID → detail `/json/object/{id}`, page `/object/{id}` |
| `objekt_name` | title |
| `objekt_inventarnr` | inventory number |
| `objekt_erfasst_am` | record creation/update time |
| `institution_id`, `institution_name` | holding museum |
| `image` | **ready relative** image path (200w preview); prefix the host |
| `image_height` | preview height |
| `total` | total hits of the search (same in every hit) |

## Object detail (`/json/object/{id}`)

| Field | Content |
|---|---|
| `object_id` | ID |
| `object_inventory_number` | inventory number |
| `object_type` | object type (text) |
| `object_name` | title |
| `object_description` | description (free text, may be multi-line) |
| `object_material_technique` | material/technique (text) |
| `object_dimensions` | dimensions (text) |
| `object_last_updated` | last change |
| `object_institution` | `{institution_id, institution_name}` |
| `md_subset` | **subset code** (e.g. `bremen`, `smb`, `nds`), needed for image URLs |
| `id_in_md_subset`, `inst_subset_id` | IDs within the subset |
| `object_images` | images (below) |
| `object_collection` | `[{collection_id, collection_name}]` |
| `object_events` | LIDO events (below) |
| `object_relation_places` / `_times` / `_people` | direct relations (often filled via events) |
| `object_tags` | `[{tag_id, tag_name, tag_name_en, relation_type, tag_note}]` |
| `exhibitions` | `{ongoing:[], past:[], upcoming:[]}` |
| `licence` | rights (below) |
| `transcripts` | `{original:[], translation:[]}` |
| `inscription` | inscriptions (text) |
| `comparable_objects` | related objects |
| `additional` | extra fields |
| `expected_language` / `langs` | language(s) |
| `objekt_socialmedia` | bool |

### `object_images[]`
| Field | Meaning |
|---|---|
| `quell_id` | resource ID |
| `name` | image title |
| `is_main` | `j`/`n` (yes/no): main image |
| `order` | order |
| `folder` | folder path, e.g. `resources/images/202505` |
| `preview` | 200w preview file name, e.g. `200w_681cc901a4468.jpg` |
| `filename_loc` | external permalink at the museum (optional) |
| `rights` | image rights (e.g. "Public Domain Mark") |
| `owner`, `creator` | rights holder / creator |
| `type` | `image` / other media types |
| `intern` | `j`/`n`: internal; don't display publicly if `j` |

### `object_events[]` (LIDO events)
Each event links the object to time/person/place in a role:

| Field | Meaning |
|---|---|
| `event_id` | ID |
| `event_type` | event type as **integer code** |
| `event_type_name` | **human-readable** type (e.g. "Hergestellt" = produced); display this |
| `people_id` + `people{}` | actor (`displayname`, `people_name`, …) |
| `time_id` + `time{}` | time (`time_name`, `time_start`, `time_end`) |
| `place_id` + `place[]` | place |
| `event_*_certain` | `j`/`n`: certainty of each statement |
| `event_note` | note |
| `sources` | sources |

> Always display the type via `event_type_name`; don't guess the integer.

### `licence`
`{ metadata_rights_holder, metadata_rights_status }`, e.g. `metadata_rights_status: "CC0"`. These are rights to the **metadata**. Image rights are separate in `object_images[].rights`. Respect both.

## Image URLs

**Scheme:** `https://<host>/data/<md_subset>/<folder>/<preview>`

- **From search hits**: `image` is already the full relative path → prefix `https://<host>/`. Helper: `Client.image_url_from_hit(hit)`.
- **From object detail**: combine `md_subset` + `object_images[].folder` + `object_images[].preview`. Helper: `Client.image_url_from_detail(img, subset)`.
- The **`200w_` preview** is reliably available. Higher resolutions vary by museum and rights; an external permalink is often in `filename_loc`. Larger derivatives don't follow a guaranteed naming scheme; check the HTML page or IIIF.

## Institution (`/json/institutions`, `/json/institution/{id}`)

| Field | Meaning |
|---|---|
| `institution_id`, `institution_name` | ID, name |
| `institution_place` | place |
| `institution_lon`, `institution_lat` | coordinates |
| `institution_url` | museum website |
| `institution_image` | logo/image (relative path) |
| `institution_collections` | number of collections |
| `institution_objects` | number of published objects |

## Collection (`/json/collection/{id}`)

| Field | Meaning |
|---|---|
| `collection_id`, `collection_name`, `collection_description` | basics |
| `collection_number_of_objects` / `_exclusive` | object count (incl./excl. sub-collections) |
| `collection_institution` | museum |
| `collection_supercollections`, `collection_subcollections` | hierarchy (collections nest) |
| `collection_tags` | tags |
| `collection_url`, `collection_mail` | links/contact |
| `md_subset`, `collection_id_in_md_subset` | subset reference |

## Series (`/json/series/{id}`)

| Field | Meaning |
|---|---|
| `series_id`, `series_name`, `series_description` | basics |
| `series_institution` | museum |
| `series_has_subordinates` | has child series? |
| `superordinate_id` | parent series |
| `series_objects` | contained objects |
| `contributors`, `places`, `times`, `weblinks` | linked data |

Hierarchy: `/json/series-get-subordinates-tree/{id}` (down), `/json/series-get-highest-superordinate/{id}` (top parent).

## Exhibitions / events

`/json/list_exhibitions` → `{results:[…]}` with `exhibition_id, name, description, start, end, institution_id, institution_name, image_path, image_license, permanent, place`. Events (appointments) analogous with `appointment_id`.

**`start`/`end` are Unix timestamps** (seconds); convert for display.

## `/json/home` (instance statistics)

`{museums, collections, objects, images, resouces (sic!), literature, exhibitions, appointments, users, avg_text_len, avg_puqi, last_update, popular:{persinst:[…], places:[…], tags:[…]}}`.

> ⚠️ The resource counter is misspelled server-side as **`resouces`**; read it exactly like that.

## Cross search (`/json/search/{q}`)

`{results:{institutions:[…], collections:[…], objects:[{id, name, institution_name, summary, image}]}}`. Object `image` is again a ready relative path.
