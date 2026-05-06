# TaxPreparerTools.com

A complete, professional tax tools website for CPAs, Enrolled Agents, tax preparers, and individuals — built as a static HTML site, deployable via GitHub Pages.

🌐 **Live Site:** [taxpreparertools.com](https://taxpreparertools.com)

---

## 📁 Project Structure

```
taxpreparertools/
├── index.html                  # Homepage
├── tools.html                  # Tools Directory (42+ tools)
├── ai-assistant.html           # AI Tax Assistant chat interface
├── deadlines.html              # 2025–2026 Tax Deadline Calendar
├── resources.html              # Resource & Reference Library
├── login.html                  # Login page
├── signup.html                 # Signup & Pricing page
├── dashboard.html              # User Dashboard
├── tools/                      # Individual Calculator Pages
│   ├── federal-tax-estimator.html
│   ├── se-tax-calculator.html
│   ├── quarterly-payments.html
│   ├── capital-gains.html
│   ├── penalty-calculator.html
│   └── qbi.html
├── assets/
│   ├── css/                    # (reserved for shared stylesheets)
│   └── js/                     # (reserved for shared scripts)
├── README.md
├── _config.yml                 # GitHub Pages configuration
├── 404.html                    # Custom 404 page
├── sitemap.xml                 # SEO sitemap
└── robots.txt                  # Search engine robots file
```

---

## 🛠️ Pages & Features

### Core Pages
| Page | Description |
|------|-------------|
| `index.html` | Homepage with hero, tool categories, live tax calculator, deadlines, and resources |
| `tools.html` | Searchable, filterable directory of 42+ tax tools |
| `ai-assistant.html` | AI-powered tax Q&A chat interface |
| `deadlines.html` | Interactive 2025–2026 deadline calendar with reminders |
| `resources.html` | Downloadable guides, checklists, templates & IRS pub links |
| `login.html` | User authentication page |
| `signup.html` | Signup with 3-tier pricing (Free / Pro / Firm) |
| `dashboard.html` | Authenticated user dashboard |

### Calculator Tools (`/tools/`)
| Calculator | Description |
|------------|-------------|
| `federal-tax-estimator.html` | 2025 federal income tax with full bracket breakdown |
| `se-tax-calculator.html` | Self-employment tax (Schedule SE) + entity comparison |
| `quarterly-payments.html` | Safe harbor quarterly estimated payment schedule |
| `capital-gains.html` | Short/long-term gains + NIIT + loss harvesting |
| `penalty-calculator.html` | FTF, FTP & underpayment penalties with interest |
| `qbi.html` | Section 199A QBI deduction with phase-out calculation |

---

## 🚀 Deployment

### GitHub Pages (Free Hosting)

1. **Fork or clone this repo**
2. Go to **Settings → Pages**
3. Set Source to **Deploy from a branch**
4. Select **main** branch, **/ (root)** folder
5. Click **Save** — your site will be live at `https://yourusername.github.io/taxpreparertools/`

### Custom Domain (taxpreparertools.com)

1. In GitHub Pages settings, enter `taxpreparertools.com` under **Custom domain**
2. In your DNS provider, add these records:
   ```
   A     @     185.199.108.153
   A     @     185.199.109.153
   A     @     185.199.110.153
   A     @     185.199.111.153
   CNAME www   yourusername.github.io
   ```
3. Enable **Enforce HTTPS** once DNS propagates (24–48 hours)

---

## 🧮 Calculator Features

All calculators use **2025 IRS rates and rules**:

- ✅ 2025 federal tax brackets (all filing statuses)
- ✅ SE tax: 15.3% with 92.35% base factor
- ✅ SS wage base: $176,100
- ✅ Standard deductions: $15,000 / $30,000 / $22,500
- ✅ QBI thresholds: $197,300 / $394,600
- ✅ LT capital gains rates: 0% / 15% / 20%
- ✅ NIIT: 3.8% over $200k / $250k
- ✅ IRS penalty rates: FTF 5%/mo, FTP 0.5%/mo
- ✅ IRS interest: ~8% compounded daily

---

## 📈 SEO

- Canonical URLs set for `taxpreparertools.com`
- Meta descriptions on all pages
- `sitemap.xml` included
- `robots.txt` configured
- Semantic HTML structure

---

## 🎨 Design System

- **Primary font:** Playfair Display (headings)
- **Body font:** DM Sans
- **Mono font:** DM Mono (numbers, codes)
- **Color palette:** Navy `#08152a` · Gold `#c8a84b` · Muted `#7a8fac`
- **Style:** Dark professional financial aesthetic
- **Responsive:** Mobile-first, works on all screen sizes

---

## 📋 Disclaimer

All calculators and content on TaxPreparerTools.com are for **informational purposes only**. Results are estimates based on published IRS rates and rules. This site is not affiliated with the IRS. Always verify tax calculations with a qualified tax professional.

---

## 📄 License

MIT License — free to use, modify, and distribute.

---

*Built for the 2025 tax year | Updated May 2026*
