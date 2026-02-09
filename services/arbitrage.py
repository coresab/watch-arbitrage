"""
Arbitrage detection engine.
Compares listings across platforms and against market values.
"""

from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session

from models import Listing, MarketPrice, ArbitrageOpportunity, WatchReference
from config import Config


class ArbitrageEngine:
    """Detects arbitrage opportunities from listings."""

    def __init__(self, session: Session):
        self.session = session

    def analyze_all(self) -> list[ArbitrageOpportunity]:
        """
        Analyze all active listings and generate arbitrage opportunities.
        Returns newly created opportunities.
        """
        # Clear old opportunities
        self.session.query(ArbitrageOpportunity).filter(
            ArbitrageOpportunity.is_active == True
        ).update({"is_active": False})

        opportunities = []

        # Get all active listings grouped by reference
        references = self.session.query(WatchReference).all()

        for ref in references:
            active_listings = self.session.query(Listing).filter(
                Listing.watch_reference_id == ref.id,
                Listing.is_active == True
            ).all()

            if not active_listings:
                continue

            # Check for cross-platform arbitrage
            cross_platform_opps = self._find_cross_platform_arbitrage(ref, active_listings)
            opportunities.extend(cross_platform_opps)

            # Check for undervalued listings
            undervalued_opps = self._find_undervalued_listings(ref, active_listings)
            opportunities.extend(undervalued_opps)

        # Save all opportunities
        for opp in opportunities:
            self.session.add(opp)

        self.session.commit()
        return opportunities

    def _find_cross_platform_arbitrage(
        self,
        ref: WatchReference,
        listings: list[Listing]
    ) -> list[ArbitrageOpportunity]:
        """Find price differences between platforms for the same watch."""
        opportunities = []

        # Group by B&P status
        by_bp_status = {}
        for listing in listings:
            bp = listing.box_papers_status
            if bp not in by_bp_status:
                by_bp_status[bp] = []
            by_bp_status[bp].append(listing)

        # Compare within each B&P tier
        for bp_status, bp_listings in by_bp_status.items():
            if len(bp_listings) < 2:
                continue

            # Separate by platform
            ebay_listings = [l for l in bp_listings if l.platform == "ebay"]
            chrono_listings = [l for l in bp_listings if l.platform == "chrono24"]

            if not ebay_listings or not chrono_listings:
                continue

            # Find the cheapest on each platform
            cheapest_ebay = min(ebay_listings, key=lambda x: x.price_usd)
            cheapest_chrono = min(chrono_listings, key=lambda x: x.price_usd)

            avg_ebay = sum(l.price_usd for l in ebay_listings) / len(ebay_listings)
            avg_chrono = sum(l.price_usd for l in chrono_listings) / len(chrono_listings)

            # Check if eBay is cheaper (sell on Chrono24)
            if cheapest_ebay.price_usd < avg_chrono * 0.9:
                opp = self._create_opportunity(
                    listing=cheapest_ebay,
                    ref=ref,
                    opportunity_type="cross_platform",
                    estimated_sell_price=avg_chrono,
                    sell_platform="chrono24",
                    fair_market_value=avg_chrono
                )
                if opp:
                    opportunities.append(opp)

            # Check if Chrono24 is cheaper (sell on eBay)
            if cheapest_chrono.price_usd < avg_ebay * 0.9:
                opp = self._create_opportunity(
                    listing=cheapest_chrono,
                    ref=ref,
                    opportunity_type="cross_platform",
                    estimated_sell_price=avg_ebay,
                    sell_platform="ebay",
                    fair_market_value=avg_ebay
                )
                if opp:
                    opportunities.append(opp)

        return opportunities

    def _find_undervalued_listings(
        self,
        ref: WatchReference,
        listings: list[Listing]
    ) -> list[ArbitrageOpportunity]:
        """Find listings priced below market value."""
        opportunities = []

        # Get market prices by B&P status
        market_prices = self.session.query(MarketPrice).filter(
            MarketPrice.watch_reference_id == ref.id
        ).all()

        market_by_bp = {mp.box_papers_status: mp.market_price_usd for mp in market_prices}

        # If no market prices, calculate from listings
        if not market_by_bp:
            market_by_bp = self._calculate_market_prices(listings)

        for listing in listings:
            bp_status = listing.box_papers_status
            market_price = market_by_bp.get(bp_status) or market_by_bp.get("unknown")

            if not market_price:
                continue

            discount_pct = (market_price - listing.price_usd) / market_price

            if discount_pct >= Config.MIN_DISCOUNT_THRESHOLD:
                opp = self._create_opportunity(
                    listing=listing,
                    ref=ref,
                    opportunity_type="undervalued",
                    estimated_sell_price=market_price,
                    sell_platform=None,
                    fair_market_value=market_price
                )
                if opp:
                    opportunities.append(opp)

        return opportunities

    def _calculate_market_prices(self, listings: list[Listing]) -> dict[str, float]:
        """Calculate market price from listing averages when no external data."""
        by_bp = {}
        for listing in listings:
            bp = listing.box_papers_status
            if bp not in by_bp:
                by_bp[bp] = []
            by_bp[bp].append(listing.price_usd)

        return {bp: sum(prices) / len(prices) for bp, prices in by_bp.items() if prices}

    def _create_opportunity(
        self,
        listing: Listing,
        ref: WatchReference,
        opportunity_type: str,
        estimated_sell_price: float,
        sell_platform: Optional[str],
        fair_market_value: float
    ) -> Optional[ArbitrageOpportunity]:
        """Create an arbitrage opportunity with profit calculations."""
        buy_price = listing.price_usd

        # Calculate fees
        if sell_platform:
            fee_rate = Config.FEES.get(sell_platform, 0.10)
        else:
            # Assume selling on same platform or private
            fee_rate = Config.FEES.get(listing.platform, 0.10)

        platform_fee = estimated_sell_price * fee_rate
        shipping = Config.DEFAULT_SHIPPING_COST

        estimated_profit = estimated_sell_price - buy_price - platform_fee - shipping
        roi_percent = (estimated_profit / buy_price) * 100 if buy_price > 0 else 0
        discount_to_market = ((fair_market_value - buy_price) / fair_market_value) * 100

        # Filter by thresholds
        if estimated_profit < Config.MIN_PROFIT_THRESHOLD:
            return None
        if roi_percent < Config.MIN_ROI_THRESHOLD * 100:
            return None

        # Calculate confidence score
        confidence = self._calculate_confidence(listing, ref)

        return ArbitrageOpportunity(
            listing_id=listing.id,
            watch_reference_id=ref.id,
            opportunity_type=opportunity_type,
            buy_price=buy_price,
            buy_platform=listing.platform,
            box_papers_status=listing.box_papers_status,
            estimated_sell_price=estimated_sell_price,
            sell_platform=sell_platform,
            fair_market_value=fair_market_value,
            discount_to_market_pct=discount_to_market,
            platform_fee_estimate=platform_fee,
            shipping_estimate=shipping,
            estimated_profit=estimated_profit,
            roi_percent=roi_percent,
            confidence_score=confidence,
            is_active=True
        )

    def _calculate_confidence(self, listing: Listing, ref: WatchReference) -> int:
        """Calculate confidence score (0-100) for an opportunity."""
        score = 50  # Base score

        # Seller rating bonus
        if listing.seller_rating:
            if listing.seller_rating >= 99:
                score += 15
            elif listing.seller_rating >= 95:
                score += 10
            elif listing.seller_rating >= 90:
                score += 5

        # B&P status clarity
        if listing.box_papers_status != "unknown":
            score += 10

        # Platform reliability
        if listing.platform == "ebay":
            score += 5  # eBay has buyer protection

        # Listing freshness (would need more data)
        # For now, just cap at 100
        return min(score, 100)
