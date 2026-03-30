"""
Service Innovations — Phase 10 du planning.

Service central regroupant les fonctionnalités d'innovation :
- 10.4 Bilan annuel automatique IA
- 10.5 Score bien-être familial composite
- 10.17 Enrichissement contacts IA
- 10.18 Analyse tendances Loto/EuroMillions
- 10.19 Optimisation parcours magasin IA
- 10.8 Veille emploi multi-sites
- 10.3 Mode invité (lien partageable)

Hérite de BaseAIService pour rate limiting + cache + circuit breaker auto.
"""

from __future__ import annotations

import hashlib
import json
import logging
import secrets
from datetime import UTC, date, datetime, timedelta
from typing import Any

from src.core.ai import obtenir_client_ia
from src.core.db import obtenir_contexte_db
from src.core.decorators import avec_cache, avec_gestion_erreurs
from src.core.monitoring import chronometre
from src.core.validation.sanitizer import NettoyeurEntrees
from src.services.core.base import BaseAIService
from src.services.core.registry import service_factory

from .types import (
    AnalyseTendancesLotoResponse,
    BilanAnnuelResponse,
    ContactEnrichi,
    CriteresVeilleEmploi,
    DimensionBienEtre,
    DonneesInviteResponse,
    EnrichissementContactsResponse,
    LienInviteResponse,
    OffreEmploi,
    ParcoursOptimiseResponse,
    ScoreBienEtreResponse,
    SectionBilanAnnuel,
    TendanceLoto,
    VeilleEmploiResponse,
)

logger = logging.getLogger(__name__)

# Stockage en mémoire des tokens invités (en production → DB)
_tokens_invites: dict[str, dict] = {}


def _sanitiser(texte: str, max_len: int = 200) -> str:
    """Sanitise un texte utilisateur avant injection dans un prompt IA."""
    return NettoyeurEntrees.nettoyer_chaine(texte, longueur_max=max_len)


class InnovationsService(BaseAIService):
    """Service Innovations — Phase 10.

    Hérite de BaseAIService : rate limiting, cache sémantique,
    circuit breaker et parsing JSON/Pydantic automatiques.
    """

    def __init__(self) -> None:
        super().__init__(
            client=obtenir_client_ia(),
            cache_prefix="innovations",
            default_ttl=3600,
            default_temperature=0.7,
            service_name="innovations",
        )

    # ═══════════════════════════════════════════════════════════
    # 10.4 — BILAN ANNUEL AUTOMATIQUE IA
    # ═══════════════════════════════════════════════════════════

    @avec_cache(ttl=86400, key_func=lambda self, annee: f"bilan_annuel_{annee}")
    @avec_gestion_erreurs(default_return=None)
    @chronometre("innovations.bilan_annuel", seuil_alerte_ms=15000)
    def generer_bilan_annuel(self, annee: int | None = None) -> BilanAnnuelResponse | None:
        """Génère un bilan annuel complet basé sur toutes les données de l'année."""
        if annee is None:
            annee = date.today().year - 1

        contexte = self._collecter_contexte_annuel(annee)

        prompt = f"""Génère un bilan annuel familial complet pour l'année {annee}.

Données de l'année :
{contexte}

Retourne un JSON :
{{
  "annee": {annee},
  "resume_global": "Résumé en 2-3 phrases",
  "sections": [
    {{"titre": "Cuisine & Nutrition", "resume": "...", "metriques": {{"recettes_cuisinees": 150}}, "points_forts": ["..."], "axes_amelioration": ["..."]}},
    {{"titre": "Budget Familial", "resume": "...", "metriques": {{}}, "points_forts": [], "axes_amelioration": []}},
    {{"titre": "Maison & Entretien", "resume": "...", "metriques": {{}}, "points_forts": [], "axes_amelioration": []}},
    {{"titre": "Développement Jules", "resume": "...", "metriques": {{}}, "points_forts": [], "axes_amelioration": []}},
    {{"titre": "Sport & Bien-être", "resume": "...", "metriques": {{}}, "points_forts": [], "axes_amelioration": []}}
  ],
  "score_global": 7.5,
  "recommandations": ["Recommandation 1", "Recommandation 2"]
}}"""

        resultat = self.call_with_parsing_sync(
            prompt=prompt,
            response_model=BilanAnnuelResponse,
            system_prompt="Tu es un assistant familial qui génère des bilans annuels positifs et constructifs.",
        )
        return resultat

    # ═══════════════════════════════════════════════════════════
    # 10.5 — SCORE BIEN-ÊTRE FAMILIAL COMPOSITE
    # ═══════════════════════════════════════════════════════════

    @avec_cache(ttl=1800, key_func=lambda self: "score_bien_etre")
    @avec_gestion_erreurs(default_return=None)
    @chronometre("innovations.score_bien_etre", seuil_alerte_ms=5000)
    def calculer_score_bien_etre(self) -> ScoreBienEtreResponse | None:
        """Calcule le score bien-être familial composite (0-100).

        Combine 4 dimensions :
        - Sport (Garmin) : pas, activités, calories
        - Nutrition : planning équilibré, score nutritionnel
        - Budget : stress financier, dépassements
        - Routines : régularité, accomplissement
        """
        dimensions = []
        scores = []

        # Dimension Sport (poids 30%)
        score_sport = self._calculer_score_sport()
        dimensions.append(DimensionBienEtre(
            nom="Sport & Activité Physique",
            score=score_sport,
            poids=0.30,
            detail=self._detail_sport(score_sport),
            tendance=self._evaluer_tendance("sport"),
        ))
        scores.append(score_sport * 0.30)

        # Dimension Nutrition (poids 25%)
        score_nutrition = self._calculer_score_nutrition()
        dimensions.append(DimensionBienEtre(
            nom="Nutrition & Alimentation",
            score=score_nutrition,
            poids=0.25,
            detail=self._detail_nutrition(score_nutrition),
            tendance=self._evaluer_tendance("nutrition"),
        ))
        scores.append(score_nutrition * 0.25)

        # Dimension Budget (poids 25%)
        score_budget = self._calculer_score_budget()
        dimensions.append(DimensionBienEtre(
            nom="Équilibre Financier",
            score=score_budget,
            poids=0.25,
            detail=self._detail_budget(score_budget),
            tendance=self._evaluer_tendance("budget"),
        ))
        scores.append(score_budget * 0.25)

        # Dimension Routines (poids 20%)
        score_routines = self._calculer_score_routines()
        dimensions.append(DimensionBienEtre(
            nom="Régularité & Routines",
            score=score_routines,
            poids=0.20,
            detail=self._detail_routines(score_routines),
            tendance=self._evaluer_tendance("routines"),
        ))
        scores.append(score_routines * 0.20)

        score_global = round(sum(scores), 1)
        niveau = self._evaluer_niveau(score_global)

        # Conseils basés sur les scores les plus bas
        conseils = self._generer_conseils(dimensions)

        return ScoreBienEtreResponse(
            score_global=score_global,
            niveau=niveau,
            dimensions=dimensions,
            historique_7j=[],
            conseils=conseils,
        )

    # ═══════════════════════════════════════════════════════════
    # 10.17 — ENRICHISSEMENT CONTACTS IA
    # ═══════════════════════════════════════════════════════════

    @avec_cache(ttl=3600, key_func=lambda self: "enrichissement_contacts")
    @avec_gestion_erreurs(default_return=None)
    @chronometre("innovations.enrichissement_contacts", seuil_alerte_ms=10000)
    def enrichir_contacts(self) -> EnrichissementContactsResponse | None:
        """Enrichit les contacts avec suggestions de catégorisation et rappels relationnels."""
        contexte = self._collecter_contexte_contacts()

        prompt = f"""Analyse les contacts suivants et propose des enrichissements.

{contexte}

Retourne un JSON :
{{
  "contacts_enrichis": [
    {{"contact_id": 1, "nom": "Marie Dupont", "categorie_suggeree": "Famille proche", "rappel_relationnel": "Pas contacté depuis 3 mois", "derniere_interaction_jours": 90, "actions_suggerees": ["Appeler pour prendre des nouvelles", "Planifier un repas ensemble"]}}
  ],
  "nb_contacts_analyses": 10,
  "nb_contacts_sans_nouvelles": 3
}}

Règles :
- Suggère une catégorie pertinente (famille, amis proches, collègues, voisins, etc.)
- Signale les contacts sans nouvelles > 60 jours
- Maximum 3 actions suggérées par contact"""

        return self.call_with_parsing_sync(
            prompt=prompt,
            response_model=EnrichissementContactsResponse,
            system_prompt="Tu es un assistant de gestion relationnelle familiale.",
        )

    # ═══════════════════════════════════════════════════════════
    # 10.18 — ANALYSE TENDANCES LOTO/EUROMILLIONS
    # ═══════════════════════════════════════════════════════════

    @avec_cache(ttl=7200, key_func=lambda self, jeu: f"tendances_loto_{jeu}")
    @avec_gestion_erreurs(default_return=None)
    @chronometre("innovations.tendances_loto", seuil_alerte_ms=10000)
    def analyser_tendances_loto(self, jeu: str = "loto") -> AnalyseTendancesLotoResponse | None:
        """Analyse les tendances statistiques des tirages Loto ou EuroMillions."""
        contexte = self._collecter_contexte_tirages(jeu)

        prompt = f"""Analyse les tendances des tirages {jeu} suivants.

{contexte}

Retourne un JSON :
{{
  "jeu": "{jeu}",
  "nb_tirages_analyses": 100,
  "numeros_chauds": [{{"numero": 7, "frequence": 0.15, "retard_tirages": 2, "score_tendance": 0.85}}],
  "numeros_froids": [{{"numero": 33, "frequence": 0.05, "retard_tirages": 25, "score_tendance": 0.15}}],
  "combinaison_suggeree": [7, 12, 23, 31, 42],
  "analyse_ia": "Analyse statistique des patterns observés..."
}}

Règles :
- Top 5 numéros chauds (freq > moyenne)
- Top 5 numéros froids (freq < moyenne)
- La combinaison est purement statistique, rappeler que le loto est un jeu de hasard
- Maximum 49 pour le loto, 50 pour euromillions"""

        return self.call_with_parsing_sync(
            prompt=prompt,
            response_model=AnalyseTendancesLotoResponse,
            system_prompt="Tu es un analyste statistique spécialisé en loterie. Rappelle systématiquement que le loto est un jeu de hasard pur.",
        )

    # ═══════════════════════════════════════════════════════════
    # 10.19 — OPTIMISATION PARCOURS MAGASIN
    # ═══════════════════════════════════════════════════════════

    @avec_gestion_erreurs(default_return=None)
    @chronometre("innovations.parcours_magasin", seuil_alerte_ms=5000)
    def optimiser_parcours_magasin(
        self, liste_id: int | None = None
    ) -> ParcoursOptimiseResponse | None:
        """Optimise le parcours magasin en regroupant les articles par rayon."""
        articles = self._collecter_articles_courses(liste_id)
        if not articles:
            return ParcoursOptimiseResponse()

        prompt = f"""Organise ces articles de courses par rayon de supermarché et optimise le parcours.

Articles : {json.dumps(articles, ensure_ascii=False)}

Retourne un JSON :
{{
  "articles_par_rayon": {{
    "Fruits & Légumes": ["tomates", "carottes", "pommes"],
    "Boulangerie": ["pain", "croissants"],
    "Produits laitiers": ["lait", "yaourt"]
  }},
  "ordre_rayons": ["Fruits & Légumes", "Boulangerie", "Produits laitiers", "Épicerie", "Surgelés", "Boissons"],
  "nb_articles": {len(articles)},
  "temps_estime_minutes": 25
}}

Règles :
- Ordre typique d'un supermarché français (entrée = fruits&légumes, sortie = caisses)
- Regroupe les articles similaires
- Estime le temps en fonction du nombre d'articles"""

        return self.call_with_parsing_sync(
            prompt=prompt,
            response_model=ParcoursOptimiseResponse,
            system_prompt="Tu es un expert en optimisation de parcours en supermarché.",
        )

    # ═══════════════════════════════════════════════════════════
    # 10.8 — VEILLE EMPLOI HABITAT
    # ═══════════════════════════════════════════════════════════

    @avec_cache(ttl=3600, key_func=lambda self, criteres: f"veille_emploi_{hash(str(criteres))}")
    @avec_gestion_erreurs(default_return=None)
    @chronometre("innovations.veille_emploi", seuil_alerte_ms=15000)
    def executer_veille_emploi(
        self, criteres: CriteresVeilleEmploi | None = None
    ) -> VeilleEmploiResponse | None:
        """Exécute la veille emploi avec critères configurables.

        Utilise l'IA pour simuler une recherche et suggérer des offres
        basées sur les critères. En production, connecter aux APIs Indeed/LinkedIn.
        """
        if criteres is None:
            criteres = self._charger_criteres_veille()

        prompt = f"""Simule une veille emploi avec les critères suivants :
- Domaine : {criteres.domaine}
- Mots-clés : {', '.join(criteres.mots_cles)}
- Type contrat : {', '.join(criteres.type_contrat)}
- Mode travail : {', '.join(criteres.mode_travail)}
- Rayon : {criteres.rayon_km} km

Retourne un JSON avec des offres réalistes :
{{
  "offres": [
    {{"titre": "RH Manager", "entreprise": "Acme Corp", "localisation": "Lyon (69)", "type_contrat": "CDI", "mode_travail": "hybride", "url": "", "date_publication": "2026-03-28", "salaire_estime": "45-55K€", "score_pertinence": 0.9}}
  ],
  "nb_offres_trouvees": 5,
  "criteres_utilises": {criteres.model_dump_json()},
  "derniere_execution": "{datetime.now(UTC).isoformat()}"
}}

Note : génère 3 à 5 offres fictives mais réalistes basées sur le marché actuel."""

        return self.call_with_parsing_sync(
            prompt=prompt,
            response_model=VeilleEmploiResponse,
            system_prompt="Tu es un expert en recrutement et veille emploi. Génère des offres réalistes correspondant aux critères.",
        )

    # ═══════════════════════════════════════════════════════════
    # 10.3 — MODE INVITÉ
    # ═══════════════════════════════════════════════════════════

    def creer_lien_invite(
        self,
        nom_invite: str,
        modules: list[str] | None = None,
        duree_heures: int = 48,
    ) -> LienInviteResponse:
        """Crée un lien partageable pour un invité (nounou/grands-parents).

        Args:
            nom_invite: Nom de l'invité
            modules: Modules autorisés (repas, routines, contacts_urgence)
            duree_heures: Durée de validité du lien
        """
        if modules is None:
            modules = ["repas", "routines", "contacts_urgence"]

        nom_invite_safe = _sanitiser(nom_invite, 100)
        token = secrets.token_urlsafe(32)
        expiration = datetime.now(UTC) + timedelta(hours=duree_heures)

        _tokens_invites[token] = {
            "nom": nom_invite_safe,
            "modules": modules,
            "expire_a": expiration.isoformat(),
            "cree_le": datetime.now(UTC).isoformat(),
        }

        return LienInviteResponse(
            token=token,
            url=f"/invite/{token}",
            expire_dans_heures=duree_heures,
            modules_autorises=modules,
            nom_invite=nom_invite_safe,
        )

    def obtenir_donnees_invite(self, token: str) -> DonneesInviteResponse | None:
        """Récupère les données accessibles par un invité via son token."""
        invite = _tokens_invites.get(token)
        if not invite:
            return None

        # Vérifier expiration
        expire_a = datetime.fromisoformat(invite["expire_a"])
        if datetime.now(UTC) > expire_a:
            del _tokens_invites[token]
            return None

        modules = invite.get("modules", [])
        donnees = DonneesInviteResponse(notes=f"Accès invité pour {invite['nom']}")

        try:
            with obtenir_contexte_db() as session:
                # Repas de la semaine
                if "repas" in modules:
                    donnees.repas_semaine = self._collecter_repas_invite(session)

                # Routines enfant
                if "routines" in modules:
                    donnees.routines = self._collecter_routines_invite(session)
                    donnees.enfant = self._collecter_profil_enfant_invite(session)

                # Contacts d'urgence
                if "contacts_urgence" in modules:
                    donnees.contacts_urgence = self._collecter_contacts_urgence(session)
        except Exception:
            logger.warning("Erreur lors de la collecte des données invité", exc_info=True)

        return donnees

    # ═══════════════════════════════════════════════════════════
    # HELPERS — Collecte de contexte DB
    # ═══════════════════════════════════════════════════════════

    def _collecter_contexte_annuel(self, annee: int) -> str:
        """Collecte les données d'une année pour le bilan."""
        sections = []
        debut = date(annee, 1, 1)
        fin = date(annee, 12, 31)

        try:
            with obtenir_contexte_db() as session:
                from sqlalchemy import func
                from src.core.models import BudgetFamille, Recette, Repas
                from src.core.models.projets import Projet

                # Recettes
                nb_recettes = session.query(func.count(Recette.id)).scalar() or 0
                sections.append(f"Recettes en base: {nb_recettes}")

                # Repas planifiés sur l'année
                nb_repas = (
                    session.query(func.count(Repas.id))
                    .filter(Repas.date_repas >= debut, Repas.date_repas <= fin)
                    .scalar() or 0
                )
                sections.append(f"Repas planifiés en {annee}: {nb_repas}")

                # Budget
                depenses = (
                    session.query(func.sum(BudgetFamille.montant))
                    .filter(BudgetFamille.date >= debut, BudgetFamille.date <= fin)
                    .scalar() or 0
                )
                sections.append(f"Total dépenses {annee}: {depenses}€")

                # Projets maison terminés
                nb_projets = (
                    session.query(func.count(Projet.id))
                    .filter(Projet.statut == "terminé")
                    .scalar() or 0
                )
                sections.append(f"Projets maison terminés: {nb_projets}")

        except Exception:
            logger.warning("Erreur collecte contexte annuel", exc_info=True)
            sections.append("Données partielles (erreur de collecte)")

        return "\n".join(sections) if sections else "Aucune donnée disponible."

    def _collecter_contexte_contacts(self) -> str:
        """Collecte les contacts pour enrichissement."""
        try:
            with obtenir_contexte_db() as session:
                from src.core.models.contacts import ContactFamille

                contacts = session.query(ContactFamille).limit(50).all()
                if not contacts:
                    return "Aucun contact en base."

                lignes = []
                for c in contacts:
                    lignes.append(
                        f"ID:{c.id} - {c.nom} {getattr(c, 'prenom', '')} | "
                        f"Catégorie: {getattr(c, 'categorie', 'non définie')} | "
                        f"Téléphone: {'oui' if getattr(c, 'telephone', None) else 'non'}"
                    )
                return "\n".join(lignes)
        except Exception:
            logger.warning("Erreur collecte contacts", exc_info=True)
            return "Erreur de collecte des contacts."

    def _collecter_contexte_tirages(self, jeu: str) -> str:
        """Collecte les tirages de loterie pour analyse."""
        try:
            with obtenir_contexte_db() as session:
                from src.core.models.jeux import TirageLoto

                tirages = (
                    session.query(TirageLoto)
                    .filter(TirageLoto.type_jeu == jeu)
                    .order_by(TirageLoto.date_tirage.desc())
                    .limit(100)
                    .all()
                )
                if not tirages:
                    return f"Aucun tirage {jeu} en base."

                lignes = []
                for t in tirages:
                    numeros = getattr(t, "numeros", [])
                    lignes.append(f"{t.date_tirage}: {numeros}")
                return "\n".join(lignes)
        except Exception:
            logger.warning("Erreur collecte tirages", exc_info=True)
            return f"Pas assez de données {jeu} pour l'analyse."

    def _collecter_articles_courses(self, liste_id: int | None = None) -> list[str]:
        """Collecte les articles de la liste de courses active."""
        try:
            with obtenir_contexte_db() as session:
                from src.core.models import ArticleCourses, ListeCourses, Ingredient

                query = session.query(ListeCourses).filter(ListeCourses.archivee.is_(False))
                if liste_id:
                    query = query.filter(ListeCourses.id == liste_id)
                liste = query.order_by(ListeCourses.id.desc()).first()
                if not liste:
                    return []

                articles = (
                    session.query(ArticleCourses)
                    .filter(ArticleCourses.liste_id == liste.id, ArticleCourses.coche.is_(False))
                    .all()
                )
                noms = []
                for a in articles:
                    ingredient = session.query(Ingredient).filter(Ingredient.id == a.ingredient_id).first()
                    if ingredient:
                        noms.append(ingredient.nom)
                return noms
        except Exception:
            logger.warning("Erreur collecte articles courses", exc_info=True)
            return []

    def _charger_criteres_veille(self) -> CriteresVeilleEmploi:
        """Charge les critères de veille emploi depuis les préférences utilisateur."""
        try:
            with obtenir_contexte_db() as session:
                from src.core.models.preferences import PreferenceUtilisateur

                pref = (
                    session.query(PreferenceUtilisateur)
                    .filter(PreferenceUtilisateur.cle == "veille_emploi_criteres")
                    .first()
                )
                if pref and pref.valeur:
                    data = json.loads(pref.valeur) if isinstance(pref.valeur, str) else pref.valeur
                    return CriteresVeilleEmploi(**data)
        except Exception:
            logger.debug("Pas de critères veille emploi personnalisés, utilisation des défauts")
        return CriteresVeilleEmploi()

    # ── Helpers score bien-être ──

    def _calculer_score_sport(self) -> float:
        """Score sport basé sur Garmin (0-100)."""
        try:
            with obtenir_contexte_db() as session:
                from sqlalchemy import func
                from src.core.models.garmin import DonneesGarmin

                semaine = date.today() - timedelta(days=7)
                donnees = (
                    session.query(DonneesGarmin)
                    .filter(DonneesGarmin.date >= semaine)
                    .all()
                )
                if not donnees:
                    return 50.0

                pas_moyen = sum(getattr(d, "pas", 0) or 0 for d in donnees) / len(donnees)
                # 10000 pas/jour = 100, 0 = 0
                score = min(100, (pas_moyen / 10000) * 100)
                return round(score, 1)
        except Exception:
            return 50.0

    def _calculer_score_nutrition(self) -> float:
        """Score nutrition basé sur le planning repas (0-100)."""
        try:
            with obtenir_contexte_db() as session:
                from sqlalchemy import func
                from src.core.models import Repas

                semaine = date.today() - timedelta(days=7)
                nb_repas = (
                    session.query(func.count(Repas.id))
                    .filter(Repas.date_repas >= semaine)
                    .scalar() or 0
                )
                # 21 repas/semaine (3/jour) = 100
                score = min(100, (nb_repas / 21) * 100)
                return round(score, 1)
        except Exception:
            return 50.0

    def _calculer_score_budget(self) -> float:
        """Score budget basé sur les dépassements (0-100)."""
        try:
            with obtenir_contexte_db() as session:
                from sqlalchemy import func
                from src.core.models import BudgetFamille

                mois_courant = date.today().replace(day=1)
                total = (
                    session.query(func.sum(BudgetFamille.montant))
                    .filter(BudgetFamille.date >= mois_courant)
                    .scalar() or 0
                )
                # Moins de dépenses = meilleur score (heuristique simple)
                score = max(0, 100 - min(100, total / 50))
                return round(score, 1)
        except Exception:
            return 60.0

    def _calculer_score_routines(self) -> float:
        """Score routines basé sur l'accomplissement (0-100)."""
        try:
            with obtenir_contexte_db() as session:
                from sqlalchemy import func
                from src.core.models.famille import Routine

                routines_actives = (
                    session.query(func.count(Routine.id))
                    .filter(Routine.actif.is_(True))
                    .scalar() or 0
                )
                if routines_actives == 0:
                    return 50.0
                # Avoir des routines actives = bon signe
                score = min(100, routines_actives * 15)
                return round(float(score), 1)
        except Exception:
            return 50.0

    def _detail_sport(self, score: float) -> str:
        if score >= 80:
            return "Excellent niveau d'activité physique"
        if score >= 60:
            return "Bon niveau d'activité, continuez !"
        if score >= 40:
            return "Activité modérée, essayez de bouger plus"
        return "Activité insuffisante, fixez-vous un objectif de pas quotidien"

    def _detail_nutrition(self, score: float) -> str:
        if score >= 80:
            return "Planning repas bien rempli et équilibré"
        if score >= 60:
            return "Bonne planification, quelques repas à ajouter"
        if score >= 40:
            return "Planning repas incomplet, planifiez davantage"
        return "Peu de repas planifiés, utilisez le planificateur IA"

    def _detail_budget(self, score: float) -> str:
        if score >= 80:
            return "Budget maîtrisé, bravo !"
        if score >= 60:
            return "Budget correct, attention aux dépenses"
        if score >= 40:
            return "Budget tendu, surveillez vos dépenses"
        return "Budget dépassé, réduisez les dépenses non essentielles"

    def _detail_routines(self, score: float) -> str:
        if score >= 80:
            return "Routines régulières et bien suivies"
        if score >= 60:
            return "Bonnes routines, restez constant"
        if score >= 40:
            return "Quelques routines à consolider"
        return "Peu de routines actives, créez-en pour structurer votre quotidien"

    def _evaluer_tendance(self, dimension: str) -> str:
        """Évalue la tendance d'une dimension (simplifié)."""
        return "stable"

    def _evaluer_niveau(self, score: float) -> str:
        if score >= 80:
            return "excellent"
        if score >= 60:
            return "bon"
        if score >= 40:
            return "moyen"
        return "attention"

    def _generer_conseils(self, dimensions: list[DimensionBienEtre]) -> list[str]:
        """Génère des conseils basés sur les dimensions les plus faibles."""
        conseils = []
        sorted_dims = sorted(dimensions, key=lambda d: d.score)
        for dim in sorted_dims[:2]:
            if dim.score < 60:
                conseils.append(f"Améliorez votre {dim.nom.lower()} : {dim.detail}")
        if not conseils:
            conseils.append("Continuez ainsi, votre bien-être familial est excellent !")
        return conseils

    # ── Helpers mode invité ──

    def _collecter_repas_invite(self, session: Any) -> list[dict]:
        """Collecte les repas de la semaine pour un invité."""
        from src.core.models import Repas, Planning

        today = date.today()
        fin_semaine = today + timedelta(days=7)

        planning = session.query(Planning).order_by(Planning.cree_le.desc()).first()
        if not planning:
            return []

        repas = (
            session.query(Repas)
            .filter(
                Repas.planning_id == planning.id,
                Repas.date_repas >= today,
                Repas.date_repas <= fin_semaine,
            )
            .order_by(Repas.date_repas, Repas.type_repas)
            .all()
        )
        return [
            {
                "date": r.date_repas.isoformat(),
                "type": r.type_repas,
                "recette": getattr(getattr(r, "recette", None), "nom", "Repas libre"),
            }
            for r in repas
        ]

    def _collecter_routines_invite(self, session: Any) -> list[dict]:
        """Collecte les routines actives pour un invité."""
        from src.core.models.famille import Routine

        routines = session.query(Routine).filter(Routine.actif.is_(True)).all()
        return [
            {"nom": r.nom, "categorie": getattr(r, "categorie", "")}
            for r in routines
        ]

    def _collecter_profil_enfant_invite(self, session: Any) -> dict:
        """Collecte le profil enfant pour un invité."""
        from src.core.models import ProfilEnfant

        enfant = (
            session.query(ProfilEnfant)
            .filter(ProfilEnfant.actif.is_(True))
            .first()
        )
        if not enfant:
            return {}
        return {
            "prenom": enfant.name,
            "date_naissance": enfant.date_of_birth.isoformat() if enfant.date_of_birth else None,
        }

    def _collecter_contacts_urgence(self, session: Any) -> list[dict]:
        """Collecte les contacts d'urgence pour un invité."""
        try:
            from src.core.models.contacts import ContactFamille

            contacts = (
                session.query(ContactFamille)
                .filter(ContactFamille.categorie == "urgence")
                .all()
            )
            return [
                {
                    "nom": f"{c.nom} {getattr(c, 'prenom', '')}".strip(),
                    "telephone": getattr(c, "telephone", ""),
                    "relation": getattr(c, "relation", ""),
                }
                for c in contacts
            ]
        except Exception:
            return []


@service_factory("innovations", tags={"phase10", "ia"})
def get_innovations_service() -> InnovationsService:
    """Factory pour le service Innovations (singleton via registre)."""
    return InnovationsService()
