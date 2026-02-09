"""
eBay Browse API client for fetching watch listings.
"""

import base64
import requests
from datetime import datetime, timedelta
from typing import Optional
import re

from config import Config


class eBayClient:
    """Client for eBay Browse API."""

    def __init__(self):
        self.client_id = Config.EBAY_CLIENT_ID
        self.client_secret = Config.EBAY_CLIENT_SECRET
        self.base_url = Config.EBAY_API_BASE
        self._access_token = None
        self._token_expires = None

    def _get_access_token(self) -> str:
        """Get OAuth access token (cached until expiry)."""
        if self._access_token and self._token_expires and datetime.now() < self._token_expires:
            return self._access_token

        # Request new token
        auth_url = f"{self.base_url}/identity/v1/oauth2/token"
        credentials = base64.b64encode(
            f"{self.client_id}:{self.client_secret}".encode()
        ).decode()

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Basic {credentials}"
        }

        data = {
            "grant_type": "client_credentials",
            "scope": "https://api.ebay.com/oauth/api_scope"
        }

        response = requests.post(auth_url, headers=headers, data=data)
        response.raise_for_status()

        token_data = response.json()
        self._access_token = token_data["access_token"]
        self._token_expires = datetime.now() + timedelta(seconds=token_data["expires_in"] - 60)

        return self._access_token

    def search_watches(
        self,
        query: str,
        min_price: int = 3000,
        max_price: Optional[int] = None,
        limit: int = 50
    ) -> list[dict]:
        """
        Search for watch listings on eBay.

        Args:
            query: Search query (e.g., "Rolex 126610LN")
            min_price: Minimum price in USD
            max_price: Maximum price in USD (optional)
            limit: Maximum results to return

        Returns:
            List of normalized listing dictionaries
        """
        token = self._get_access_token()

        # Build price filter
        price_filter = f"price:[{min_price}.."
        if max_price:
            price_filter += f"{max_price}"
        price_filter += "]"

        # Category 31387 is "Wristwatches"
        params = {
            "q": query,
            "filter": f"{price_filter},categoryIds:{{31387}}",
            "limit": limit,
            "sort": "price"
        }

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "X-EBAY-C-MARKETPLACE-ID": "EBAY_US"
        }

        url = f"{self.base_url}/buy/browse/v1/item_summary/search"
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()

        data = response.json()
        items = data.get("itemSummaries", [])

        return [self._normalize_listing(item, query) for item in items]

    def _normalize_listing(self, item: dict, search_query: str) -> dict:
        """Convert eBay item to our normalized listing format."""
        price_info = item.get("price", {})
        price = float(price_info.get("value", 0))
        currency = price_info.get("currency", "USD")

        # Convert to USD if needed (simplified - assumes USD for now)
        price_usd = price

        # Extract box/papers status from title and condition
        title = item.get("title", "").lower()
        condition = item.get("condition", "")
        bp_status = self._detect_box_papers(title)

        return {
            "platform": "ebay",
            "external_id": item.get("itemId"),
            "price": price,
            "currency": currency,
            "price_usd": price_usd,
            "box_papers_status": bp_status,
            "condition": condition,
            "seller_name": item.get("seller", {}).get("username"),
            "seller_rating": item.get("seller", {}).get("feedbackPercentage"),
            "listing_url": item.get("itemWebUrl"),
            "image_url": item.get("image", {}).get("imageUrl"),
            "location": item.get("itemLocation", {}).get("country"),
            "title": item.get("title"),
            "search_query": search_query
        }

    def _detect_box_papers(self, text: str) -> str:
        """Detect box & papers status from listing text."""
        text = text.lower()

        # Full set indicators
        full_set_patterns = [
            "full set", "box and papers", "box & papers", "b&p",
            "complete set", "with box and papers", "w/ box papers"
        ]
        for pattern in full_set_patterns:
            if pattern in text:
                return "full_set"

        # Papers only
        papers_patterns = ["papers only", "with papers", "w/ papers", "card only"]
        for pattern in papers_patterns:
            if pattern in text:
                return "papers_only"

        # Box only
        box_patterns = ["box only", "with box", "w/ box"]
        no_papers = "no papers" in text or "without papers" in text
        for pattern in box_patterns:
            if pattern in text or no_papers:
                return "box_only"

        # No box or papers
        no_bp_patterns = ["no box", "no papers", "watch only", "naked"]
        if any(p in text for p in no_bp_patterns):
            return "none"

        return "unknown"


# Singleton instance
ebay_client = eBayClient()
