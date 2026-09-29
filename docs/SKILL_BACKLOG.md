# Skill backlog

Ideas with a one-line spec. "Key" = needs an API key via environment variable. Pick one, build it following [CLAUDE.md](../CLAUDE.md), move it to *Done*.

## Development & GitHub
- [ ] `release-notes`: release text from merged PRs (features, fixes, breaking changes), GitHub release draft.
- [ ] `issue-triage`: label, dedupe and prioritise open issues; propose (not apply) label changes.
- [ ] `dependency-check`: `composer outdated` / `npm outdated` / `pip list --outdated` with a risk note per update (major bumps, changelog breaking changes).
- [ ] `license-audit`: licences of all dependencies, flag copyleft/unknown/incompatible.
- [ ] `repo-bootstrap`: new repo with README, LICENSE, `.gitignore`, `.env.example`, CI, issue templates.
- [ ] `dockerfile-review`: image size, root user, layer caching, pinned base images, healthchecks, secrets in layers.
- [ ] `github-actions-builder`: CI workflows for PHP, Node, Python; caching; matrix builds.
- [ ] `adr-writer`: Architecture Decision Records (context, decision, consequences).

## Web & WordPress
- [ ] `wp-plugin-scaffold`: plugin skeleton with nonces, capabilities, i18n, uninstall hook.
- [ ] `wp-readme-txt`: generate/validate wordpress.org `readme.txt`.
- [ ] `wp-security-check`: checklist for plugins, file permissions, `wp-config`, XML-RPC, users.
- [ ] `seo-audit`: meta tags, Open Graph, sitemap, robots.txt, canonical, headings.
- [ ] `accessibility-audit`: WCAG 2.2 checks (contrast, alt text, focus, ARIA, forms).
- [ ] `pagespeed-check`: Core Web Vitals via PageSpeed Insights API. Key: `PAGESPEED_API_KEY` (optional).
- [ ] `broken-link-checker`: crawl a site or repo docs for dead links.
- [ ] `schema-jsonld`: schema.org JSON-LD for Event, Organization, Product, Article; validate.
- [ ] `og-image-generator`: social preview images (SVG/PNG) from a template.
- [ ] `impressum-check` (German): checklist for Impressum (DDG) and Datenschutzerklärung (DSGVO); no legal advice.

## Open data & archives
- [ ] `crossref-doi`: DOI metadata and BibTeX/CSL-JSON export.
- [ ] `openlibrary-isbn`: book lookup by ISBN/title, cover URLs.
- [ ] `ddb-search`: Deutsche Digitale Bibliothek API. Key: `DDB_API_KEY`.
- [ ] `europeana-search`: Europeana search/record API. Key: `EUROPEANA_API_KEY`.
- [ ] `wayback-archiver`: save URLs to the Internet Archive, find snapshots (CDX API).
- [ ] `nominatim-geocode`: geocoding/reverse geocoding via OpenStreetMap Nominatim (respect 1 req/s).
- [ ] `dwd-weather`: German weather data via Bright Sky (DWD open data).
- [ ] `bundestag-dip`: Bundestag DIP API (documents, proceedings). Key: public demo key or `DIP_API_KEY`.

## Business & office (German-specific ones in German)
- [ ] `e-rechnung`: validate/create XRechnung and ZUGFeRD (EN 16931), explain validator errors.
- [ ] `ustid-check`: VAT ID check via EU VIES (and German checksum).
- [ ] `iban-check`: IBAN checksum, bank lookup.
- [ ] `feiertage`: public holidays and bridge days per German state.
- [ ] `mahnung`: dunning letters with deadlines and statutory default interest (§ 288 BGB).
- [ ] `angebot`: quotes from a service list and hourly rates.
- [ ] `dsgvo-avv-check`: checklist for data processing agreements (Art. 28 DSGVO).

## Writing & language
- [ ] `leichte-sprache`: rewrite German texts following the rules for Leichte Sprache.
- [ ] `business-email-de`: German business e-mail tone, Du/Sie, formulas.
- [ ] `protokoll`: meeting minutes with decisions and to-dos from a transcript.
- [ ] `glossar-builder`: consistent terminology for translations.

## Media & events
- [ ] `ics-generator`: dates and schedules as `.ics` (RFC 5545, time zones).
- [ ] `youtube-metadata`: title, description and chapters from a transcript.
- [ ] `srt-tools`: shift, merge, translate and validate subtitles.
- [ ] `alt-text-writer`: good alt text for images (context, length, decorative vs informative).
- [ ] `ffmpeg-recipes`: tested commands for cutting, converting, loudness (EBU R128), thumbnails.
- [ ] `social-variants`: one piece of content as posts for Instagram, LinkedIn, Mastodon, Bluesky.

## Meta
- [ ] `postmortem`: incident analysis (timeline, root cause, actions), blameless.
- [ ] `prompt-improver`: sharpen prompts and skill descriptions so they trigger reliably.

## Done
- [x] `citation-checker`, `secret-scan`, `changelog-writer`, `gnd-lookup`, `rechnung-pruefen` (09/2026)
