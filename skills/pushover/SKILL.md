---
name: pushover
description: Send push notifications to phones via the Pushover API with a single curl call. Use whenever the user wants to notify themselves or someone else, including explicit phrases like "send a push", "Pushover", "ping me", "notify me when done", "let me know when the build finishes", "schick mir ein Pushover", "benachrichtige mich", "sag mir Bescheid wenn X fertig ist", "ping mich". Also use at the end of long-running tasks when the user asked to be told when they're done. Supports title, priority (incl. emergency with retry/expire), sounds, URLs, HTML, monospace, TTL, image attachments and multiple recipients. Sends immediately; delayed reminders ("remind me at 5") need a scheduler, which this skill hands off to. Credentials come from a credential proxy or environment variables.
---

# Pushover Notifications

Send push notifications via the [Pushover API](https://pushover.net/api) with one `curl` call. No scripts or dependencies beyond `curl`.

## Self-improvement
If a run deviates from this skill (an error or field not covered here, a changed UI, you had to improvise, the user corrects the result), finish the task first, then load the `skill-self-improvement` skill and propose an improvement. Don't edit the skill files directly: in Claude apps they are a read-only copy. Typical signals here: an `errors` entry not listed under "Errors and limits", a parameter the API rejects or renamed, the proxy target behaving differently from the setup below, the user wanting a different default sound or priority.

## Credentials

Use the first source that is available:

1. **Credential proxy (MCP).** If a proxy such as Aegis is connected and `mcp__Aegis__list_targets` lists a `pushover` target, send through `mcp__Aegis__http_request` (`POST https://api.pushover.net/1/messages.json`, form-encoded `body`, header `Content-Type: application/x-www-form-urlencoded`). The server adds the app token; never put it in the request. Read the target's description for how the recipient key is handled. If the proxy is connected but has no `pushover` target, tell the user it can be added there.
2. **Environment variables**, for `curl` from a shell:
   ```bash
   export PUSHOVER_APP_TOKEN="YOUR_APP_TOKEN"    # application token
   export PUSHOVER_USER_KEY="YOUR_USER_KEY"     # default recipient
   # optional additional recipients, one variable per person:
   export PUSHOVER_USER_ALEX="YOUR_USER_KEY_FOR_ALEX"
   ```
   Check: `[ -n "$PUSHOVER_APP_TOKEN" ] && [ -n "$PUSHOVER_USER_KEY" ] || echo "Pushover credentials missing"`
3. **Neither available:** tell the user what to set up (an app at <https://pushover.net/apps/build>, their user key from the dashboard, then option 1 or 2). Don't ask them to paste keys into the chat, and never write real keys into this file, a repo or a log.

The `curl` examples below use the environment variables; with the proxy, send the same fields minus `token`.

## Quickstart

```bash
curl -s --form-string "token=$PUSHOVER_APP_TOKEN" \
     --form-string "user=$PUSHOVER_USER_KEY" \
     --form-string "message=Your message here" \
     https://api.pushover.net/1/messages.json
```

`{"status":1,...}` = sent. `{"status":0,"errors":[...]}` = failed; show the errors verbatim.

## When to trigger

- **Explicit**: "Pushover", "push notification", "ping me", "notify me", "schick mir ein Pushover", "benachrichtige mich".
- **Implicit**: the user asks to be told when something finishes ("let me know when the deploy is done", "sag Bescheid wenn der Build durch ist"). Do the task, then send a push with a short result summary. They already asked; don't ask again.
- **Other people**: "tell Alex dinner is ready" → use `PUSHOVER_USER_ALEX` if it exists. If no key for that person is configured, say so instead of guessing.
- Pushover sends **immediately**. For "remind me at 5 pm" or "in two hours", use a scheduler and let it fire the push: in Claude apps a scheduled task or `send_later` tool if available, otherwise cron, n8n or similar. A short wait inside a running session (`sleep 300 && curl …`) is fine. Never claim a message will arrive later when it was sent now.

## Why `--form-string`

It sends multipart form data and treats values as literal strings: UTF-8, newlines, quotes, `&` and leading `@` are safe. Only for file attachments use `--form "attachment=@/path/file.png"`, where `@` must be interpreted.

## Parameters

| Parameter | Required | Notes |
|---|---|---|
| `token` | yes | `$PUSHOVER_APP_TOKEN` |
| `user` | yes | one user key, or several comma-separated |
| `message` | yes | max 1024 chars, UTF-8 |
| `title` | no | max 250 chars; default is the app name |
| `priority` | no | `-2` in the app only, no alert; `-1` no sound/vibration; `0` normal; `1` high, bypasses quiet hours; `2` emergency |
| `sound` | no | see list below |
| `url` / `url_title` | no | link under the message (512 / 100 chars) |
| `device` | no | send to one registered device only |
| `html` | no | `1` enables `<b> <i> <u> <font color> <a href>`; excludes `monospace` |
| `monospace` | no | `1` for fixed-width text; excludes `html` |
| `ttl` | no | seconds until the message disappears (not for priority 2) |
| `timestamp` | no | Unix time to show instead of receive time |
| `attachment` | no | image ≤ 5 MB (JPEG/PNG/GIF), via `--form` and `@path` |
| `attachment_base64` + `attachment_type` | no | alternative to `attachment`: base64 image as a string plus its MIME type; use this through the proxy, where file uploads are not possible |
| `retry` / `expire` | prio 2 | retry ≥ 30 s, expire ≤ 10800 s; both required |

## Patterns

Title and sound:
```bash
curl -s --form-string "token=$PUSHOVER_APP_TOKEN" --form-string "user=$PUSHOVER_USER_KEY" \
     --form-string "title=Build status" --form-string "sound=magic" \
     --form-string "message=Build #423 finished. All tests passed." \
     https://api.pushover.net/1/messages.json
```

Link:
```bash
curl -s --form-string "token=$PUSHOVER_APP_TOKEN" --form-string "user=$PUSHOVER_USER_KEY" \
     --form-string "message=PR #42 is waiting for review" \
     --form-string "url=https://github.com/OWNER/REPO/pull/42" --form-string "url_title=Open PR" \
     https://api.pushover.net/1/messages.json
```

Image:
```bash
curl -s --form-string "token=$PUSHOVER_APP_TOKEN" --form-string "user=$PUSHOVER_USER_KEY" \
     --form-string "message=Today's chart" --form "attachment=@/tmp/chart.png" \
     https://api.pushover.net/1/messages.json
```

Several recipients: `--form-string "user=$PUSHOVER_USER_KEY,$PUSHOVER_USER_ALEX"`. If it's unclear who should get it ("let us know"), confirm briefly first.

Short-lived info: add `--form-string "ttl=300"`.

## Priority 2 (emergency): confirm first

Emergency priority re-alerts every `retry` seconds until acknowledged in the app, for up to `expire` seconds. Words like "urgent" or "wichtig" do **not** automatically mean that. Always ask: "Send as emergency? It keeps ringing until you acknowledge it in the app." If confirmed, use `retry=60`, `expire=3600`. The response contains a `receipt`: `GET /1/receipts/<receipt>.json?token=…` shows whether it was acknowledged, `POST /1/receipts/<receipt>/cancel.json` stops the alerts (<https://pushover.net/api/receipts>).

## Sounds

`pushover` (default), `bike`, `bugle`, `cashregister`, `classical`, `cosmic`, `falling`, `gamelan`, `incoming`, `intermission`, `magic`, `mechanical`, `pianobar`, `siren`, `spacealarm`, `tugboat`, `alien`, `climb`, `persistent`, `echo`, `updown`, `vibrate`, `none`.

Success → `magic`/`cosmic`; warning → `intermission`/`bugle`; critical → `siren`; don't wake anyone → `vibrate`/`none`.

## Preview before risky sends

For emergency priority, multiple recipients on an unclear request, or attachments whose path may not exist, show the exact command (with `$VARIABLES`, never expanded secrets) and ask before running it. Ordinary sends to the default recipient: just send.

## Errors and limits

- Invalid token/user key → check the environment variables.
- `message` > 1024 bytes (UTF-8 bytes, not characters) → shorten or split.
- Attachment > 5 MB or not JPEG/PNG/GIF → rejected.
- 10,000 messages per app per month, shared by all recipients; `curl -i` shows `X-Limit-App-Remaining`.
- Priority 2 without `retry`/`expire` is rejected.

Out of scope: scheduling itself (hand off as above), polling emergency receipts, Glances widgets, managing groups/licenses.
