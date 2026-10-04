# TaxPreparerTools Deployment Guide

TaxPreparerTools is a **static site** published directly from the repository root. There is no application build step for the public site.

## Recommended production setup: Cloudflare Pages

Connect the GitHub repository:

- Repository: `cpahyk/taxpreparertools`
- Production branch: `main`
- Framework preset: **None**
- Build command: `exit 0`
- Build output directory: `.`

Every commit pushed to `main` should create a new production deployment.

### Custom domains

Attach both:

- `taxpreparertools.com`
- `www.taxpreparertools.com`

Choose one canonical host and redirect the other to it. The HTML currently uses `https://www.taxpreparertools.com/` as the canonical public origin.

Before changing DNS or removing an older host, verify:

1. Homepage loads over HTTPS.
2. `/tools.html`, `/resources.html`, `/deadlines.html`, and `/blog/` load.
3. Calculator pages execute JavaScript normally.
4. `professional-light.css` is served and the white theme is visible.
5. Images, downloads, PDF tools, and converter pages load.
6. `sitemap.xml`, `robots.txt`, `ads.txt`, and `llms.txt` are accessible.
7. Legacy routes in `_redirects` resolve correctly.
8. The custom 404 page works.
9. Both apex and `www` domains have valid SSL.

## Static-host compatibility files

The repository includes:

- `_headers` — Cloudflare Pages/static-host security headers.
- `_redirects` — legacy-route redirects for Cloudflare Pages-compatible hosts.
- `404.html` — branded not-found and clean-URL recovery page.
- `.nojekyll` — prevents GitHub Pages Jekyll processing if GitHub Pages is used as a fallback.
- `CNAME` — retained for GitHub Pages compatibility.
- `netlify.toml` — compatibility configuration if the site is temporarily deployed through Netlify.
- `_config.yml` — legacy GitHub Pages metadata only; the production site does not require a Jekyll build.

## GitHub validation

The workflow at `.github/workflows/validate-site.yml` runs on every push to `main` and checks:

- inline JavaScript syntax,
- JSON-LD validity,
- sitemap file coverage,
- professional-light theme coverage,
- internal HTML links,
- tools-directory integrity, and
- live tool routes.

A failed validation should be fixed before treating the deployment as production-ready.

## Normal update workflow

1. Make the site change.
2. Commit it to `main`.
3. Confirm the validation workflow passes.
4. Confirm the hosting provider created a deployment for the same commit.
5. Verify the live site before considering the change complete.

## Deployment troubleshooting

If GitHub `main` contains newer content but the public site still shows an older version:

1. Check the hosting provider's latest production deployment SHA.
2. Confirm the connected repository is `cpahyk/taxpreparertools`.
3. Confirm the production branch is `main`.
4. Confirm build output is the repository root (`.`).
5. Trigger a new deployment from the latest `main` commit.
6. Purge the CDN cache only after confirming the deployment contains the new files.
7. Verify `index.html` and `professional-light.css` directly on the production domain.

Do not delete the old hosting configuration until the new production host, custom domains, SSL, redirects, calculators, images, downloads, and principal pages have all been verified.
