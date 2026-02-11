"""
Luxury Watch Arbitrage Dashboard
Built with Dash + Plotly
"""

import dash
from dash import html, dcc, dash_table, callback, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime

from models import init_db, get_session, Brand, WatchReference, Listing, ArbitrageOpportunity
from services import ArbitrageEngine, Scanner
from config import Config

# Initialize database
init_db()

# Auto-seed if database is empty
def auto_seed_if_needed():
    """Seed the database if no brands exist."""
    session = get_session()
    brand_count = session.query(Brand).count()
    session.close()

    if brand_count == 0:
        print("Database empty - running seed_data.py...")
        from seed_data import seed_database
        seed_database()
        print("Seeding complete!")

auto_seed_if_needed()

# Initialize Dash app with Bootstrap theme
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.DARKLY],
    suppress_callback_exceptions=True,
    title="Watch Arbitrage"
)

server = app.server  # For deployment

# Custom CSS for Helvetica font
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            * {
                font-family: Helvetica, Arial, sans-serif !important;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# Color scheme
COLORS = {
    "profit": "#00d97e",
    "loss": "#e63757",
    "neutral": "#6c757d",
    "ebay": "#0064d2",
    "chrono24": "#f5a623",
    "background": "#1a1d21",
    "card": "#2c3034"
}


def get_brands():
    """Get all brands from database."""
    session = get_session()
    brands = session.query(Brand).all()
    session.close()
    return [{"label": b.name, "value": b.id} for b in brands]


def get_opportunities(brand_id=None, min_profit=0, min_roi=0, bp_status=None):
    """Get arbitrage opportunities with filters."""
    session = get_session()
    query = session.query(ArbitrageOpportunity).filter(
        ArbitrageOpportunity.is_active == True
    )

    if brand_id:
        query = query.join(WatchReference).filter(WatchReference.brand_id == brand_id)
    if min_profit > 0:
        query = query.filter(ArbitrageOpportunity.estimated_profit >= min_profit)
    if min_roi > 0:
        query = query.filter(ArbitrageOpportunity.roi_percent >= min_roi)
    if bp_status and bp_status != "all":
        query = query.filter(ArbitrageOpportunity.box_papers_status == bp_status)

    opportunities = query.order_by(ArbitrageOpportunity.estimated_profit.desc()).limit(50).all()

    results = []
    for opp in opportunities:
        ref = session.query(WatchReference).get(opp.watch_reference_id)
        brand = session.query(Brand).get(ref.brand_id)
        listing = session.query(Listing).get(opp.listing_id)

        results.append({
            "id": opp.id,
            "brand": brand.name,
            "model": ref.model_name,
            "reference": ref.reference_number,
            "buy_price": opp.buy_price,
            "sell_price": opp.estimated_sell_price,
            "profit": opp.estimated_profit,
            "roi": opp.roi_percent,
            "discount": opp.discount_to_market_pct,
            "platform": opp.buy_platform,
            "bp_status": opp.box_papers_status,
            "confidence": opp.confidence_score,
            "url": listing.listing_url if listing else None,
            "image": listing.image_url if listing else None
        })

    session.close()
    return results


def get_stats():
    """Get dashboard statistics."""
    from sqlalchemy import func
    session = get_session()

    total_opps = session.query(ArbitrageOpportunity).filter(
        ArbitrageOpportunity.is_active == True
    ).count()

    total_listings = session.query(Listing).filter(Listing.is_active == True).count()

    avg_profit = session.query(func.avg(ArbitrageOpportunity.estimated_profit)).filter(
        ArbitrageOpportunity.is_active == True
    ).scalar() or 0

    session.close()

    return {
        "total_opportunities": total_opps,
        "total_listings": total_listings,
        "avg_profit": avg_profit
    }


# Navbar
navbar = dbc.Navbar(
    dbc.Container([
        dbc.NavbarBrand("⌚ Watch Arbitrage", className="ms-2 fs-4 fw-bold"),
        dbc.Nav([
            dbc.NavItem(dbc.NavLink("Dashboard", href="/", active="exact")),
            dbc.NavItem(dbc.NavLink("Explorer", href="/explorer")),
            dbc.NavItem(dbc.NavLink("Market", href="/market")),
        ], className="ms-auto", navbar=True),
        dbc.Button("Scan Now", id="scan-button", color="success", className="ms-3", size="sm"),
    ], fluid=True),
    color="dark",
    dark=True,
    className="mb-4"
)


# Filter bar
filter_bar = dbc.Card([
    dbc.CardBody([
        dbc.Row([
            dbc.Col([
                html.Label("Brand", className="text-muted small"),
                dcc.Dropdown(
                    id="brand-filter",
                    options=[{"label": "All Brands", "value": ""}] + get_brands(),
                    value="",
                    placeholder="All Brands",
                    className="mb-2"
                )
            ], md=3),
            dbc.Col([
                html.Label("Min Profit ($)", className="text-muted small"),
                dcc.Input(
                    id="min-profit-filter",
                    type="number",
                    value=200,
                    min=0,
                    className="form-control"
                )
            ], md=2),
            dbc.Col([
                html.Label("Min ROI (%)", className="text-muted small"),
                dcc.Input(
                    id="min-roi-filter",
                    type="number",
                    value=5,
                    min=0,
                    className="form-control"
                )
            ], md=2),
            dbc.Col([
                html.Label("Box & Papers", className="text-muted small"),
                dcc.Dropdown(
                    id="bp-filter",
                    options=[
                        {"label": "All", "value": "all"},
                        {"label": "Full Set", "value": "full_set"},
                        {"label": "Papers Only", "value": "papers_only"},
                        {"label": "Box Only", "value": "box_only"},
                        {"label": "None", "value": "none"},
                    ],
                    value="all",
                    className="mb-2"
                )
            ], md=3),
            dbc.Col([
                html.Label(" ", className="text-muted small d-block"),
                dbc.Button("Apply Filters", id="apply-filters", color="primary", className="w-100")
            ], md=2),
        ])
    ])
], className="mb-4")


# Opportunity card component
def make_opportunity_card(opp):
    """Create a card for a single arbitrage opportunity."""
    platform_color = COLORS.get(opp["platform"], COLORS["neutral"])

    bp_labels = {
        "full_set": "Full Set",
        "papers_only": "Papers Only",
        "box_only": "Box Only",
        "none": "No B&P",
        "unknown": "Unknown"
    }

    return dbc.Card([
        dbc.Row([
            dbc.Col([
                html.Img(
                    src=opp["image"] or "https://via.placeholder.com/120",
                    style={"width": "100%", "maxWidth": "120px", "borderRadius": "8px"}
                )
            ], width=2, className="d-flex align-items-center"),
            dbc.Col([
                html.H5(f"{opp['brand']} {opp['model']}", className="mb-1"),
                html.P(f"Ref: {opp['reference']}", className="text-muted mb-1 small"),
                dbc.Badge(bp_labels.get(opp["bp_status"], "Unknown"), color="secondary", className="me-2"),
                dbc.Badge(opp["platform"].upper(), style={"backgroundColor": platform_color}),
            ], width=4),
            dbc.Col([
                html.Div([
                    html.Span("Buy: ", className="text-muted"),
                    html.Span(f"${opp['buy_price']:,.0f}", className="fw-bold")
                ]),
                html.Div([
                    html.Span("Sell: ", className="text-muted"),
                    html.Span(f"${opp['sell_price']:,.0f}", className="fw-bold")
                ]),
            ], width=2, className="text-center"),
            dbc.Col([
                html.H4(f"${opp['profit']:,.0f}", className="text-success mb-0"),
                html.Small(f"{opp['roi']:.1f}% ROI", className="text-muted"),
            ], width=2, className="text-center"),
            dbc.Col([
                dbc.Button(
                    "View Listing",
                    href=opp["url"],
                    target="_blank",
                    color="outline-light",
                    size="sm",
                    className="mb-2 w-100"
                ),
                html.Div([
                    html.Small(f"Confidence: {opp['confidence']}%", className="text-muted")
                ], className="text-center")
            ], width=2, className="d-flex flex-column justify-content-center"),
        ], className="g-0 p-3")
    ], className="mb-3", style={"backgroundColor": COLORS["card"]})


# Main dashboard layout
dashboard_layout = html.Div([
    # Stats row
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H6("Active Opportunities", className="text-muted"),
                    html.H3(id="stat-opportunities", children="0", className="text-success")
                ])
            ])
        ], md=4),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H6("Total Listings", className="text-muted"),
                    html.H3(id="stat-listings", children="0")
                ])
            ])
        ], md=4),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H6("Avg Profit", className="text-muted"),
                    html.H3(id="stat-avg-profit", children="$0", className="text-success")
                ])
            ])
        ], md=4),
    ], className="mb-4"),

    # Filters
    filter_bar,

    # Opportunities list
    html.Div(id="opportunities-list"),

    # Scan status
    dcc.Loading(
        id="loading-scan",
        type="default",
        children=html.Div(id="scan-output")
    ),

    # Auto-refresh interval (every 5 minutes)
    dcc.Interval(id="refresh-interval", interval=5*60*1000, n_intervals=0)
])


# App layout with routing
app.layout = html.Div([
    dcc.Location(id="url", refresh=False),
    navbar,
    dbc.Container([
        html.Div(id="page-content")
    ], fluid=True, className="px-4")
])


# Routing callback
@callback(
    Output("page-content", "children"),
    Input("url", "pathname")
)
def display_page(pathname):
    if pathname == "/explorer":
        return html.Div([
            html.H3("Watch Explorer"),
            html.P("Coming soon - browse all watches and compare prices.", className="text-muted")
        ])
    elif pathname == "/market":
        return html.Div([
            html.H3("Market Overview"),
            html.P("Coming soon - brand trends and top movers.", className="text-muted")
        ])
    else:
        return dashboard_layout


# Update opportunities list
@callback(
    Output("opportunities-list", "children"),
    [Input("apply-filters", "n_clicks"),
     Input("refresh-interval", "n_intervals")],
    [State("brand-filter", "value"),
     State("min-profit-filter", "value"),
     State("min-roi-filter", "value"),
     State("bp-filter", "value")]
)
def update_opportunities(n_clicks, n_intervals, brand_id, min_profit, min_roi, bp_status):
    opportunities = get_opportunities(
        brand_id=brand_id if brand_id else None,
        min_profit=min_profit or 0,
        min_roi=min_roi or 0,
        bp_status=bp_status
    )

    if not opportunities:
        return dbc.Alert(
            "No arbitrage opportunities found. Try adjusting filters or run a scan.",
            color="info"
        )

    return html.Div([make_opportunity_card(opp) for opp in opportunities])


# Scan button callback
@callback(
    Output("scan-output", "children"),
    Input("scan-button", "n_clicks"),
    prevent_initial_call=True
)
def run_scan(n_clicks):
    if n_clicks:
        try:
            print("=== SCAN STARTED ===")

            # Check database state
            session = get_session()
            brand_count = session.query(Brand).count()
            ref_count = session.query(WatchReference).count()
            print(f"Database state: {brand_count} brands, {ref_count} references")
            session.close()

            if ref_count == 0:
                return dbc.Alert(
                    "No watch references in database. Seeding failed.",
                    color="danger"
                )

            print("Creating scanner...")
            scanner = Scanner()

            print("Starting scan_all_references...")
            stats = scanner.scan_all_references()
            print(f"Scan stats: {stats}")

            # Run arbitrage detection
            print("Running arbitrage detection...")
            session = get_session()
            engine = ArbitrageEngine(session)
            opportunities = engine.analyze_all()
            session.close()

            print(f"=== SCAN COMPLETE: {len(opportunities)} opportunities ===")

            return dbc.Alert(
                f"Scan complete! Found {len(opportunities)} opportunities from "
                f"{stats['ebay_listings']} eBay + {stats['chrono24_listings']} Chrono24 listings.",
                color="success",
                dismissable=True
            )
        except Exception as e:
            import traceback
            error_msg = traceback.format_exc()
            print(f"=== SCAN ERROR ===\n{error_msg}")
            return dbc.Alert(
                f"Scan failed: {str(e)}",
                color="danger",
                dismissable=True
            )
    return ""


# Update stats
@callback(
    [Output("stat-opportunities", "children"),
     Output("stat-listings", "children"),
     Output("stat-avg-profit", "children")],
    Input("refresh-interval", "n_intervals")
)
def update_stats(n):
    session = get_session()

    opps = session.query(ArbitrageOpportunity).filter(
        ArbitrageOpportunity.is_active == True
    ).count()

    listings = session.query(Listing).filter(Listing.is_active == True).count()

    from sqlalchemy import func
    avg = session.query(func.avg(ArbitrageOpportunity.estimated_profit)).filter(
        ArbitrageOpportunity.is_active == True
    ).scalar() or 0

    session.close()

    return str(opps), str(listings), f"${avg:,.0f}"


if __name__ == "__main__":
    app.run(debug=Config.DEBUG, host="0.0.0.0", port=8050)
