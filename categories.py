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
    "L ALAMEDA CARNICE": "Groceries",
    "PESCADOS PACO": "Groceries",
    "CARREF ALFAFAR": "Groceries",
    "SILVESTRE AGRICUl": "Groceries",
    "CARNICE": "Groceries",
    "POLLOS CRESPO": "Groceries",
    "AGRONOI": "Groceries",
    "ESTELLES RUZAFA E": "Groceries",

    # Amazon
    "AMZN Mktp": "Amazon (others)",
    "aliexpress": "Amazon (others)",
    "HOGAR Y MODA XXI": "Amazon (others)",

    # Utilities
    "NATURGY": "Energy",
    "ENDESA": "Energy",
    "Luz": "Energy",
    "GLOBAL OMNIUM INV": "Water",
    "GASEXPRESS E.S. F": "Gasolina",
    "REPSOL": "Gasolina",

    # Transport & Fuel
    "RENFE": "Transport",
    "EESS": "Transport",
    "PARKING": "Transport",
    "TAXI": "Transport",
    "UBER": "Transport",
    "BUS": "Transport",
    "METRO": "Transport",
    "FURGO CAR SA": "Transport",

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
    "TRANSF. A SU FAVOR": "Income",

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
    "SPORTS DIRECT": "Shopping",
    "TIENDA VCF COLON": "Shopping",
    "SP MURIS BRANDS": "Shopping",

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
    "Sofa": "House",
    "DeLonghi": "House",
    "LEROY MERLIN": "House",

    # Travel
    "BKG*BOOKING.COM F": "Travel",
    "Goldcar": "Travel", 
    "Trip.com": "Travel",
    "RYANAIR": "Travel",
    "EASYJET": "Travel",
    "SP HOLAFLY.COM": "Travel",
    "UKVI ETA": "Travel",
    "IBERIA": "Travel",

    # Ayuntamiento
    "TRIBUTOS": "Ayuntamiento",
    "AJUNT.DE FOIOS": "Ayuntamiento",
    "AYTO.DE FOIOS": "Ayuntamiento",


}

# Savings account categorization
SAVINGS_CATEGORY_MAPPING = {
    # Investments
    "COMP.LU": "Investments",
    "FMRTOEST": "Investments",

    # Internal Transfers (movements between savings accounts)
    "TRASPASO PROPIO": "Internal Transfer",

    # Fees
    "P.SERV": "Fees",
    "COMISION": "Fees",

    # Others
    "BYD": "Compra BYD Dolphin",
    "HACIENDA": "Hacienda",
    "IMPUESTO RENTA": "Hacienda",
    "TRASPASO DE FONDOS": "Amortizacion hipoteca",
    "TRANSF. A SU FAVOR": "Transferencia recibida",
    "F0001/26 - Letici": "Nerosolar",
    "Pago 2 de 2. Leti": "Morata puertas"


}


def categorize_savings_transaction(description: str) -> str:
    """
    Categorize a savings transaction based on its description.

    Uses case-insensitive keyword matching. Returns the first matching category
    from SAVINGS_CATEGORY_MAPPING, or "Uncategorized" if no match found.

    Args:
        description: Transaction description from bank CSV

    Returns:
        Category name (str)
    """
    description_upper = description.upper()

    for keyword, category in SAVINGS_CATEGORY_MAPPING.items():
        if keyword.upper() in description_upper:
            return category

    return "Uncategorized"


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
