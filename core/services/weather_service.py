def get_weather(ville: str):
    """
    Exemple minimal de service météo.
    Retourne un dictionnaire fictif pour test.
    """
    # Données fictives pour test
    return {
        "temp": 18,
        "description": "Ensoleillé",
        "humidity": 45,
        "wind": 10,
        "forecast": [
            {"date": "2025-11-13", "description": "Nuageux", "temp": 17},
            {"date": "2025-11-14", "description": "Pluie légère", "temp": 16},
            {"date": "2025-11-15", "description": "Ensoleillé", "temp": 19},
        ]
    }
