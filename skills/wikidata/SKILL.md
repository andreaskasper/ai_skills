---
name: wikidata
description: Read from and write to Wikidata, the free collaborative knowledge base. Use whenever the user wants to search Wikidata entities, fetch structured data about items or properties, run SPARQL queries against the Wikidata Query Service, check stored Q-IDs for deletions or merges, or edit data (labels, descriptions, aliases, statements, new items). Triggers include "search Wikidata", "Q-ID", "P-ID", "SPARQL", "Wikidata item", "create Wikidata item", "add a statement", "Wikidata-Eintrag bearbeiten", "Wikidata-Item anlegen", "Q-IDs prüfen". Reading needs no login; writing uses a BotPassword from environment variables. Always use this skill before raw curl calls to Wikidata.
---

# Wikidata

Work with Wikidata through:
1. **MediaWiki Action API** for search, read and write
2. **Wikidata Query Service (SPARQL)** for complex queries
3. **BotPassword login** for writes

| Service | URL |
|---|---|
| Action API | `https://www.wikidata.org/w/api.php` |
| SPARQL | `https://query.wikidata.org/sparql` |

## Setup

Reading works without an account. Every request **must** send a descriptive `User-Agent` with contact info; Wikidata blocks requests without one.

For writing, create a BotPassword at [Special:BotPasswords](https://www.wikidata.org/wiki/Special:BotPasswords) with the grants "Basic rights", "Edit existing pages" and "Create, edit, and move pages" (nothing more). Provide it via environment variables, **never** in this file or the chat:

```bash
export WIKIDATA_BOT_USER="YourAccount@YourBotName"    # login name shown on Special:BotPasswords
export WIKIDATA_BOT_PASSWORD="…"                       # generated bot password
export WIKIDATA_CONTACT="you@example.org"              # for the User-Agent
```

```bash
UA="WikidataSkill/1.0 (${WIKIDATA_CONTACT:-contact-missing})"
API="https://www.wikidata.org/w/api.php"
```

> Your **main account password does not work for the API** when 2FA or modern login is active: `action=login` answers `Aborted — Authentication requires user interaction`. Only BotPasswords are suitable for automation. If one expires or is revoked, a human has to create a new one (the page asks for password re-confirmation).

## 1. Search entities

```bash
curl -s "$API" -H "User-Agent: $UA" \
  --data-urlencode "action=wbsearchentities" --data-urlencode "search=Douglas Adams" \
  --data-urlencode "language=en" --data-urlencode "type=item" \
  --data-urlencode "limit=10" --data-urlencode "format=json"
```
`type`: `item` (Q-IDs) or `property` (P-IDs). Response: `id`, `label`, `description`, `aliases`, `url`.

## 2. Fetch entity data

```bash
curl -s "$API" -H "User-Agent: $UA" \
  --data-urlencode "action=wbgetentities" --data-urlencode "ids=Q42|Q1|P31" \
  --data-urlencode "languages=en|de" \
  --data-urlencode "props=labels|descriptions|claims|aliases|sitelinks" --data-urlencode "format=json"
```

```
entities.Q42.labels.en.value                 → English label
entities.Q42.claims.P31[0].mainsnak.datavalue.value.id   → value Q-ID
entities.Q42.claims.P31[0].id                → statement GUID (needed for updates)
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
?item wdt:P31 wd:QXXXX .                            # instance of
SERVICE wikibase:label { bd:serviceParam wikibase:language 'en,de' }
OPTIONAL { ?item wdt:P856 ?website }               # make missing values visible
FILTER(YEAR(?born) > 1900)
```
CSV: `-H "Accept: text/csv"`.

**SPARQL reads from a lagging replica.** Right after a write it often still shows the old value. Verify writes with `wbgetentities` or `list=usercontribs`, not SPARQL.

## 4. Log in (writes only)

```bash
[ -n "$WIKIDATA_BOT_USER" ] && [ -n "$WIKIDATA_BOT_PASSWORD" ] || echo "BotPassword env vars missing"
JAR=$(mktemp)

TOKEN=$(curl -s "$API" -H "User-Agent: $UA" -c "$JAR" \
  --data-urlencode "action=query" --data-urlencode "meta=tokens" --data-urlencode "type=login" \
  --data-urlencode "format=json" | python3 -c "import sys,json;print(json.load(sys.stdin)['query']['tokens']['logintoken'])")

curl -s "$API" -H "User-Agent: $UA" -b "$JAR" -c "$JAR" \
  --data-urlencode "action=login" --data-urlencode "lgname=$WIKIDATA_BOT_USER" \
  --data-urlencode "lgpassword=$WIKIDATA_BOT_PASSWORD" --data-urlencode "lgtoken=$TOKEN" \
  --data-urlencode "format=json"

CSRF=$(curl -s "$API" -H "User-Agent: $UA" -b "$JAR" \
  --data-urlencode "action=query" --data-urlencode "meta=tokens" --data-urlencode "format=json" \
  | python3 -c "import sys,json;print(json.load(sys.stdin)['query']['tokens']['csrftoken'])")
```

Expected login response: `{"login":{"result":"Success","lgusername":"YourAccount"}}`; `lgusername` is the main account, not the bot name. That's correct.

Check rights: `action=query&meta=userinfo&uiprop=rights|groups` must include `edit`. A missing `writeapi` is normal for BotPasswords and harmless.

Sessions last about 30 minutes; on `badtoken` repeat the login. Delete the cookie jar when done: `rm -f "$JAR"`.

## 5. Labels, descriptions, aliases

```bash
curl -s "$API" -H "User-Agent: $UA" -b "$JAR" \
  --data-urlencode "action=wbsetlabel" --data-urlencode "id=Q12345" \
  --data-urlencode "language=en" --data-urlencode "value=My label" \
  --data-urlencode "token=$CSRF" --data-urlencode "format=json"
# description: action=wbsetdescription (same shape)
# aliases:     action=wbsetaliases with add=Alias1|Alias2
```

## 6. Statements

Create:
```bash
curl -s "$API" -H "User-Agent: $UA" -b "$JAR" \
  --data-urlencode "action=wbcreateclaim" --data-urlencode "entity=Q12345" \
  --data-urlencode "snaktype=value" --data-urlencode "property=P31" \
  --data-urlencode 'value={"entity-type":"item","numeric-id":5}' \
  --data-urlencode "token=$CSRF" --data-urlencode "format=json"
```

Change an existing value (for corrections, **don't** add a second statement; replace the value using the GUID from `claims.P856[0].id`):
```bash
curl -s "$API" -H "User-Agent: $UA" -b "$JAR" \
  --data-urlencode "action=wbsetclaimvalue" \
  --data-urlencode "claim=Q12345\$6db78f39-41f0-c633-c08c-78780430850e" \
  --data-urlencode "snaktype=value" --data-urlencode 'value="https://example.org/"' \
  --data-urlencode "summary=Update official website (P856): old domain redirects" \
  --data-urlencode "token=$CSRF" --data-urlencode "format=json"
```

Two traps: the `$` in the GUID must be escaped (`\$`) inside double quotes, otherwise the claim ID is empty. And string values need **their own quotes inside the JSON value**: `value="https://…"` including the quotes.

Other value types:
```
String:      "My text"
Time:        {"time":"+1952-03-11T00:00:00Z","timezone":0,"before":0,"after":0,"precision":11,"calendarmodel":"http://www.wikidata.org/entity/Q1985727"}
Coordinates: {"latitude":48.14,"longitude":11.58,"precision":0.0001,"globe":"http://www.wikidata.org/entity/Q2"}
Quantity:    {"amount":"+1000000","unit":"1"}
```
Time precision: 9 = year, 10 = month, 11 = day.

## 7. Create an item

```bash
curl -s "$API" -H "User-Agent: $UA" -b "$JAR" \
  --data-urlencode "action=wbeditentity" --data-urlencode "new=item" \
  --data-urlencode 'data={
    "labels": {"en": {"language":"en","value":"New item"}, "de": {"language":"de","value":"Neues Item"}},
    "descriptions": {"en": {"language":"en","value":"short description"}},
    "claims": {"P31": [{"mainsnak":{"snaktype":"value","property":"P31",
      "datavalue":{"value":{"entity-type":"item","numeric-id":5},"type":"wikibase-entityid"}},
      "type":"statement","rank":"normal"}]}
  }' \
  --data-urlencode "token=$CSRF" --data-urlencode "format=json"
```
Search first (section 1) to avoid creating duplicates.

## 8. Principle: when in doubt, leave it out

An empty property is better than a wrong one.
- **Verify the item is the intended one** before writing: look at labels, description and sitelinks; don't trust a stored Q-ID blindly. An item without label and claims is almost always a mistake.
- **Don't derive values** (issue numbers, founding years) by counting backwards. No source, no statement.
- **Edit summaries in English, stating the reason**, not just the value: "Update official website (P856): old domain redirects" instead of "update P856".
- Show the user the planned edits before running a batch.

## 9. Errors

| Code | Cause | Fix |
|---|---|---|
| `badtoken` | CSRF token expired | log in again |
| `notloggedin` | session expired | log in again |
| `no-such-entity` | ID doesn't exist | check for deletion/merge |
| `invalid-json` | malformed `data`/`value` | validate JSON |
| `modification-failed` | edit blocked | check rights / constraints |
| `editconflict` | concurrent edit | retry with fresh token |
| `maxlag` | replication lag | see below |
| `Aborted` at login | main password used | use the BotPassword |

## 10. maxlag and pacing

`maxlag=5` is meant for **bulk runs** and aborts even at normal lag ("Waiting for wdqs…: 155 seconds lagged"); the query-service lag often throttles even when the database is healthy.
- A few single edits: omit `maxlag`.
- Bulk runs: `maxlag=5`, on abort wait 30–60 s before retrying.
- Pause 1 s between writes, 2–3 s in bulk.
- Check with `wbgetentities` whether the value is already set before writing.

## 11. Common properties

| P-ID | Meaning | Type |
|---|---|---|
| P31 | instance of | item |
| P279 | subclass of | item |
| P18 | image | media |
| P569 / P570 | date of birth / death | time |
| P19 | place of birth | item |
| P27 | country of citizenship | item |
| P106 | occupation | item |
| P571 | inception | time |
| P577 | publication date | time |
| P625 | coordinates | geo |
| P856 | official website | URL |
| P17 | country | item |
| P131 | located in admin. entity | item |

## 12. Verify after writing

```bash
curl -s "$API" -H "User-Agent: $UA" --data-urlencode "action=wbgetentities" \
  --data-urlencode "ids=Q12345" --data-urlencode "props=claims" --data-urlencode "format=json"

curl -s "$API" -H "User-Agent: $UA" --data-urlencode "action=query" --data-urlencode "list=usercontribs" \
  --data-urlencode "ucuser=${WIKIDATA_BOT_USER%@*}" --data-urlencode "uclimit=5" \
  --data-urlencode "ucprop=title|timestamp|comment" --data-urlencode "format=json"
```
Not via SPARQL (lagging replica, see section 3).
