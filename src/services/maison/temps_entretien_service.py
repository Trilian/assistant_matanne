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
from decimal import Decimal

from src.core.ai import ClientIA
from src.services.base import BaseAIService

from .schemas import (
    AnalyseTempsIA,
    AnalyseTempsRequest,
    NiveauUrgence,
    PrioriteRemplacement,
    RecommandationMateriel,
    ResumeTempsHebdo,
    SessionTravail,
    StatistiqueTempsActivite,
    StatistiqueTempsZone,
    SuggestionOptimisation,
    TypeActiviteEntretien,
)

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


class TempsEntretienService(BaseAIService):
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

    # ═══════════════════════════════════════════════════════
    # ANALYSE IA
    # ═══════════════════════════════════════════════════════

    async def analyser_temps_ia(
        self,
        request: AnalyseTempsRequest,
    ) -> AnalyseTempsIA:
        """Analyse le temps passé avec suggestions IA.

        Args:
            request: Paramètres d'analyse

        Returns:
            Analyse complète avec suggestions et recommandations
        """
        # Déterminer la période
        periodes_jours = {
            "semaine": 7,
            "mois": 30,
            "trimestre": 90,
            "annee": 365,
        }
        jours = periodes_jours.get(request.periode, 30)

        # Collecter les données
        stats_activites = self.obtenir_statistiques_activite(jours)
        resume_semaine = self.obtenir_resume_semaine()

        # Préparer les données pour l'IA
        temps_total = sum(s.temps_total_minutes for s in stats_activites)
        repartition = {s.type_activite.value: s.temps_total_minutes for s in stats_activites}

        # Préparer le contexte pour l'IA
        contexte = self._preparer_contexte_analyse(
            stats_activites,
            resume_semaine,
            request,
        )

        # Appeler l'IA pour les suggestions
        suggestions = []
        recommandations = []

        if request.inclure_suggestions:
            suggestions = await self._generer_suggestions_ia(contexte)

        if request.inclure_materiel:
            recommandations = await self._generer_recommandations_materiel_ia(
                contexte,
                budget_max=request.budget_materiel_max,
            )

        # Générer le résumé textuel
        resume = await self._generer_resume_ia(contexte)

        # Calculer le score d'efficacité
        score = self._calculer_score_efficacite(stats_activites, resume_semaine)

        return AnalyseTempsIA(
            periode_analysee=request.periode,
            resume_textuel=resume,
            temps_total_minutes=temps_total,
            repartition_par_categorie=repartition,
            suggestions_optimisation=suggestions,
            recommandations_materiel=recommandations,
            objectif_temps_suggere_min=self._suggerer_objectif(temps_total, jours),
            score_efficacite=score,
        )

    def _preparer_contexte_analyse(
        self,
        stats: list[StatistiqueTempsActivite],
        resume: ResumeTempsHebdo,
        request: AnalyseTempsRequest,
    ) -> str:
        """Prépare le contexte textuel pour l'IA."""
        lignes = [
            f"## Analyse temps entretien maison - Période: {request.periode}",
            "",
            "### Statistiques par activité:",
        ]

        for stat in stats[:10]:
            icone = stat.icone
            lignes.append(
                f"- {icone} {stat.type_activite.value}: "
                f"{stat.temps_total_minutes} min ({stat.nb_sessions} sessions), "
                f"tendance {stat.tendance}"
            )

        lignes.extend(
            [
                "",
                "### Résumé semaine actuelle:",
                f"- Temps total: {resume.temps_total_minutes} min",
                f"- Jardin: {resume.temps_jardin_minutes} min",
                f"- Ménage: {resume.temps_menage_minutes} min",
                f"- Bricolage: {resume.temps_bricolage_minutes} min",
                f"- Jour le plus actif: {resume.jour_plus_actif or 'N/A'}",
                f"- Évolution vs semaine précédente: {resume.comparaison_semaine_precedente:+.1f}%",
            ]
        )

        if request.objectif_temps_hebdo_min:
            lignes.append(f"- Objectif utilisateur: {request.objectif_temps_hebdo_min} min/semaine")

        return "\n".join(lignes)

    async def _generer_suggestions_ia(
        self,
        contexte: str,
    ) -> list[SuggestionOptimisation]:
        """Génère des suggestions d'optimisation via IA."""
        prompt = f"""
{contexte}

En tant qu'expert en organisation domestique, analyse ces données et propose
3-5 suggestions pour optimiser le temps d'entretien:

Types de suggestions possibles:
- regroupement: Combiner des tâches similaires
- planification: Meilleure répartition dans la semaine
- materiel: Équipement qui pourrait aider (traiter dans recommandations_materiel)
- delegation: Tâches à déléguer ou externaliser

Pour chaque suggestion, indique:
- titre: Titre court et accrocheur
- description: Explication détaillée
- type_suggestion: parmi [regroupement, planification, delegation]
- temps_economise_estime_min: Estimation du temps gagné par semaine
- activites_concernees: Liste des activités impactées
- priorite: haute, moyenne ou basse

Réponds uniquement en JSON avec une liste de suggestions.
"""

        try:
            result = await self.call_with_list_parsing(
                prompt=prompt,
                item_model=SuggestionOptimisation,
                system_prompt="Tu es un expert en organisation et optimisation du temps domestique.",
            )
            return result
        except Exception as e:
            logger.warning(f"Erreur génération suggestions IA: {e}")
            return self._suggestions_par_defaut()

    async def _generer_recommandations_materiel_ia(
        self,
        contexte: str,
        budget_max: Decimal | None = None,
    ) -> list[RecommandationMateriel]:
        """Génère des recommandations de matériel via IA."""
        budget_str = f"Budget maximum: {budget_max}€" if budget_max else "Pas de limite de budget"

        prompt = f"""
{contexte}

{budget_str}

En tant qu'expert en équipement domestique et jardin, propose 2-4 équipements
qui permettraient de gagner du temps sur l'entretien:

Pour chaque recommandation:
- nom_materiel: Nom du produit/équipement
- description: Pourquoi cet équipement est utile
- categorie: jardin, menage, ou bricolage
- prix_estime_min: Prix minimum estimé en euros
- prix_estime_max: Prix maximum estimé en euros
- temps_economise_par_session_min: Minutes gagnées par utilisation
- retour_investissement_semaines: Nombre de semaines avant rentabilisation
- activites_ameliorees: Liste des activités optimisées
- priorite_achat: urgente, haute, normale, basse, future

Privilégie les équipements avec le meilleur rapport temps gagné / prix.
Réponds uniquement en JSON avec une liste de recommandations.
"""

        try:
            result = await self.call_with_list_parsing(
                prompt=prompt,
                item_model=RecommandationMateriel,
                system_prompt="Tu es un expert en équipement domestique et jardinage.",
            )
            return result
        except Exception as e:
            logger.warning(f"Erreur génération recommandations matériel: {e}")
            return self._recommandations_par_defaut()

    async def _generer_resume_ia(self, contexte: str) -> str:
        """Génère un résumé textuel de l'analyse."""
        prompt = f"""
{contexte}

Rédige un résumé concis (3-4 phrases) de cette analyse du temps d'entretien.
Mentionne les points clés: temps total, activités principales, tendances.
Sois encourageant mais objectif.
"""

        try:
            result = await self.client.chat(
                prompt=prompt,
                system_prompt="Tu es un assistant familial bienveillant.",
            )
            return result.strip()
        except Exception as e:
            logger.warning(f"Erreur génération résumé: {e}")
            return "Analyse du temps d'entretien disponible. Consultez les statistiques pour plus de détails."

    def _calculer_score_efficacite(
        self,
        stats: list[StatistiqueTempsActivite],
        resume: ResumeTempsHebdo,
    ) -> int:
        """Calcule un score d'efficacité global (0-100)."""
        score = 50  # Base

        # Bonus régularité (sessions régulières)
        if resume.nb_sessions >= 5:
            score += 10
        elif resume.nb_sessions >= 3:
            score += 5

        # Bonus répartition équilibrée
        categories = [
            resume.temps_jardin_minutes,
            resume.temps_menage_minutes,
            resume.temps_bricolage_minutes,
        ]
        categories_actives = sum(1 for c in categories if c > 0)
        if categories_actives >= 2:
            score += 10

        # Bonus tendance positive
        tendances_hausse = sum(1 for s in stats if s.tendance == "hausse")
        tendances_baisse = sum(1 for s in stats if s.tendance == "baisse")
        if tendances_baisse > tendances_hausse:
            score += 15  # Temps qui diminue = plus efficace

        # Bonus satisfaction moyenne
        sessions_avec_note = [s for s in self._historique if s.satisfaction is not None]
        if sessions_avec_note:
            satisfaction_moyenne = sum(s.satisfaction for s in sessions_avec_note) / len(
                sessions_avec_note
            )
            score += int((satisfaction_moyenne - 3) * 5)

        return max(0, min(100, score))

    def _suggerer_objectif(self, temps_actuel: int, jours: int) -> int:
        """Suggère un objectif hebdomadaire basé sur l'historique."""
        temps_hebdo_actuel = (temps_actuel / jours) * 7
        # Suggérer une légère réduction (-10%)
        return int(temps_hebdo_actuel * 0.9)

    def _suggestions_par_defaut(self) -> list[SuggestionOptimisation]:
        """Suggestions par défaut si l'IA échoue."""
        return [
            SuggestionOptimisation(
                titre="Regrouper les tâches jardin",
                description="Faites tonte + désherbage + arrosage dans la même session",
                type_suggestion="regroupement",
                temps_economise_estime_min=30,
                activites_concernees=[
                    TypeActiviteEntretien.TONTE,
                    TypeActiviteEntretien.DESHERBAGE,
                    TypeActiviteEntretien.ARROSAGE,
                ],
                priorite=NiveauUrgence.MOYENNE,
            ),
            SuggestionOptimisation(
                titre="Planifier le ménage sur 2 jours",
                description="Répartissez aspirateur/sols sur 2 jours plutôt qu'un seul",
                type_suggestion="planification",
                temps_economise_estime_min=15,
                activites_concernees=[
                    TypeActiviteEntretien.ASPIRATEUR,
                    TypeActiviteEntretien.LAVAGE_SOL,
                ],
                priorite=NiveauUrgence.BASSE,
            ),
        ]

    def _recommandations_par_defaut(self) -> list[RecommandationMateriel]:
        """Recommandations par défaut si l'IA échoue."""
        return [
            RecommandationMateriel(
                nom_materiel="Robot tondeuse",
                description="Tond automatiquement pendant que vous faites autre chose",
                categorie="jardin",
                prix_estime_min=Decimal("300"),
                prix_estime_max=Decimal("1200"),
                temps_economise_par_session_min=45,
                retour_investissement_semaines=26,
                activites_ameliorees=[TypeActiviteEntretien.TONTE],
                priorite_achat=PrioriteRemplacement.NORMALE,
            ),
            RecommandationMateriel(
                nom_materiel="Aspirateur robot",
                description="Aspire automatiquement chaque jour",
                categorie="menage",
                prix_estime_min=Decimal("150"),
                prix_estime_max=Decimal("800"),
                temps_economise_par_session_min=30,
                retour_investissement_semaines=12,
                activites_ameliorees=[TypeActiviteEntretien.ASPIRATEUR],
                priorite_achat=PrioriteRemplacement.HAUTE,
            ),
        ]


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
