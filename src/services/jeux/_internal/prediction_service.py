"""
Service de prédiction des résultats de matchs.

Algorithme basé sur:
- Forme récente (5 derniers matchs)
- Avantage domicile (+12%)
- Historique face-à-face
- Régression vers la moyenne
- Cotes des bookmakers
"""

import logging
from typing import Any

from pydantic import BaseModel, Field

from src.services.core.registry import service_factory

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════
# CONSTANTES
# ═══════════════════════════════════════════════════════════

AVANTAGE_DOMICILE = 0.12
SEUIL_CONFIANCE_HAUTE = 70
SEUIL_CONFIANCE_MOYENNE = 55
SEUIL_SERIE_SANS_NUL = 5


# ═══════════════════════════════════════════════════════════
# MODÈLES PYDANTIC
# ═══════════════════════════════════════════════════════════


class FormEquipe(BaseModel):
    """Données de forme d'une équipe."""

    score: int = Field(default=50, ge=0, le=100)
    nb_matchs: int = Field(default=0, ge=0)
    forme_str: str = ""
    serie_en_cours: str = ""
    matchs_sans_nul: int = Field(default=0, ge=0)
    buts_marques: int = Field(default=0, ge=0)
    buts_encaisses: int = Field(default=0, ge=0)


class H2HData(BaseModel):
    """Données historique face-à-face."""

    nb_matchs: int = Field(default=0, ge=0)
    avantage: str | None = None


class CotesMatch(BaseModel):
    """Cotes d'un match."""

    domicile: float = Field(default=2.0, gt=1.0)
    nul: float = Field(default=3.5, gt=1.0)
    exterieur: float = Field(default=3.0, gt=1.0)


class PredictionResultat(BaseModel):
    """Résultat d'une prédiction de match."""

    prediction: str
    probabilites: dict[str, float]
    confiance: float
    niveau_confiance: str
    raisons: list[str]
    conseil: str


class PredictionOverUnder(BaseModel):
    """Résultat d'une prédiction Over/Under."""

    prediction: str
    seuil: float
    buts_attendus: float
    probabilite_over: float
    probabilite_under: float
    confiance: float


class ConseilPari(BaseModel):
    """Conseil de pari structuré."""

    type: str
    message: str
    niveau: str
    mise_suggere: str


# ═══════════════════════════════════════════════════════════
# SERVICE DE PRÉDICTION
# ═══════════════════════════════════════════════════════════


class PredictionService:
    """Service de prédiction des résultats de matchs."""

    def __init__(self):
        """Initialise le service."""
        self.avantage_domicile = AVANTAGE_DOMICILE
        self.seuil_confiance_haute = SEUIL_CONFIANCE_HAUTE
        self.seuil_confiance_moyenne = SEUIL_CONFIANCE_MOYENNE
        self.seuil_serie_sans_nul = SEUIL_SERIE_SANS_NUL

    def predire_resultat_match(
        self,
        forme_domicile: dict[str, Any],
        forme_exterieur: dict[str, Any],
        h2h: dict[str, Any],
        cotes: dict[str, float] | None = None,
        facteurs_supplementaires: dict[str, Any] | None = None,
    ) -> PredictionResultat:
        """Prédit le résultat d'un match."""
        score_dom = forme_domicile.get("score", 50)
        score_ext = forme_exterieur.get("score", 50)

        total = score_dom + score_ext + 50
        proba_dom = score_dom / total
        proba_ext = score_ext / total
        proba_nul = 50 / total

        proba_dom += self.avantage_domicile
        proba_ext -= self.avantage_domicile * 0.7
        proba_nul -= self.avantage_domicile * 0.3

        if h2h.get("nb_matchs", 0) >= 3:
            avantage = h2h.get("avantage")
            if avantage == "domicile":
                proba_dom += 0.05
                proba_ext -= 0.03
                proba_nul -= 0.02
            elif avantage == "exterieur":
                proba_ext += 0.05
                proba_dom -= 0.03
                proba_nul -= 0.02

        serie_dom = forme_domicile.get("serie_en_cours")
        serie_ext = forme_exterieur.get("serie_en_cours")

        proba_dom, proba_ext = self._appliquer_regression_defaites(
            proba_dom, proba_ext, serie_dom, serie_ext
        )
        proba_dom, proba_ext = self._appliquer_regression_victoires(
            proba_dom, proba_ext, serie_dom, serie_ext
        )

        matchs_sans_nul_dom = forme_domicile.get("matchs_sans_nul", 0)
        matchs_sans_nul_ext = forme_exterieur.get("matchs_sans_nul", 0)

        bonus_nul = self._calculer_bonus_nul_regression(matchs_sans_nul_dom, matchs_sans_nul_ext)
        if bonus_nul > 0:
            proba_nul += bonus_nul
            proba_dom -= bonus_nul * 0.5
            proba_ext -= bonus_nul * 0.5

        if cotes:
            proba_dom, proba_nul, proba_ext = self._ajuster_selon_cotes(
                proba_dom, proba_nul, proba_ext, cotes
            )

        total = proba_dom + proba_nul + proba_ext
        proba_dom /= total
        proba_nul /= total
        proba_ext /= total

        probas = {"1": proba_dom, "N": proba_nul, "2": proba_ext}
        prediction = max(probas.keys(), key=lambda k: probas[k])

        probas_triees = sorted(probas.values(), reverse=True)
        ecart = probas_triees[0] - probas_triees[1]
        confiance = min(95, 40 + ecart * 150)

        if forme_domicile.get("nb_matchs", 0) < 3 or forme_exterieur.get("nb_matchs", 0) < 3:
            confiance *= 0.8

        raisons = self._generer_raisons(
            forme_domicile,
            forme_exterieur,
            h2h,
            serie_dom,
            serie_ext,
            bonus_nul,
            matchs_sans_nul_dom,
            matchs_sans_nul_ext,
        )

        if confiance >= self.seuil_confiance_haute:
            niveau = "haute"
        elif confiance >= self.seuil_confiance_moyenne:
            niveau = "moyenne"
        else:
            niveau = "faible"

        return PredictionResultat(
            prediction=prediction,
            probabilites={
                "domicile": round(proba_dom * 100, 1),
                "nul": round(proba_nul * 100, 1),
                "exterieur": round(proba_ext * 100, 1),
            },
            confiance=round(confiance, 1),
            niveau_confiance=niveau,
            raisons=raisons,
            conseil=self._generer_conseil_pari(prediction, confiance, cotes),
        )

    def _appliquer_regression_defaites(
        self,
        proba_dom: float,
        proba_ext: float,
        serie_dom: str | None,
        serie_ext: str | None,
    ) -> tuple[float, float]:
        if serie_dom and "D" in serie_dom:
            try:
                nb_defaites = int(serie_dom.replace("D", ""))
                if nb_defaites >= 3:
                    proba_dom += 0.03 * (nb_defaites - 2)
            except ValueError:
                pass

        if serie_ext and "D" in serie_ext:
            try:
                nb_defaites = int(serie_ext.replace("D", ""))
                if nb_defaites >= 3:
                    proba_ext += 0.03 * (nb_defaites - 2)
            except ValueError:
                pass

        return proba_dom, proba_ext

    def _appliquer_regression_victoires(
        self,
        proba_dom: float,
        proba_ext: float,
        serie_dom: str | None,
        serie_ext: str | None,
    ) -> tuple[float, float]:
        if serie_dom and "V" in serie_dom:
            try:
                nb_victoires = int(serie_dom.replace("V", ""))
                if nb_victoires >= 5:
                    proba_dom -= 0.02
            except ValueError:
                pass

        if serie_ext and "V" in serie_ext:
            try:
                nb_victoires = int(serie_ext.replace("V", ""))
                if nb_victoires >= 5:
                    proba_ext -= 0.02
            except ValueError:
                pass

        return proba_dom, proba_ext

    def _calculer_bonus_nul_regression(
        self, matchs_sans_nul_dom: int, matchs_sans_nul_ext: int
    ) -> float:
        bonus = 0.0

        if matchs_sans_nul_dom >= self.seuil_serie_sans_nul:
            bonus += 0.03 * (matchs_sans_nul_dom - self.seuil_serie_sans_nul + 1)

        if matchs_sans_nul_ext >= self.seuil_serie_sans_nul:
            bonus += 0.03 * (matchs_sans_nul_ext - self.seuil_serie_sans_nul + 1)

        return min(bonus, 0.15)

    def _ajuster_selon_cotes(
        self,
        proba_dom: float,
        proba_nul: float,
        proba_ext: float,
        cotes: dict[str, float],
    ) -> tuple[float, float, float]:
        cote_dom = cotes.get("domicile", 2.0)
        cote_nul = cotes.get("nul", 3.5)
        cote_ext = cotes.get("exterieur", 3.0)

        proba_impl_dom = 1 / cote_dom
        proba_impl_nul = 1 / cote_nul
        proba_impl_ext = 1 / cote_ext
        total_impl = proba_impl_dom + proba_impl_nul + proba_impl_ext

        proba_impl_dom /= total_impl
        proba_impl_nul /= total_impl
        proba_impl_ext /= total_impl

        proba_dom = proba_dom * 0.9 + proba_impl_dom * 0.1
        proba_nul = proba_nul * 0.9 + proba_impl_nul * 0.1
        proba_ext = proba_ext * 0.9 + proba_impl_ext * 0.1

        return proba_dom, proba_nul, proba_ext

    def _generer_raisons(
        self,
        forme_dom: dict,
        forme_ext: dict,
        h2h: dict,
        serie_dom: str | None,
        serie_ext: str | None,
        bonus_nul: float,
        sans_nul_dom: int,
        sans_nul_ext: int,
    ) -> list[str]:
        raisons = []
        score_dom = forme_dom.get("score", 50)
        score_ext = forme_ext.get("score", 50)

        if score_dom > score_ext + 15:
            raisons.append(f"Forme domicile supérieure ({forme_dom.get('forme_str', '?')})")
        elif score_ext > score_dom + 15:
            raisons.append(f"Forme extérieur supérieure ({forme_ext.get('forme_str', '?')})")

        if serie_dom and "D" in serie_dom:
            try:
                nb = int(serie_dom.replace("D", ""))
                if nb >= 3:
                    raisons.append(f"Régression attendue après {serie_dom}")
            except ValueError:
                pass

        if h2h.get("avantage") == "domicile":
            raisons.append("Historique favorable à domicile")
        elif h2h.get("avantage") == "exterieur":
            raisons.append("Historique favorable à l'extérieur")

        raisons.append("Avantage terrain (+12% domicile)")

        if bonus_nul > 0.05:
            if sans_nul_dom >= self.seuil_serie_sans_nul:
                raisons.append(f"⚠️ {sans_nul_dom} matchs sans nul (dom) → nul probable")
            if sans_nul_ext >= self.seuil_serie_sans_nul:
                raisons.append(f"⚠️ {sans_nul_ext} matchs sans nul (ext) → nul probable")

        return raisons

    def _generer_conseil_pari(
        self,
        prediction: str,
        confiance: float,
        cotes: dict[str, float] | None = None,
    ) -> str:
        labels = {"1": "Victoire domicile", "N": "Match nul", "2": "Victoire extérieur"}
        conseils = []

        if confiance >= self.seuil_confiance_haute:
            conseils.append(f"✅ **PARIER**: {labels[prediction]} (confiance {confiance:.0f}%)")
            conseils.append("💰 Mise suggérée: 3-5% de ta bankroll")
        elif confiance >= self.seuil_confiance_moyenne:
            conseils.append(f"⚠️ **PRUDENT**: {labels[prediction]} risqué")
            conseils.append("💰 Mise suggérée: 1-2% max")
        else:
            conseils.append("❌ **ÉVITER** ce match - trop incertain")
            conseils.append("💡 Attends un match plus clair")
            return " | ".join(conseils)

        if cotes:
            cle_cote = {"1": "domicile", "N": "nul", "2": "exterieur"}[prediction]
            cote_pred = cotes.get(cle_cote, 2.0)
            proba_modele = confiance / 100
            ev = (proba_modele * cote_pred) - 1

            if ev > 0.15:
                conseils.append(
                    f"🔥 **VALUE BET**: Cote {cote_pred:.2f} trop haute! (EV: +{ev:.0%})"
                )
            elif ev > 0.05:
                conseils.append(f"💎 Value détectée (EV: +{ev:.0%})")
            elif ev < -0.1:
                conseils.append(f"⛔ Cote trop basse, pas rentable (EV: {ev:.0%})")

        return " | ".join(conseils)

    def predire_over_under(
        self,
        forme_domicile: dict[str, Any],
        forme_exterieur: dict[str, Any],
        seuil: float = 2.5,
    ) -> PredictionOverUnder:
        nb_matchs_dom = forme_domicile.get("nb_matchs", 1) or 1
        nb_matchs_ext = forme_exterieur.get("nb_matchs", 1) or 1

        buts_marques_dom = forme_domicile.get("buts_marques", 0) / nb_matchs_dom
        buts_encaisses_dom = forme_domicile.get("buts_encaisses", 0) / nb_matchs_dom
        buts_marques_ext = forme_exterieur.get("buts_marques", 0) / nb_matchs_ext
        buts_encaisses_ext = forme_exterieur.get("buts_encaisses", 0) / nb_matchs_ext

        buts_attendus = (buts_marques_dom + buts_encaisses_ext) / 2 + (
            buts_marques_ext + buts_encaisses_dom
        ) / 2

        ecart_seuil = buts_attendus - seuil

        if ecart_seuil > 0.8:
            proba_over = 0.75
        elif ecart_seuil > 0.3:
            proba_over = 0.60
        elif ecart_seuil > -0.3:
            proba_over = 0.50
        elif ecart_seuil > -0.8:
            proba_over = 0.40
        else:
            proba_over = 0.25

        prediction = "over" if proba_over > 0.5 else "under"

        return PredictionOverUnder(
            prediction=prediction,
            seuil=seuil,
            buts_attendus=round(buts_attendus, 2),
            probabilite_over=round(proba_over * 100, 1),
            probabilite_under=round((1 - proba_over) * 100, 1),
            confiance=round(abs(proba_over - 0.5) * 200, 1),
        )

    def generer_conseils_avances(
        self,
        forme_dom: dict[str, Any],
        forme_ext: dict[str, Any],
        cotes: dict[str, float] | None = None,
    ) -> list[ConseilPari]:
        conseils = []

        matchs_sans_nul_dom = forme_dom.get("matchs_sans_nul", 0)
        matchs_sans_nul_ext = forme_ext.get("matchs_sans_nul", 0)

        if matchs_sans_nul_dom >= 6 or matchs_sans_nul_ext >= 6:
            total_sans_nul = matchs_sans_nul_dom + matchs_sans_nul_ext
            conseils.append(
                ConseilPari(
                    type="🎯 MATCH NUL",
                    message=f"Les équipes n'ont pas fait de nul depuis {matchs_sans_nul_dom}+{matchs_sans_nul_ext} matchs.",
                    niveau="haute" if total_sans_nul >= 10 else "moyenne",
                    mise_suggere="2-3%" if total_sans_nul >= 10 else "1-2%",
                )
            )

        serie_dom = forme_dom.get("serie_en_cours", "")
        if serie_dom and "D" in serie_dom:
            try:
                nb = int(serie_dom.replace("D", ""))
                if nb >= 4:
                    conseils.append(
                        ConseilPari(
                            type="📈 REBOND ATTENDU",
                            message=f"L'équipe domicile a perdu {nb} matchs d'affilée.",
                            niveau="moyenne",
                            mise_suggere="1-2%",
                        )
                    )
            except ValueError:
                pass

        nb_matchs_dom = max(1, forme_dom.get("nb_matchs", 1))
        nb_matchs_ext = max(1, forme_ext.get("nb_matchs", 1))

        buts_moy_dom = (
            forme_dom.get("buts_marques", 0) + forme_dom.get("buts_encaisses", 0)
        ) / nb_matchs_dom
        buts_moy_ext = (
            forme_ext.get("buts_marques", 0) + forme_ext.get("buts_encaisses", 0)
        ) / nb_matchs_ext
        buts_attendus = (buts_moy_dom + buts_moy_ext) / 2

        if buts_attendus > 3.0:
            conseils.append(
                ConseilPari(
                    type="⚽ OVER 2.5",
                    message=f"Moyenne de {buts_attendus:.1f} buts/match entre ces équipes.",
                    niveau="moyenne",
                    mise_suggere="1-2%",
                )
            )
        elif buts_attendus < 2.0:
            conseils.append(
                ConseilPari(
                    type="🛡️ UNDER 2.5",
                    message=f"Équipes défensives ({buts_attendus:.1f} buts/match).",
                    niveau="moyenne",
                    mise_suggere="1-2%",
                )
            )

        if cotes:
            cote_nul = cotes.get("nul", 3.5)
            if cote_nul >= 3.8 and (matchs_sans_nul_dom >= 4 or matchs_sans_nul_ext >= 4):
                conseils.append(
                    ConseilPari(
                        type="💎 VALUE BET NUL",
                        message=f"Cote nul à {cote_nul:.2f} + série sans nul = opportunité!",
                        niveau="haute",
                        mise_suggere="2-3%",
                    )
                )

        return conseils


# ═══════════════════════════════════════════════════════════
# FACTORY
# ═══════════════════════════════════════════════════════════


def obtenir_service_predictions_jeux() -> PredictionService:
    """Factory pour créer une instance du service de prédiction (convention française)."""
    return PredictionService()


@service_factory("prediction", tags={"jeux", "ia", "prediction"})
def get_prediction_service() -> PredictionService:
    """Factory pour créer une instance du service de prédiction (alias anglais)."""
    return obtenir_service_predictions_jeux()


# ═══════════════════════════════════════════════════════════
# FONCTIONS DE COMPATIBILITÉ
# ═══════════════════════════════════════════════════════════

_service: PredictionService | None = None


def _get_service() -> PredictionService:
    global _service
    if _service is None:
        _service = PredictionService()
    return _service


def predire_resultat_match(
    forme_domicile: dict[str, Any],
    forme_exterieur: dict[str, Any],
    h2h: dict[str, Any],
    cotes: dict[str, float] | None = None,
    facteurs_supplementaires: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Fonction de compatibilité avec l'ancienne API."""
    service = _get_service()
    result = service.predire_resultat_match(
        forme_domicile, forme_exterieur, h2h, cotes, facteurs_supplementaires
    )
    return result.model_dump()


def predire_over_under(
    forme_domicile: dict[str, Any],
    forme_exterieur: dict[str, Any],
    seuil: float = 2.5,
) -> dict[str, Any]:
    """Fonction de compatibilité avec l'ancienne API."""
    service = _get_service()
    result = service.predire_over_under(forme_domicile, forme_exterieur, seuil)
    return result.model_dump()


def generer_conseils_avances(
    forme_dom: dict[str, Any],
    forme_ext: dict[str, Any],
    cotes: dict[str, float] | None = None,
) -> list[dict[str, str]]:
    """Fonction de compatibilité avec l'ancienne API."""
    service = _get_service()
    results = service.generer_conseils_avances(forme_dom, forme_ext, cotes)
    return [r.model_dump() for r in results]


def generer_conseil_pari(
    prediction: str,
    confiance: float,
    cotes: dict[str, float] | None = None,
    proba_nul: float = 0.25,
) -> str:
    """Fonction de compatibilité avec l'ancienne API."""
    service = _get_service()
    return service._generer_conseil_pari(prediction, confiance, cotes)
