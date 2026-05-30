# TaxPreparerTools.com — SEO Audit & Roadmap

This follows the AdSense remediation pass (see `ADSENSE-AUDIT.md`). That work already handled most of SEO's *technical foundation* — www canonicalization, a clean 42‑URL sitemap, `robots.txt`, duplicate‑content removal, and a big lift in crawlable content depth. This document covers the SEO‑specific layer on top of that: structured‑data correctness, on‑page metadata, and the off‑page/content roadmap.

**Everything in the "What I changed" section is applied to the attached repo and verified.** The "Recommendations" sections are deliberately *not* auto‑applied — they involve title wording and product decisions you should own.

---

## What I changed (applied + verified)

### 1. Fixed dead structured‑data URLs on 19 pages *(correctness bug from the AdSense dedup)*
Removing the `/tools/` duplicate directory left **19 pages whose JSON‑LD still pointed at the deleted `/tools/<name>` paths** — `WebApplication.url` and breadcrumb `item` fields advertising URLs that now 404 and contradict each page's canonical. Search engines reading that get mixed signals.
- Rewrote each page's dead `/tools/<name>` schema URL to that page's **actual canonical** (e.g. `…/tools/mileage` → `…/mileage`). The mapping isn't a blind strip — `ctc-estimator.html` canonicalizes to `/ctc`, etc. — so each was resolved against its own `<link rel="canonical">`.
- Fixed `tools.html`'s `ItemList` so each directory entry links to the tool's real page (`/mileage`, `/depreciation`, …) rather than a dead path.
- Left the legitimate `/tools` hub breadcrumb intact (it's a real, indexed page).
- *Verified: 0 dead `/tools/<name>` URLs remain in any JSON‑LD.*

### 2. Added complete structured data to the 5 calculators that had none
`amt-calculator`, `ctc-estimator`, `education-credits`, `extension-toolkit`, and `itemized-vs-standard` were the only indexable tool pages carrying **no JSON‑LD at all** — they had rich FAQ prose (from the content enrichment) but nothing machine‑readable to earn rich results.
- Added `WebApplication` (FinanceApplication, free `Offer`, `Organization` provider) + `BreadcrumbList` to all 5.
- Added `FAQPage` to the 4 that have a real, visible FAQ — **mirroring the on‑page question/answer text verbatim** (Google requires schema to match visible content). `extension-toolkit` has no FAQ section, so it correctly got no `FAQPage`.
- All 10 new blocks are **valid JSON** (double‑quoted, properly escaped).
- *Result: 42/42 indexable pages now have structured data.* Schema type tally now includes `WebApplication` ×37, `BreadcrumbList` (all tools), `FAQPage` ×17.

### 3. Trimmed 22 over‑length meta descriptions for full SERP display
Google shows ~150–160 characters of a meta description; the rest is truncated, hurting click‑through. **22 descriptions ran 166–277 chars.** I trimmed each to ~145–161, keeping the primary keyword front‑loaded, cutting redundant tails, and removing **brittle hard‑coded counts** ("53 notices", "25+ reject codes") that would silently go stale as you add content.
- *Verified: every page site‑wide (root + blog) is now ≤165 chars.*
- **One factual fix folded in:** `itemized-vs-standard.html`'s description said the $40,000 SALT cap was "for 2026" — it's effective **2025** (now consistent with the corrected on‑page content and the new FAQ schema).

### 4. Added 9 redirect stubs for the removed `/tools/` URLs *(post‑migration hygiene)*
The duplicate‑content finding proves Google had already crawled the `/tools/` pages; deleting them outright would leave 9 URLs returning 404 with no path to their replacements. GitHub Pages can't issue server 301s, so I recreated `/tools/<name>.html` as **lightweight `noindex,follow` redirect stubs** (canonical → root, meta‑refresh + JS redirect, **no AdSense, not in the sitemap**) — the same pattern already used for `deadline-calendar.html`.
- These consolidate old links and crawler‑known URLs to the canonical root pages **without reintroducing duplicate content** (they're noindexed redirects, not copies). In Search Console they'll resolve as "Excluded by 'noindex'", which is the correct end state.

---

## Current SEO health snapshot

| Area | State |
|---|---|
| Canonical / host consistency | ✅ All www, matches serving host |
| Sitemap | ✅ 42 clean indexable URLs, no stale/noindex entries |
| `robots.txt` | ✅ Present, points to sitemap |
| Duplicate content | ✅ `/tools/` mirror removed; old URLs now redirect |
| Crawlable content depth | ✅ Thin pages enriched to 800+ words (AdSense pass) |
| One `<title>` + one `<h1>` per page | ✅ All pages |
| Meta descriptions | ✅ Present on every page, all ≤165 chars |
| Open Graph / Twitter cards | ✅ Present site‑wide |
| Structured data coverage | ✅ 42/42 pages; `WebApplication` + `FAQPage` + `BreadcrumbList` on tools |
| HTTPS / mobile / speed | ✅ Static site — fast by default (confirm mobile + PSI, below) |
| Title length | ⚠️ ~20 titles exceed Google's ~60‑char display (recommendations below) |
| Keyword cannibalization | ⚠️ Two QBI pages compete (below) |
| Legacy JSON‑LD validity | ⚠️ 9 older blocks use single quotes (below) |

The foundation is genuinely strong. The remaining items are optimization and growth, not fixes.

---

## Recommendation A — Title tightening (review & apply)

Titles are the single highest‑weight on‑page ranking element, and yours are keyword‑rich (good) but ~20 exceed the ~60‑char display width, so Google truncates the tail (usually the brand) in results. Front‑loaded keywords survive, so this is a polish item — but tighter titles read better and improve CTR. I did **not** auto‑apply these (wording is yours to own); here are ready‑to‑use rewrites for the worst offenders. Tell me to apply any subset and I will.

| Page | Suggested title (≤~62 chars) |
|---|---|
| `self-employed-retirement-calculator` | `SEP-IRA vs Solo 401(k) vs SIMPLE Calculator 2025 \| TaxPreparerTools` |
| `state-tax-rates` | `State Tax Rate Lookup — All 50 States 2025 \| TaxPreparerTools` |
| `irs-notice-decoder` | `IRS Notice Decoder — Plain-English Lookup \| TaxPreparerTools` |
| `irs-transcript-decoder` | `IRS Transcript Code Decoder (TC 150, 570, 846) \| TaxPreparerTools` |
| `s-corp-audit-exposure-calculator` | `S-Corp Reasonable Comp Audit Calculator \| TaxPreparerTools` |
| `reasonable-compensation-calculator` | `Reasonable Compensation Calculator for S-Corps \| TaxPreparerTools` |
| `irs-efile-reject-decoder` | `IRS E-File Reject Code Lookup & Fixes \| TaxPreparerTools` |
| `extension-toolkit` | `Tax Extension Toolkit — Form 4868 & 7004 \| TaxPreparerTools` |
| `property-tax-search` | `Property Tax Search — 50 States, 300+ Counties \| TaxPreparerTools` |
| `amt-calculator` | `AMT Calculator (Form 6251) 2025 \| TaxPreparerTools` |
| `refund-tracker` | `IRS Refund Tracker & Timeline 2026 \| TaxPreparerTools` |
| `ctc-estimator` | `Child Tax Credit Estimator 2025 (CTC, ACTC) \| TaxPreparerTools` |

---

## Recommendation B — Resolve the QBI keyword cannibalization

You have **two pages targeting the same query**: `/qbi` ("QBI Deduction Calculator 2025") and `/qbi-deduction-calculator` ("QBI Deduction Calculator §199A — 2025 + 2026 OBBBA Rules"). Google has to pick one, and they split each other's ranking signals. Options, best first:
1. **Pick the stronger page** (likely `/qbi-deduction-calculator` — fuller, OBBBA‑aware) as the canonical QBI tool, and point the other's `<link rel="canonical">` at it (or 301‑stub the weaker one like the `/tools/` redirects). Consolidates all signal onto one URL.
2. **Differentiate intent**: make one the *calculator* and the other a *guide/explainer* targeting a distinct query (e.g. `/qbi` → "what is the QBI deduction" informational; `/qbi-deduction-calculator` → the tool). Only worth it if you'll invest in genuinely different content.

Say which page should win and I'll wire up the canonical/redirect.

---

## Recommendation C — Harden the 9 legacy JSON‑LD blocks (low priority)

Nine older schema blocks (the original calculator `@graph` blocks, e.g. on `mileage`, `home-office`, `depreciation`) use **single quotes** for JSON values. Google's structured‑data parser is lenient and accepts this, so they currently work — but single‑quoted JSON is technically invalid and stricter consumers (some validators, other engines) may reject it. The 10 blocks I added this session are already valid double‑quoted JSON. Converting the legacy ones is a robustness nice‑to‑have; I left them alone to avoid introducing apostrophe‑escaping bugs across many files. Run any page through the Rich Results Test to confirm current eligibility; flag me if you want the conversion done carefully.

---

## Per‑page keyword map

Assign one primary keyword per page so titles, H1s, and content stay focused. Current pages map cleanly to high‑intent professional/consumer queries:

| Page | Primary keyword |
|---|---|
| `/` | free tax tools for tax preparers / CPAs |
| `/federal-tax-estimator` | federal income tax calculator 2025 |
| `/se-tax-calculator` | self-employment tax calculator |
| `/qbi-deduction-calculator` | QBI deduction calculator (§199A) |
| `/penalty-calculator` | IRS penalty and interest calculator |
| `/mileage` | mileage deduction calculator 2025 |
| `/depreciation` | MACRS depreciation calculator / section 179 calculator |
| `/capital-gains` | capital gains tax calculator 2025 |
| `/home-office` | home office deduction calculator |
| `/quarterly-payments` | quarterly estimated tax calculator |
| `/amt` | AMT calculator / alternative minimum tax 2025 |
| `/ctc` | child tax credit calculator 2025 |
| `/education-credits` | education tax credit calculator (AOTC vs LLC) |
| `/itemized-vs-standard` | itemized vs standard deduction calculator 2025 |
| `/extensions` | tax extension calculator (Form 4868 / 7004) |
| `/reasonable-compensation-calculator` | S-corp reasonable compensation calculator |
| `/s-corp-audit-exposure-calculator` | S-corp reasonable compensation audit risk |
| `/self-employed-retirement-calculator` | SEP-IRA vs Solo 401(k) calculator |
| `/refund-tracker` | IRS refund schedule 2026 |
| `/state-tax-rates` | state income tax rates by state 2025 |
| `/property-tax-search` | property tax records lookup by address |
| `/irs-notice-decoder` | IRS notice lookup (CP2000, CP14 meaning) |
| `/irs-transcript-decoder` | IRS transcript codes (TC 846, 570 meaning) |
| `/irs-efile-reject-decoder` | IRS e-file reject codes (R0000-504 fix) |
| `/acronyms` | tax acronyms / abbreviations glossary |
| `/deadlines` | 2025–2026 tax filing deadlines |
| `/amended-return` | Form 1040-X amended return checklist |

---

## Recommendation D — Internal linking (hub‑and‑spoke)

You have breadcrumbs and the `tools.html` directory, which is a good base. Strengthen the spokes:
- **Cross‑link related tools** from each calculator's content section (2–3 contextual links). Natural clusters: SE‑tax ↔ QBI ↔ quarterly‑payments ↔ self‑employed‑retirement; CTC ↔ education‑credits ↔ federal‑estimator; reasonable‑comp ↔ s‑corp‑audit‑exposure ↔ se‑tax; itemized‑vs‑standard ↔ home‑office ↔ mileage; the three IRS decoders ↔ each other (the `/decoders` hub already does some of this).
- **Blog → tool**, every post: penalty‑abatement post → `/penalty-calculator`; both QBI posts → `/qbi-deduction-calculator`; bonus‑depreciation post → `/depreciation`; notices post → `/irs-notice-decoder`. This passes authority to the money pages and lifts engagement.
- **Tool → blog**, where a post adds depth (e.g. the depreciation calculator linking to the bonus‑depreciation explainer).

---

## Recommendation E — Content roadmap

Existing posts: bonus depreciation, first‑time penalty abatement, IRS notices decoded, OBBBA §199A, QBI SSTB phase‑out. Strong start. The highest‑value gaps each **tie to a tool you already have** (so every article has a built‑in internal link + conversion path), prioritized by intent + freshness + low competition:

1. **S‑Corp Reasonable Compensation: Setting a Defensible Salary (2025)** → links `/reasonable-compensation-calculator` + `/s-corp-audit-exposure-calculator`. High practitioner intent, ties two tools.
2. **The OBBBA $6,000 Senior Deduction: Who Qualifies and How to Claim It** → `/itemized-vs-standard`. Fresh OBBBA topic, very low competition right now.
3. **2026 Estimated‑Tax Safe Harbor Rules for Clients** → `/quarterly-payments`. Evergreen + seasonal.
4. **AOTC vs Lifetime Learning Credit: Which to Claim** → `/education-credits`.
5. **Home Office Deduction: Simplified vs Regular Method (2025)** → `/home-office`.
6. **AMT & Incentive Stock Options: When the Bargain Element Bites** → `/amt`.
7. **1099‑NEC & W‑2 Filing Deadlines and Penalties (2026)** → `/deadlines` + `/penalty-calculator`.
8. **Standard Mileage vs Actual Expenses (2025/2026 rates)** → `/mileage`.

Start with #1, #2, #3. I can draft any of these as a publish‑ready post in your house style + byline.

---

## Recommendation F — Off‑page / backlinks

On‑page is solid; rankings now need authority signals. In rough priority:
- **Free‑tool directories**: Product Hunt (a launch with all calculators), AlternativeTo, SaaSHub, Capterra/G2 if the toolkit qualifies as software. One‑time effort, lasting links.
- **Communities — lead with value, never drop‑and‑run**: Reddit `r/taxpros`, `r/accounting`, `r/tax`; LinkedIn tax‑pro groups; tax‑preparer Facebook groups. Answer a real question, link the relevant tool when it genuinely helps.
- **"Embed this calculator" widget**: give each tool an `<iframe>` embed snippet so other tax blogs can host your calculator with an automatic backlink. This is the most scalable link‑building lever for a tool site — each embed is a do‑follow link and referral traffic.
- **Outreach**: EA/CPA exam‑prep blogs, state CPA‑society newsletters, and tax bloggers for tool round‑up mentions.
- **LinkedIn cadence**: post each new tool and blog (tag Yatin, 3–5 niche hashtags); repurpose posts into carousels. Compounds with your existing presence.

---

## Pre‑flight checklist

1. **Apply & push** (workflow in `ADSENSE-AUDIT.md`), then hard‑refresh and spot‑check a page with new schema (e.g. `/amt`).
2. **Google Search Console**: re‑submit `sitemap.xml`; URL‑inspect + "Request indexing" on the 5 newly‑schema'd pages (`/amt`, `/ctc`, `/education-credits`, `/extensions`, `/itemized-vs-standard`); check Coverage — the old `/tools/` URLs should move to "Excluded by 'noindex'".
3. **Rich Results Test** (`search.google.com/test/rich-results`) on `/mileage`, `/amt`, `/ctc`, `/depreciation` → confirm FAQ + WebApplication eligibility.
4. **Bing Webmaster Tools**: add the site, submit the sitemap (~10% of search, often ignored).
5. **PageSpeed Insights** + **Mobile‑Friendly Test**: a static site should score well; just confirm no surprises on mobile.
6. *(Optional)* Resolve the QBI cannibalization (Rec. B) and convert the legacy single‑quote JSON‑LD (Rec. C).

---

*Generated to accompany the SEO pass on the attached repo. The "What I changed" items are live in the files; the lettered recommendations are yours to direct — tell me which to execute.*
