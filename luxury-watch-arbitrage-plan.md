# Luxury Watch Arbitrage Dashboard — Build Plan

## Overview

A fully automated web-based dashboard that finds arbitrage opportunities across luxury watch marketplaces. It scans listings by reference number, compares prices across platforms, benchmarks against fair market value, and surfaces deals — all with zero manual input.

**Target Market:** Luxury watches priced $3,000+

**Supported Brands (v1):**
- Rolex
- Patek Philippe
- Audemars Piguet
- Omega
- Tudor
- Breitling
- IWC
- Vacheron Constantin
- Cartier
- Jaeger-LeCoultre

**Marketplaces (v1):**
- Chrono24 (Python scraper via `chrono24` library)
- eBay (Browse API)
- WatchCharts (API — fair market value benchmark + historical trends)

---

## Core Concepts

### Reference Number is King
The watch reference number (e.g., Rolex 126610LN, AP 15500ST.OO.1220ST.01) is the **primary key** for all matching. Every listing is mapped to a ref number. This is how the app knows a $12,000 Submariner on eBay is the same watch as a $14,500 Submariner on Chrono24.

### Box & Papers Status (4 Tiers)
The B&P status significantly affects resale value. Every listing is categorized into one of four tiers:

| Tier | Label | Typical Price Impact |
|------|-------|---------------------|
| 1 | **Full Set (Box + Papers)** | Highest value — full premium |
| 2 | **Papers Only** | Moderate premium — proves authenticity |
| 3 | **Box Only** | Small premium — presentation value |
| 4 | **No Box or Papers** | Lowest value — biggest discount |

The app compares like-for-like: a "papers only" listing is compared against other "papers only" comps and the fair market value for that B&P tier.

### Dual Purpose: Flip + Collect
The dashboard serves two goals:
- **Flip:** Find watches listed below market value, buy and resell for profit. Dashboard shows ROI %, estimated profit after fees, and time-to-sell estimates.
- **Collect:** Find watches at fair or below-fair prices that are trending up in value. Dashboard shows 30/60/90-day price trends and long-term value retention.

---

## Core Features

### 1. Automated Cross-Platform Price Scanning
- The app maintains a **watch catalog** of popular references across all 10 brands.
- A background job periodically scans Chrono24 and eBay for active listings matching these references.
- Each listing is normalized: ref number, price, B&P status, platform, seller, URL, timestamp.
- No manual searching required — deals appear on the dashboard automatically.

### 2. Arbitrage Detection Engine
Two types of arbitrage are detected automatically:

**Cross-Platform Arbitrage:**
- Same ref + same B&P tier is listed cheaper on one platform vs. another.
- Example: Omega Speedmaster 310.30.42.50.01.001 listed at $5,200 on eBay, selling for $6,400 average on Chrono24. Spread = $1,200.

**Undervalued Listings:**
- A listing is priced significantly below the WatchCharts fair market value for that ref + B&P tier.
- Example: Tudor Black Bay 79230N with full set listed at $3,100 on Chrono24, but WatchCharts market price is $3,800. That's 18% below market.

### 3. Full Deal Breakdown
For every opportunity, the dashboard shows:

| Field | Description |
|-------|-------------|
| **Watch** | Brand, model, ref number, image |
| **Buy Price** | Listing price on source platform |
| **B&P Status** | Full Set / Papers Only / Box Only / None |
| **Fair Market Value** | WatchCharts market price for this ref + B&P tier |
| **Estimated Sell Price** | Based on recent sold comps on target platform |
| **Platform Fees** | eBay ~13%, Chrono24 ~6.5% (buyer premium) |
| **Estimated Shipping** | Based on insured shipping for luxury watches (~$50-100) |
| **Estimated Profit** | Sell price - buy price - fees - shipping |
| **ROI %** | Profit / buy price × 100 |
| **Discount to Market** | How far below fair market value (%) |
| **Confidence Score** | Based on # of recent comps, price stability, listing quality |

### 4. Historical Price Trends
- For any reference number, show a price chart over 30/60/90 days.
- Data sourced from WatchCharts API.
- Indicates whether a watch is appreciating (good for collecting) or declining (risky flip).
- Overlay the current listing price on the trend chart to visualize the deal.

### 5. Dashboard Views

**Arbitrage Feed (Main View):**
- Auto-populated list of the best current deals, sorted by ROI % or profit $.
- Each card shows: watch image, ref number, brand, buy price, estimated profit, ROI %, B&P status, platform, and a direct link to the listing.
- Filters: brand, minimum profit, minimum ROI %, B&P status, platform.
- No manual searching — this is a live feed of opportunities.

**Watch Explorer:**
- Search or browse by brand/ref number.
- See all active listings across platforms for a given reference.
- Side-by-side price comparison with fair market value overlay.
- Price trend chart.

**Market Overview:**
- Brand-level trends (which brands are appreciating/depreciating).
- Top 10 fastest appreciating references.
- Top 10 most undervalued listings right now.

---

## Tech Stack

| Layer | Tech | Why |
|-------|------|-----|
| Frontend | Next.js (React) | Modern, fast, great for dashboards |
| Styling | Tailwind CSS | Clean, utility-first, rapid development |
| Backend | Next.js API routes | Keep it simple — JS everywhere |
| Database | SQLite (dev) → PostgreSQL (prod) | Store listings, price history, cached data |
| Charts | Recharts | React-native charting, great for price trends |
| Chrono24 Data | Python `chrono24` library + FlareSolverr | Unofficial but effective scraper |
| eBay Data | eBay Browse API (REST) | Official API, free tier |
| Market Data | WatchCharts API | Fair market value, price history, trends |
| Job Scheduler | node-cron or BullMQ | Automated background scanning |
| Hosting | Vercel (frontend) + Railway (backend/DB) | Easy deploy, good free tiers |

---

## Data Sources & API Details

### Chrono24 (Scraper)
- **Library:** `chrono24` Python package (GitHub: irahorecka/chrono24)
- **What it provides:** Active listings with price, condition, B&P status, seller info, location
- **Setup:** Requires FlareSolverr (Docker container) to bypass Cloudflare anti-bot
- **Rate limiting:** ~1 request per 120 posts (standard search). Be conservative to avoid blocks.
- **Search by:** Brand + reference number
- **Install:** `pip install chrono24`
- **Example:**
  ```python
  import chrono24
  results = chrono24.query("Rolex 126610LN")
  listings = results.search(limit=50)
  ```

### eBay Browse API
- **Endpoint:** `GET /buy/browse/v1/item_summary/search`
- **What it provides:** Active listings with price, condition, seller, item URL, images
- **Auth:** OAuth client credentials (free developer account)
- **Sign up:** https://developer.ebay.com
- **Rate limits:** Generous for personal use (5,000 calls/day)
- **Key filters:** Category ID for watches, price range ($3,000+), keyword = ref number
- **Note:** Returns Buy It Now listings by default. Auction listings accessible with filter.
- **Example:**
  ```
  GET /buy/browse/v1/item_summary/search?q=Rolex+126610LN&filter=price:[3000..],categoryIds:{31387}
  ```

### WatchCharts API
- **Base URL:** `https://api.watchcharts.com/v3/`
- **What it provides:** Fair market value (dealer + private sale), price history, market trends, brand indexes
- **Auth:** API key (requires Professional + API subscription)
- **Pricing:** Starts at ~$5,000/year for business use. Has a 7-day free trial to validate.
- **Rate limits:** 1 request/second, up to 5 API keys
- **Workflow:**
  1. Search by brand + ref → get UUID: `GET /search/watch?brand_name=rolex&reference=126610LN`
  2. Get market data by UUID: `GET /watch/{uuid}/price`
- **Covers:** 29,000+ watches across 100+ brands, including all 10 target brands
- **Fallback for v1:** If WatchCharts cost is prohibitive, use Chrono24 sold listings + eBay completed listings to calculate your own fair market value average.

---

## Data Model

```
Brand {
  id
  name                    -- "Rolex", "Patek Philippe", etc.
  slug                    -- "rolex", "patek-philippe"
}

WatchReference {
  id
  brand_id
  reference_number        -- "126610LN" (PRIMARY IDENTIFIER)
  model_name              -- "Submariner Date"
  collection              -- "Submariner"
  case_size_mm            -- 41
  movement                -- "Automatic"
  image_url
  watchcharts_uuid        -- UUID from WatchCharts API (for price lookups)
}

Listing {
  id
  watch_reference_id
  platform                -- "chrono24" | "ebay"
  price                   -- listing price in USD
  currency                -- original currency
  price_usd               -- normalized to USD
  box_papers_status       -- "full_set" | "papers_only" | "box_only" | "none"
  condition               -- raw condition text from platform
  seller_name
  seller_rating
  listing_url             -- direct link to buy
  image_url
  location                -- seller location
  is_active               -- boolean (still available?)
  scraped_at              -- timestamp
  created_at
}

MarketPrice {
  id
  watch_reference_id
  box_papers_status       -- "full_set" | "papers_only" | "box_only" | "none"
  market_price_usd        -- WatchCharts fair market value
  dealer_price_usd        -- WatchCharts dealer price
  source                  -- "watchcharts" | "calculated"
  recorded_at             -- timestamp
}

PriceHistory {
  id
  watch_reference_id
  date
  market_price_usd
  num_listings
  num_sold
  source
}

ArbitrageOpportunity {
  id
  listing_id              -- the underpriced listing
  watch_reference_id
  opportunity_type        -- "cross_platform" | "undervalued"
  buy_price
  buy_platform
  box_papers_status
  estimated_sell_price
  sell_platform            -- where to sell (for cross-platform arb)
  fair_market_value        -- WatchCharts benchmark
  discount_to_market_pct   -- how far below market (%)
  platform_fee_estimate
  shipping_estimate
  estimated_profit
  roi_percent
  confidence_score         -- 0-100 based on data quality
  found_at
  is_active
}
```

---

## Automated Scanning Pipeline

The app runs on autopilot with this background job pipeline:

### Job 1: Catalog Builder (runs weekly)
- Maintains the list of watch references to track.
- Seeds with the most popular/traded references for each of the 10 brands.
- Can be expanded manually or by detecting new popular refs from listing data.

### Job 2: Listing Scanner (runs every 4-6 hours)
- For each reference in the catalog:
  - Query Chrono24 via Python scraper → normalize and store listings
  - Query eBay Browse API → normalize and store listings
- Mark stale listings as inactive.
- Rate-limit aware: staggers requests to avoid blocks.

### Job 3: Market Price Updater (runs daily)
- For each reference, pull fair market value from WatchCharts API.
- Store in MarketPrice table with timestamp.
- Build PriceHistory over time.

### Job 4: Arbitrage Calculator (runs after each scan)
- Compare all active listings against:
  - Other platform listings (cross-platform arb)
  - WatchCharts fair market value (undervalued detection)
- Match by ref number + B&P status.
- Calculate profit after fees and shipping.
- Generate/update ArbitrageOpportunity records.
- Score confidence based on: number of comps, price stability, seller rating.

### Job 5: Stale Listing Cleanup (runs daily)
- Re-check listings older than 24 hours to see if still active.
- Remove sold/expired listings from the opportunity feed.

---

## Fee & Profit Calculation

### Platform Fees (Selling)
| Platform | Fee Structure |
|----------|--------------|
| eBay | ~13% final value fee + $0.30 |
| Chrono24 | ~6.5% buyer premium (seller pays listing fee ~€49-199) |
| Private sale | 0% (if selling via forums, local) |

### Shipping (Insured)
- Domestic (US): ~$50-75 (FedEx/UPS insured)
- International: ~$75-150 (FedEx International insured)
- Default estimate: $75 (configurable)

### Profit Formula
```
estimated_profit = estimated_sell_price - buy_price - platform_fee - shipping_estimate
roi_percent = (estimated_profit / buy_price) × 100
```

### Confidence Score (0-100)
| Factor | Weight | Logic |
|--------|--------|-------|
| Number of comps | 30% | More sold comps = higher confidence |
| Price stability | 25% | Low variance in recent sales = higher confidence |
| Listing age | 15% | Fresh listings score higher |
| Seller rating | 15% | Higher rated sellers = more reliable listing |
| B&P match quality | 15% | Exact B&P match in comps = higher confidence |

---

## MVP Scope (Week 1 Target)

### Must Have (Ship It)
- [ ] Watch reference catalog seeded with top 5-10 refs per brand (50-100 total)
- [ ] Chrono24 scraper pulling active listings by ref number
- [ ] eBay Browse API pulling active listings by ref number
- [ ] Listing normalization: ref number, price (USD), B&P status, platform, URL
- [ ] Cross-platform price comparison per ref + B&P tier
- [ ] Basic arbitrage detection (flag listings with 10%+ spread)
- [ ] Profit calculator with platform fees and shipping estimate
- [ ] Dashboard UI: arbitrage feed with filters (brand, min profit, min ROI, B&P status)
- [ ] Watch detail page: all listings + price comparison for a single ref
- [ ] Direct links to listings so you can buy immediately

### Nice to Have (Week 2-3)
- [ ] WatchCharts API integration for fair market value benchmarks
- [ ] Historical price trend charts (30/60/90 days)
- [ ] Market overview page (brand trends, top movers)
- [ ] Confidence scoring
- [ ] Automated background scanning on a schedule (cron jobs)
- [ ] Stale listing detection and cleanup
- [ ] Currency conversion for international listings
- [ ] Email digest: daily summary of top opportunities

### Future Ideas
- [ ] AI-powered buy/hold/sell recommendations (Claude API)
- [ ] Portfolio tracker: log your watches, see current value vs. purchase price
- [ ] Additional platforms: Crown & Caliber, Bob's Watches, WatchBox, FB Marketplace
- [ ] Mobile app or PWA
- [ ] Alert system for specific references you're watching
- [ ] Dealer vs. private seller price comparison
- [ ] Authentication risk scoring (is this listing likely authentic?)

---

## Project Structure

```
watch-arbitrage/
├── src/
│   ├── app/                          # Next.js app router
│   │   ├── page.tsx                  # Dashboard (arbitrage feed)
│   │   ├── watch/[ref]/page.tsx      # Watch detail page
│   │   ├── market/page.tsx           # Market overview
│   │   └── layout.tsx                # App layout
│   ├── components/
│   │   ├── ArbitrageCard.tsx         # Single deal card
│   │   ├── ArbitrageFeed.tsx         # Scrollable deal feed
│   │   ├── PriceChart.tsx            # Price trend chart (Recharts)
│   │   ├── ListingTable.tsx          # Side-by-side listing comparison
│   │   ├── FilterBar.tsx             # Brand, B&P, profit filters
│   │   ├── WatchHeader.tsx           # Watch info + image
│   │   └── ProfitBreakdown.tsx       # Fee + profit calculator display
│   ├── lib/
│   │   ├── db.ts                     # Database connection + queries
│   │   ├── ebay.ts                   # eBay Browse API client
│   │   ├── watchcharts.ts            # WatchCharts API client
│   │   ├── arbitrage.ts              # Arbitrage detection logic
│   │   ├── fees.ts                   # Platform fee calculations
│   │   └── types.ts                  # TypeScript types
│   └── api/
│       ├── scan/route.ts             # Trigger a scan
│       ├── opportunities/route.ts    # Get arbitrage opportunities
│       ├── watch/[ref]/route.ts      # Get data for a specific ref
│       └── market/route.ts           # Market overview data
├── scripts/
│   ├── scraper.py                    # Chrono24 Python scraper
│   ├── seed-catalog.ts               # Seed watch reference catalog
│   └── scan-all.ts                   # Full scan pipeline
├── prisma/
│   └── schema.prisma                 # Database schema (if using Prisma)
├── package.json
├── tailwind.config.js
└── .env                              # API keys (eBay, WatchCharts)
```

---

## Claude Code Kickoff Prompt

Copy and paste this into Claude Code to get started:

```
I want to build a Luxury Watch Arbitrage Dashboard — a fully automated web app that finds
underpriced luxury watches across Chrono24 and eBay, compares them to fair market value,
and shows me profit opportunities on a dashboard.

## Key Details

**Brands:** Rolex, Patek Philippe, Audemars Piguet, Omega, Tudor, Breitling, IWC,
Vacheron Constantin, Cartier, Jaeger-LeCoultre

**Price floor:** $3,000+ watches only

**Primary key:** Watch reference number (e.g., Rolex 126610LN)

**Box & Papers tiers:** Full Set, Papers Only, Box Only, No B&P — this affects value
and must be factored into all comparisons.

**Data sources:**
1. Chrono24 — use the Python `chrono24` library (pip install chrono24) to scrape listings
2. eBay — use the Browse API (GET /buy/browse/v1/item_summary/search) with OAuth
3. WatchCharts — use their API (https://api.watchcharts.com/v3/) for fair market value
   and price history. Start with placeholder/mock data if I don't have the API key yet.

**What the app does (zero manual work):**
- Maintains a catalog of popular watch references across all 10 brands
- Background jobs scan Chrono24 and eBay for active listings every few hours
- Normalizes all listings: ref number, price in USD, B&P status, platform, listing URL
- Detects two types of arbitrage:
  1. Cross-platform: same watch cheaper on one platform vs another
  2. Undervalued: listed below WatchCharts fair market value
- Calculates profit after fees (eBay ~13%, Chrono24 ~6.5%) and shipping (~$75)
- Shows ROI % and confidence score

**Tech stack:**
- Next.js with App Router + Tailwind CSS
- SQLite database (Prisma ORM)
- Recharts for price trend charts
- node-cron for background scanning jobs

**MVP pages:**
1. Dashboard/Arbitrage Feed — auto-populated list of best deals, filterable by brand,
   min profit, min ROI %, B&P status
2. Watch Detail Page — all listings for a specific ref, side-by-side price comparison,
   price trend chart
3. Market Overview — brand-level trends, top movers

**Start by:**
1. Set up Next.js project with Tailwind and Prisma
2. Define the database schema (WatchReference, Listing, MarketPrice, ArbitrageOpportunity)
3. Seed the catalog with 5-10 popular references per brand
4. Build the eBay API integration first (it's the most straightforward)
5. Build the arbitrage detection logic
6. Create the dashboard UI

Let's build this step by step. Ask me questions if anything is unclear.
```

---

## Setup Checklist

Before starting, you'll need:

- [ ] **Node.js 18+** installed
- [ ] **Python 3.9+** installed (for Chrono24 scraper)
- [ ] **Docker** installed (for FlareSolverr — Chrono24 anti-bot bypass)
- [ ] **eBay Developer Account** — sign up at https://developer.ebay.com, create an app, get OAuth credentials
- [ ] **WatchCharts Account** — sign up for Professional + API plan (start with 7-day free trial) at https://watchcharts.com/subscribe
- [ ] **FlareSolverr** running: `docker run -p 8191:8191 flaresolverr/flaresolverr`

---

## Notes & Tips

- **Start with eBay** — it has the most reliable API and will let you build the full pipeline (scan → normalize → compare → display) before tackling Chrono24's scraping complexity.
- **Mock WatchCharts data initially** — if you don't want to pay for the API right away, calculate your own "fair market value" by averaging recent eBay sold prices + Chrono24 listings for each ref. Add WatchCharts later for accuracy.
- **B&P detection from listings** — eBay and Chrono24 listings often mention B&P status in the title or description. You'll need some parsing logic (keyword matching: "full set", "box and papers", "no box", "papers only", etc.) to categorize each listing.
- **Currency normalization** — Chrono24 is global, so prices come in EUR, GBP, CHF, etc. Convert everything to USD using a free exchange rate API (e.g., exchangerate-api.com).
- **Be respectful with scraping** — Chrono24 is not an official API. Space out requests, cache aggressively, and don't hammer their servers. A scan every 4-6 hours is plenty.
- **The $3K floor is your friend** — it keeps the dataset manageable and ensures every opportunity is worth your time.
