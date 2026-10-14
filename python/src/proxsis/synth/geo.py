"""Reference geography for the FICTIONAL world.

Coordinates are APPROXIMATE town centres (≈1 km), typed from general
knowledge for simulation purposes only. Real pipelines must use the
official commune register (OFS) and swisstopo geocoding instead.
"""

from __future__ import annotations

import math

# (commune, canton, lat, lon, weight ~ relative economic size, rough)
COMMUNES: list[tuple[str, str, float, float, float]] = [
    # Valais romand
    ("Sion", "VS", 46.233, 7.360, 3.0),
    ("Sierre", "VS", 46.292, 7.535, 2.0),
    ("Martigny", "VS", 46.102, 7.072, 2.0),
    ("Monthey", "VS", 46.255, 6.954, 2.0),
    ("Conthey", "VS", 46.224, 7.305, 1.0),
    ("Saint-Maurice", "VS", 46.218, 7.003, 0.6),
    ("Fully", "VS", 46.138, 7.114, 0.8),
    ("Collombey-Muraz", "VS", 46.270, 6.948, 0.9),
    ("Vétroz", "VS", 46.222, 7.278, 0.6),
    ("Crans-Montana", "VS", 46.311, 7.481, 0.8),
    # Haut-Valais
    ("Visp", "VS", 46.294, 7.881, 1.8),
    ("Brig-Glis", "VS", 46.316, 7.988, 1.5),
    ("Naters", "VS", 46.326, 7.989, 0.8),
    ("Zermatt", "VS", 46.020, 7.749, 0.7),
    ("Leuk", "VS", 46.317, 7.634, 0.5),
    ("Steg-Hohtenn", "VS", 46.315, 7.744, 0.4),
    # Vaud
    ("Lausanne", "VD", 46.520, 6.633, 5.0),
    ("Yverdon-les-Bains", "VD", 46.778, 6.641, 1.8),
    ("Montreux", "VD", 46.433, 6.911, 1.2),
    ("Vevey", "VD", 46.462, 6.843, 1.0),
    ("Nyon", "VD", 46.383, 6.239, 1.3),
    ("Morges", "VD", 46.511, 6.498, 1.2),
    ("Renens", "VD", 46.539, 6.588, 1.2),
    ("Aigle", "VD", 46.318, 6.970, 0.8),
    ("Payerne", "VD", 46.822, 6.938, 0.7),
    ("Crissier", "VD", 46.548, 6.576, 0.9),
    ("Le Chenit", "VD", 46.606, 6.229, 0.6),
    # Genève
    ("Genève", "GE", 46.204, 6.143, 6.0),
    ("Vernier", "GE", 46.217, 6.085, 1.5),
    ("Lancy", "GE", 46.189, 6.114, 1.2),
    ("Meyrin", "GE", 46.234, 6.080, 1.3),
    ("Carouge", "GE", 46.181, 6.139, 1.0),
    ("Plan-les-Ouates", "GE", 46.168, 6.117, 1.0),
    ("Satigny", "GE", 46.214, 6.035, 0.6),
    # Fribourg
    ("Fribourg", "FR", 46.806, 7.162, 2.0),
    ("Bulle", "FR", 46.619, 7.057, 1.4),
    ("Villars-sur-Glâne", "FR", 46.791, 7.123, 0.8),
    ("Estavayer", "FR", 46.849, 6.846, 0.6),
    ("Romont", "FR", 46.697, 6.919, 0.5),
    ("Düdingen", "FR", 46.849, 7.189, 0.6),
    ("Murten", "FR", 46.928, 7.117, 0.6),
    # Neuchâtel, Jura, Jura bernois
    ("Neuchâtel", "NE", 46.990, 6.931, 2.0),
    ("La Chaux-de-Fonds", "NE", 47.100, 6.826, 1.8),
    ("Le Locle", "NE", 47.057, 6.749, 1.0),
    ("La Tène", "NE", 47.010, 6.996, 0.6),
    ("Delémont", "JU", 47.365, 7.345, 1.0),
    ("Porrentruy", "JU", 47.415, 7.076, 0.8),
    ("Moutier", "JU", 47.280, 7.371, 0.6),
    ("Saint-Imier", "BE", 47.153, 6.996, 0.6),
    ("Tramelan", "BE", 47.223, 7.103, 0.4),
    # Suisse alémanique
    ("Bern", "BE", 46.948, 7.447, 4.0),
    ("Biel/Bienne", "BE", 47.137, 7.247, 2.0),
    ("Thun", "BE", 46.758, 7.628, 1.5),
    ("Burgdorf", "BE", 47.059, 7.628, 0.8),
    ("Langenthal", "BE", 47.215, 7.794, 0.8),
    ("Zürich", "ZH", 47.377, 8.540, 8.0),
    ("Winterthur", "ZH", 47.500, 8.724, 2.5),
    ("Uster", "ZH", 47.348, 8.718, 1.0),
    ("Dübendorf", "ZH", 47.397, 8.618, 1.0),
    ("Dietikon", "ZH", 47.405, 8.400, 1.0),
    ("Kloten", "ZH", 47.452, 8.584, 1.0),
    ("Aarau", "AG", 47.393, 8.044, 1.3),
    ("Baden", "AG", 47.473, 8.307, 1.4),
    ("Wohlen", "AG", 47.351, 8.278, 0.7),
    ("Zofingen", "AG", 47.288, 7.946, 0.7),
    ("Brugg", "AG", 47.482, 8.208, 0.6),
    ("Solothurn", "SO", 47.208, 7.537, 1.0),
    ("Olten", "SO", 47.350, 7.903, 1.0),
    ("Grenchen", "SO", 47.193, 7.396, 0.8),
    ("Liestal", "BL", 47.484, 7.734, 0.8),
    ("Pratteln", "BL", 47.521, 7.693, 0.9),
    ("Muttenz", "BL", 47.523, 7.645, 0.9),
    ("Basel", "BS", 47.560, 7.589, 4.0),
    ("Luzern", "LU", 47.050, 8.309, 2.5),
    ("Emmen", "LU", 47.078, 8.300, 1.0),
    ("Kriens", "LU", 47.033, 8.280, 0.8),
    ("St. Gallen", "SG", 47.424, 9.376, 2.0),
    ("Wil", "SG", 47.462, 9.045, 0.8),
    ("Rapperswil-Jona", "SG", 47.227, 8.818, 0.8),
]

# Sector-specific location preferences (multiplicative on commune weight).
SECTOR_CANTON_AFFINITY: dict[str, dict[str, float]] = {
    "horlogerie": {"NE": 6.0, "JU": 5.0, "BE": 3.0, "GE": 3.0, "VD": 2.0, "SO": 3.0},
    "pharma": {"BS": 6.0, "BL": 5.0, "VS": 2.5, "GE": 2.0, "VD": 1.5, "AG": 2.0, "ZH": 1.5},
    "logistique": {"AG": 2.0, "SO": 2.0, "VD": 1.3, "ZH": 1.3, "VS": 1.0, "BL": 1.5},
}

# Agencies of the FICTIONAL world (towns only; brands and staff are invented).
AGENCY_TOWNS: list[str] = [
    "Sion",
    "Martigny",
    "Monthey",
    "Visp",
    "Lausanne",
    "Genève",
    "Fribourg",
    "Neuchâtel",
    "Delémont",
    "Bern",
    "Zürich",
    "Aarau",
    "Olten",
    "Basel",
    "Luzern",
    "St. Gallen",
]


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = p2 - p1, math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))
