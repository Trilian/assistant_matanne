"""
Fonctions helper pour le module inventaire UI.
Préparation des DataFrames pour l'affichage.
"""

import pandas as pd
from typing import Any


def _prepare_inventory_dataframe(inventaire: list[dict[str, Any]]) -> pd.DataFrame:
    """Prépare un DataFrame pour affichage inventaire"""
    data = []
    for article in inventaire:
        statut_icon = {
            "critique": "❌",
            "stock_bas": "⚠",
            "peremption_proche": "⏰",
            "ok": "✅"
        }.get(article["statut"], "❓")
        
        data.append({
            "Statut": f"{statut_icon} {article['statut']}",
            "Article": article["ingredient_nom"],
            "Catégorie": article["ingredient_categorie"],
            "Quantité": f"{article['quantite']:.1f} {article['unite']}",
            "Seuil min": f"{article['quantite_min']:.1f} {article['unite']}",
            "Emplacement": article["emplacement"] or "-",
            "Jours": article["jours_avant_peremption"] or "-",
            "Maj": pd.Timestamp(article["derniere_maj"]).strftime("%d/%m/%Y") if "derniere_maj" in article else "-",
        })
    
    return pd.DataFrame(data)


def _prepare_alert_dataframe(articles: list[dict[str, Any]]) -> pd.DataFrame:
    """Prépare un DataFrame pour affichage alertes"""
    data = []
    for article in articles:
        statut_icon = {
            "critique": "❌",
            "stock_bas": "⚠",
            "peremption_proche": "⏰",
        }.get(article["statut"], "❓")
        
        jours = ""
        if article["jours_avant_peremption"] is not None:
            jours = f"{article['jours_avant_peremption']} jours"
        
        data.append({
            "Article": article["ingredient_nom"],
            "Catégorie": article["ingredient_categorie"],
            "Quantité": f"{article['quantite']:.1f} {article['unite']}",
            "Seuil": f"{article['quantite_min']:.1f}",
            "Emplacement": article["emplacement"] or "-",
            "Problème": jours if jours else "Stock critique",
        })
    
    return pd.DataFrame(data)


__all__ = ["_prepare_inventory_dataframe", "_prepare_alert_dataframe"]
