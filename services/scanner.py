"""
Scanner service that fetches listings from all platforms.
"""

from datetime import datetime
from typing import Optional

from models import get_session, WatchReference, Listing, Brand
from api import ebay_client, chrono24_client
from config import Config


class Scanner:
    """Scans platforms for watch listings."""

    def __init__(self):
        self.session = get_session()

    def scan_all_references(self) -> dict:
        """
        Scan all watch references across all platforms.
        Returns stats about the scan.
        """
        stats = {
            "references_scanned": 0,
            "ebay_listings": 0,
            "chrono24_listings": 0,
            "errors": []
        }

        references = self.session.query(WatchReference).all()

        for ref in references:
            brand = self.session.query(Brand).get(ref.brand_id)
            query = f"{brand.name} {ref.reference_number}"

            print(f"Scanning: {query}")

            # Scan eBay
            try:
                ebay_results = ebay_client.search_watches(
                    query=query,
                    min_price=Config.MIN_PRICE_USD,
                    limit=25
                )
                saved = self._save_listings(ebay_results, ref.id)
                stats["ebay_listings"] += saved
            except Exception as e:
                stats["errors"].append(f"eBay error for {query}: {str(e)}")

            # Scan Chrono24 (if available)
            if chrono24_client.is_available():
                try:
                    chrono_results = chrono24_client.search_watches(
                        query=query,
                        min_price=Config.MIN_PRICE_USD,
                        limit=25
                    )
                    saved = self._save_listings(chrono_results, ref.id)
                    stats["chrono24_listings"] += saved
                except Exception as e:
                    stats["errors"].append(f"Chrono24 error for {query}: {str(e)}")

            stats["references_scanned"] += 1

        return stats

    def scan_single_reference(self, reference_number: str) -> dict:
        """Scan a single reference across all platforms."""
        ref = self.session.query(WatchReference).filter(
            WatchReference.reference_number == reference_number
        ).first()

        if not ref:
            return {"error": f"Reference {reference_number} not found"}

        brand = self.session.query(Brand).get(ref.brand_id)
        query = f"{brand.name} {ref.reference_number}"

        stats = {"ebay": 0, "chrono24": 0, "errors": []}

        # eBay
        try:
            results = ebay_client.search_watches(query, Config.MIN_PRICE_USD)
            stats["ebay"] = self._save_listings(results, ref.id)
        except Exception as e:
            stats["errors"].append(str(e))

        # Chrono24
        if chrono24_client.is_available():
            try:
                results = chrono24_client.search_watches(query, Config.MIN_PRICE_USD)
                stats["chrono24"] = self._save_listings(results, ref.id)
            except Exception as e:
                stats["errors"].append(str(e))

        return stats

    def _save_listings(self, listings: list[dict], reference_id: int) -> int:
        """Save listings to database, avoiding duplicates."""
        saved_count = 0

        for listing_data in listings:
            # Check for existing listing by external ID and platform
            existing = self.session.query(Listing).filter(
                Listing.external_id == listing_data.get("external_id"),
                Listing.platform == listing_data.get("platform")
            ).first()

            if existing:
                # Update existing listing
                existing.price = listing_data["price"]
                existing.price_usd = listing_data["price_usd"]
                existing.is_active = True
                existing.scraped_at = datetime.utcnow()
            else:
                # Create new listing
                listing = Listing(
                    watch_reference_id=reference_id,
                    platform=listing_data["platform"],
                    external_id=listing_data.get("external_id"),
                    price=listing_data["price"],
                    currency=listing_data.get("currency", "USD"),
                    price_usd=listing_data["price_usd"],
                    box_papers_status=listing_data.get("box_papers_status", "unknown"),
                    condition=listing_data.get("condition"),
                    seller_name=listing_data.get("seller_name"),
                    seller_rating=listing_data.get("seller_rating"),
                    listing_url=listing_data["listing_url"],
                    image_url=listing_data.get("image_url"),
                    location=listing_data.get("location"),
                    is_active=True
                )
                self.session.add(listing)
                saved_count += 1

        self.session.commit()
        return saved_count

    def mark_stale_listings(self, hours: int = 24):
        """Mark listings older than X hours as inactive."""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        self.session.query(Listing).filter(
            Listing.scraped_at < cutoff,
            Listing.is_active == True
        ).update({"is_active": False})
        self.session.commit()


# Add missing import
from datetime import timedelta
