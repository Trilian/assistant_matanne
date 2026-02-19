"""
Utilitaires d'opérations pour les backups.

Contient les fonctions de :
- Ordonnancement des tables pour la restauration (respect des FK)
- Calcul et comparaison de statistiques de backup
- Rotation automatique des anciens backups
- Détermination de la nécessité d'un backup
"""

from datetime import datetime

# ═══════════════════════════════════════════════════════════
# ORDRE DE RESTAURATION (RESPECTE LES FK)
# ═══════════════════════════════════════════════════════════


def get_restore_order() -> list[str]:
    """
    Retourne l'ordre de restauration des tables (respecte les FK).

    Les tables sans dépendances sont en premier, celles avec FK en dernier.

    Returns:
        Liste ordonnée des noms de tables

    Examples:
        >>> order = get_restore_order()
        >>> order[0]
        'ingredients'
        >>> 'recette_ingredients' in order
        True
    """
    return [
        "ingredients",
        "recettes",
        "recette_ingredients",
        "etapes_recette",
        "versions_recette",
        "articles_inventaire",
        "plannings",
        "repas",
        "articles_courses",
        "child_profiles",
        "milestones",
        "wellbeing_entries",
        "family_activities",
        "family_budgets",
        "health_routines",
        "health_objectives",
        "health_entries",
        "projects",
        "project_tasks",
        "routines",
        "routine_tasks",
        "garden_items",
        "garden_logs",
        "calendar_events",
    ]


def filter_and_order_tables(tables: list[str]) -> list[str]:
    """
    Filtre et ordonne une liste de tables selon l'ordre de restauration.

    Args:
        tables: Liste de noms de tables

    Returns:
        Liste ordonnée des tables présentes

    Examples:
        >>> filter_and_order_tables(['repas', 'ingredients', 'recettes'])
        ['ingredients', 'recettes', 'repas']
    """
    order = get_restore_order()
    return [t for t in order if t in tables]


# ═══════════════════════════════════════════════════════════
# STATISTIQUES DE BACKUP
# ═══════════════════════════════════════════════════════════


def calculate_backup_stats(backup_data: dict) -> dict:
    """
    Calcule les statistiques d'un backup.

    Args:
        backup_data: Données complètes du backup

    Returns:
        Dict avec tables_count, total_records, par table

    Examples:
        >>> data = {'data': {'recettes': [1,2,3], 'ingredients': [1,2]}}
        >>> stats = calculate_backup_stats(data)
        >>> stats['total_records']
        5
    """
    data_section = backup_data.get("data", {})

    stats = {
        "tables_count": len(data_section),
        "total_records": 0,
        "records_per_table": {},
    }

    for table_name, records in data_section.items():
        count = len(records) if isinstance(records, list) else 0
        stats["records_per_table"][table_name] = count
        stats["total_records"] += count

    return stats


def compare_backup_stats(original: dict, restored: dict) -> dict:
    """
    Compare les statistiques entre original et restauré.

    Args:
        original: Stats du backup original
        restored: Stats après restauration

    Returns:
        Dict avec les différences
    """
    diff = {
        "tables_diff": original.get("tables_count", 0) - restored.get("tables_count", 0),
        "records_diff": original.get("total_records", 0) - restored.get("total_records", 0),
        "tables_missing": [],
        "tables_extra": [],
    }

    orig_tables = set(original.get("records_per_table", {}).keys())
    rest_tables = set(restored.get("records_per_table", {}).keys())

    diff["tables_missing"] = list(orig_tables - rest_tables)
    diff["tables_extra"] = list(rest_tables - orig_tables)

    return diff


# ═══════════════════════════════════════════════════════════
# ROTATION DE BACKUPS
# ═══════════════════════════════════════════════════════════


def get_backups_to_rotate(
    backup_files: list[tuple[str, float]],  # (filename, mtime)
    max_backups: int,
) -> list[str]:
    """
    Détermine quels backups doivent être supprimés lors de la rotation.

    Args:
        backup_files: Liste de tuples (filename, modification_time)
        max_backups: Nombre maximum de backups à conserver

    Returns:
        Liste des fichiers à supprimer (les plus anciens)

    Examples:
        >>> files = [('a.json', 100), ('b.json', 200), ('c.json', 300)]
        >>> get_backups_to_rotate(files, max_backups=2)
        ['a.json']
    """
    if len(backup_files) <= max_backups:
        return []

    # Trier par date (plus récent en premier)
    sorted_files = sorted(backup_files, key=lambda x: x[1], reverse=True)

    # Retourner les plus anciens à supprimer
    return [f[0] for f in sorted_files[max_backups:]]


def should_run_backup(
    last_backup_time: datetime | None, interval_hours: int, current_time: datetime | None = None
) -> bool:
    """
    Vérifie s'il faut exécuter un backup automatique.

    Args:
        last_backup_time: Date du dernier backup
        interval_hours: Intervalle en heures entre backups
        current_time: Heure actuelle (défaut: maintenant)

    Returns:
        True si un backup doit être exécuté

    Examples:
        >>> from datetime import datetime, timedelta
        >>> last = datetime.now() - timedelta(hours=25)
        >>> should_run_backup(last, interval_hours=24)
        True
    """
    if current_time is None:
        current_time = datetime.now()

    if last_backup_time is None:
        return True

    elapsed = current_time - last_backup_time
    return elapsed.total_seconds() >= interval_hours * 3600


__all__ = [
    "get_restore_order",
    "filter_and_order_tables",
    "calculate_backup_stats",
    "compare_backup_stats",
    "get_backups_to_rotate",
    "should_run_backup",
]
