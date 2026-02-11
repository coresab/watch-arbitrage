# Watch Arbitrage Dashboard

## Project Purpose
A Dash/Plotly web dashboard that identifies luxury watch arbitrage opportunities by scanning eBay and Chrono24 for underpriced listings compared to market values.

## Architecture
```
watches/
├── app.py              # Main Dash application, layout, callbacks
├── config.py           # Environment config (API keys, fees, thresholds)
├── models.py           # SQLAlchemy models and database setup
├── seed_data.py        # Seeds 60+ watch references across 10 brands
├── mock_data.py        # Generates mock listings for testing
├── api/
│   ├── ebay.py         # eBay Browse API client with OAuth
│   └── chrono24.py     # Chrono24 scraper (uses chrono24 library)
├── services/
│   ├── scanner.py      # Scans all references across platforms
│   └── arbitrage.py    # Detects cross-platform and undervalued opportunities
├── Procfile            # Gunicorn deployment command
├── render.yaml         # Render.com deployment config
└── requirements.txt    # Python dependencies
```

## Tech Stack
- **Framework**: Dash (Plotly), dash-bootstrap-components (DARKLY theme)
- **Database**: SQLAlchemy with SQLite (watches.db)
- **APIs**: eBay Browse API (OAuth), Chrono24 scraping
- **Deployment**: Render.com (gunicorn)

## Database Models

| Model | Purpose |
|-------|---------|
| `Brand` | Watch brands (Rolex, Omega, etc.) |
| `WatchReference` | Specific watch models with reference numbers |
| `Listing` | Individual listings from eBay/Chrono24 |
| `MarketPrice` | Fair market values by box/papers status |
| `PriceHistory` | Historical price tracking |
| `ArbitrageOpportunity` | Detected arbitrage opportunities |

## Key Files

| File | Purpose |
|------|---------|
| `app.py` | Dash app with routing, filter bar, opportunity cards, scan button |
| `models.py` | All SQLAlchemy models, `init_db()`, `get_session()` |
| `config.py` | eBay credentials, fee rates (13% eBay, 6.5% Chrono24), thresholds |
| `services/scanner.py` | `Scanner.scan_all_references()` - fetches listings |
| `services/arbitrage.py` | `ArbitrageEngine.analyze_all()` - finds opportunities |
| `seed_data.py` | Pre-populates brands and watch references |

## Environment Variables
```
DATABASE_URL=sqlite:///watches.db
EBAY_CLIENT_ID=your_client_id
EBAY_CLIENT_SECRET=your_client_secret
WATCHCHARTS_API_KEY=optional
FLARESOLVERR_URL=http://localhost:8191/v1  # For Chrono24 Cloudflare bypass
DEBUG=True
SCAN_INTERVAL_HOURS=6
```

## Arbitrage Thresholds (config.py)
- `MIN_PROFIT_THRESHOLD`: $200 minimum profit to flag
- `MIN_ROI_THRESHOLD`: 5% minimum ROI
- `MIN_DISCOUNT_THRESHOLD`: 10% below market value

## Platform Fees
- eBay: ~13% final value fee
- Chrono24: ~6.5% buyer premium
- Private sale: 0%

## Development Commands
```bash
# Setup
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Initialize database and seed data
python -c "from models import init_db; init_db()"
python seed_data.py

# Run locally
python app.py  # Runs on port 8050

# Or with gunicorn
gunicorn app:server --bind 0.0.0.0:8050
```

## Dashboard Features
- **Filter Bar**: Brand, min profit, min ROI, box/papers status
- **Scan Now Button**: Triggers live scan of eBay/Chrono24
- **Opportunity Cards**: Shows buy/sell price, profit, ROI, confidence score
- **Stats Row**: Active opportunities, total listings, avg profit
- **Auto-refresh**: Every 5 minutes

## Deployment (Render.com)
- Uses `Procfile`: `web: gunicorn app:server --bind 0.0.0.0:$PORT`
- Set environment variables in Render dashboard
- Database persists between deploys (SQLite file)

## Important Notes
- Run `seed_data.py` after first deploy to populate watch references
- eBay API requires approved developer account with OAuth credentials
- Chrono24 scraping may require FlareSolverr for Cloudflare bypass
- Font: Helvetica (custom CSS in app.index_string)
