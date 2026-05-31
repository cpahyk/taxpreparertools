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

### 5. Applied the 12 title rewrites (was Recommendation A)
Shortened the 12 longest `<title>` tags — previously 76–105 chars and truncated in results — to **50–67 chars**, keeping the primary keyword front‑loaded and standardizing the suffix to `| TaxPreparerTools`. The before/after table is preserved under Recommendation A below. `og:title`/`twitter:title` were left as‑is where they were already written differently from the page title (a legitimate pattern).

### 6. Consolidated the duplicate QBI pages (was Recommendation B)
`/qbi-deduction-calculator` is the content **superset** of `/qbi` — same purpose (QBI §199A calculator) but materially more coverage (OBBBA 2025+2026 rules, the $400 minimum deduction, expanded phase‑in ranges, more inputs). I pointed `/qbi`'s `<link rel="canonical">` **and** `og:url` at it and removed `/qbi` from the sitemap (now 41 URLs). `rel=canonical` passes `/qbi`'s ranking signals — including any backlinks — to the stronger page, so this is **equity‑safe** even if `/qbi` is the older / more‑linked URL. `/qbi` stays live and usable; its internal nav links were left in place (Google follows the canonical), which also keeps the change **trivially reversible** — restore one canonical line plus the sitemap entry. *If Search Console shows `/qbi` is actually your stronger URL and you'd rather keep it as primary, tell me and I'll flip the direction and port the richer content onto it.*

### 7. Strengthened internal linking (was Recommendation D)
A link‑graph audit found 7 tools with no contextual inbound links and 10 "Related Tools" slots that pointed at the generic `/tools` hub despite being labeled as a specific tool. Repointed all 10 to their real pages and ensured every tool now has at least one topical inbound link, which also connected the previously siloed S‑corp/QBI calculators to the rest of the set. Details under Recommendation D below.

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
| Title length | ✅ 12 longest titles tightened to 50–67 chars (Rec A applied) |
| Keyword cannibalization | ✅ QBI pages consolidated via canonical (Rec B applied, reversible) |
| Legacy JSON‑LD validity | ⚠️ 9 older blocks use single quotes (below) |

The foundation is genuinely strong. The remaining items are optimization and growth, not fixes.

---

## Recommendation A — Title tightening — ✓ APPLIED

**Done this session.** The 12 longest titles were truncating in results (~76–105 chars); they're now 50–67 chars with the keyword front‑loaded and a consistent `| TaxPreparerTools` suffix. Below is exactly what was applied — the prior wording is recoverable from git if you want any of it back.

| Page | Applied title (≤~67 chars) |
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

## Recommendation B — QBI keyword cannibalization — ✓ APPLIED (reversible)

`/qbi` and `/qbi-deduction-calculator` were both targeting "QBI deduction calculator." Inspection confirmed they're the **same tool, not differentiated** — `/qbi-deduction-calculator` simply covers more (OBBBA 2025+2026 rules, the $400 minimum deduction, expanded phase‑in, more inputs; ~866 words / 7 fields vs ~732 / 6). So consolidation is the right call rather than differentiation.

**What I did:** pointed `/qbi`'s `<link rel="canonical">` and `og:url` at `/qbi-deduction-calculator`, and dropped `/qbi` from the sitemap. Signals (incl. backlinks) now consolidate onto the stronger page; `/qbi` stays live for anyone who lands on it. Reversible by restoring the canonical line + sitemap entry.

**The one case to flip it:** if your Search Console shows `/qbi` carries most of the QBI traffic/backlinks and you'd rather keep that shorter URL as primary, say so — I'll reverse the canonical direction and port the richer 2025/2026 content onto `/qbi` instead. As a follow‑up either way, repointing the 5 internal nav links to the chosen canonical URL is a nice‑to‑have.

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

## Recommendation D — Internal linking (hub‑and‑spoke) — ✓ APPLIED (core pass)

**Audited and strengthened this session.** The foundation was already solid — most calculators had populated "Related Tools" sections and every tool is linked from the `tools.html` directory and the sitemap. A link‑graph audit surfaced two real gaps, both now fixed:

- **7 tools had zero contextual inbound links** (education‑credits, amt‑calculator, mileage, itemized‑vs‑standard, extension‑toolkit, ctc‑estimator, amended‑return‑checklist). Each now has at least one, from a topically‑related page.
- **10 "Related Tools" slots were labeled as a specific tool but linked to the generic `/tools` hub** (e.g. "Itemized vs Standard", "IRS Notice Decoder", "S‑Corp Payroll Optimizer"). All 10 are repointed to their real pages — four to existing exact matches, six relabeled to the most relevant real tool — which both fixes misleading links and routes link equity to real pages instead of the hub. This also connected the previously **siloed S‑corp/QBI cluster** to the broader tool set (reasonable‑comp inbound 3→5, audit‑exposure 3→4).

Edits touched 5 source pages (federal‑tax‑estimator, se‑tax‑calculator, penalty‑calculator, qbi, capital‑gains), each preserving the page's existing markup; verified no broken links and one `<title>`/`<footer>` per page.

**Still worth doing (didn't auto‑apply — lower priority):** the blog → tool and tool → blog links. The new S‑corp post already links both S‑corp calculators; extending the same pattern to the older posts (penalty‑abatement → `/penalty-calculator`, depreciation → `/depreciation`, notices → `/irs-notice-decoder`) is a quick follow‑up I can do on request.

---

## Recommendation E — Content roadmap

Existing posts: bonus depreciation, first‑time penalty abatement, IRS notices decoded, OBBBA §199A, QBI SSTB phase‑out. Strong start. The highest‑value gaps each **tie to a tool you already have** (so every article has a built‑in internal link + conversion path), prioritized by intent + freshness + low competition:

1. **S‑Corp Reasonable Compensation: How to Set a Salary That Survives an Audit** → links `/reasonable-compensation-calculator` + `/s-corp-audit-exposure-calculator`. High practitioner intent, ties two tools. **✓ WRITTEN this session** — live at `/blog/s-corp-reasonable-compensation` (~1,500 words, BlogPosting + FAQPage schema, two tool CTAs, added to the sitemap and blog index).
2. **The OBBBA $6,000 Senior Deduction: Who Qualifies and How to Claim It** → `/itemized-vs-standard`. Fresh OBBBA topic, very low competition right now. **✓ WRITTEN this session** — live at `/blog/obbba-senior-deduction-2025` (~1,130 words, BlogPosting + FAQPage schema, figures verified against current guidance, links `/itemized-vs-standard` + `/federal-tax-estimator` + `/quarterly-payments`; added to sitemap and blog index).
3. **2026 Estimated‑Tax Safe Harbor Rules for Clients** → `/quarterly-payments`. Evergreen + seasonal.
4. **AOTC vs Lifetime Learning Credit: Which to Claim** → `/education-credits`.
5. **Home Office Deduction: Simplified vs Regular Method (2025)** → `/home-office`.
6. **AMT & Incentive Stock Options: When the Bargain Element Bites** → `/amt`.
7. **1099‑NEC & W‑2 Filing Deadlines and Penalties (2026)** → `/deadlines` + `/penalty-calculator`.
8. **Standard Mileage vs Actual Expenses (2025/2026 rates)** → `/mileage`.

#1 and #2 are done. #3 (estimated‑tax safe harbor) is the natural next one — say the word and I'll draft it in your house style + byline.

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
6. *(Optional)* Convert the legacy single‑quote JSON‑LD (Rec. C) — the only remaining hardening item; QBI consolidation (Rec B) and titles (Rec A) are already applied.

---

*Generated to accompany the SEO pass on the attached repo. The "What I changed" items are live in the files; the lettered recommendations are yours to direct — tell me which to execute.*
