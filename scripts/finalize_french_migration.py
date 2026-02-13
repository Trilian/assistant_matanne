#!/usr/bin/env python3
"""
Script de migration finale: Supprime les alias et met Ã  jour tous les imports.
"""

import re
from pathlib import Path

# Mapping complet anglais -> franÃ§ais
MAPPINGS: dict[str, str] = {
    # lazy_loader.py
    "LazyModuleLoader": "ChargeurModuleDiffere",
    "OptimizedRouter": "RouteurOptimise",
    "render_lazy_loading_stats": "afficher_stats_chargement_differe",
    # cache_multi.py
    "CacheEntry": "EntreeCache",
    "CacheStats": "StatistiquesCache",
    "L1MemoryCache": "CacheMemoireN1",
    "L2SessionCache": "CacheSessionN2",
    "L3FileCache": "CacheFichierN3",
    "MultiLevelCache": "CacheMultiNiveau",
    "get_cache": "obtenir_cache",
    # performance.py
    "ComponentLoader": "ChargeurComposant",
    "FunctionProfiler": "ProfileurFonction",
    "FunctionStats": "StatistiquesFonction",
    "MemoryMonitor": "MoniteurMemoire",
    "PerformanceDashboard": "TableauBordPerformance",
    "PerformanceMetric": "MetriquePerformance",
    "SQLOptimizer": "OptimiseurSQL",
    # sql_optimizer.py
    "BatchLoader": "ChargeurParLots",
    "N1Detection": "DetectionN1",
    "N1Detector": "DetecteurN1",
    "OptimizedQueryBuilder": "ConstructeurRequeteOptimisee",
    "QueryInfo": "InfoRequete",
    "SQLAlchemyListener": "EcouteurSQLAlchemy",
    # redis_cache.py
    "MemoryCache": "CacheMemoire",
    "RedisCache": "CacheRedis",
    "RedisConfig": "ConfigurationRedis",
    # offline.py
    "ConnectionManager": "GestionnaireConnexion",
    "ConnectionStatus": "StatutConnexion",
    "OfflineQueue": "FileAttenteHorsLigne",
    "OfflineSynchronizer": "SynchroniseurHorsLigne",
    "OperationType": "TypeOperation",
    "PendingOperation": "OperationEnAttente",
    "offline_aware": "avec_mode_hors_ligne",
    "render_connection_status": "afficher_statut_connexion",
    "render_sync_panel": "afficher_panneau_sync",
    # multi_tenant.py
    "MultiTenantQuery": "RequeteMultiLocataire",
    "MultiTenantService": "ServiceMultiLocataire",
    "UserContext": "ContexteUtilisateur",
    "with_user_isolation": "avec_isolation_utilisateur",
    "require_user": "exiger_utilisateur",
    "init_user_context_streamlit": "initialiser_contexte_utilisateur_streamlit",
    "set_user_from_auth": "definir_utilisateur_from_auth",
    "create_multi_tenant_service": "creer_multi_tenant_service",
}

# Fichiers Ã  exclure (dÃ©jÃ  migrÃ©s ou Ã  ignorer)
EXCLUDE_PATTERNS = [
    "backups/",
    "__pycache__",
    ".git",
    "htmlcov/",
    "scripts/finalize_french_migration.py",
    "scripts/migrate_to_french.py",
]


def should_exclude(path: Path) -> bool:
    """VÃ©rifie si le fichier doit Ãªtre exclu."""
    path_str = str(path)
    return any(excl in path_str for excl in EXCLUDE_PATTERNS)


def remove_alias_sections(content: str) -> tuple[str, int]:
    """Supprime les sections d'alias de compatibilitÃ©."""
    lines = content.split("\n")
    new_lines = []
    in_alias_section = False
    removed_count = 0

    for i, line in enumerate(lines):
        # DÃ©tection du dÃ©but de section alias
        if "ALIAS DE COMPATIBILITÃ‰" in line.upper() or "ALIAS DE COMPATIBILITE" in line.upper():
            in_alias_section = True
            # Supprimer aussi le commentaire de sÃ©paration prÃ©cÃ©dent si prÃ©sent
            while new_lines and (
                new_lines[-1].strip().startswith("#")
                or new_lines[-1].strip() == ""
                or "â•" in new_lines[-1]
            ):
                new_lines.pop()
            removed_count += 1
            continue

        if in_alias_section:
            # Une ligne vide suivie de code = fin de section
            stripped = line.strip()
            if stripped.startswith("class ") or stripped.startswith("def "):
                in_alias_section = False
                new_lines.append(line)
            elif stripped and not stripped.startswith("#"):
                # C'est un alias, on le saute
                if " = " in line:
                    continue
            # Sinon on saute (commentaires, lignes vides dans la section)
            continue
        else:
            new_lines.append(line)

    # Nettoyer les lignes vides multiples Ã  la fin
    while len(new_lines) > 1 and new_lines[-1].strip() == "" and new_lines[-2].strip() == "":
        new_lines.pop()

    return "\n".join(new_lines), removed_count


def replace_names(content: str, file_path: str) -> tuple[str, int]:
    """Remplace les noms anglais par les noms franÃ§ais."""
    changes = 0

    for eng, fr in MAPPINGS.items():
        # Utiliser word boundary pour Ã©viter les faux positifs
        pattern = r"\b" + re.escape(eng) + r"\b"
        new_content = re.sub(pattern, fr, content)
        if new_content != content:
            count = len(re.findall(pattern, content))
            changes += count
            content = new_content

    return content, changes


def process_file(file_path: Path) -> tuple[int, int]:
    """Traite un fichier: supprime alias et remplace noms."""
    try:
        content = file_path.read_text(encoding="utf-8-sig")
    except Exception as e:
        print(f"  Erreur lecture {file_path}: {e}")
        return 0, 0

    original = content

    # 1. Supprimer les sections d'alias
    content, alias_removed = remove_alias_sections(content)

    # 2. Remplacer les noms anglais
    content, name_changes = replace_names(content, str(file_path))

    if content != original:
        try:
            file_path.write_text(content, encoding="utf-8")
            if alias_removed > 0:
                print(
                    f"  {file_path}: {name_changes} remplacements, {alias_removed} sections alias supprimÃ©es"
                )
            elif name_changes > 0:
                print(f"  {file_path}: {name_changes} remplacements")
        except Exception as e:
            print(f"  Erreur Ã©criture {file_path}: {e}")
            return 0, 0

    return name_changes, alias_removed


def main():
    root = Path(".")
    total_changes = 0
    total_alias = 0
    files_modified = 0

    print("=" * 60)
    print("MIGRATION FINALE: Suppression alias + remplacement noms")
    print("=" * 60)

    # Traiter src/ et tests/
    for directory in ["src", "tests"]:
        dir_path = root / directory
        if not dir_path.exists():
            continue

        print(f"\nðŸ“ Traitement {directory}/")

        for py_file in dir_path.rglob("*.py"):
            if should_exclude(py_file):
                continue

            changes, alias = process_file(py_file)
            if changes > 0 or alias > 0:
                total_changes += changes
                total_alias += alias
                files_modified += 1

    print("\n" + "=" * 60)
    print(f"âœ… TERMINÃ‰: {total_changes} remplacements dans {files_modified} fichiers")
    print(f"   {total_alias} sections d'alias supprimÃ©es")
    print("=" * 60)


if __name__ == "__main__":
    main()
