"""
Generate mock listings and arbitrage opportunities for testing.
Run this after seed_data.py to populate the dashboard.
"""

import random
from datetime import datetime, timedelta

from models import init_db, get_session, Brand, WatchReference, Listing, ArbitrageOpportunity, MarketPrice

# Mock listing data - realistic prices for popular references
MOCK_LISTINGS = [
    # Rolex
    {"ref": "126610LN", "market": 14500, "listings": [
        {"platform": "ebay", "price": 12800, "bp": "full_set", "seller": "watchdealer123", "rating": 99.2},
        {"platform": "ebay", "price": 13200, "bp": "full_set", "seller": "luxurywatch_nyc", "rating": 98.5},
        {"platform": "chrono24", "price": 14200, "bp": "full_set", "seller": "Prestige Time", "rating": 4.8},
        {"platform": "chrono24", "price": 14800, "bp": "full_set", "seller": "WatchBox", "rating": 4.9},
        {"platform": "ebay", "price": 11500, "bp": "papers_only", "seller": "timer_deals", "rating": 97.1},
        {"platform": "chrono24", "price": 13500, "bp": "papers_only", "seller": "Crown Watch", "rating": 4.7},
    ]},
    {"ref": "126710BLRO", "market": 21000, "listings": [
        {"platform": "ebay", "price": 18500, "bp": "full_set", "seller": "pepsi_watches", "rating": 99.5},
        {"platform": "chrono24", "price": 20500, "bp": "full_set", "seller": "Hodinkee Shop", "rating": 5.0},
        {"platform": "chrono24", "price": 21200, "bp": "full_set", "seller": "Bob's Watches", "rating": 4.9},
        {"platform": "ebay", "price": 17200, "bp": "box_only", "seller": "vintage_rollie", "rating": 96.8},
    ]},
    {"ref": "116500LN", "market": 32000, "listings": [
        {"platform": "ebay", "price": 28500, "bp": "full_set", "seller": "daytona_king", "rating": 99.8},
        {"platform": "chrono24", "price": 31500, "bp": "full_set", "seller": "Authentic Watches", "rating": 4.9},
        {"platform": "ebay", "price": 27000, "bp": "papers_only", "seller": "lux_chrono", "rating": 98.2},
        {"platform": "chrono24", "price": 33000, "bp": "full_set", "seller": "DavidSW", "rating": 5.0},
    ]},
    # Omega
    {"ref": "310.30.42.50.01.001", "market": 6800, "listings": [
        {"platform": "ebay", "price": 5400, "bp": "full_set", "seller": "speedy_fan", "rating": 99.1},
        {"platform": "ebay", "price": 5800, "bp": "full_set", "seller": "omega_collector", "rating": 98.7},
        {"platform": "chrono24", "price": 6500, "bp": "full_set", "seller": "Omega Boutique", "rating": 4.8},
        {"platform": "chrono24", "price": 6900, "bp": "full_set", "seller": "Moon Watch Co", "rating": 4.7},
        {"platform": "ebay", "price": 4800, "bp": "none", "seller": "watch_deals_99", "rating": 95.5},
    ]},
    {"ref": "210.30.42.20.03.001", "market": 5200, "listings": [
        {"platform": "ebay", "price": 4200, "bp": "full_set", "seller": "seamaster_shop", "rating": 98.9},
        {"platform": "chrono24", "price": 5000, "bp": "full_set", "seller": "Dive Watch Store", "rating": 4.6},
        {"platform": "ebay", "price": 3900, "bp": "box_only", "seller": "blue_dial_dan", "rating": 97.3},
    ]},
    # Tudor
    {"ref": "79230N", "market": 3800, "listings": [
        {"platform": "ebay", "price": 3100, "bp": "full_set", "seller": "tudor_time", "rating": 99.0},
        {"platform": "chrono24", "price": 3600, "bp": "full_set", "seller": "Black Bay Bros", "rating": 4.7},
        {"platform": "ebay", "price": 2900, "bp": "papers_only", "seller": "heritage_watches", "rating": 96.5},
        {"platform": "chrono24", "price": 3900, "bp": "full_set", "seller": "Tudor AD", "rating": 4.9},
    ]},
    {"ref": "M79830RB-0001", "market": 4200, "listings": [
        {"platform": "ebay", "price": 3500, "bp": "full_set", "seller": "gmt_hunter", "rating": 98.4},
        {"platform": "chrono24", "price": 4000, "bp": "full_set", "seller": "GMT World", "rating": 4.8},
        {"platform": "ebay", "price": 3200, "bp": "none", "seller": "watch_flipper", "rating": 94.2},
    ]},
    # Cartier
    {"ref": "WSSA0018", "market": 6500, "listings": [
        {"platform": "ebay", "price": 5400, "bp": "full_set", "seller": "santos_lover", "rating": 99.3},
        {"platform": "chrono24", "price": 6200, "bp": "full_set", "seller": "Cartier Specialist", "rating": 4.8},
        {"platform": "ebay", "price": 5100, "bp": "papers_only", "seller": "elegant_time", "rating": 97.8},
    ]},
    # Audemars Piguet
    {"ref": "15500ST.OO.1220ST.01", "market": 42000, "listings": [
        {"platform": "ebay", "price": 37500, "bp": "full_set", "seller": "ap_specialist", "rating": 99.7},
        {"platform": "chrono24", "price": 41000, "bp": "full_set", "seller": "Royal Oak Club", "rating": 4.9},
        {"platform": "chrono24", "price": 43500, "bp": "full_set", "seller": "AP Boutique", "rating": 5.0},
        {"platform": "ebay", "price": 35000, "bp": "papers_only", "seller": "luxury_ap", "rating": 98.1},
    ]},
    # IWC
    {"ref": "IW371605", "market": 8500, "listings": [
        {"platform": "ebay", "price": 6900, "bp": "full_set", "seller": "iwc_collector", "rating": 98.6},
        {"platform": "chrono24", "price": 8200, "bp": "full_set", "seller": "Portugieser Pro", "rating": 4.7},
        {"platform": "ebay", "price": 6500, "bp": "box_only", "seller": "chrono_deals", "rating": 96.9},
    ]},
]


def generate_mock_data():
    """Generate mock listings and detect arbitrage opportunities."""
    init_db()
    session = get_session()

    try:
        # Clear existing listings and opportunities
        session.query(ArbitrageOpportunity).delete()
        session.query(Listing).delete()
        session.query(MarketPrice).delete()
        session.commit()

        total_listings = 0

        for watch_data in MOCK_LISTINGS:
            ref_num = watch_data["ref"]
            market_price = watch_data["market"]

            # Find the watch reference
            ref = session.query(WatchReference).filter(
                WatchReference.reference_number == ref_num
            ).first()

            if not ref:
                print(f"Reference {ref_num} not found, skipping...")
                continue

            # Add market price
            mp = MarketPrice(
                watch_reference_id=ref.id,
                box_papers_status="full_set",
                market_price_usd=market_price,
                source="mock"
            )
            session.add(mp)

            # Add listings
            for listing_data in watch_data["listings"]:
                listing = Listing(
                    watch_reference_id=ref.id,
                    platform=listing_data["platform"],
                    external_id=f"mock_{ref_num}_{listing_data['platform']}_{random.randint(1000,9999)}",
                    price=listing_data["price"],
                    currency="USD",
                    price_usd=listing_data["price"],
                    box_papers_status=listing_data["bp"],
                    condition="Pre-owned, Excellent",
                    seller_name=listing_data["seller"],
                    seller_rating=listing_data["rating"],
                    listing_url=f"https://example.com/listing/{random.randint(10000,99999)}",
                    image_url=f"https://picsum.photos/seed/{ref_num}/300/300",
                    location="United States",
                    is_active=True,
                    scraped_at=datetime.utcnow() - timedelta(hours=random.randint(1, 12))
                )
                session.add(listing)
                total_listings += 1

        session.commit()
        print(f"Created {total_listings} mock listings")

        # Now detect arbitrage opportunities
        from services.arbitrage import ArbitrageEngine
        engine = ArbitrageEngine(session)
        opportunities = engine.analyze_all()
        print(f"Found {len(opportunities)} arbitrage opportunities")

        session.commit()

    except Exception as e:
        session.rollback()
        print(f"Error: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    # First run seed_data to ensure brands/references exist
    from seed_data import seed_database
    print("Seeding watch catalog...")
    seed_database()

    print("\nGenerating mock listings...")
    generate_mock_data()

    print("\nDone! Run 'python app.py' to start the dashboard.")
