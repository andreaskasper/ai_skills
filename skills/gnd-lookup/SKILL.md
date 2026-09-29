---
name: gnd-lookup
description: Search and resolve records in the GND (Gemeinsame Normdatei), the authority file of the German National Library, for persons, organisations, places, subjects, works and events, via the free lobid-gnd API. Use to find a GND ID for a name, get dates, professions and variant names for an ID, reconcile a list of names to GND, or jump from GND to Wikidata/VIAF/LoC. Triggers include "GND", "GND-Nummer", "Normdatei", "d-nb.info/gnd", "lobid", "Personennormdatei", "find the GND ID", "authority record for", "Normdaten abgleichen". Read-only, no API key. Pairs with the wikidata, museum-digital and avefi skills.
---

# GND Lookup

The GND identifies people, corporate bodies, places, subject headings, works and events used by German-speaking libraries, archives and museums. Identifiers look like `11852786X` (URI `https://d-nb.info/gnd/11852786X`). [lobid-gnd](https://lobid.org/gnd/api) (run by hbz) serves the data as JSON without a key.

## Quick use

```bash
python3 scripts/gnd.py search "Albrecht Dürer" --type Person
python3 scripts/gnd.py get 11852786X              # condensed: name, dates, professions, links
python3 scripts/gnd.py get 11852786X --raw        # full JSON-LD record
python3 scripts/gnd.py match "Fritz Lang" --born 1890   # ranked candidates for reconciliation
```

Types for `--type`: `Person`, `CorporateBody`, `PlaceOrGeographicName`, `SubjectHeading`, `Work`, `ConferenceOrEvent`, `Family`.

Direct HTTP works too:
```bash
curl -s "https://lobid.org/gnd/search?q=Dürer&filter=type:Person&format=json&size=5"
curl -s "https://lobid.org/gnd/11852786X.json"
```

Useful search features: field queries like `q=preferredName:"Lang, Fritz"`, `q=dateOfBirth:1890*`, filters combined with `AND`, `format=json:preferredName` for a plain autocomplete list. Full syntax: <https://lobid.org/gnd/api>.

## Reconciliation rules

Names are ambiguous; the GND has many homonyms and also undifferentiated name records.

- **Match on more than the name**: life dates, profession, place, a known work. A single hit for a common name is not a confirmation.
- Prefer records typed `DifferentiatedPerson`. `UndifferentiatedPerson` records bundle several people and are poor targets.
- If two candidates remain plausible, present both with their distinguishing data instead of guessing.
- Check `variants` for historical spellings, pseudonyms and name changes.
- Record the full URI (`https://d-nb.info/gnd/…`), not just the number, when writing data back.

## Cross-links

`links` in the condensed output contains Wikidata, VIAF, LoC, ISNI and ORCID IDs when the GND record has them. Use them to continue with the `wikidata` skill, or to pass GND IDs into museum-digital's Beacon resolver (`…/resolver/actor/gnd/<id>`).

## Output

Give name, GND ID with link, dates, professions and why this record matches; mention the runner-up if the match isn't certain. Keep the API attribution in mind for published data: GND data is CC0, lobid is a service of hbz.
