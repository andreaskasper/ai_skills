---
name: pushover
description: Send push notifications to phones via the Pushover API with a single curl call. Use whenever the user wants to notify themselves or someone else, including explicit phrases like "send a push", "Pushover", "ping me", "notify me when done", "let me know when the build finishes", "schick mir ein Pushover", "benachrichtige mich", "sag mir Bescheid wenn X fertig ist", "ping mich". Also use proactively at the end of long-running tasks when the user asked to be told when they're done. Supports title, priority (incl. emergency with retry/expire), sounds, URLs, HTML, monospace, TTL, image attachments and multiple recipients. Credentials come from environment variables.
---

# Pushover Notifications

Send push notifications via the [Pushover API](https://pushover.net/api) with one `curl` call. No scripts or dependencies beyond `curl`.

## Setup (once)

Create an application at <https://pushover.net/apps/build> and note your user key from the Pushover dashboard. Then provide them as environment variables (shell profile, `.env`, agent settings):

```bash
export PUSHOVER_APP_TOKEN="YOUR_APP_TOKEN"    # application token
export PUSHOVER_USER_KEY="YOUR_USER_KEY"     # default recipient
# optional additional recipients, one variable per person:
export PUSHOVER_USER_ALEX="u..."
```

**Never write real tokens into this file, a repo, or a chat log.** If the variables are missing, tell the user what to set; don't ask them to paste keys into the conversation unless there is no other way, and never store them.

Check before sending:
```bash
[ -n "$PUSHOVER_APP_TOKEN" ] && [ -n "$PUSHOVER_USER_KEY" ] || echo "Pushover credentials missing"
```

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
- Pushover sends **immediately**. For "remind me in 5 minutes", either `sleep 300 && curl …` within the session or hand it to a scheduler; never pretend the message will be delayed.

## Why `--form-string`

It sends multipart form data and treats values as literal strings: UTF-8, newlines, quotes, `&` and leading `@` are safe. Only for file attachments use `--form "attachment=@/path/file.png"`, where `@` must be interpreted.

## Parameters

| Parameter | Required | Notes |
|---|---|---|
| `token` | yes | `$PUSHOVER_APP_TOKEN` |
| `user` | yes | one user key, or several comma-separated |
| `message` | yes | max 1024 chars, UTF-8 |
| `title` | no | max 250 chars; default is the app name |
| `priority` | no | `-2` silent, `-1` quiet, `0` normal, `1` high, `2` emergency |
| `sound` | no | see list below |
| `url` / `url_title` | no | link under the message (512 / 100 chars) |
| `device` | no | send to one registered device only |
| `html` | no | `1` enables `<b> <i> <u> <font color> <a href>`; excludes `monospace` |
| `monospace` | no | `1` for fixed-width text; excludes `html` |
| `ttl` | no | seconds until the message disappears (not for priority 2) |
| `timestamp` | no | Unix time to show instead of receive time |
| `attachment` | no | image ≤ 5 MB (JPEG/PNG/GIF), via `--form` and `@path` |
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

Emergency priority re-alerts every `retry` seconds until acknowledged in the app, for up to `expire` seconds. Words like "urgent" or "wichtig" do **not** automatically mean that. Always ask: "Send as emergency? It keeps ringing until you acknowledge it in the app." If confirmed, use `retry=60`, `expire=3600`. The response contains a `receipt` for checking or cancelling (<https://pushover.net/api/receipts>).

## Sounds

`pushover` (default), `bike`, `bugle`, `cashregister`, `classical`, `cosmic`, `falling`, `gamelan`, `incoming`, `intermission`, `magic`, `mechanical`, `pianobar`, `siren`, `spacealarm`, `tugboat`, `alien`, `climb`, `persistent`, `echo`, `updown`, `vibrate`, `none`.

Success → `magic`/`cosmic`; warning → `intermission`/`bugle`; critical → `siren`; don't wake anyone → `vibrate`/`none`.

## Preview before risky sends

For emergency priority, multiple recipients on an unclear request, or attachments whose path may not exist, show the exact command (with `$VARIABLES`, never expanded secrets) and ask before running it. Ordinary sends to the default recipient: just send.

## Errors and limits

- Invalid token/user key → check the environment variables.
- `message` > 1024 bytes → shorten or split.
- 10,000 messages per app per month; `curl -i` shows `X-Limit-App-Remaining`.
- Priority 2 without `retry`/`expire` is rejected.

Out of scope: scheduling, polling emergency receipts, Glances widgets, managing groups/licenses.
