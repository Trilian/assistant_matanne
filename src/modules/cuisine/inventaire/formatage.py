"""Formatage et utilitaires d'affichage pour l'inventaire."""

from datetime import date, datetime

from .alertes_logic import alertes_critiques_existent, calculer_alertes, compter_alertes
from .constants import STATUS_CONFIG
from .stats import calculer_statistiques_inventaire, calculer_statistiques_par_emplacement
from .status import calculer_status_global, calculer_status_peremption, calculer_status_stock


def formater_article_label(article: dict) -> str:
    """
    Formate le label d'affichage d'un article d'inventaire.

    Args:
        article: Dictionnaire de l'article

    Returns:
        Label formate
    """
    status = calculer_status_global(article)
    emoji = status["config"]["emoji"]

    nom = article.get("ingredient_nom", "???")
    quantite = article.get("quantite", 0)
    unite = article.get("unite", "")

    label = f"{emoji} {nom} ({quantite} {unite})"

    # Ajouter la date de peremption si proche
    if status["status_peremption"] in ["perime", "bientot_perime"]:
        date_peremption = article.get("date_peremption")
        if date_peremption:
            if isinstance(date_peremption, datetime):
                date_peremption = date_peremption.date()
            label += f" | 📅 {date_peremption.strftime('%d/%m')}"

    return label


def formater_inventaire_rapport(articles: list[dict]) -> str:
    """
    Formate l'inventaire pour un rapport.

    Args:
        articles: Liste des articles

    Returns:
        Texte formate
    """
    stats = calculer_statistiques_inventaire(articles)
    alertes = calculer_alertes(articles)

    lignes = [
        "=" * 40,
        "RAPPORT D'INVENTAIRE",
        "=" * 40,
        f"Date: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
        "",
        "📊 RÉSUMÉ",
        "-" * 20,
        f"Total articles: {stats['total_articles']}",
        f"Articles OK: {stats['articles_ok']} ({stats['pct_ok']:.1f}%)",
        f"Alertes: {stats['articles_alerte']}",
        f"Valeur totale: {stats['valeur_totale']:.2f}€",
        "",
    ]

    # Alertes
    if alertes_critiques_existent(alertes):
        lignes.append("⚠️ ALERTES CRITIQUES")
        lignes.append("-" * 20)

        for article in alertes.get("critique", []):
            lignes.append(f"  ❌ {article.get('ingredient_nom')} - Stock critique")

        for article in alertes.get("perime", []):
            lignes.append(f"  ⚫ {article.get('ingredient_nom')} - PÉRIMÉ")

        lignes.append("")

    # Par emplacement
    lignes.append("📦 PAR EMPLACEMENT")
    lignes.append("-" * 20)

    stats_emp = calculer_statistiques_par_emplacement(articles)
    for emplacement, emp_stats in sorted(stats_emp.items()):
        lignes.append(f"  {emplacement}: {emp_stats['count']} articles")

    lignes.append("\n" + "=" * 40)

    return "\n".join(lignes)


def calculer_jours_avant_peremption(article: dict) -> int | None:
    """
    Calcule le nombre de jours avant peremption.

    Args:
        article: Dictionnaire de l'article

    Returns:
        Nombre de jours ou None si pas de date
    """
    date_peremption = article.get("date_peremption")

    if not date_peremption:
        return None

    if isinstance(date_peremption, str):
        try:
            date_peremption = datetime.fromisoformat(date_peremption).date()
        except ValueError:
            return None
    elif isinstance(date_peremption, datetime):
        date_peremption = date_peremption.date()

    return (date_peremption - date.today()).days


def grouper_par_emplacement(articles: list[dict]) -> dict[str, list[dict]]:
    """
    Groupe les articles par emplacement.

    Args:
        articles: Liste des articles

    Returns:
        Dictionnaire {emplacement: [articles]}
    """
    groupes = {}
    for article in articles:
        emplacement = article.get("emplacement", "Autre")
        if emplacement not in groupes:
            groupes[emplacement] = []
        groupes[emplacement].append(article)
    return groupes


def grouper_par_categorie(articles: list[dict]) -> dict[str, list[dict]]:
    """
    Groupe les articles par categorie.

    Args:
        articles: Liste des articles

    Returns:
        Dictionnaire {categorie: [articles]}
    """
    groupes = {}
    for article in articles:
        categorie = article.get("categorie", "Autre")
        if categorie not in groupes:
            groupes[categorie] = []
        groupes[categorie].append(article)
    return groupes


def trier_par_peremption(articles: list[dict]) -> list[dict]:
    """
    Trie les articles par date de peremption (plus proche en premier).

    Args:
        articles: Liste des articles

    Returns:
        Liste triee
    """

    def sort_key(article):
        jours = calculer_jours_avant_peremption(article)
        return jours if jours is not None else 9999

    return sorted(articles, key=sort_key)


def trier_par_urgence(articles: list[dict]) -> list[dict]:
    """
    Trie les articles par urgence (perimes/critiques en premier).

    Args:
        articles: Liste des articles

    Returns:
        Liste triee
    """
    ordre_priorite = {"perime": 0, "critique": 1, "bientot_perime": 2, "stock_bas": 3, "ok": 4}

    def sort_key(article):
        status = calculer_status_global(article)["status_prioritaire"]
        return ordre_priorite.get(status, 99)

    return sorted(articles, key=sort_key)


def formater_article_inventaire(article: dict) -> dict:
    """
    Formate un article d'inventaire pour l'affichage.

    Args:
        article: Article brut de la base de donnees

    Returns:
        Article formate avec des champs supplementaires pour l'UI
    """
    status_stock = calculer_status_stock(article)
    status_peremption = calculer_status_peremption(article)

    emoji_stock = STATUS_CONFIG.get(status_stock, {}).get("emoji", "❓")
    emoji_peremption = STATUS_CONFIG.get(status_peremption, {}).get("emoji", "❓")

    jours_peremption = calculer_jours_avant_peremption(article)

    return {
        **article,
        "status_stock": status_stock,
        "status_peremption": status_peremption,
        "emoji_stock": emoji_stock,
        "emoji_peremption": emoji_peremption,
        "jours_avant_peremption": jours_peremption,
        "affichage_stock": f"{emoji_stock} {article.get('ingredient_nom', 'Inconnu')}",
        "affichage_quantite": f"{article.get('quantite', 0)} {article.get('unite', '')}".strip(),
    }
