"""
Fonctions utilitaires pures pour le batch cooking.

Ces fonctions ne dépendent pas de la base de données et peuvent être
testées unitairement sans mocking.
"""

from datetime import datetime, time, date, timedelta
from typing import Any

from .constantes import JOURS_SEMAINE, ROBOTS_DISPONIBLES


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# CALCULS DE DURÉE
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


def calculer_duree_totale_etapes(etapes: list[dict]) -> int:
    """Calcule la durée totale estimée de toutes les étapes.
    
    Args:
        etapes: Liste de dictionnaires avec clé 'duree_minutes'
    
    Returns:
        Durée totale en minutes
    """
    return sum(e.get("duree_minutes", 10) for e in etapes)


def calculer_duree_parallele(etapes: list[dict]) -> int:
    """Calcule la durée en tenant compte des étapes parallèles.
    
    Les étapes avec le même groupe_parallele s'exécutent simultanément.
    
    Args:
        etapes: Liste de dictionnaires avec 'duree_minutes' et 'groupe_parallele'
    
    Returns:
        Durée effective en minutes
    """
    if not etapes:
        return 0
    
    # Grouper les étapes par groupe parallèle
    groupes: dict[int, list[int]] = {}
    for etape in etapes:
        groupe = etape.get("groupe_parallele", 0)
        duree = etape.get("duree_minutes", 10)
        if groupe not in groupes:
            groupes[groupe] = []
        groupes[groupe].append(duree)
    
    # Pour chaque groupe, prendre le max (exécution parallèle)
    duree_totale = 0
    for groupe_id, durees in groupes.items():
        if groupe_id == 0:
            # Groupe 0 = séquentiel
            duree_totale += sum(durees)
        else:
            # Groupes parallèles: prendre le max
            duree_totale += max(durees) if durees else 0
    
    return duree_totale


def calculer_duree_reelle(heure_debut: datetime, heure_fin: datetime) -> int:
    """Calcule la durée réelle en minutes entre deux datetime.
    
    Args:
        heure_debut: Début de l'étape
        heure_fin: Fin de l'étape
    
    Returns:
        Durée en minutes (arrondi)
    """
    if not heure_debut or not heure_fin:
        return 0
    
    delta = heure_fin - heure_debut
    return int(delta.total_seconds() / 60)


def estimer_heure_fin(heure_debut: time, duree_minutes: int) -> time:
    """Estime l'heure de fin Ã  partir de l'heure de début et la durée.
    
    Args:
        heure_debut: Heure de début
        duree_minutes: Durée estimée en minutes
    
    Returns:
        Heure de fin estimée
    """
    debut_dt = datetime.combine(date.today(), heure_debut)
    fin_dt = debut_dt + timedelta(minutes=duree_minutes)
    return fin_dt.time()


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# ROBOTS ET ÉQUIPEMENTS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


def obtenir_info_robot(robot_id: str) -> dict:
    """Récupère les informations d'un robot.
    
    Args:
        robot_id: Identifiant du robot
    
    Returns:
        Dictionnaire avec nom, emoji, parallele
    """
    return ROBOTS_DISPONIBLES.get(robot_id, {"nom": robot_id, "emoji": "ðŸ”§", "parallele": True})


def obtenir_nom_robot(robot_id: str) -> str:
    """Récupère le nom d'affichage d'un robot.
    
    Args:
        robot_id: Identifiant du robot
    
    Returns:
        Nom d'affichage
    """
    info = obtenir_info_robot(robot_id)
    return info.get("nom", robot_id)


def obtenir_emoji_robot(robot_id: str) -> str:
    """Récupère l'emoji d'un robot.
    
    Args:
        robot_id: Identifiant du robot
    
    Returns:
        Emoji du robot
    """
    info = obtenir_info_robot(robot_id)
    return info.get("emoji", "ðŸ”§")


def est_robot_parallele(robot_id: str) -> bool:
    """Vérifie si un robot peut fonctionner en parallèle.
    
    Args:
        robot_id: Identifiant du robot
    
    Returns:
        True si parallélisable
    """
    info = obtenir_info_robot(robot_id)
    return info.get("parallele", True)


def formater_liste_robots(robot_ids: list[str]) -> str:
    """Formate une liste de robots pour affichage.
    
    Args:
        robot_ids: Liste des identifiants de robots
    
    Returns:
        Chaîne formatée avec noms
    """
    if not robot_ids:
        return "Aucun"
    
    noms = [obtenir_nom_robot(r) for r in robot_ids]
    return ", ".join(noms)


def filtrer_robots_paralleles(robot_ids: list[str]) -> list[str]:
    """Filtre les robots qui peuvent fonctionner en parallèle.
    
    Args:
        robot_ids: Liste des identifiants de robots
    
    Returns:
        Liste des robots parallélisables
    """
    return [r for r in robot_ids if est_robot_parallele(r)]


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# JOURS ET DATES
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


def obtenir_nom_jour(index: int) -> str:
    """Récupère le nom du jour de la semaine.
    
    Args:
        index: 0 (Lundi) Ã  6 (Dimanche)
    
    Returns:
        Nom du jour
    """
    if 0 <= index < 7:
        return JOURS_SEMAINE[index]
    return ""


def obtenir_index_jour(nom: str) -> int:
    """Récupère l'index d'un jour Ã  partir de son nom.
    
    Args:
        nom: Nom du jour (insensible Ã  la casse)
    
    Returns:
        Index 0-6, ou -1 si non trouvé
    """
    nom_lower = nom.lower()
    for i, jour in enumerate(JOURS_SEMAINE):
        if jour.lower() == nom_lower:
            return i
    return -1


def formater_jours_batch(indices: list[int]) -> str:
    """Formate une liste d'indices de jours en chaîne.
    
    Args:
        indices: Liste d'indices (0-6)
    
    Returns:
        Chaîne formatée ex: "Samedi, Dimanche"
    """
    noms = [obtenir_nom_jour(i) for i in sorted(indices) if obtenir_nom_jour(i)]
    return ", ".join(noms) if noms else "Aucun"


def est_jour_batch(jour: date, jours_batch: list[int]) -> bool:
    """Vérifie si une date est un jour de batch cooking.
    
    Args:
        jour: Date Ã  vérifier
        jours_batch: Liste des indices de jours de batch (0-6)
    
    Returns:
        True si c'est un jour de batch
    """
    # weekday() retourne 0 (lundi) Ã  6 (dimanche)
    return jour.weekday() in jours_batch


def prochain_jour_batch(depuis: date, jours_batch: list[int]) -> date | None:
    """Trouve le prochain jour de batch cooking.
    
    Args:
        depuis: Date de départ
        jours_batch: Liste des indices de jours de batch
    
    Returns:
        Prochaine date de batch, ou None si pas de jours définis
    """
    if not jours_batch:
        return None
    
    for i in range(1, 8):  # On cherche dans les 7 prochains jours
        candidat = depuis + timedelta(days=i)
        if candidat.weekday() in jours_batch:
            return candidat
    
    return None


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# CONTEXTE RECETTES
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


def construire_contexte_recette(
    nom: str,
    temps_preparation: int | None = None,
    temps_cuisson: int | None = None,
    portions: int | None = None,
    compatible_batch: bool = False,
    congelable: bool = False,
    robots_compatibles: list[str] | None = None,
    etapes: list[dict] | None = None,
) -> str:
    """Construit le contexte texte d'une recette pour l'IA.
    
    Args:
        nom: Nom de la recette
        temps_preparation: Temps de préparation en minutes
        temps_cuisson: Temps de cuisson en minutes
        portions: Nombre de portions
        compatible_batch: Est compatible batch cooking
        congelable: Peut être congelé
        robots_compatibles: Liste des robots compatibles
        etapes: Liste des étapes {ordre, description, duree}
    
    Returns:
        Texte de contexte formaté
    """
    etapes_text = ""
    if etapes:
        etapes_text = "\n".join([
            f"  {e.get('ordre', i+1)}. {e.get('description', '')} ({e.get('duree', '?')} min)"
            for i, e in enumerate(etapes)
        ])
    
    robots_text = ", ".join(robots_compatibles) if robots_compatibles else "Aucun"
    
    return f"""
Recette: {nom}
- Temps préparation: {temps_preparation or '?'} min
- Temps cuisson: {temps_cuisson or '?'} min
- Portions: {portions or '?'}
- Compatible batch: {'Oui' if compatible_batch else 'Non'}
- Congelable: {'Oui' if congelable else 'Non'}
- Robots: {robots_text}
- Étapes:
{etapes_text}
"""


def construire_contexte_jules(present: bool = True) -> str:
    """Construit le contexte pour la présence de Jules.
    
    Args:
        present: Jules sera-t-il présent
    
    Returns:
        Texte de contexte
    """
    if not present:
        return ""
    
    return """
âš ï¸ IMPORTANT - JULES (bébé 19 mois) sera présent !
- Éviter les étapes bruyantes pendant la sieste (13h-15h)
- Prévoir des moments calmes où il peut observer/aider
- Signaler les étapes dangereuses (four chaud, friture, couteaux)
- Optimiser pour terminer avant 12h si possible
"""


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# CALCULS DE SESSION
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


def calculer_progression_session(
    etapes_terminees: int,
    etapes_total: int,
) -> float:
    """Calcule le pourcentage de progression d'une session.
    
    Args:
        etapes_terminees: Nombre d'étapes terminées
        etapes_total: Nombre total d'étapes
    
    Returns:
        Pourcentage de progression (0-100)
    """
    if etapes_total == 0:
        return 0.0
    return (etapes_terminees / etapes_total) * 100


def calculer_temps_restant(
    etapes_restantes: list[dict],
    utiliser_parallele: bool = True,
) -> int:
    """Calcule le temps restant estimé pour les étapes non terminées.
    
    Args:
        etapes_restantes: Liste des étapes restantes
        utiliser_parallele: Tenir compte du parallélisme
    
    Returns:
        Temps restant en minutes
    """
    if not etapes_restantes:
        return 0
    
    if utiliser_parallele:
        return calculer_duree_parallele(etapes_restantes)
    else:
        return calculer_duree_totale_etapes(etapes_restantes)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# PRÉPARATIONS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


def calculer_portions_restantes(portions_initiales: int, consommees: int) -> int:
    """Calcule le nombre de portions restantes.
    
    Args:
        portions_initiales: Nombre de portions au départ
        consommees: Nombre de portions consommées
    
    Returns:
        Portions restantes (minimum 0)
    """
    return max(0, portions_initiales - consommees)


def est_preparation_expiree(
    date_preparation: date,
    conservation_jours: int,
    date_reference: date | None = None,
) -> bool:
    """Vérifie si une préparation a dépassé sa date de conservation.
    
    Args:
        date_preparation: Date de création
        conservation_jours: Durée de conservation en jours
        date_reference: Date de référence (défaut: aujourd'hui)
    
    Returns:
        True si expiré
    """
    if date_reference is None:
        date_reference = date.today()
    
    date_expiration = date_preparation + timedelta(days=conservation_jours)
    return date_reference > date_expiration


def jours_avant_expiration(
    date_preparation: date,
    conservation_jours: int,
    date_reference: date | None = None,
) -> int:
    """Calcule le nombre de jours avant expiration.
    
    Args:
        date_preparation: Date de création
        conservation_jours: Durée de conservation en jours
        date_reference: Date de référence (défaut: aujourd'hui)
    
    Returns:
        Jours restants (négatif si expiré)
    """
    if date_reference is None:
        date_reference = date.today()
    
    date_expiration = date_preparation + timedelta(days=conservation_jours)
    delta = date_expiration - date_reference
    return delta.days


def est_preparation_a_risque(
    date_preparation: date,
    conservation_jours: int,
    seuil_alerte_jours: int = 2,
    date_reference: date | None = None,
) -> bool:
    """Vérifie si une préparation va bientôt expirer.
    
    Args:
        date_preparation: Date de création
        conservation_jours: Durée de conservation en jours
        seuil_alerte_jours: Nombre de jours avant alerte
        date_reference: Date de référence (défaut: aujourd'hui)
    
    Returns:
        True si expire dans les prochains jours
    """
    jours = jours_avant_expiration(date_preparation, conservation_jours, date_reference)
    return 0 < jours <= seuil_alerte_jours


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# VALIDATION
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


def valider_jours_batch(jours: list[int]) -> list[int]:
    """Valide et nettoie une liste de jours de batch.
    
    Args:
        jours: Liste d'indices de jours (0-6)
    
    Returns:
        Liste validée (indices 0-6 uniquement, sans doublons)
    """
    return sorted(list(set(j for j in jours if 0 <= j <= 6)))


def valider_duree(duree: int | None, defaut: int = 10) -> int:
    """Valide une durée en minutes.
    
    Args:
        duree: Durée Ã  valider
        defaut: Valeur par défaut si invalide
    
    Returns:
        Durée validée (1-480 minutes)
    """
    if duree is None or duree < 1:
        return defaut
    return min(duree, 480)  # Max 8 heures


def valider_portions(portions: int | None, defaut: int = 4) -> int:
    """Valide un nombre de portions.
    
    Args:
        portions: Nombre de portions
        defaut: Valeur par défaut si invalide
    
    Returns:
        Portions validées (1-20)
    """
    if portions is None or portions < 1:
        return defaut
    return min(portions, 20)


def valider_conservation(jours: int | None, defaut: int = 3) -> int:
    """Valide une durée de conservation.
    
    Args:
        jours: Jours de conservation
        defaut: Valeur par défaut si invalide
    
    Returns:
        Jours validés (1-90)
    """
    if jours is None or jours < 1:
        return defaut
    return min(jours, 90)


__all__ = [
    # Durées
    "calculer_duree_totale_etapes",
    "calculer_duree_parallele",
    "calculer_duree_reelle",
    "estimer_heure_fin",
    # Robots
    "obtenir_info_robot",
    "obtenir_nom_robot",
    "obtenir_emoji_robot",
    "est_robot_parallele",
    "formater_liste_robots",
    "filtrer_robots_paralleles",
    # Jours
    "obtenir_nom_jour",
    "obtenir_index_jour",
    "formater_jours_batch",
    "est_jour_batch",
    "prochain_jour_batch",
    # Contexte
    "construire_contexte_recette",
    "construire_contexte_jules",
    # Session
    "calculer_progression_session",
    "calculer_temps_restant",
    # Préparations
    "calculer_portions_restantes",
    "est_preparation_expiree",
    "jours_avant_expiration",
    "est_preparation_a_risque",
    # Validation
    "valider_jours_batch",
    "valider_duree",
    "valider_portions",
    "valider_conservation",
]
