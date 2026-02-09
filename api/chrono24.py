"""
Chrono24 scraper using the chrono24 Python library.
Requires FlareSolverr running for Cloudflare bypass.
"""

from typing import Optional
import re

from config import Config

# Note: chrono24 library requires FlareSolverr
# docker run -p 8191:8191 flaresolverr/flaresolverr
try:
    import chrono24
    CHRONO24_AVAILABLE = True
except ImportError:
    CHRONO24_AVAILABLE = False


class Chrono24Client:
    """Client for scraping Chrono24 listings."""

    def __init__(self):
        self.flaresolverr_url = Config.FLARESOLVERR_URL

    def is_available(self) -> bool:
        """Check if chrono24 library is available."""
        return CHRONO24_AVAILABLE

    def search_watches(
        self,
        query: str,
        min_price: int = 3000,
        max_price: Optional[int] = None,
        limit: int = 50
    ) -> list[dict]:
        """
        Search for watch listings on Chrono24.

        Args:
            query: Search query (e.g., "Rolex 126610LN")
            min_price: Minimum price in USD
            max_price: Maximum price in USD (optional)
            limit: Maximum results to return

        Returns:
            List of normalized listing dictionaries
        """
        if not CHRONO24_AVAILABLE:
            print("chrono24 library not available. Install with: pip install chrono24")
            return []

        try:
            results = chrono24.query(query)
            listings = results.search(limit=limit)

            normalized = []
            for listing in listings:
                # Filter by price
                price = listing.get("price", {}).get("value", 0)
                if price < min_price:
                    continue
                if max_price and price > max_price:
                    continue

                normalized.append(self._normalize_listing(listing, query))

            return normalized

        except Exception as e:
            print(f"Chrono24 search error: {e}")
            return []

    def _normalize_listing(self, item: dict, search_query: str) -> dict:
        """Convert Chrono24 item to our normalized listing format."""
        price_info = item.get("price", {})
        price = float(price_info.get("value", 0))
        currency = price_info.get("currency", "USD")

        # Currency conversion would go here
        price_usd = price  # Simplified

        # Extract box/papers from listing details
        title = item.get("title", "").lower()
        description = item.get("description", "").lower()
        bp_status = self._detect_box_papers(f"{title} {description}")

        return {
            "platform": "chrono24",
            "external_id": item.get("id"),
            "price": price,
            "currency": currency,
            "price_usd": price_usd,
            "box_papers_status": bp_status,
            "condition": item.get("condition"),
            "seller_name": item.get("merchant", {}).get("name"),
            "seller_rating": item.get("merchant", {}).get("rating"),
            "listing_url": item.get("url"),
            "image_url": item.get("image"),
            "location": item.get("location", {}).get("country"),
            "title": item.get("title"),
            "search_query": search_query
        }

    def _detect_box_papers(self, text: str) -> str:
        """Detect box & papers status from listing text."""
        text = text.lower()

        # Chrono24 often has structured fields, but we parse text as backup
        full_set_patterns = [
            "full set", "box and papers", "box & papers", "b&p",
            "complete set", "original box", "original papers",
            "with box, papers"
        ]
        for pattern in full_set_patterns:
            if pattern in text:
                return "full_set"

        papers_patterns = ["papers only", "with papers", "warranty card"]
        has_papers = any(p in text for p in papers_patterns)

        box_patterns = ["with box", "original box", "inner box", "outer box"]
        has_box = any(p in text for p in box_patterns)

        no_papers = "no papers" in text or "without papers" in text
        no_box = "no box" in text or "without box" in text

        if has_papers and not has_box:
            return "papers_only"
        if has_box and not has_papers:
            return "box_only"
        if no_box and no_papers:
            return "none"
        if has_box and has_papers:
            return "full_set"

        return "unknown"


# Singleton instance
chrono24_client = Chrono24Client()
