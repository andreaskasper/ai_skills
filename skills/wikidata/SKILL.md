---
name: wikidata
description: Read from and write to Wikidata, the free collaborative knowledge base. Use whenever the user wants to search Wikidata entities, fetch structured data about items or properties, run SPARQL queries against the Wikidata Query Service, check stored Q-IDs for deletions or merges, or edit data (labels, descriptions, aliases, statements, new items). Triggers include "search Wikidata", "Q-ID", "P-ID", "SPARQL", "Wikidata item", "create Wikidata item", "add a statement", "Wikidata-Eintrag bearbeiten", "Wikidata-Item anlegen", "Wikidata abfragen", "Q-IDs prüfen". Reading needs no login; writing uses a credential proxy or a BotPassword from environment variables, after the user confirms the edits. Use this skill before raw curl calls to Wikidata.
---

# Wikidata

Two services: the **MediaWiki Action API** (`https://www.wikidata.org/w/api.php`) for search, read and write, and the **Wikidata Query Service** (`https://query.wikidata.org/sparql`) for SPARQL. Reading needs no account. Writing is covered in `references/writing.md`.

## Self-improvement
If a run deviates from this skill (an error or field not covered here, a changed UI, you had to improvise, the user corrects the result), finish the task first, then load the `skill-self-improvement` skill and propose an improvement. Don't edit the skill files directly: in Claude apps they are a read-only copy. Typical signals here: an API error code missing from the tables, a login or token step failing as documented, an edit the user had to revert, a rate-limit or lag behaviour different from what is described.

## Setup

Every request sends a descriptive `User-Agent` with contact information; Wikimedia blocks or throttles requests without one.

```bash
UA="WikidataSkill/1.0 (${WIKIDATA_CONTACT:-https://github.com/andreaskasper/ai_skills})"
API="https://www.wikidata.org/w/api.php"
```

`WIKIDATA_CONTACT` is the operator's e-mail or user page; set it for anything beyond occasional reads. Credentials for writing: see `references/writing.md` (credential proxy first, then environment variables).

## 1. Search entities

```bash
curl -s "$API" -H "User-Agent: $UA" \
  --data-urlencode "action=wbsearchentities" --data-urlencode "search=Douglas Adams" \
  --data-urlencode "language=en" --data-urlencode "type=item" \
  --data-urlencode "limit=10" --data-urlencode "format=json"
```
`type`: `item` (Q-IDs) or `property` (P-IDs; use this to find the right property instead of guessing). Response: `id`, `label`, `description`, `aliases`, `url`.

## 2. Fetch entity data

```bash
curl -s "$API" -H "User-Agent: $UA" \
  --data-urlencode "action=wbgetentities" --data-urlencode "ids=Q42|Q1|P31" \
  --data-urlencode "languages=en|de" \
  --data-urlencode "props=labels|descriptions|claims|aliases|sitelinks" --data-urlencode "format=json"
```

```
entities.Q42.labels.en.value                             → English label
entities.Q42.claims.P31[0].mainsnak.datavalue.value.id   → value Q-ID
entities.Q42.claims.P31[0].id                            → statement GUID (needed for updates)
```

### Detect deleted and merged IDs

`wbgetentities` reveals both, up to 50 IDs per request:
- **Deleted**: the entry has a `missing` field.
- **Merged**: the returned `id` differs from the requested key (the old ID redirects).

```python
for q, e in d["entities"].items():
    if "missing" in e:        print(q, "does not exist")
    elif e.get("id") != q:    print(q, "→", e["id"])   # merge
```

Worth running regularly for any database that stores Q-IDs: merges are frequent and silent, deletions leave dead links. Watch for transposed digits: a deleted `Q3046722` next to the intended `Q3046725` looks right at a glance.

## 3. SPARQL

```bash
curl -s -G "https://query.wikidata.org/sparql" -H "User-Agent: $UA" \
  -H "Accept: application/sparql-results+json" \
  --data-urlencode "query=SELECT ?item ?itemLabel WHERE {
    ?item wdt:P31 wd:Q5 ; wdt:P19 wd:Q1741 .
    SERVICE wikibase:label { bd:serviceParam wikibase:language 'en,de' }
  } LIMIT 10"
```

```sparql
VALUES ?item { wd:Q123 wd:Q456 }                  # check several known items
SERVICE wikibase:label { bd:serviceParam wikibase:language 'en,de' }   # needed for ?xLabel
OPTIONAL { ?item wdt:P856 ?website }               # make missing values visible
```
CSV: `-H "Accept: text/csv"`.

**SPARQL reads from a lagging replica.** Right after a write it often still shows the old value. Verify writes with `wbgetentities`, not SPARQL.

## 4. Rate limits

The Action API answers **HTTP 429** with a plain-text body ("You are making too many requests to the API") instead of JSON. Shared cloud IPs hit this even at low volume (seen 10/2026). Then: wait and retry with backoff, do reads via SPARQL where possible (it was still answering in that situation), or run the calls from the user's machine. Don't parse the 429 body as JSON.

## 5. Writing

Before any write, show the user the planned edits (item, property, old → new value, edit summary) and wait for an explicit OK; edits are public and attributed to the account. Then follow `references/writing.md`: credentials, login, labels/aliases, statements and value formats, creating items, error codes, maxlag and pacing, verification.

Principle for every write: **when in doubt, leave it out.** An empty property is better than a wrong one.
- Verify the item is the intended one (labels, description, sitelinks); don't trust a stored Q-ID blindly. An item without label and claims is almost always a mistake.
- No source, no statement. Don't derive values (issue numbers, founding years) by counting backwards.
- Edit summaries in English, stating the reason: "Update official website (P856): old domain redirects", not "update P856".
