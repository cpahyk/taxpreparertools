# TaxPreparerTools.com — Maximum US Reach Plan

A focused growth plan to maximize US organic reach. It complements `SEO-AUDIT.md` (which covers the on-page/technical fixes already applied) and concentrates on the levers that actually add *new* reach.

## The diagnosis

On-page is done: 42/42 pages have structured data, titles and descriptions are optimized, internal linking is sound, the sitemap is clean. So reach is no longer limited by on-page quality — it's limited by two things:

1. **How many high-volume US queries the site has a page for.** Almost everything is framed for the narrow "tax preparer" niche. But the calculators answer questions that *millions of US taxpayers* search too ("2026 tax brackets", "child tax credit", "capital gains tax"). That audience is 100x the size of the practitioner niche, and the same pages can serve both.
2. **Off-site authority (backlinks).** A new site ranks for long-tail queries on content quality alone, but head terms need links.

This plan attacks both.

## Done this session

- **Flagship high-volume reference page shipped:** `/blog/2026-tax-brackets-standard-deduction` — the complete 2026 brackets, standard deduction, capital gains, AMT, CTC, EITC, and QBI numbers (IRS Rev. Proc. 2025-32), in snippet-friendly tables, funneling to six calculators. "2026 tax brackets" and "2026 standard deduction" are among the highest-volume evergreen US tax queries that exist; the site had no page for them. This is the template for Lever 1.
- **`lang="en-US"` set site-wide** (was `lang="en"` on 60 files) — an explicit US-English signal.

## Lever 1 — Own the high-volume evergreen queries *(biggest near-term reach)*

Build clean, tables-first reference pages like the brackets page — each targeting a high-volume query and funneling to the matching tool. Priority by US search volume:

1. ✓ **2026 tax brackets & standard deduction** — done.
2. **"When are taxes due 2026" / 2026 IRS deadlines** — you already have `/deadlines`; make sure it targets the calendar-year phrasing, add an FAQ + FAQPage, and link it from the brackets page.
3. **"How much is the Child Tax Credit 2026"** — short reference → `/ctc`.
4. **"2026 standard mileage rate"** — high seasonal volume → `/mileage`.
5. **"Capital gains tax 2026 / how much is capital gains tax"** → `/capital-gains`.
6. **"Is Social Security taxable in 2026"** — partly covered by the senior-deduction post; a dedicated angle would capture more.

Each should lead with a table (snippet bait), answer the question in the first 100 words, and link the calculator. I can draft any of these.

## Lever 2 — Off-site authority *(the binding constraint on head terms)*

- **Embed widget — the single highest-leverage backlink engine for a tool site.** A small "Embed this calculator" `<iframe>` snippet other tax/finance blogs paste into their posts → automatic do-follow backlinks + referral traffic + brand reach, scaling with every embed. This is worth building before chasing manual links. *(I can build a clean embeddable version of a calculator + a copy-paste embed generator.)*
- **Free-tool directories** (one-time, durable links): Product Hunt launch, AlternativeTo, SaaSHub, Capterra/G2.
- **Communities, value-first:** r/tax, r/taxpros, r/accounting; tax-pro LinkedIn and Facebook groups. Answer real questions; link a tool only when it genuinely helps.
- **Digital PR:** timely OBBBA explainers (the senior-deduction and brackets pages) are linkable assets — pitch them to tax-pro newsletters and state CPA-society bulletins around filing season.
- **LinkedIn cadence** (already started): post each new reference page and guide; tag Yatin Savani.

## Lever 3 — Technical reach

- ✓ **`lang="en-US"`** applied site-wide this session.
- **Core Web Vitals / speed:** static hosting is fast, but every page inlines its own copy of the CSS and a few pages are heavy (the property-tax page is ~115KB with inlined data). A shared external stylesheet would cut page weight and improve repeat-view speed. Run the top pages through PageSpeed Insights + the Mobile-Friendly Test and fix any LCP/CLS flags.
- **Search Console + Bing:** resubmit the sitemap; request indexing on the new high-volume pages (start with the brackets page); then watch the Performance report and double down on the queries where you're landing on page 2 — those are the fastest wins.
- **Sitelinks searchbox:** `WebSite` + `SearchAction` schema is already on the homepage. Good.

## Lever 4 — SERP features *(free reach without ranking #1)*

- **FAQPage schema** on every reference/guide (done on the new pages) → eligibility for FAQ rich results and "People Also Ask".
- **Tables-first formatting** (brackets page) → featured-snippet eligibility for "what is the 2026 standard deduction", "2026 tax brackets", etc.
- **Mine "People Also Ask"** for each target query and answer those exact questions as H2/H3 headings.

## 30-day priority sequence

1. **Push everything**, then in Search Console request indexing on `/blog/2026-tax-brackets-standard-deduction` (highest-volume target) and the two earlier posts.
2. **Build the embed widget** — the backlink engine.
3. **Publish reference pages #2–#3** (2026 deadlines query + Child Tax Credit).
4. **Run PageSpeed + mobile** on the top 5 pages; submit Bing Webmaster Tools.
5. **Start the off-site push** — Product Hunt/AlternativeTo, one helpful community post, and a LinkedIn post per new page.

I can take any of these next — most impactful are the **embed widget** (Lever 2) and **reference page #2** (Lever 1). Say which.
