# Wikidata: writing

Read this only after the user has confirmed the planned edits (SKILL.md section 5). Variables `$UA` and `$API` as defined in SKILL.md.

Contents:
1. Credentials
2. Log in (BotPassword)
3. Labels, descriptions, aliases
4. Statements and value formats
5. Create an item
6. Errors
7. maxlag and pacing
8. Verify after writing

## 1. Credentials

Use the first source that is available:

1. **Credential proxy (MCP).** If a proxy such as Aegis is connected and `mcp__Aegis__list_targets` lists a `wikidata` target for `https://www.wikidata.org/w/api.php`, send every request through `mcp__Aegis__http_request` (POST, form-encoded `body`, header `Content-Type: application/x-www-form-urlencoded`, your `User-Agent`). The server attaches the credential; a natural fit is an OAuth 2.0 owner-only access token, which needs no login step. Skip section 2 and start by fetching the CSRF token (`action=query&meta=tokens`) through the proxy. If the target's description says it works differently, follow the description. If the proxy is connected but has no `wikidata` target, tell the user it can be added there.
2. **Environment variables** with a BotPassword:
   ```bash
   export WIKIDATA_BOT_USER="YourAccount@YourBotName"    # login name shown on Special:BotPasswords
   export WIKIDATA_BOT_PASSWORD="YOUR_BOT_PASSWORD"
   export WIKIDATA_CONTACT="YOUR_CONTACT"                 # e-mail or user page, for the User-Agent
   ```
   Create the BotPassword at [Special:BotPasswords](https://www.wikidata.org/wiki/Special:BotPasswords) with only the grants "Basic rights", "Edit existing pages" and "Create, edit, and move pages" (no deletion, no rights or account management).
3. **Neither available:** tell the user what to set up (option 1 or 2). Don't ask for a password in the chat, and never write one into a skill, repo or log.

The **main account password does not work for the API** when 2FA or modern login is active: `action=login` answers `Aborted — Authentication requires user interaction`, and `action=clientlogin` asks for an e-mailed code. Only BotPasswords (or OAuth) suit automation. If a BotPassword expires or is revoked, a human has to create a new one (the page asks for password re-confirmation).

## 2. Log in (BotPassword)

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

## 3. Labels, descriptions, aliases

```bash
curl -s "$API" -H "User-Agent: $UA" -b "$JAR" \
  --data-urlencode "action=wbsetlabel" --data-urlencode "id=Q12345" \
  --data-urlencode "language=en" --data-urlencode "value=My label" \
  --data-urlencode "token=$CSRF" --data-urlencode "format=json"
# description: action=wbsetdescription (same shape)
# aliases:     action=wbsetaliases with add=Alias1|Alias2
```

## 4. Statements and value formats

Create:
```bash
curl -s "$API" -H "User-Agent: $UA" -b "$JAR" \
  --data-urlencode "action=wbcreateclaim" --data-urlencode "entity=Q12345" \
  --data-urlencode "snaktype=value" --data-urlencode "property=P31" \
  --data-urlencode 'value={"entity-type":"item","numeric-id":5}' \
  --data-urlencode "token=$CSRF" --data-urlencode "format=json"
```

Change an existing value: for corrections, don't add a second statement; replace the value using the GUID from `claims.P856[0].id`:
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

## 5. Create an item

Search first (SKILL.md section 1) to avoid duplicates.

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

## 6. Errors

| Code | Cause | Fix |
|---|---|---|
| `badtoken` | CSRF token expired | log in again |
| `notloggedin` | session expired | log in again |
| `no-such-entity` | ID doesn't exist | check for deletion/merge |
| `invalid-json` | malformed `data`/`value` | validate JSON |
| `modification-failed` | edit blocked | check rights / constraints |
| `editconflict` | concurrent edit | retry with fresh token |
| `maxlag` | replication lag | section 7 |
| `Aborted` at login | main password used | use the BotPassword |
| HTTP 429, plain text | rate limit | SKILL.md section 4 |

## 7. maxlag and pacing

`maxlag=5` is meant for **bulk runs** and aborts even at normal lag ("Waiting for wdqs…: 155 seconds lagged"); the query-service lag often throttles even when the database is healthy.
- A few single edits: omit `maxlag`.
- Bulk runs: `maxlag=5`, on abort wait 30–60 s before retrying.
- Pause 1 s between writes, 2–3 s in bulk.
- Check with `wbgetentities` whether the value is already set before writing.

## 8. Verify after writing

```bash
curl -s "$API" -H "User-Agent: $UA" --data-urlencode "action=wbgetentities" \
  --data-urlencode "ids=Q12345" --data-urlencode "props=claims" --data-urlencode "format=json"

curl -s "$API" -H "User-Agent: $UA" --data-urlencode "action=query" --data-urlencode "list=usercontribs" \
  --data-urlencode "ucuser=${WIKIDATA_BOT_USER%@*}" --data-urlencode "uclimit=5" \
  --data-urlencode "ucprop=title|timestamp|comment" --data-urlencode "format=json"
```
Not via SPARQL (lagging replica).
