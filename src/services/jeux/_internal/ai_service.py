"""
Service IA pour les Jeux - Analyse Mistral

Hérite de BaseAIService pour bénéficier automatiquement de:
- ✅ Rate limiting unifié (RateLimitIA)
- ✅ Cache sémantique (CacheIA) — économise les appels API
- ✅ Métriques et logging
- ✅ Health check

⚠️ RAPPEL: Les prédictions IA ne changent pas les probabilités.
Les jeux de hasard restent du hasard.
"""

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from src.core.ai import obtenir_client_ia
from src.core.ai.client import ClientIA
from src.core.exceptions import ErreurLimiteDebit, ErreurServiceIA
from src.core.monitoring import chronometre
from src.services.core.base.ai_service import BaseAIService
from src.services.core.base.async_utils import sync_wrapper
from src.services.core.registry import service_factory
from src.services.jeux._internal.series_service import (
    SEUIL_VALUE_ALERTE,
    SEUIL_VALUE_HAUTE,
    SeriesService,
)

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# TYPES
# ═══════════════════════════════════════════════════════════


@dataclass
class AnalyseIA:
    """Résultat d'une analyse IA"""

    type_analyse: str  # "paris", "loto", "global"
    resume: str
    points_cles: list[str]
    recommandations: list[str]
    avertissement: str
    confiance: float  # 0-1
    genere_le: datetime


@dataclass
class OpportuniteAnalysee:
    """Opportunité avec analyse IA"""

    identifiant: str  # Ex: "Ligue1_More_2_5"
    type_jeu: str  # "paris", "loto"
    value: float
    serie: int
    frequence: float
    niveau: str  # "🟢", "🟡", "⚪"
    analyse_ia: str
    score_confiance: float


# ═══════════════════════════════════════════════════════════
# SERVICE PRINCIPAL
# ═══════════════════════════════════════════════════════════


class JeuxAIService(BaseAIService):
    """
    Service d'analyse IA pour les jeux.

    Hérite de BaseAIService pour bénéficier automatiquement de:
    - Rate limiting unifié via RateLimitIA
    - Cache sémantique via CacheIA (économise les appels IA)
    - Métriques et logging
    - Health check

    Utilise Mistral pour générer des analyses intelligentes
    des opportunités détectées par la loi des séries.

    ⚠️ Les analyses IA sont indicatives et ne garantissent
    aucun résultat. Les jeux restent du hasard.
    """

    # Prompt système pour les analyses
    SYSTEM_PROMPT = """Tu es un analyste de données spécialisé dans les statistiques des jeux.

RÈGLES IMPORTANTES:
1. Tu analyses des DONNÉES HISTORIQUES, pas des prédictions
2. Tu rappelles TOUJOURS que les jeux de hasard sont IMPRÉVISIBLES
    (ancienne variante d'encodage rencontrée: IMPRÃ‰VISIBLES)
    (ancienne variante d'encodage rencontrée: IMPRÃ‰VISIBLES)
3. Tu ne promets JAMAIS de gain ou de résultat
4. Tu utilises un ton factuel et prudent

CONTEXTE "LOI DES SÉRIES":
- La "loi des séries" est une PERCEPTION PSYCHOLOGIQUE
- Un événement "en retard" n'a PAS plus de chances de se produire
- Chaque tirage/match est INDÉPENDANT
- Tu analyses les écarts à la moyenne, pas des "probabilités futures"

FORMAT DE RÉPONSE:
- Résumé court (2-3 phrases)
- Points clés (bullet points)
- Recommandations (prudentes)
- Toujours finir par un rappel sur le hasard"""

    AVERTISSEMENT_STANDARD = (
        "⚠️ Rappel: Les jeux de hasard sont imprévisibles. "
        "Cette analyse est basée sur des données historiques et ne garantit aucun résultat. "
        "Ne jouez que ce que vous pouvez vous permettre de perdre."
    )

    def __init__(self):
        """Initialise le service IA Jeux via BaseAIService."""
        self._client_ia: ClientIA | None = None
        super().__init__(
            client=None,  # Lazy-loaded via property
            cache_prefix="jeux",
            default_ttl=3600,
            default_temperature=0.3,
            service_name="jeux",
        )

    @property  # type: ignore[override]  # Intentionnel: property remplace l'attribut parent pour lazy-loading
    def client(self) -> ClientIA | None:
        """Lazy loading du client IA."""
        if self._client_ia is None:
            try:
                self._client_ia = obtenir_client_ia()
            except Exception as e:
                logger.debug("Client IA indisponible: %s", e)
                return None
        return self._client_ia

    @client.setter
    def client(self, value: ClientIA | None) -> None:
        """Setter pour compatibilité avec BaseAIService.__init__."""
        self._client_ia = value

    # ───────────────────────────────────────────────────────────────
    # ANALYSES PARIS SPORTIFS
    # ───────────────────────────────────────────────────────────────

    async def analyser_paris_async(
        self,
        opportunites: list[dict[str, Any]],
        competition: str = "Général",
    ) -> AnalyseIA:
        """
        Analyse les opportunités Paris sportifs avec IA.

        Args:
            opportunites: Liste des opportunités détectées
            competition: Nom de la compétition

        Returns:
            AnalyseIA avec résumé et recommandations
        """
        if not opportunites:
            return AnalyseIA(
                type_analyse="paris",
                resume="Aucune opportunité détectée actuellement.",
                points_cles=["Pas d'opportunité significative"],
                recommandations=["Attendre de nouvelles données"],
                avertissement=self.AVERTISSEMENT_STANDARD,
                confiance=0.0,
                genere_le=datetime.now(),
            )

        # Construire le prompt
        prompt = self._construire_prompt_paris(opportunites, competition)

        try:
            reponse = await self.call_with_cache(
                prompt=prompt,
                system_prompt=self.SYSTEM_PROMPT,
                temperature=0.3,
                max_tokens=800,
            )

            if not reponse:
                return self._analyse_fallback("paris", opportunites)

            return self._parser_reponse_analyse(reponse, "paris")

        except (ErreurServiceIA, ErreurLimiteDebit) as e:
            logger.warning(f"Erreur IA Paris: {e}")
            return self._analyse_fallback("paris", opportunites)

    @chronometre("ia.jeux.analyser_paris", seuil_alerte_ms=10000)
    def analyser_paris(
        self,
        opportunites: list[dict[str, Any]],
        competition: str = "Général",
    ) -> AnalyseIA:
        """Version synchrone de analyser_paris_async."""
        _sync = sync_wrapper(self.analyser_paris_async)
        return _sync(opportunites, competition)

    def _construire_prompt_paris(self, opportunites: list[dict[str, Any]], competition: str) -> str:
        """Construit le prompt pour l'analyse Paris."""
        lignes = [f"Analyse des opportunités Paris Sportifs - {competition}:", ""]

        for opp in opportunites[:10]:  # Max 10 pour le prompt
            niveau = SeriesService.niveau_opportunite(opp.get("value", 0))
            lignes.append(
                f"- {opp.get('marche', 'Marché')}: "
                f"Value={opp.get('value', 0):.2f}, "
                f"Série={opp.get('serie', 0)}, "
                f"Fréquence={opp.get('frequence', 0):.1%} "
                f"[{niveau}]"
            )

        lignes.extend(
            [
                "",
                f"Total opportunités: {len(opportunites)}",
                f"- Très en retard (🟢): {sum(1 for o in opportunites if o.get('value', 0) >= SEUIL_VALUE_HAUTE)}",
                f"- En retard (🟡): {sum(1 for o in opportunites if SEUIL_VALUE_ALERTE <= o.get('value', 0) < SEUIL_VALUE_HAUTE)}",
                "",
                "Analyse ces données et fournis un résumé avec recommandations prudentes.",
            ]
        )

        return "\n".join(lignes)

    # ───────────────────────────────────────────────────────────────
    # ANALYSES LOTO
    # ───────────────────────────────────────────────────────────────

    async def analyser_loto_async(
        self,
        numeros_retard: list[dict[str, Any]],
        type_numero: str = "principal",
    ) -> AnalyseIA:
        """
        Analyse les numéros en retard pour le Loto avec IA.

        Args:
            numeros_retard: Liste des numéros en retard
            type_numero: "principal" ou "chance"

        Returns:
            AnalyseIA avec résumé et recommandations
        """
        if not numeros_retard:
            return AnalyseIA(
                type_analyse="loto",
                resume="Aucun numéro significativement en retard.",
                points_cles=["Distribution normale des tirages"],
                recommandations=["Tout numéro a la même probabilité"],
                avertissement=self.AVERTISSEMENT_STANDARD,
                confiance=0.0,
                genere_le=datetime.now(),
            )

        prompt = self._construire_prompt_loto(numeros_retard, type_numero)

        try:
            reponse = await self.call_with_cache(
                prompt=prompt,
                system_prompt=self.SYSTEM_PROMPT,
                temperature=0.3,
                max_tokens=800,
            )

            if not reponse:
                return self._analyse_fallback("loto", numeros_retard)

            return self._parser_reponse_analyse(reponse, "loto")

        except (ErreurServiceIA, ErreurLimiteDebit) as e:
            logger.warning(f"Erreur IA Loto: {e}")
            return self._analyse_fallback("loto", numeros_retard)

    def analyser_loto(
        self,
        numeros_retard: list[dict[str, Any]],
        type_numero: str = "principal",
    ) -> AnalyseIA:
        """Version synchrone de analyser_loto_async."""
        _sync = sync_wrapper(self.analyser_loto_async)
        return _sync(numeros_retard, type_numero)

    def _construire_prompt_loto(
        self, numeros_retard: list[dict[str, Any]], type_numero: str
    ) -> str:
        """Construit le prompt pour l'analyse Loto."""
        type_label = (
            "Numéros principaux (1-49)" if type_numero == "principal" else "Numéros Chance (1-10)"
        )

        lignes = [f"Analyse des numéros en retard - Loto {type_label}:", ""]

        for num in numeros_retard[:15]:  # Max 15
            niveau = SeriesService.niveau_opportunite(num.get("value", 0))
            lignes.append(
                f"- Numéro {num.get('numero', '?')}: "
                f"Value={num.get('value', 0):.2f}, "
                f"Série={num.get('serie', 0)} tirages, "
                f"Fréquence={num.get('frequence', 0):.1%} "
                f"[{niveau}]"
            )

        freq_theorique = 5 / 49 if type_numero == "principal" else 1 / 10
        lignes.extend(
            [
                "",
                f"Fréquence théorique: {freq_theorique:.1%}",
                f"Total en retard: {len(numeros_retard)}",
                "",
                "RAPPEL: Chaque tirage est INDÉPENDANT. Un numéro 'en retard' n'a pas plus de chances.",
                "",
                "Analyse ces données avec prudence et rappelle que le Loto est un jeu de hasard pur.",
            ]
        )

        return "\n".join(lignes)

    # ───────────────────────────────────────────────────────────────
    # RÉSUMÉ MENSUEL IA
    # ───────────────────────────────────────────────────────────────

    async def generer_resume_mensuel_async(
        self,
        mois: str,
        kpis: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Génère un résumé mensuel IA enrichi avec analyse Mistral.

        Args:
            mois: Format "YYYY-MM"
            kpis: Dictionnaire avec roi_mois, taux_reussite_mois, benefice_mois, paris_actifs

        Returns:
            Dict avec analyse, points_forts, points_faibles, recommandations
        """
        roi = kpis.get("roi_mois", 0.0)
        taux = kpis.get("taux_reussite_mois", 0.0)
        benefice = kpis.get("benefice_mois", 0.0)
        nb_paris = kpis.get("nb_paris_total", 0)

        prompt = f"""Génère un résumé mensuel pour un joueur de paris sportifs.

DONNÉES DU MOIS ({mois}):
- ROI: {roi:.1f}%
- Taux de réussite: {taux:.1f}%
- Bénéfice: {benefice:.2f}€
- Nombre de paris: {nb_paris}

INSTRUCTIONS:
1. Rédige une analyse courte (3-4 phrases) du mois
2. Liste 2-3 points forts (si ROI > 0 ou taux > 50%)
3. Liste 2-3 points faibles (si ROI < 0 ou taux < 50%)
4. Propose 2-3 recommandations concrètes
5. Reste factuel et neutre

FORMAT ATTENDU (JSON):
{{
  "analyse": "Analyse du mois...",
  "points_forts": ["Point 1", "Point 2"],
  "points_faibles": ["Faible 1", "Faible 2"],
  "recommandations": ["Recommandation 1", "Recommandation 2"]
}}
"""

        try:
            reponse = await self.call_with_parsing_async(
                prompt=prompt,
                response_model=dict,
                system_prompt="Tu es un analyste de données sportives factuel et neutre. Tu analyses les performances historiques sans promesse de résultat futur. Les paris sont du hasard.",
                temperature=0.5,
                max_tokens=800,
            )

            if not reponse or not isinstance(reponse, dict):
                return self._resume_fallback(mois, kpis)

            return {
                "mois": mois,
                "analyse": reponse.get("analyse", f"En {mois}, vous avez placé {nb_paris} paris."),
                "points_forts": reponse.get("points_forts", []),
                "points_faibles": reponse.get("points_faibles", []),
                "recommandations": reponse.get("recommandations", [
                    "Continuez à privilégier les value bets",
                    "Respectez votre budget mensuel"
                ]),
                "kpis": kpis,
            }

        except (ErreurServiceIA, ErreurLimiteDebit) as e:
            logger.warning(f"Erreur IA résumé mensuel: {e}")
            return self._resume_fallback(mois, kpis)

    @chronometre("ia.jeux.resume_mensuel", seuil_alerte_ms=12000)
    def generer_resume_mensuel(
        self,
        mois: str,
        kpis: dict[str, Any],
    ) -> dict[str, Any]:
        """Version synchrone de generer_resume_mensuel_async."""
        _sync = sync_wrapper(self.generer_resume_mensuel_async)
        return _sync(mois, kpis)

    def _resume_fallback(self, mois: str, kpis: dict[str, Any]) -> dict[str, Any]:
        """Résumé fallback si IA indisponible."""
        roi = kpis.get("roi_mois", 0.0)
        taux = kpis.get("taux_reussite_mois", 0.0)
        benefice = kpis.get("benefice_mois", 0.0)
        nb_paris = kpis.get("nb_paris_total", 0)

        points_forts = []
        points_faibles = []

        if roi > 0:
            points_forts.append(f"ROI positif de {roi:.1f}%")
        elif roi < 0:
            points_faibles.append(f"ROI négatif de {roi:.1f}%")

        if taux >= 50:
            points_forts.append(f"Taux de réussite de {taux:.1f}%")
        elif taux > 0:
            points_faibles.append(f"Taux de réussite bas: {taux:.1f}%")

        if nb_paris == 0:
            points_faibles.append("Aucun pari ce mois")

        return {
            "mois": mois,
            "analyse": f"En {mois}, vous avez placé {nb_paris} paris pour un ROI de {roi:.1f}% et un bénéfice de {benefice:.2f}€.",
            "points_forts": points_forts or ["Aucun point fort ce mois"],
            "points_faibles": points_faibles or ["Performances à améliorer"],
            "recommandations": [
                "Continuez à privilégier les value bets avec edge > 5%",
                "Fixez-vous un budget mensuel et respectez-le",
                "Analysez vos performances par championnat et type de pari",
            ],
            "kpis": kpis,
        }

    # ───────────────────────────────────────────────────────────────
    # ANALYSE GLOBALE
    # ───────────────────────────────────────────────────────────────

    async def generer_synthese_async(
        self,
        alertes_actives: int,
        opportunites_paris: int,
        opportunites_loto: int,
    ) -> AnalyseIA:
        """
        Génère une synthèse globale des opportunités.

        Args:
            alertes_actives: Nombre d'alertes actives
            opportunites_paris: Nombre d'opportunités Paris
            opportunites_loto: Nombre d'opportunités Loto

        Returns:
            AnalyseIA synthèse
        """
        prompt = f"""Synthèse des opportunités détectées par la "loi des séries":

- Alertes actives: {alertes_actives}
- Opportunités Paris sportifs: {opportunites_paris}
- Numéros Loto en retard: {opportunites_loto}

Génère un résumé court (3-4 phrases) avec:
1. État actuel des opportunités
2. Points d'attention
3. Rappel sur le caractère aléatoire des jeux
"""

        try:
            reponse = await self.call_with_cache(
                prompt=prompt,
                system_prompt=self.SYSTEM_PROMPT,
                temperature=0.4,
                max_tokens=500,
            )

            if not reponse:
                return AnalyseIA(
                    type_analyse="global",
                    resume=f"{alertes_actives} alertes actives.",
                    points_cles=["Service IA indisponible"],
                    recommandations=["Réessayer ultérieurement"],
                    avertissement=self.AVERTISSEMENT_STANDARD,
                    confiance=0.3,
                    genere_le=datetime.now(),
                )

            return self._parser_reponse_analyse(reponse, "global")

        except (ErreurServiceIA, ErreurLimiteDebit) as e:
            logger.warning(f"Erreur IA synthèse: {e}")
            return AnalyseIA(
                type_analyse="global",
                resume=f"{alertes_actives} alertes actives, {opportunites_paris + opportunites_loto} opportunités totales.",
                points_cles=[
                    f"Paris sportifs: {opportunites_paris} marchés en retard",
                    f"Loto: {opportunites_loto} numéros en retard",
                ],
                recommandations=["Consulter les détails par catégorie"],
                avertissement=self.AVERTISSEMENT_STANDARD,
                confiance=0.5,
                genere_le=datetime.now(),
            )

    def generer_synthese(
        self,
        alertes_actives: int,
        opportunites_paris: int,
        opportunites_loto: int,
    ) -> AnalyseIA:
        """Version synchrone de generer_synthese_async."""
        _sync = sync_wrapper(self.generer_synthese_async)
        return _sync(alertes_actives, opportunites_paris, opportunites_loto)

    # ───────────────────────────────────────────────────────────────
    # GÉNÉRATEUR GRILLES IA PONDÉRÉ 
    # ───────────────────────────────────────────────────────────────

    async def generer_grille_ia_ponderee_async(
        self,
        stats_frequences: dict[int, dict],
        mode: str = "equilibre",
    ) -> dict[str, Any]:
        """
        Génère une grille loto intelligente pondérée par fréquences et séries.

        Args:
            stats_frequences: Stats par numéro {num: {freq: int, ecart: int, dernier: str}}
            mode: "chauds" (fréquents) | "froids" (en retard) | "equilibre" (mixte)

        Returns:
            Dict avec numeros (list[int]), numero_chance (int), analyse (str), confiance (float)
        """
        prompt = f"""Génère UNE grille Loto (5 numéros de 1 à 49 + 1 numéro chance de 1 à 10) optimisée.

MODE: {mode}
STATISTIQUES DES 20 DERNIERS TIRAGES:
{self._formater_stats_pour_prompt(stats_frequences, top_n=15)}

CONSIGNES:
- Mode "chauds": privilégier numéros fréquents (sortis récemment)
- Mode "froids": privilégier numéros en retard (écart élevé)
- Mode "equilibre": mix 2-3 chauds + 2-3 froids
- ÉVITER les suites évidentes (1-2-3-4-5)
- Équilibrer pairs/impairs et petits/grands
- Expliquer brièvement la logique

RÉPONSE AU FORMAT JSON:
{{
  "numeros": [5, 12, 23, 34, 45],
  "numero_chance": 7,
  "analyse": "Grille équilibrée avec 3 numéros chauds (5, 12, 23) et 2 en retard (34, 45). Repartition pairs/impairs: 3/2.",
  "confiance": 0.6
}}"""

        try:
            reponse = await self.call_with_parsing_async(
                prompt=prompt,
                system_prompt=self.SYSTEM_PROMPT
                + "\n\nTu génères des grilles Loto intelligentes basées sur statistiques.",
                temperature=0.6,  # Plus de créativité
                max_tokens=400,
            )

            if not reponse:
                return self._grille_fallback(mode)

            # Valider la grille
            if not self._valider_grille(reponse):
                logger.warning("Grille IA invalide, fallback aléatoire")
                return self._grille_fallback(mode)

            return reponse

        except Exception as e:
            logger.warning(f"Erreur génération grille IA: {e}")
            return self._grille_fallback(mode)

    def generer_grille_ia_ponderee(
        self,
        stats_frequences: dict[int, dict],
        mode: str = "equilibre",
    ) -> dict[str, Any]:
        """Version synchrone de generer_grille_ia_ponderee_async."""
        _sync = sync_wrapper(self.generer_grille_ia_ponderee_async)
        return _sync(stats_frequences, mode)

    # ───────────────────────────────────────────────────────────────
    # ANALYSE GRILLES JOUEUR 
    # ───────────────────────────────────────────────────────────────

    async def analyser_grille_joueur_async(
        self,
        numeros: list[int],
        numero_chance: int,
        stats_frequences: dict[int, dict],
    ) -> dict[str, Any]:
        """
        Analyse une grille jouée par l'utilisateur avec critique IA.

        Args:
            numeros: Liste 5 numéros (1-49)
            numero_chance: Numéro chance (1-10)
            stats_frequences: Stats historiques

        Returns:
            Dict avec note (0-10), points_forts (list), points_faibles (list), recommandations (list)
        """
        prompt = f"""Analyse cette grille Loto jouée par un utilisateur:

GRILLE: {sorted(numeros)} + N°{numero_chance}

STATISTIQUES (20 derniers tirages):
{self._formater_stats_pour_prompt(stats_frequences, top_n=10)}

CONSIGNES D'ANALYSE:
1. Évalue l'équilibre pairs/impairs (idéal: 2-3 / 3-2)
2. Vérifie la répartition petits (1-25) / grands (26-49)
3. Regarde si des numéros sont statistiquement "chauds" ou "froids"
4. Détecte les patterns évidents (suite, multiples de 5...)
5. Donne une NOTE sur 10 et des recommandations

⚠️ IMPORTANT: Ne JAMAIS promettre de gain. Les jeux sont du hasard.

RÉPONSE AU FORMAT JSON:
{{
  "note": 7,
  "points_forts": ["Bon équilibre pairs/impairs (3/2)", "Mix numéros chauds et froids"],
  "points_faibles": ["Concentration de petits numéros (4/5 sous 25)"],
  "recommandations": ["Ajouter 1-2 numéros dans la tranche 30-49", "Le numéro chance 7 est très fréquent"],
  "appreciation": "Grille correcte mais déséquilibrée vers les petits numéros."
}}"""

        try:
            reponse = await self.call_with_parsing_async(
                prompt=prompt,
                system_prompt=self.SYSTEM_PROMPT
                + "\n\nTu analyses des grilles Loto avec un ton constructif et pédagogique.",
                temperature=0.4,
                max_tokens=500,
            )

            if not reponse:
                return self._analyse_grille_fallback(numeros, numero_chance)

            return reponse

        except Exception as e:
            logger.warning(f"Erreur analyse grille: {e}")
            return self._analyse_grille_fallback(numeros, numero_chance)

    def analyser_grille_joueur(
        self,
        numeros: list[int],
        numero_chance: int,
        stats_frequences: dict[int, dict],
    ) -> dict[str, Any]:
        """Version synchrone de analyser_grille_joueur_async."""
        _sync = sync_wrapper(self.analyser_grille_joueur_async)
        return _sync(numeros, numero_chance, stats_frequences)

    # ───────────────────────────────────────────────────────────────
    # HELPERS
    # ───────────────────────────────────────────────────────────────

    def _parser_reponse_analyse(self, reponse: str, type_analyse: str) -> AnalyseIA:
        """Parse la réponse IA en AnalyseIA structurée."""
        def _normaliser_texte(value: str) -> str:
            sortie = value
            for _ in range(2):
                if "Ã" in sortie or "ã" in sortie or "�" in sortie:
                    try:
                        normalisee = sortie.encode("latin1", errors="ignore").decode("utf-8", errors="ignore")
                    except Exception:
                        break
                    if not normalisee or normalisee == sortie:
                        break
                    sortie = normalisee
                    continue
                break
            return sortie

        reponse = _normaliser_texte(reponse)
        lignes = reponse.strip().split("\n")

        # Extraire sections
        resume = ""
        points_cles: list[str] = []
        recommandations: list[str] = []

        section_courante = "resume"

        for ligne in lignes:
            ligne = ligne.strip()
            if not ligne:
                continue

            ligne_lower = ligne.lower()

            # Détecter sections
            if "point" in ligne_lower and ("clé" in ligne_lower or "cle" in ligne_lower):
                section_courante = "points"
                continue
            elif "recommand" in ligne_lower:
                section_courante = "reco"
                continue
            elif "avertissement" in ligne_lower or "rappel" in ligne_lower:
                section_courante = "avert"
                continue

            # Ajouter à la section
            if section_courante == "resume":
                resume += ligne + " "
            elif section_courante == "points":
                if ligne.startswith("-") or ligne.startswith("•"):
                    points_cles.append(ligne.lstrip("-•").strip())
                elif points_cles:
                    points_cles[-1] += " " + ligne
            elif section_courante == "reco":
                if ligne.startswith("-") or ligne.startswith("•"):
                    recommandations.append(ligne.lstrip("-•").strip())
                elif recommandations:
                    recommandations[-1] += " " + ligne

        return AnalyseIA(
            type_analyse=type_analyse,
            resume=resume.strip() or reponse[:200],
            points_cles=points_cles or ["Analyse complétée"],
            recommandations=recommandations or ["Consulter les détails"],
            avertissement=self.AVERTISSEMENT_STANDARD,
            confiance=0.7,
            genere_le=datetime.now(),
        )

    def _analyse_fallback(self, type_analyse: str, donnees: list[dict[str, Any]]) -> AnalyseIA:
        """Génère une analyse de fallback sans IA."""
        nb_haute = sum(1 for d in donnees if d.get("value", 0) >= SEUIL_VALUE_HAUTE)
        nb_moyenne = sum(
            1 for d in donnees if SEUIL_VALUE_ALERTE <= d.get("value", 0) < SEUIL_VALUE_HAUTE
        )

        if type_analyse == "paris":
            resume = f"{len(donnees)} marchés en retard détectés ({nb_haute} très en retard, {nb_moyenne} en retard)."
        else:
            resume = f"{len(donnees)} numéros en retard ({nb_haute} très en retard, {nb_moyenne} en retard)."

        return AnalyseIA(
            type_analyse=type_analyse,
            resume=resume,
            points_cles=[
                f"🟢 Très en retard: {nb_haute}",
                f"🟡 En retard: {nb_moyenne}",
            ],
            recommandations=[
                "Analyse IA indisponible",
                "Consulter les données brutes",
            ],
            avertissement=self.AVERTISSEMENT_STANDARD,
            confiance=0.3,
            genere_le=datetime.now(),
        )

    def _formater_stats_pour_prompt(self, stats: dict[int, dict], top_n: int = 10) -> str:
        """Formate les stats pour le prompt IA."""
        if not stats:
            return "Aucune statistique disponible."

        # Trier par fréquence décroissante
        sorted_stats = sorted(
            stats.items(), key=lambda x: x[1].get("freq", 0), reverse=True
        )[:top_n]

        lignes = []
        for num, data in sorted_stats:
            freq = data.get("freq", 0)
            ecart = data.get("ecart", 0)
            lignes.append(f"  - N°{num}: {freq} fois, écart {ecart} tirages")

        return "\n".join(lignes)

    def _valider_grille(self, grille: dict) -> bool:
        """Valide qu'une grille IA a le bon format."""
        if not isinstance(grille, dict):
            return False

        numeros = grille.get("numeros", [])
        numero_chance = grille.get("numero_chance")

        # Vérifications
        if not isinstance(numeros, list) or len(numeros) != 5:
            return False
        if not all(isinstance(n, int) and 1 <= n <= 49 for n in numeros):
            return False
        if len(set(numeros)) != 5:  # Pas de doublons
            return False
        if not isinstance(numero_chance, int) or not 1 <= numero_chance <= 10:
            return False

        return True

    def _grille_fallback(self, mode: str) -> dict[str, Any]:
        """Génère une grille aléatoire en fallback."""
        import random

        numeros = sorted(random.sample(range(1, 50), 5))
        numero_chance = random.randint(1, 10)

        return {
            "numeros": numeros,
            "numero_chance": numero_chance,
            "analyse": f"Grille aléatoire générée (mode {mode}). Service IA indisponible.",
            "confiance": 0.3,
        }

    def _analyse_grille_fallback(self, numeros: list[int], numero_chance: int) -> dict[str, Any]:
        """Analyse basique sans IA."""
        nb_pairs = sum(1 for n in numeros if n % 2 == 0)
        nb_impairs = 5 - nb_pairs
        nb_petits = sum(1 for n in numeros if n <= 25)
        nb_grands = 5 - nb_petits

        points_forts = []
        points_faibles = []

        # Équilibre pairs/impairs
        if 2 <= nb_pairs <= 3:
            points_forts.append(f"Bon équilibre pairs/impairs ({nb_pairs}/{nb_impairs})")
        else:
            points_faibles.append(f"Déséquilibre pairs/impairs ({nb_pairs}/{nb_impairs})")

        # Équilibre petits/grands
        if 2 <= nb_petits <= 3:
            points_forts.append(f"Bonne répartition petits/grands ({nb_petits}/{nb_grands})")
        else:
            points_faibles.append(f"Déséquilibre petits/grands ({nb_petits}/{nb_grands})")

        # Note basique
        note = 5 + len(points_forts) - len(points_faibles)
        note = max(1, min(10, note))

        return {
            "note": note,
            "points_forts": points_forts or ["Grille valide"],
            "points_faibles": points_faibles or ["Analyse IA indisponible"],
            "recommandations": [
                "Privilégier un équilibre pairs/impairs (2-3 ou 3-2)",
                "Répartir entre petits (1-25) et grands (26-49) numéros",
            ],
            "appreciation": f"Grille analysée automatiquement. Note: {note}/10.",
        }


# ═══════════════════════════════════════════════════════════
# FACTORY
# ═══════════════════════════════════════════════════════════


@service_factory("jeux_ai", tags={"jeux", "ia"})
def obtenir_jeux_ai_service() -> JeuxAIService:
    """Factory singleton pour le service IA Jeux."""
    return JeuxAIService()


def obtenir_service_ia_jeux() -> JeuxAIService:
    """Alias français pour obtenir_jeux_ai_service (singleton via registre)."""
    return obtenir_jeux_ai_service()


# ═══════════════════════════════════════════════════════════
# EXPORTS
# ═══════════════════════════════════════════════════════════

__all__ = [
    "JeuxAIService",
    "AnalyseIA",
    "OpportuniteAnalysee",
    "obtenir_service_ia_jeux",
    "obtenir_jeux_ai_service",
]


# ─── Aliases rétrocompatibilité  ───────────────────────────────
obtenir_jeux_ai_service = obtenir_jeux_ai_service  # alias rétrocompatibilité 
