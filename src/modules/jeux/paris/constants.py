"""
Constantes pour le module de paris sportifs.
"""

# Championnats supportés
CHAMPIONNATS = [
    "Ligue 1",
    "Premier League",
    "La Liga",
    "Serie A",
    "Bundesliga",
]

# Avantage domicile (+12% de chances de victoire à domicile)
AVANTAGE_DOMICILE = 0.12

# Seuils de confiance pour les prédictions
SEUIL_CONFIANCE_HAUTE = 65
SEUIL_CONFIANCE_MOYENNE = 50

# Seuils pour la régression des nuls (loi des grands nombres)
SEUIL_SERIE_SANS_NUL = 5  # Après 5 matchs sans nul, proba augmente
BONUS_NUL_PAR_MATCH = 0.03  # +3% par match supplémentaire sans nul

# Poids pour les 5 derniers matchs (du plus récent au plus ancien)
POIDS_FORME = [1.0, 0.85, 0.7, 0.55, 0.4]
