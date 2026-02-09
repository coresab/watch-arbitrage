from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
import enum

from config import Config

Base = declarative_base()


class BoxPapersStatus(enum.Enum):
    FULL_SET = "full_set"
    PAPERS_ONLY = "papers_only"
    BOX_ONLY = "box_only"
    NONE = "none"
    UNKNOWN = "unknown"


class Platform(enum.Enum):
    EBAY = "ebay"
    CHRONO24 = "chrono24"


class Brand(Base):
    __tablename__ = "brands"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    slug = Column(String(100), nullable=False, unique=True)

    watches = relationship("WatchReference", back_populates="brand")


class WatchReference(Base):
    __tablename__ = "watch_references"

    id = Column(Integer, primary_key=True)
    brand_id = Column(Integer, ForeignKey("brands.id"), nullable=False)
    reference_number = Column(String(100), nullable=False, index=True)
    model_name = Column(String(200))
    collection = Column(String(100))
    case_size_mm = Column(Integer)
    movement = Column(String(100))
    image_url = Column(String(500))
    watchcharts_uuid = Column(String(100))

    brand = relationship("Brand", back_populates="watches")
    listings = relationship("Listing", back_populates="watch_reference")
    market_prices = relationship("MarketPrice", back_populates="watch_reference")
    price_history = relationship("PriceHistory", back_populates="watch_reference")


class Listing(Base):
    __tablename__ = "listings"

    id = Column(Integer, primary_key=True)
    watch_reference_id = Column(Integer, ForeignKey("watch_references.id"), nullable=False)
    platform = Column(String(20), nullable=False)
    external_id = Column(String(100))  # Platform's listing ID
    price = Column(Float, nullable=False)
    currency = Column(String(10), default="USD")
    price_usd = Column(Float, nullable=False)
    box_papers_status = Column(String(20), default="unknown")
    condition = Column(String(200))
    seller_name = Column(String(200))
    seller_rating = Column(Float)
    listing_url = Column(String(500), nullable=False)
    image_url = Column(String(500))
    location = Column(String(200))
    is_active = Column(Boolean, default=True)
    scraped_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

    watch_reference = relationship("WatchReference", back_populates="listings")


class MarketPrice(Base):
    __tablename__ = "market_prices"

    id = Column(Integer, primary_key=True)
    watch_reference_id = Column(Integer, ForeignKey("watch_references.id"), nullable=False)
    box_papers_status = Column(String(20), nullable=False)
    market_price_usd = Column(Float, nullable=False)
    dealer_price_usd = Column(Float)
    source = Column(String(50), default="calculated")  # "watchcharts" or "calculated"
    recorded_at = Column(DateTime, default=datetime.utcnow)

    watch_reference = relationship("WatchReference", back_populates="market_prices")


class PriceHistory(Base):
    __tablename__ = "price_history"

    id = Column(Integer, primary_key=True)
    watch_reference_id = Column(Integer, ForeignKey("watch_references.id"), nullable=False)
    date = Column(DateTime, nullable=False)
    market_price_usd = Column(Float)
    avg_listing_price = Column(Float)
    num_listings = Column(Integer)
    source = Column(String(50))

    watch_reference = relationship("WatchReference", back_populates="price_history")


class ArbitrageOpportunity(Base):
    __tablename__ = "arbitrage_opportunities"

    id = Column(Integer, primary_key=True)
    listing_id = Column(Integer, ForeignKey("listings.id"), nullable=False)
    watch_reference_id = Column(Integer, ForeignKey("watch_references.id"), nullable=False)
    opportunity_type = Column(String(20), nullable=False)  # "cross_platform" or "undervalued"
    buy_price = Column(Float, nullable=False)
    buy_platform = Column(String(20), nullable=False)
    box_papers_status = Column(String(20))
    estimated_sell_price = Column(Float)
    sell_platform = Column(String(20))
    fair_market_value = Column(Float)
    discount_to_market_pct = Column(Float)
    platform_fee_estimate = Column(Float)
    shipping_estimate = Column(Float, default=75)
    estimated_profit = Column(Float)
    roi_percent = Column(Float)
    confidence_score = Column(Integer)  # 0-100
    found_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    listing = relationship("Listing")
    watch_reference = relationship("WatchReference")


# Database setup
engine = create_engine(Config.DATABASE_URL, echo=Config.DEBUG)


def init_db():
    """Create all tables."""
    Base.metadata.create_all(engine)


def get_session():
    """Get a new database session."""
    Session = sessionmaker(bind=engine)
    return Session()
