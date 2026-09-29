---
name: citation-checker
description: Verify references and citations. Checks that DOIs, ISBNs and URLs actually exist, fetch their real metadata, and judge whether each source supports the claim it is attached to. Catches invented sources, wrong authors/years, dead links, search-page links, chatbot citation artefacts and "real source, wrong claim". Use for fact-checking drafts, Wikipedia-style articles, papers, reports and AI-generated texts, and before publishing anything with a reference list. Triggers include "check these sources", "are these citations real", "verify references", "fact-check the bibliography", "Quellen prüfen", "stimmen die Belege", "Literaturangaben überprüfen", "gibt es diese Quelle wirklich". Complements vermenschlichen / humanize-english.
---

# Citation Checker

Two separate questions per reference: **Does the source exist?** and **Does it say what the text claims?** A citation that exists but doesn't support its claim is as bad as an invented one, and more common in AI-written text.

## 1. Extract

List every reference with the claim it supports (quote the sentence). Pull out identifiers: DOI (`10.xxxx/...`), ISBN, URL, or else author + title + year.

## 2. Check existence

```bash
python3 scripts/check_ref.py 10.1038/nature14539 9783161484100 https://example.org/report
python3 scripts/check_ref.py --file refs.txt --json
```

- **DOI** → Crossref metadata (title, authors, journal, year, type); DataCite-style DOIs fall back to doi.org resolution.
- **ISBN** → checksum + Open Library record. Open Library sometimes maps an ISBN to the wrong work (the Wikipedia sample ISBN 978-3-16-148410-0 returns "Harry Potter"), so always compare the title. "Not found" there is not proof of non-existence; then search the German National Library (`https://portal.dnb.de/opac.htm?query=<isbn>`) or WorldCat.
- **URL** → status, final URL, page title; for dead links the closest Internet Archive snapshot. Flags search-results pages and `utm_source=chatgpt.com`.
- **No identifier** → web search for exact title + author; check the publisher's page or a library catalogue.

Set `CROSSREF_MAILTO=you@example.org` to use Crossref's polite pool (optional; an e-mail address, not a secret).

## 3. Compare with the citation

For each existing source compare **title, authors, year, venue, page** with how it is cited. Typical defects:
- DOI valid but points to a different paper than the cited title.
- Right paper, wrong year/authors/journal (often hallucinated details around a real core).
- Book cited without page number for a specific claim.
- Link to a homepage or search page instead of the document.
- Reference in the bibliography that no sentence uses.

## 4. Check support

Open the source (abstract, relevant section, page) and decide per claim:

| Verdict | Meaning |
|---|---|
| Supported | the source states it (quote or paraphrase the passage, give page/section) |
| Partly | source is related but the claim goes further (numbers, generalisation, causality) |
| Not supported | source doesn't say it, or says the opposite |
| Unverifiable | full text not accessible; say what was checked (abstract only, etc.) |
| Not found | source doesn't exist as cited |

Never mark "Supported" based on the title alone.

## 5. Report

Table: reference, exists?, metadata correct?, supports claim?, note/fix. Then concrete fixes: corrected citation, a better source if you actually found one, or "remove claim/soften wording". Do not invent replacement sources; if nothing verifiable is found, say so.
