"""
Service Suivi du Temps - Entretien et Jardinage.

Features:
- Chronomètre start/stop pour sessions de travail
- Statistiques par activité, zone, période
- Historique des sessions
- Calcul tendances et comparaisons
- Analyse IA avec suggestions d'optimisation
- Recommandations matériel pour gagner du temps
"""

import logging
from collections import defaultdict
from datetime import date, datetime, timedelta

from src.core.ai import ClientIA
from src.services.core.base import BaseAIService

from .schemas import (
    ResumeTempsHebdo,
    SessionTravail,
    StatistiqueTempsActivite,
    StatistiqueTempsZone,
    TypeActiviteEntretien,
)
from .temps_entretien_ia_mixin import TempsEntretienIAMixin

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# CONSTANTES
# ═══════════════════════════════════════════════════════════

# Icônes par type d'activité
ICONES_ACTIVITES = {
    TypeActiviteEntretien.ARROSAGE: "💧",
    TypeActiviteEntretien.TONTE: "🌿",
    TypeActiviteEntretien.TAILLE: "✂️",
    TypeActiviteEntretien.DESHERBAGE: "🌱",
    TypeActiviteEntretien.PLANTATION: "🌷",
    TypeActiviteEntretien.RECOLTE: "🥕",
    TypeActiviteEntretien.COMPOST: "♻️",
    TypeActiviteEntretien.TRAITEMENT: "🧪",
    TypeActiviteEntretien.MENAGE_GENERAL: "🧹",
    TypeActiviteEntretien.ASPIRATEUR: "🧹",
    TypeActiviteEntretien.LAVAGE_SOL: "🪣",
    TypeActiviteEntretien.POUSSIERE: "🪶",
    TypeActiviteEntretien.VITRES: "🪟",
    TypeActiviteEntretien.LESSIVE: "👕",
    TypeActiviteEntretien.REPASSAGE: "👔",
    TypeActiviteEntretien.BRICOLAGE: "🔧",
    TypeActiviteEntretien.PEINTURE: "🎨",
    TypeActiviteEntretien.PLOMBERIE: "🚿",
    TypeActiviteEntretien.ELECTRICITE: "💡",
    TypeActiviteEntretien.NETTOYAGE_EXTERIEUR: "🏠",
    TypeActiviteEntretien.RANGEMENT: "📦",
    TypeActiviteEntretien.ADMINISTRATIF: "📋",
    TypeActiviteEntretien.AUTRE: "⏱️",
}

# Catégories regroupées
CATEGORIES_ACTIVITES = {
    "jardin": [
        TypeActiviteEntretien.ARROSAGE,
        TypeActiviteEntretien.TONTE,
        TypeActiviteEntretien.TAILLE,
        TypeActiviteEntretien.DESHERBAGE,
        TypeActiviteEntretien.PLANTATION,
        TypeActiviteEntretien.RECOLTE,
        TypeActiviteEntretien.COMPOST,
        TypeActiviteEntretien.TRAITEMENT,
    ],
    "menage": [
        TypeActiviteEntretien.MENAGE_GENERAL,
        TypeActiviteEntretien.ASPIRATEUR,
        TypeActiviteEntretien.LAVAGE_SOL,
        TypeActiviteEntretien.POUSSIERE,
        TypeActiviteEntretien.VITRES,
        TypeActiviteEntretien.LESSIVE,
        TypeActiviteEntretien.REPASSAGE,
    ],
    "bricolage": [
        TypeActiviteEntretien.BRICOLAGE,
        TypeActiviteEntretien.PEINTURE,
        TypeActiviteEntretien.PLOMBERIE,
        TypeActiviteEntretien.ELECTRICITE,
        TypeActiviteEntretien.NETTOYAGE_EXTERIEUR,
    ],
    "autre": [
        TypeActiviteEntretien.RANGEMENT,
        TypeActiviteEntretien.ADMINISTRATIF,
        TypeActiviteEntretien.AUTRE,
    ],
}


# ═══════════════════════════════════════════════════════════
# SERVICE SUIVI DU TEMPS
# ═══════════════════════════════════════════════════════════


class TempsEntretienService(TempsEntretienIAMixin, BaseAIService):
    """Service pour le suivi du temps d'entretien et jardinage.

    Fonctionnalités:
    - Chronomètre start/stop pour sessions
    - Statistiques par activité/zone/période
    - Suggestions IA d'optimisation
    - Recommandations matériel

    Example:
        >>> service = get_temps_entretien_service()
        >>> session = service.demarrer_session(TypeActiviteEntretien.TONTE)
        >>> # ... travail ...
        >>> service.arreter_session(session.id)
        >>> stats = service.obtenir_statistiques_semaine()
    """

    def __init__(self, client: ClientIA | None = None):
        """Initialise le service temps.

        Args:
            client: Client IA optionnel
        """
        if client is None:
            client = ClientIA()
        super().__init__(
            client=client,
            cache_prefix="temps_entretien",
            default_ttl=1800,  # 30 min
        )
        self._sessions_actives: dict[int, SessionTravail] = {}
        self._historique: list[SessionTravail] = []
        self._prochain_id = 1

    # ═══════════════════════════════════════════════════════
    # GESTION DES SESSIONS
    # ═══════════════════════════════════════════════════════

    def demarrer_session(
        self,
        type_activite: TypeActiviteEntretien,
        zone_id: int | None = None,
        piece_id: int | None = None,
        description: str | None = None,
    ) -> SessionTravail:
        """Démarre une nouvelle session de travail (chronomètre).

        Args:
            type_activite: Type d'activité (tonte, ménage, etc.)
            zone_id: Zone jardin optionnelle
            piece_id: Pièce optionnelle
            description: Description libre

        Returns:
            Session créée avec ID unique
        """
        session_id = self._prochain_id
        self._prochain_id += 1

        session = SessionTravail(
            id=session_id,
            type_activite=type_activite,
            zone_id=zone_id,
            piece_id=piece_id,
            description=description,
            debut=datetime.now(),
            fin=None,
            duree_minutes=None,
            date_creation=datetime.now(),
        )

        self._sessions_actives[session_id] = session
        logger.info(f"Session {session_id} démarrée: {type_activite.value}")

        return session

    def arreter_session(
        self,
        session_id: int,
        notes: str | None = None,
        difficulte: int | None = None,
        satisfaction: int | None = None,
    ) -> SessionTravail:
        """Arrête une session en cours.

        Args:
            session_id: ID de la session à arrêter
            notes: Notes optionnelles
            difficulte: Niveau de difficulté (1-5)
            satisfaction: Niveau de satisfaction (1-5)

        Returns:
            Session mise à jour avec durée

        Raises:
            ValueError: Si la session n'existe pas
        """
        if session_id not in self._sessions_actives:
            raise ValueError(f"Session {session_id} non trouvée ou déjà terminée")

        session = self._sessions_actives.pop(session_id)
        fin = datetime.now()
        duree = int((fin - session.debut).total_seconds() / 60)

        # Créer session complète
        session_complete = SessionTravail(
            id=session.id,
            type_activite=session.type_activite,
            zone_id=session.zone_id,
            piece_id=session.piece_id,
            description=session.description,
            debut=session.debut,
            fin=fin,
            duree_minutes=duree,
            notes=notes,
            difficulte=difficulte,
            satisfaction=satisfaction,
            date_creation=session.date_creation,
        )

        self._historique.append(session_complete)
        logger.info(
            f"Session {session_id} terminée: {duree} min pour {session.type_activite.value}"
        )

        return session_complete

    def obtenir_session_active(self, session_id: int) -> SessionTravail | None:
        """Récupère une session active par son ID."""
        return self._sessions_actives.get(session_id)

    def lister_sessions_actives(self) -> list[SessionTravail]:
        """Liste toutes les sessions en cours.

        Returns:
            Liste des sessions actives avec temps écoulé calculé
        """
        sessions = []
        now = datetime.now()

        for session in self._sessions_actives.values():
            # Calcul du temps écoulé
            duree = int((now - session.debut).total_seconds() / 60)
            session_avec_duree = SessionTravail(
                **session.model_dump(exclude={"duree_minutes"}),
                duree_minutes=duree,
            )
            sessions.append(session_avec_duree)

        return sessions

    def annuler_session(self, session_id: int) -> bool:
        """Annule une session sans l'enregistrer.

        Args:
            session_id: ID de la session à annuler

        Returns:
            True si annulée, False si non trouvée
        """
        if session_id in self._sessions_actives:
            del self._sessions_actives[session_id]
            logger.info(f"Session {session_id} annulée")
            return True
        return False

    # ═══════════════════════════════════════════════════════
    # STATISTIQUES
    # ═══════════════════════════════════════════════════════

    def obtenir_statistiques_activite(
        self,
        periode_jours: int = 30,
    ) -> list[StatistiqueTempsActivite]:
        """Calcule les statistiques par type d'activité.

        Args:
            periode_jours: Nombre de jours à analyser

        Returns:
            Liste de statistiques par activité
        """
        date_debut = datetime.now() - timedelta(days=periode_jours)
        sessions_periode = [
            s for s in self._historique if s.debut >= date_debut and s.duree_minutes is not None
        ]

        # Regrouper par activité
        par_activite: dict[TypeActiviteEntretien, list[SessionTravail]] = defaultdict(list)
        for session in sessions_periode:
            par_activite[session.type_activite].append(session)

        stats = []
        for activite, sessions in par_activite.items():
            temps_total = sum(s.duree_minutes or 0 for s in sessions)
            nb_sessions = len(sessions)
            derniere = max((s.debut for s in sessions), default=None)

            # Calcul tendance (comparer première et deuxième moitié)
            mi_periode = date_debut + timedelta(days=periode_jours // 2)
            premiere_moitie = sum(s.duree_minutes or 0 for s in sessions if s.debut < mi_periode)
            deuxieme_moitie = sum(s.duree_minutes or 0 for s in sessions if s.debut >= mi_periode)

            if premiere_moitie > 0:
                ratio = deuxieme_moitie / premiere_moitie
                tendance = "hausse" if ratio > 1.1 else "baisse" if ratio < 0.9 else "stable"
            else:
                tendance = "stable"

            stats.append(
                StatistiqueTempsActivite(
                    type_activite=activite,
                    icone=ICONES_ACTIVITES.get(activite, "⏱️"),
                    temps_total_minutes=temps_total,
                    nb_sessions=nb_sessions,
                    temps_moyen_minutes=temps_total / nb_sessions if nb_sessions > 0 else 0,
                    derniere_session=derniere,
                    tendance=tendance,
                )
            )

        # Trier par temps total décroissant
        stats.sort(key=lambda s: s.temps_total_minutes, reverse=True)
        return stats

    def obtenir_statistiques_zone(
        self,
        periode_jours: int = 30,
    ) -> list[StatistiqueTempsZone]:
        """Calcule les statistiques par zone/pièce.

        Args:
            periode_jours: Nombre de jours à analyser

        Returns:
            Liste de statistiques par zone
        """
        date_debut = datetime.now() - timedelta(days=periode_jours)
        sessions_periode = [
            s for s in self._historique if s.debut >= date_debut and s.duree_minutes is not None
        ]

        # Regrouper par zone
        par_zone: dict[tuple[int | None, int | None], list[SessionTravail]] = defaultdict(list)
        for session in sessions_periode:
            key = (session.zone_id, session.piece_id)
            par_zone[key].append(session)

        stats = []
        for (zone_id, piece_id), sessions in par_zone.items():
            temps_total = sum(s.duree_minutes or 0 for s in sessions)
            activites = list(set(s.type_activite.value for s in sessions))

            # Déterminer le nom et type
            if zone_id:
                nom = f"Zone Jardin #{zone_id}"
                type_zone = "jardin"
            elif piece_id:
                nom = f"Pièce #{piece_id}"
                type_zone = "piece"
            else:
                nom = "Non spécifié"
                type_zone = "autre"

            stats.append(
                StatistiqueTempsZone(
                    zone_nom=nom,
                    zone_type=type_zone,
                    temps_total_minutes=temps_total,
                    nb_sessions=len(sessions),
                    activites_principales=activites[:5],
                )
            )

        stats.sort(key=lambda s: s.temps_total_minutes, reverse=True)
        return stats

    def obtenir_resume_semaine(
        self,
        date_ref: date | None = None,
    ) -> ResumeTempsHebdo:
        """Génère le résumé de la semaine.

        Args:
            date_ref: Date de référence (défaut: aujourd'hui)

        Returns:
            Résumé hebdomadaire complet
        """
        if date_ref is None:
            date_ref = date.today()

        # Calculer début/fin de semaine (lundi-dimanche)
        jour_semaine = date_ref.weekday()
        semaine_debut = date_ref - timedelta(days=jour_semaine)
        semaine_fin = semaine_debut + timedelta(days=6)

        datetime_debut = datetime.combine(semaine_debut, datetime.min.time())
        datetime_fin = datetime.combine(semaine_fin, datetime.max.time())

        # Filtrer sessions de la semaine
        sessions_semaine = [
            s
            for s in self._historique
            if datetime_debut <= s.debut <= datetime_fin and s.duree_minutes is not None
        ]

        # Calculer totaux par catégorie
        temps_jardin = 0
        temps_menage = 0
        temps_bricolage = 0
        temps_par_jour: dict[int, int] = defaultdict(int)
        compteur_activites: dict[TypeActiviteEntretien, int] = defaultdict(int)

        for session in sessions_semaine:
            duree = session.duree_minutes or 0
            jour = session.debut.weekday()
            temps_par_jour[jour] += duree
            compteur_activites[session.type_activite] += 1

            if session.type_activite in CATEGORIES_ACTIVITES["jardin"]:
                temps_jardin += duree
            elif session.type_activite in CATEGORIES_ACTIVITES["menage"]:
                temps_menage += duree
            elif session.type_activite in CATEGORIES_ACTIVITES["bricolage"]:
                temps_bricolage += duree

        temps_total = sum(s.duree_minutes or 0 for s in sessions_semaine)

        # Jour le plus actif
        jours_noms = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
        jour_plus_actif = None
        if temps_par_jour:
            jour_max = max(temps_par_jour, key=temps_par_jour.get)
            jour_plus_actif = jours_noms[jour_max]

        # Activité la plus fréquente
        activite_plus_frequente = None
        if compteur_activites:
            activite_plus_frequente = max(compteur_activites, key=compteur_activites.get)

        # Comparaison semaine précédente
        semaine_prec_debut = datetime_debut - timedelta(days=7)
        semaine_prec_fin = datetime_fin - timedelta(days=7)
        sessions_prec = [
            s
            for s in self._historique
            if semaine_prec_debut <= s.debut <= semaine_prec_fin and s.duree_minutes is not None
        ]
        temps_prec = sum(s.duree_minutes or 0 for s in sessions_prec)
        comparaison = 0.0
        if temps_prec > 0:
            comparaison = ((temps_total - temps_prec) / temps_prec) * 100

        return ResumeTempsHebdo(
            semaine_debut=semaine_debut,
            semaine_fin=semaine_fin,
            temps_total_minutes=temps_total,
            temps_jardin_minutes=temps_jardin,
            temps_menage_minutes=temps_menage,
            temps_bricolage_minutes=temps_bricolage,
            nb_sessions=len(sessions_semaine),
            jour_plus_actif=jour_plus_actif,
            activite_plus_frequente=activite_plus_frequente,
            comparaison_semaine_precedente=comparaison,
        )

    def obtenir_historique(
        self,
        limite: int = 50,
        type_activite: TypeActiviteEntretien | None = None,
    ) -> list[SessionTravail]:
        """Récupère l'historique des sessions.

        Args:
            limite: Nombre max de sessions
            type_activite: Filtrer par type

        Returns:
            Liste des sessions récentes
        """
        sessions = self._historique.copy()

        if type_activite:
            sessions = [s for s in sessions if s.type_activite == type_activite]

        sessions.sort(key=lambda s: s.debut, reverse=True)
        return sessions[:limite]


# ═══════════════════════════════════════════════════════════
# FACTORY
# ═══════════════════════════════════════════════════════════


_service_instance: TempsEntretienService | None = None


def obtenir_service_temps_entretien() -> TempsEntretienService:
    """Factory pour obtenir le service de suivi du temps (convention française).

    Returns:
        Instance singleton du service
    """
    global _service_instance
    if _service_instance is None:
        _service_instance = TempsEntretienService()
    return _service_instance


def get_temps_entretien_service() -> TempsEntretienService:
    """Factory pour obtenir le service de suivi du temps (alias anglais)."""
    return obtenir_service_temps_entretien()
