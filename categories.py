# Category mapping dictionary + logic

CATEGORY_MAPPING = {
    # Groceries
    "MERCADONA": "Groceries",
    "CASA PLANES": "Groceries",
    "CONSUM": "Groceries",
    "ALDI": "Groceries",
    "CARREFOUR": "Groceries",
    "LIDL": "Groceries",
    "ALCAMPO": "Groceries",
    "SUPER": "Groceries",
    "CHARTER": "Groceries",
    "Rossmann": "Groceries",
    "MERCA CHAYOE": "Groceries",
    "FRUTES PEPET": "Groceries",
    "LILLYDOO GMBH": "Groceries",
    "HERBASANA": "Groceries",
    "L ALAMEDA CARNICER": "Groceries",
    "PESCADOS PACO": "Groceries",
    "CARREF ALFAFAR": "Groceries",
    "SILVESTRE AGRICUl": "Groceries",
    "CARNICERIA MONTANA": "Groceries",
    "POLLOS CRESPO": "Groceries",

    # Amazon
    "AMZN Mktp": "Amazon (others)",
    "aliexpress": "Amazon (others)",
    "HOGAR Y MODA XXI": "Amazon (others)",

    # Utilities
    "NATURGY": "Energy",
    "ENDESA": "Energy",
    "GLOBAL OMNIUM INV": "Water",

    # Transport & Fuel
    "RENFE": "Transport",
    "EESS": "Transport",
    "PARKING": "Transport",
    "TAXI": "Transport",
    "UBER": "Transport",
    "BUS": "Transport",
    "METRO": "Transport",

    # Insurance
    "LINEA DIRECTA": "Insurance",
    "OCASO SA SEG.REAS": "Insurance",
    "RECIBO UNICO MYBOX": "Insurance",

    # Internet & TV
    "QUATTRE INTERNET": "Internet/TV",
    "MOVISTAR": "Internet/TV",
    "TELEFONICA": "Internet/TV",
    "VODAFONE": "Internet/TV",
    "ORANGE": "Internet/TV",

    # ATM
    "REINT.CAJERO": "ATM",
    "CAJERO": "ATM",
    "RETIRADA": "ATM",

    # Income
    "NOMINA": "Income",
    "BIZUM RECIBIDO": "Income",

    # Pharmacy
    "FARMACIA": "Pharmacy",
    "FARMACIA ESTACION": "Pharmacy",

    # Health & Fitness
    "CLINICA": "Health",
    "DENTAL": "Health",
    "MEDICO": "Health",
    "SINERGYA": "Fitness",
    "FREELETICS": "Fitness",

    # Retail & Shopping
    "KIABI": "Shopping",
    "LEGO": "Shopping",
    "CORTE INGLES": "Shopping",
    "H&M": "Shopping",
    "ZARA": "Shopping",
    "AMAZON": "Shopping",
    "DECATHLON": "Shopping",
    "Lefties.com": "Shopping",

    # Restaurants & Dining
    "RESTAURANT": "Dining",
    "BAR": "Dining",
    "CAFE": "Dining",
    "COMIDA": "Dining",
    "PIZZA": "Dining",
    "BURGER": "Dining",
    "MC DONALD": "Dining",

    # Entertainment
    "CINE": "Entertainment",
    "CINEMA": "Entertainment",
    "VALENCIACF": "Entertainment",
    "CONCERT": "Entertainment",
    "ENTRADA": "Entertainment",

    # Education
    "CAXTON COLLEGE": "Education",
    "KUMON SAGUNTO ANG": "Education",

    # Coche
    "WAGEN GROUP RETAIL": "Car",
    "CENTERTORRENT": "Car",
    "CA AUTO BANK S.P.": "Car",
    "FEU VERT": "Car",
    "VOLKSWAGEN RENTIN": "Car",

    # House
    "PRES.32271394678": "House",

    # Travel
    "BKG*BOOKING.COM F": "Travel",
    "Goldcar": "Travel", 
    "Trip.com": "Travel",
    "RYANAIR": "Travel",
    "EASYJET": "Travel",
    "SP HOLAFLY.COM": "Travel",
    "UKVI ETA": "Travel",
    "IBERIA LAE SA OPER": "Travel",

    # Ayuntamiento
    "TRIBUTOS": "Ayuntamiento",
    "AJUNT.DE FOIOS": "Ayuntamiento",
    "AYTO.DE FOIOS": "Ayuntamiento",


}


def categorize_transaction(description: str) -> str:
    """
    Categorize a transaction based on its description.

    Uses case-insensitive keyword matching. Returns the first matching category
    from CATEGORY_MAPPING, or "Uncategorized" if no match found.

    Args:
        description: Transaction description from bank CSV

    Returns:
        Category name (str)
    """
    description_upper = description.upper()

    for keyword, category in CATEGORY_MAPPING.items():
        if keyword.upper() in description_upper:
            return category

    return "Uncategorized"


def add_categories(df) -> None:
    """
    Add 'category' column to DataFrame by categorizing 'description' column.
    Modifies DataFrame in-place.

    Args:
        df: pandas DataFrame with 'description' column
    """
    df["category"] = df["description"].apply(categorize_transaction)
