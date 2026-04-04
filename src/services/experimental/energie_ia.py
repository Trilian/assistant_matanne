"""Fonctions energie extraites du service innovations."""

from __future__ import annotations

import logging
import os
import re
from datetime import UTC, date, datetime, timedelta
from typing import Any

from src.core.db import obtenir_contexte_db
from src.core.decorators import avec_cache, avec_gestion_erreurs

from .types import (
    AnomalieEnergieDetail,
    AnomaliesEnergieResponse,
    ComparateurEnergieResponse,
    EnergieTempsReelResponse,
    OffreEnergieAlternative,
    ScoreEcoResponsableResponse,
)

logger = logging.getLogger(__name__)


def detecter_anomalies_energie(service) -> AnomaliesEnergieResponse | None:
    """Anomalies énergie : détecte des anomalies eau/gaz/électricité."""
    from src.services.maison.energie_anomalies_ia import obtenir_service_energie_anomalies_ia

    service = obtenir_service_energie_anomalies_ia()
    details: list[AnomalieEnergieDetail] = []
    for type_compteur in ("electricite", "gaz", "eau"):
        resultat = service.analyser_anomalies(type_compteur=type_compteur, nb_mois=12, seuil_pct=20)
        for a in resultat.get("anomalies", []):
            details.append(
                AnomalieEnergieDetail(
                    type_energie=type_compteur,
                    mois=str(a.get("mois", "")),
                    ecart_pct=float(a.get("ecart_pct", 0.0) or 0.0),
                    severite=str(a.get("severite", "moyenne")),
                    explication=str(a.get("explication", "Variation significative détectée.")),
                )
            )

    score_risque = round(min(100.0, len(details) * 18.0), 1)
    recommandations = [
        "Vérifier les appareils énergivores des 30 derniers jours",
        "Contrôler les fuites potentielles (eau/gaz)",
    ]
    return AnomaliesEnergieResponse(
        nb_anomalies=len(details),
        score_risque=score_risque,
        anomalies=details,
        recommandations=recommandations,
    )

def comparer_fournisseurs_energie(
    self,
    prix_kwh_actuel_eur: float = 0.2516,
    abonnement_mensuel_eur: float = 14.0,
) -> ComparateurEnergieResponse | None:
    """Comparateur énergie : compare des offres énergie sur la base de la consommation."""
    conso = self._consommation_annuelle_kwh()
    cout_actuel = round(conso * prix_kwh_actuel_eur + abonnement_mensuel_eur * 12, 2)

    offres = [
        OffreEnergieAlternative(
            fournisseur="Offre EcoFix",
            prix_kwh_eur=round(prix_kwh_actuel_eur * 0.95, 4),
            abonnement_mensuel_eur=max(0.0, abonnement_mensuel_eur - 1.5),
        ),
        OffreEnergieAlternative(
            fournisseur="Offre Tempo+",
            prix_kwh_eur=round(prix_kwh_actuel_eur * 0.92, 4),
            abonnement_mensuel_eur=abonnement_mensuel_eur + 1.0,
        ),
        OffreEnergieAlternative(
            fournisseur="Offre Verte Locale",
            prix_kwh_eur=round(prix_kwh_actuel_eur * 0.97, 4),
            abonnement_mensuel_eur=abonnement_mensuel_eur,
        ),
    ]

    for offre in offres:
        offre.cout_annuel_estime_eur = round(
            conso * offre.prix_kwh_eur + offre.abonnement_mensuel_eur * 12,
            2,
        )

    economie = round(max(0.0, cout_actuel - min((o.cout_annuel_estime_eur for o in offres), default=cout_actuel)), 2)
    return ComparateurEnergieResponse(
        consommation_annuelle_kwh=conso,
        cout_actuel_estime_eur=cout_actuel,
        economie_max_estimee_eur=economie,
        offres=offres,
    )

def calculer_score_eco_responsable(service) -> ScoreEcoResponsableResponse | None:
    """P9-10 : calcule un score écologique mensuel."""
    score_recettes = service._score_recettes_eco()
    score_energie = max(0.0, 100.0 - service._score_risque_energie_simple())
    score_global = round(score_recettes * 0.5 + score_energie * 0.5, 1)
    return ScoreEcoResponsableResponse(
        score_global=score_global,
        details={
            "alimentation_locale_bio": round(score_recettes, 1),
            "efficacite_energetique": round(score_energie, 1),
        },
        recommandations=[
            "Privilégier les recettes de saison et locales",
            "Suivre les pics de consommation hebdomadaires",
        ],
    )

def obtenir_tableau_bord_energie_temps_reel(service) -> EnergieTempsReelResponse | None:
    """Énergie temps-réel : tableau énergie temps-réel (Linky si connecté, sinon estimation)."""
    from sqlalchemy import func

    with obtenir_contexte_db() as session:
        from src.core.models.utilitaires import ReleveEnergie

        aujourd_hui = date.today()
        conso_mois = (
            session.query(func.sum(ReleveEnergie.consommation))
            .filter(
                ReleveEnergie.type_energie == "electricite",
                ReleveEnergie.annee == aujourd_hui.year,
                ReleveEnergie.mois == aujourd_hui.month,
            )
            .scalar()
        )
        conso_mois_prec = (
            session.query(func.sum(ReleveEnergie.consommation))
            .filter(
                ReleveEnergie.type_energie == "electricite",
                ReleveEnergie.annee == (aujourd_hui.year if aujourd_hui.month > 1 else aujourd_hui.year - 1),
                ReleveEnergie.mois == (aujourd_hui.month - 1 if aujourd_hui.month > 1 else 12),
            )
            .scalar()
        )

    consommation_mois = float(conso_mois or 0.0)
    consommation_mois_prec = float(conso_mois_prec or 0.0)
    jours_ecoules = max(1, date.today().day)
    consommation_jour = round(consommation_mois / jours_ecoules, 2) if consommation_mois > 0 else None

    puissance_linky = service._lire_puissance_linky_configuree()
    linky_connecte = puissance_linky is not None
    puissance_estimee = None
    if consommation_jour is not None:
        puissance_estimee = round((consommation_jour / 24.0) * 1000.0, 1)

    puissance_finale = puissance_linky if puissance_linky is not None else puissance_estimee

    if consommation_mois_prec <= 0:
        tendance = "stable"
    elif consommation_mois > consommation_mois_prec * 1.1:
        tendance = "hausse"
    elif consommation_mois < consommation_mois_prec * 0.9:
        tendance = "baisse"
    else:
        tendance = "stable"

    alertes: list[str] = []
    if tendance == "hausse":
        alertes.append("Consommation en hausse par rapport au mois précédent")
    if puissance_finale is not None and puissance_finale > 4500:
        alertes.append("Pic de puissance détecté: vérifier les appareils énergivores")

    return EnergieTempsReelResponse(
        linky_connecte=linky_connecte,
        source="linky" if linky_connecte else "estimation_releves",
        horodatage=datetime.now(UTC).isoformat(),
        puissance_instantanee_w=puissance_finale,
        consommation_jour_estimee_kwh=consommation_jour,
        consommation_mois_kwh=round(consommation_mois, 2),
        tendance=tendance,
        alertes=alertes,
    )

def _score_risque_energie_simple(service) -> float:
    """Score de risque énergie simplifié (0 faible risque, 100 risque élevé)."""
    data = service.detecter_anomalies_energie()
    if not data:
        return 40.0
    return data.score_risque

def _lire_puissance_linky_configuree(service) -> float | None:
    """Lit une puissance Linky instantanée depuis la configuration (intégration best-effort)."""
    if os.getenv("LINKY_ENABLED", "false").lower() not in {"1", "true", "yes", "on"}:
        return None

    brute = os.getenv("LINKY_REALTIME_WATTS", "").strip()
    if not brute:
        return None

    try:
        return float(brute)
    except ValueError:
        return None

def _consommation_annuelle_kwh(service) -> float:
    """Estime la consommation annuelle kWh à partir des relevés."""
    try:
        with obtenir_contexte_db() as session:
            from sqlalchemy import func
            from src.core.models.utilitaires import ReleveEnergie

            annee = date.today().year
            total = (
                session.query(func.sum(ReleveEnergie.consommation))
                .filter(ReleveEnergie.annee == annee, ReleveEnergie.type_energie == "electricite")
                .scalar()
            )
            return round(float(total or 3200.0), 2)
    except Exception:
        return 3200.0
