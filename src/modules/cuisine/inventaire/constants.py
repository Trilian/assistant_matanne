"""Constantes du module Inventaire."""

EMPLACEMENTS = ["Réfrigérateur", "Congélateur", "Garde-manger", "Placard cuisine", "Cave", "Autre"]

CATEGORIES = [
    "Fruits & Légumes",
    "Viandes & Poissons",
    "Produits laitiers",
    "Épicerie",
    "Surgelés",
    "Boissons",
    "Condiments",
    "Autre",
]

STATUS_CONFIG = {
    "critique": {"color": "red", "emoji": "❌", "label": "Critique"},
    "stock_bas": {"color": "orange", "emoji": "🎯", "label": "Stock bas"},
    "ok": {"color": "green", "emoji": "💡", "label": "OK"},
    "perime": {"color": "black", "emoji": "⚫", "label": "Perime"},
    "bientot_perime": {"color": "yellow", "emoji": "📅", "label": "Bientôt perime"},
}
