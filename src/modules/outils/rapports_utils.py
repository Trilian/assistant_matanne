"""
Logique metier du module Rapports (generation rapports) - Separee de l'UI
Ce module contient toute la logique pure, testable sans Streamlit
"""

from datetime import date, timedelta
from typing import Optional, Dict, Any, List
import logging

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# GÉNÉRATION RAPPORTS
# ═══════════════════════════════════════════════════════════

def generer_rapport_synthese(data: Dict[str, Any], periode: str = "mois") -> Dict[str, Any]:
    """
    Genère un rapport de synthèse.
    
    Args:
        data: Donnees sources
        periode: Periode du rapport (jour, semaine, mois, annee)
        
    Returns:
        Rapport genere
    """
    if periode == "jour":
        jours = 1
    elif periode == "semaine":
        jours = 7
    elif periode == "mois":
        jours = 30
    else:  # annee
        jours = 365
    
    date_debut = date.today() - timedelta(days=jours)
    date_fin = date.today()
    
    return {
        "titre": f"Rapport {periode}",
        "periode": periode,
        "date_debut": date_debut,
        "date_fin": date_fin,
        "date_generation": date.today(),
        "statistiques": {
            "recettes": len(data.get("recettes", [])),
            "courses": len(data.get("courses", [])),
            "activites": len(data.get("activites", [])),
            "inventaire": len(data.get("inventaire", []))
        },
        "sections": []
    }


def calculer_statistiques_periode(items: List[Dict[str, Any]], date_debut: date, date_fin: date) -> Dict[str, int]:
    """
    Calcule les statistiques sur une periode.
    
    Args:
        items: Liste d'items avec dates
        date_debut: Date de debut
        date_fin: Date de fin
        
    Returns:
        Statistiques calculees
    """
    resultats = {"total": 0, "par_jour": {}}
    
    for item in items:
        date_item = item.get("date")
        if isinstance(date_item, str):
            from datetime import datetime
            date_item = datetime.fromisoformat(date_item).date()
        
        if date_item and date_debut <= date_item <= date_fin:
            resultats["total"] += 1
            jour_key = date_item.strftime("%Y-%m-%d")
            resultats["par_jour"][jour_key] = resultats["par_jour"].get(jour_key, 0) + 1
    
    return resultats


def generer_section_recettes(recettes: List[Dict[str, Any]], periode: str) -> Dict[str, Any]:
    """Genère la section recettes du rapport."""
    total = len(recettes)
    
    # Par type
    par_type = {}
    for recette in recettes:
        type_repas = recette.get("type_repas", "Autre")
        par_type[type_repas] = par_type.get(type_repas, 0) + 1
    
    # Par difficulte
    par_difficulte = {}
    for recette in recettes:
        diff = recette.get("difficulte", "moyen")
        par_difficulte[diff] = par_difficulte.get(diff, 0) + 1
    
    return {
        "titre": "📅 Recettes",
        "total": total,
        "par_type": par_type,
        "par_difficulte": par_difficulte,
        "moyenne_par_jour": total / 30 if periode == "mois" else total
    }


def generer_section_courses(courses: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Genère la section courses du rapport."""
    total = len(courses)
    achetes = len([c for c in courses if c.get("achete", False)])
    
    # Montants
    montant_total = sum(c.get("prix", 0) * c.get("quantite", 1) for c in courses)
    
    # Par categorie
    par_categorie = {}
    for course in courses:
        cat = course.get("categorie", "Autre")
        par_categorie[cat] = par_categorie.get(cat, 0) + 1
    
    return {
        "titre": "💡 Courses",
        "total": total,
        "achetes": achetes,
        "non_achetes": total - achetes,
        "taux_completion": (achetes / total * 100) if total > 0 else 0,
        "montant_total": montant_total,
        "par_categorie": par_categorie
    }


def generer_section_activites(activites: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Genère la section activites du rapport."""
    total = len(activites)
    
    # Par type
    par_type = {}
    for act in activites:
        type_act = act.get("type", "Autre")
        par_type[type_act] = par_type.get(type_act, 0) + 1
    
    # Coûts
    cout_total = sum(act.get("cout", 0) for act in activites)
    
    return {
        "titre": "🎯 Activités",
        "total": total,
        "par_type": par_type,
        "cout_total": cout_total,
        "cout_moyen": cout_total / total if total > 0 else 0
    }


# ═══════════════════════════════════════════════════════════
# ANALYSE COMPARATIVE
# ═══════════════════════════════════════════════════════════

def comparer_periodes(data_periode1: Dict[str, Any], data_periode2: Dict[str, Any]) -> Dict[str, Any]:
    """
    Compare deux periodes.
    
    Args:
        data_periode1: Donnees periode 1 (ex: mois precedent)
        data_periode2: Donnees periode 2 (ex: mois actuel)
        
    Returns:
        Comparaison
    """
    def calculer_evolution(val1: float, val2: float) -> Dict[str, Any]:
        if val1 == 0:
            return {"evolution": 0, "pourcentage": 0, "tendance": "stable"}
        
        diff = val2 - val1
        pct = (diff / val1) * 100
        
        if pct > 10:
            tendance = "hausse"
        elif pct < -10:
            tendance = "baisse"
        else:
            tendance = "stable"
        
        return {
            "evolution": diff,
            "pourcentage": pct,
            "tendance": tendance
        }
    
    return {
        "recettes": calculer_evolution(
            len(data_periode1.get("recettes", [])),
            len(data_periode2.get("recettes", []))
        ),
        "courses": calculer_evolution(
            len(data_periode1.get("courses", [])),
            len(data_periode2.get("courses", []))
        ),
        "activites": calculer_evolution(
            len(data_periode1.get("activites", [])),
            len(data_periode2.get("activites", []))
        )
    }


# ═══════════════════════════════════════════════════════════
# FORMATAGE RAPPORTS
# ═══════════════════════════════════════════════════════════

def formater_rapport_texte(rapport: Dict[str, Any]) -> str:
    """
    Formate un rapport en texte brut.
    
    Args:
        rapport: Rapport à formater
        
    Returns:
        Texte formate
    """
    lignes = [
        "═══════════════════════════════════════════════════════════" * 60,
        f"[CHART] {rapport.get('titre', 'RAPPORT').upper()}",
        "═══════════════════════════════════════════════════════════" * 60,
        f"Periode: {rapport.get('periode', 'N/A')}",
        f"Du {rapport.get('date_debut')} au {rapport.get('date_fin')}",
        f"Genere le: {rapport.get('date_generation')}",
        "",
        "STATISTIQUES GLOBALES:",
        "â”€" * 60,
    ]
    
    stats = rapport.get("statistiques", {})
    for cle, valeur in stats.items():
        lignes.append(f"  • {cle.capitalize()}: {valeur}")
    
    # Sections
    if rapport.get("sections"):
        lignes.append("")
        lignes.append("DÉTAILS PAR SECTION:")
        lignes.append("â”€" * 60)
        
        for section in rapport["sections"]:
            lignes.append(f"\n{section.get('titre', 'Section')}")
            lignes.append(f"  Total: {section.get('total', 0)}")
    
    lignes.append("")
    lignes.append("═══════════════════════════════════════════════════════════" * 60)
    
    return "\n".join(lignes)


def formater_rapport_markdown(rapport: Dict[str, Any]) -> str:
    """
    Formate un rapport en Markdown.
    
    Args:
        rapport: Rapport à formater
        
    Returns:
        Markdown formate
    """
    lignes = [
        f"# [CHART] {rapport.get('titre', 'Rapport')}",
        "",
        f"**Periode:** {rapport.get('periode', 'N/A')}  ",
        f"**Dates:** Du {rapport.get('date_debut')} au {rapport.get('date_fin')}  ",
        f"**Genere le:** {rapport.get('date_generation')}",
        "",
        "## Statistiques Globales",
        ""
    ]
    
    stats = rapport.get("statistiques", {})
    for cle, valeur in stats.items():
        lignes.append(f"- **{cle.capitalize()}:** {valeur}")
    
    # Sections
    if rapport.get("sections"):
        lignes.append("")
        lignes.append("## Details")
        
        for section in rapport["sections"]:
            lignes.append(f"\n### {section.get('titre', 'Section')}")
            lignes.append(f"\n**Total:** {section.get('total', 0)}")
            
            if "par_type" in section:
                lignes.append("\n**Repartition:**")
                for type_key, count in section["par_type"].items():
                    lignes.append(f"- {type_key}: {count}")
    
    return "\n".join(lignes)


def formater_rapport_html(rapport: Dict[str, Any]) -> str:
    """
    Formate un rapport en HTML.
    
    Args:
        rapport: Rapport à formater
        
    Returns:
        HTML formate
    """
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{rapport.get('titre', 'Rapport')}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ color: #333; }}
        .stats {{ background: #f5f5f5; padding: 15px; border-radius: 5px; }}
        .section {{ margin: 20px 0; padding: 15px; border-left: 3px solid #007bff; }}
    </style>
</head>
<body>
    <h1>[CHART] {rapport.get('titre', 'Rapport')}</h1>
    
    <div class="stats">
        <p><strong>Periode:</strong> {rapport.get('periode', 'N/A')}</p>
        <p><strong>Dates:</strong> Du {rapport.get('date_debut')} au {rapport.get('date_fin')}</p>
        <p><strong>Genere le:</strong> {rapport.get('date_generation')}</p>
    </div>
    
    <h2>Statistiques Globales</h2>
    <ul>
"""
    
    stats = rapport.get("statistiques", {})
    for cle, valeur in stats.items():
        html += f"        <li><strong>{cle.capitalize()}:</strong> {valeur}</li>\n"
    
    html += "    </ul>\n"
    
    # Sections
    if rapport.get("sections"):
        html += "    <h2>Details</h2>\n"
        
        for section in rapport["sections"]:
            html += f"""
    <div class="section">
        <h3>{section.get('titre', 'Section')}</h3>
        <p><strong>Total:</strong> {section.get('total', 0)}</p>
    </div>
"""
    
    html += """
</body>
</html>
"""
    
    return html


# ═══════════════════════════════════════════════════════════
# EXPORT
# ═══════════════════════════════════════════════════════════

def preparer_export_csv(data: List[Dict[str, Any]], colonnes: List[str]) -> str:
    """
    Prepare les donnees pour export CSV.
    
    Args:
        data: Donnees à exporter
        colonnes: Colonnes à inclure
        
    Returns:
        Contenu CSV
    """
    lignes = [";".join(colonnes)]
    
    for item in data:
        valeurs = [str(item.get(col, "")) for col in colonnes]
        lignes.append(";".join(valeurs))
    
    return "\n".join(lignes)
