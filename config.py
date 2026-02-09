import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///watches.db")

    # eBay API
    EBAY_CLIENT_ID = os.getenv("EBAY_CLIENT_ID", "")
    EBAY_CLIENT_SECRET = os.getenv("EBAY_CLIENT_SECRET", "")
    EBAY_API_BASE = "https://api.ebay.com"

    # WatchCharts API
    WATCHCHARTS_API_KEY = os.getenv("WATCHCHARTS_API_KEY", "")
    WATCHCHARTS_API_BASE = "https://api.watchcharts.com/v3"

    # FlareSolverr (for Chrono24)
    FLARESOLVERR_URL = os.getenv("FLARESOLVERR_URL", "http://localhost:8191/v1")

    # App settings
    DEBUG = os.getenv("DEBUG", "True").lower() == "true"
    SCAN_INTERVAL_HOURS = int(os.getenv("SCAN_INTERVAL_HOURS", "6"))

    # Price settings
    MIN_PRICE_USD = 3000
    DEFAULT_SHIPPING_COST = 75

    # Platform fees (as decimals)
    FEES = {
        "ebay": 0.13,        # ~13% final value fee
        "chrono24": 0.065,   # ~6.5% buyer premium
        "private": 0.0
    }

    # Arbitrage thresholds
    MIN_PROFIT_THRESHOLD = 200      # Minimum $ profit to flag
    MIN_ROI_THRESHOLD = 0.05        # Minimum 5% ROI to flag
    MIN_DISCOUNT_THRESHOLD = 0.10   # Minimum 10% below market to flag
