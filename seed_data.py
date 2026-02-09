"""
Seed the database with popular watch references.
Run this once after setting up the database.
"""

from models import init_db, get_session, Brand, WatchReference

# Popular references for each brand (5-10 per brand)
SEED_DATA = {
    "Rolex": {
        "slug": "rolex",
        "watches": [
            {"ref": "126610LN", "model": "Submariner Date", "collection": "Submariner", "size": 41},
            {"ref": "126610LV", "model": "Submariner Date Kermit", "collection": "Submariner", "size": 41},
            {"ref": "124060", "model": "Submariner No Date", "collection": "Submariner", "size": 41},
            {"ref": "126711CHNR", "model": "GMT-Master II Root Beer", "collection": "GMT-Master", "size": 40},
            {"ref": "126710BLRO", "model": "GMT-Master II Pepsi", "collection": "GMT-Master", "size": 40},
            {"ref": "126710BLNR", "model": "GMT-Master II Batman", "collection": "GMT-Master", "size": 40},
            {"ref": "116500LN", "model": "Daytona", "collection": "Daytona", "size": 40},
            {"ref": "126334", "model": "Datejust 41", "collection": "Datejust", "size": 41},
            {"ref": "226570", "model": "Explorer II", "collection": "Explorer", "size": 42},
            {"ref": "124270", "model": "Explorer", "collection": "Explorer", "size": 36},
        ]
    },
    "Patek Philippe": {
        "slug": "patek-philippe",
        "watches": [
            {"ref": "5711/1A-010", "model": "Nautilus Blue", "collection": "Nautilus", "size": 40},
            {"ref": "5712/1A-001", "model": "Nautilus Power Reserve", "collection": "Nautilus", "size": 40},
            {"ref": "5167A-001", "model": "Aquanaut", "collection": "Aquanaut", "size": 40},
            {"ref": "5168G-001", "model": "Aquanaut Travel Time", "collection": "Aquanaut", "size": 42},
            {"ref": "5726/1A-014", "model": "Nautilus Annual Calendar", "collection": "Nautilus", "size": 40},
            {"ref": "5205G-001", "model": "Complications Annual Calendar", "collection": "Complications", "size": 40},
        ]
    },
    "Audemars Piguet": {
        "slug": "audemars-piguet",
        "watches": [
            {"ref": "15500ST.OO.1220ST.01", "model": "Royal Oak Blue", "collection": "Royal Oak", "size": 41},
            {"ref": "15500ST.OO.1220ST.02", "model": "Royal Oak Black", "collection": "Royal Oak", "size": 41},
            {"ref": "15500ST.OO.1220ST.04", "model": "Royal Oak Grey", "collection": "Royal Oak", "size": 41},
            {"ref": "26331ST.OO.1220ST.01", "model": "Royal Oak Chrono Blue", "collection": "Royal Oak", "size": 41},
            {"ref": "15202ST.OO.1240ST.01", "model": "Royal Oak Jumbo", "collection": "Royal Oak", "size": 39},
            {"ref": "26470ST.OO.A801CR.01", "model": "Royal Oak Offshore", "collection": "Royal Oak Offshore", "size": 42},
        ]
    },
    "Omega": {
        "slug": "omega",
        "watches": [
            {"ref": "310.30.42.50.01.001", "model": "Speedmaster Moonwatch", "collection": "Speedmaster", "size": 42},
            {"ref": "310.30.42.50.01.002", "model": "Speedmaster Sapphire", "collection": "Speedmaster", "size": 42},
            {"ref": "210.30.42.20.01.001", "model": "Seamaster Diver 300M Black", "collection": "Seamaster", "size": 42},
            {"ref": "210.30.42.20.03.001", "model": "Seamaster Diver 300M Blue", "collection": "Seamaster", "size": 42},
            {"ref": "210.32.42.20.01.001", "model": "Seamaster Diver 300M Rubber", "collection": "Seamaster", "size": 42},
            {"ref": "220.10.41.21.01.001", "model": "Aqua Terra Black", "collection": "Seamaster", "size": 41},
            {"ref": "311.30.42.30.01.005", "model": "Speedmaster Reduced", "collection": "Speedmaster", "size": 39},
        ]
    },
    "Tudor": {
        "slug": "tudor",
        "watches": [
            {"ref": "79230N", "model": "Black Bay", "collection": "Black Bay", "size": 41},
            {"ref": "79230R", "model": "Black Bay Red", "collection": "Black Bay", "size": 41},
            {"ref": "79230B", "model": "Black Bay Blue", "collection": "Black Bay", "size": 41},
            {"ref": "M79360N-0001", "model": "Black Bay Chrono", "collection": "Black Bay", "size": 41},
            {"ref": "M79830RB-0001", "model": "Black Bay GMT", "collection": "Black Bay", "size": 41},
            {"ref": "M25600TN-0001", "model": "Pelagos", "collection": "Pelagos", "size": 42},
            {"ref": "79500-0001", "model": "Black Bay 58", "collection": "Black Bay", "size": 39},
        ]
    },
    "Breitling": {
        "slug": "breitling",
        "watches": [
            {"ref": "AB0118221B1A1", "model": "Navitimer B01 Chrono 43", "collection": "Navitimer", "size": 43},
            {"ref": "AB2010121B1A1", "model": "Superocean Heritage II 42", "collection": "Superocean", "size": 42},
            {"ref": "A17367D71B1A1", "model": "Superocean 44", "collection": "Superocean", "size": 44},
            {"ref": "AB0138241C1A1", "model": "Chronomat B01 42", "collection": "Chronomat", "size": 42},
            {"ref": "A13314101B1A1", "model": "Avenger Chronograph 45", "collection": "Avenger", "size": 45},
        ]
    },
    "IWC": {
        "slug": "iwc",
        "watches": [
            {"ref": "IW371605", "model": "Portugieser Chronograph", "collection": "Portugieser", "size": 41},
            {"ref": "IW500710", "model": "Portugieser Automatic", "collection": "Portugieser", "size": 42},
            {"ref": "IW377717", "model": "Pilot's Watch Chronograph 43", "collection": "Pilot's Watch", "size": 43},
            {"ref": "IW328802", "model": "Pilot's Mark XX", "collection": "Pilot's Watch", "size": 40},
            {"ref": "IW329303", "model": "Big Pilot 43", "collection": "Big Pilot", "size": 43},
        ]
    },
    "Vacheron Constantin": {
        "slug": "vacheron-constantin",
        "watches": [
            {"ref": "4500V/110A-B128", "model": "Overseas Blue", "collection": "Overseas", "size": 41},
            {"ref": "4500V/110A-B483", "model": "Overseas Black", "collection": "Overseas", "size": 41},
            {"ref": "2000V/120A-B122", "model": "Overseas Small", "collection": "Overseas", "size": 37},
            {"ref": "85180/000G-9230", "model": "Patrimony", "collection": "Patrimony", "size": 40},
        ]
    },
    "Cartier": {
        "slug": "cartier",
        "watches": [
            {"ref": "WSSA0018", "model": "Santos Medium", "collection": "Santos", "size": 35},
            {"ref": "WSSA0030", "model": "Santos Large", "collection": "Santos", "size": 40},
            {"ref": "WSCA0006", "model": "Santos Blue", "collection": "Santos", "size": 40},
            {"ref": "WGCA0006", "model": "Calibre de Cartier", "collection": "Calibre", "size": 42},
            {"ref": "CRWSBB0039", "model": "Ballon Bleu 40mm", "collection": "Ballon Bleu", "size": 40},
        ]
    },
    "Jaeger-LeCoultre": {
        "slug": "jaeger-lecoultre",
        "watches": [
            {"ref": "Q3828420", "model": "Reverso Classic Medium", "collection": "Reverso", "size": 40},
            {"ref": "Q3858520", "model": "Reverso Tribute", "collection": "Reverso", "size": 45},
            {"ref": "Q1548420", "model": "Master Ultra Thin Moon", "collection": "Master", "size": 39},
            {"ref": "Q9028480", "model": "Polaris Automatic", "collection": "Polaris", "size": 41},
            {"ref": "Q9068670", "model": "Polaris Chrono", "collection": "Polaris", "size": 42},
        ]
    },
}


def seed_database():
    """Seed brands and watch references."""
    init_db()
    session = get_session()

    try:
        # Clear existing data
        session.query(WatchReference).delete()
        session.query(Brand).delete()
        session.commit()

        total_watches = 0

        for brand_name, data in SEED_DATA.items():
            # Create brand
            brand = Brand(name=brand_name, slug=data["slug"])
            session.add(brand)
            session.flush()  # Get the brand ID

            # Create watch references
            for watch in data["watches"]:
                ref = WatchReference(
                    brand_id=brand.id,
                    reference_number=watch["ref"],
                    model_name=watch["model"],
                    collection=watch.get("collection"),
                    case_size_mm=watch.get("size"),
                    movement="Automatic"
                )
                session.add(ref)
                total_watches += 1

            print(f"Added {brand_name}: {len(data['watches'])} watches")

        session.commit()
        print(f"\nTotal: {total_watches} watches across {len(SEED_DATA)} brands")

    except Exception as e:
        session.rollback()
        print(f"Error seeding database: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    seed_database()
