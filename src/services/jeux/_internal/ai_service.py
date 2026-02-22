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
from src.core.errors_base import ErreurLimiteDebit, ErreurServiceIA
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

    @property  # type: ignore[override]
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
    # HELPERS
    # ───────────────────────────────────────────────────────────────

    def _parser_reponse_analyse(self, reponse: str, type_analyse: str) -> AnalyseIA:
        """Parse la réponse IA en AnalyseIA structurée."""
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


# ═══════════════════════════════════════════════════════════
# FACTORY
# ═══════════════════════════════════════════════════════════


_jeux_ai_service_instance: JeuxAIService | None = None


def obtenir_service_ia_jeux() -> JeuxAIService:
    """Factory pour obtenir le service IA Jeux (singleton, convention française)."""
    global _jeux_ai_service_instance
    if _jeux_ai_service_instance is None:
        _jeux_ai_service_instance = JeuxAIService()
    return _jeux_ai_service_instance


@service_factory("jeux_ai", tags={"jeux", "ia"})
def get_jeux_ai_service() -> JeuxAIService:
    """Factory pour obtenir le service IA Jeux (alias anglais)."""
    return obtenir_service_ia_jeux()


# ═══════════════════════════════════════════════════════════
# EXPORTS
# ═══════════════════════════════════════════════════════════

__all__ = [
    "JeuxAIService",
    "AnalyseIA",
    "OpportuniteAnalysee",
    "obtenir_service_ia_jeux",
    "get_jeux_ai_service",
]
