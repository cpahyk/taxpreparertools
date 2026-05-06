# 🚀 GitHub Pages Deployment Guide — TaxPreparerTools.com

## Quick Deploy (5 minutes)

### Step 1 — Create the GitHub Repository

1. Go to **https://github.com/new**
2. Set **Repository name** → `taxpreparertools` *(or any name you like)*
3. Set visibility → **Public** *(required for free GitHub Pages)*
4. ✅ Do **NOT** check "Initialize this repository" — leave it empty
5. Click **Create repository**

---

### Step 2 — Push the Code

Open your terminal, `cd` into the extracted folder, then run:

```bash
cd taxpreparertools

# Initialize git
git init
git add .
git commit -m "Initial deploy — full site with all tools and pages"

# Replace YOUR_USERNAME with your GitHub username
git remote add origin https://github.com/YOUR_USERNAME/taxpreparertools.git
git branch -M main
git push -u origin main
```

---

### Step 3 — Enable GitHub Pages

1. In your repo on GitHub, go to **Settings → Pages**
2. Under **Source**, select **Deploy from a branch**
3. Branch: **main** · Folder: **/ (root)**
4. Click **Save**

GitHub will show a green banner: *"Your site is live at https://YOUR_USERNAME.github.io/taxpreparertools/"*

⏱ Takes **1–3 minutes** to go live after first push.

---

### Step 4 (Optional) — Connect Your Custom Domain

If you own `taxpreparertools.com`:

1. In **Settings → Pages → Custom domain**, enter `taxpreparertools.com`
2. Click **Save** — GitHub creates a `CNAME` file automatically *(already included in this repo)*
3. At your domain registrar (Namecheap, GoDaddy, Cloudflare, etc.), add these DNS records:

```
Type    Host    Value
A       @       185.199.108.153
A       @       185.199.109.153
A       @       185.199.110.153
A       @       185.199.111.153
CNAME   www     YOUR_USERNAME.github.io
```

4. ✅ Check **Enforce HTTPS** in Settings → Pages (after DNS propagates, ~10 min)

---

## Updating the Site Later

```bash
# Make your edits, then:
git add .
git commit -m "Update: describe what changed"
git push
```

GitHub Pages auto-redeploys within ~60 seconds.

---

## Clean URL Routing

GitHub Pages serves static `.html` files. To make `/tools/se-tax-calculator` work
instead of `/tools/se-tax-calculator.html`, two approaches are included:

**Option A (Recommended) — Jekyll permalink trick:**
The `_config.yml` and `.nojekyll` files are both included. For clean URLs with Jekyll off,
links like `/tools/se-tax-calculator` need either server-side routing (not available on
free Pages) or a hosting provider that supports it (see Netlify below).

**Option B — Netlify (free, better clean URLs):**
Netlify handles clean URLs natively. Just connect your GitHub repo at
**https://app.netlify.com** → "Import from Git" → select repo → deploy.
Add a `netlify.toml` (included in this repo) and clean URLs work instantly.

---

## Netlify Deploy (Alternative — Recommended for Clean URLs)

```bash
# Install Netlify CLI
npm install -g netlify-cli

# Deploy from the project folder
netlify deploy --prod --dir .
```

Or use the Netlify dashboard: https://app.netlify.com → New site → Import from Git

The included `netlify.toml` already configures:
- Clean URL redirects (`/tools/se-tax-calculator` → works)
- Custom 404 page
- Security headers (X-Frame-Options, CSP, etc.)

---

## File Structure

```
taxpreparertools/
├── index.html                    # Homepage
├── tools.html                    # Tools directory
├── ai-assistant.html             # AI Tax Assistant
├── dashboard.html                # User dashboard
├── deadlines.html                # Tax deadline calendar
├── resources.html                # Resource library
├── login.html / signup.html      # Auth pages
├── contact.html                  # Contact form
├── privacy.html / terms.html     # Legal pages
├── forgot-password.html          # Password reset
├── 404.html                      # Custom 404
├── tools/
│   ├── federal-tax-estimator.html
│   ├── se-tax-calculator.html
│   ├── quarterly-payments.html
│   ├── qbi.html
│   ├── capital-gains.html
│   ├── penalty-calculator.html
│   ├── home-office.html          ← NEW
│   ├── mileage.html              ← NEW
│   └── depreciation.html         ← NEW
├── sitemap.xml                   # SEO sitemap
├── robots.txt                    # Search engine directives
├── CNAME                         # Custom domain config
├── _config.yml                   # Jekyll config
├── .nojekyll                     # Disables Jekyll processing
└── netlify.toml                  # Netlify deploy config
```
