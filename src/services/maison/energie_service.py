"""
Service Énergie - Analyse consommation et éco-score gamifié.

Features:
- Analyse détaillée des consommations (gaz, eau, électricité)
- Détection d'anomalies automatique
- Corrélation météo/chauffage
- Éco-score mensuel gamifié avec badges
- Simulation d'économies
"""

import logging
from datetime import date, timedelta
from decimal import Decimal

from sqlalchemy import func
from sqlalchemy.orm import Session

from src.core.ai import ClientIA
from src.core.database import obtenir_contexte_db
from src.core.models import HouseExpense
from src.services.base import BaseAIService

from .schemas import (
    AnalyseEnergie,
    BadgeEco,
    EcoScoreResult,
)

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════
# CONSTANTES
# ═══════════════════════════════════════════════════════════

ENERGIES = {
    "electricite": {
        "emoji": "⚡",
        "couleur": "#FFEB3B",
        "unite": "kWh",
        "label": "Électricité",
        "prix_moyen": Decimal("0.22"),  # €/kWh
        "conso_moyenne_mois": 400,  # kWh pour maison moyenne
    },
    "gaz": {
        "emoji": "🔥",
        "couleur": "#FF5722",
        "unite": "m³",
        "label": "Gaz",
        "prix_moyen": Decimal("0.11"),  # €/m³
        "conso_moyenne_mois": 150,  # m³ pour maison moyenne
    },
    "eau": {
        "emoji": "💧",
        "couleur": "#2196F3",
        "unite": "m³",
        "label": "Eau",
        "prix_moyen": Decimal("4.50"),  # €/m³
        "conso_moyenne_mois": 10,  # m³ pour famille 3 personnes
    },
}

# Seuils pour badges éco
BADGES_DEFINITIONS = {
    "econome_eau": {
        "nom": "💧 Économe en eau",
        "description": "Consommation eau -20% vs moyenne",
        "condition": lambda conso, moyenne: conso < moyenne * 0.8,
        "categorie": "eau",
    },
    "econome_elec": {
        "nom": "⚡ Électricité maîtrisée",
        "description": "Consommation élec -15% vs moyenne",
        "condition": lambda conso, moyenne: conso < moyenne * 0.85,
        "categorie": "energie",
    },
    "econome_gaz": {
        "nom": "🔥 Chauffage optimisé",
        "description": "Consommation gaz -10% vs moyenne",
        "condition": lambda conso, moyenne: conso < moyenne * 0.9,
        "categorie": "energie",
    },
    "streak_7": {
        "nom": "🔥 7 jours d'affilée",
        "description": "7 jours sous la moyenne",
        "condition": lambda streak, _: streak >= 7,
        "categorie": "general",
    },
    "streak_30": {
        "nom": "🏆 Champion du mois",
        "description": "30 jours sous la moyenne",
        "condition": lambda streak, _: streak >= 30,
        "categorie": "general",
    },
}


# ═══════════════════════════════════════════════════════════
# SERVICE ÉNERGIE
# ═══════════════════════════════════════════════════════════


class EnergieService(BaseAIService):
    """Service IA pour l'analyse énergétique et l'éco-score.

    Fonctionnalités:
    - Analyse consommations avec détection anomalies
    - Corrélation météo/chauffage
    - Éco-score gamifié avec badges et streaks
    - Simulation d'économies potentielles

    Example:
        >>> service = get_energie_service()
        >>> eco_score = service.calculer_eco_score(date(2026, 2, 1))
        >>> print(f"Score: {eco_score.score}/100")
    """

    def __init__(self, client: ClientIA | None = None):
        """Initialise le service énergie.

        Args:
            client: Client IA optionnel
        """
        if client is None:
            client = ClientIA()
        super().__init__(
            client=client,
            cache_prefix="energie",
            default_ttl=1800,  # 30 min cache
            service_name="energie",
        )

    # ─────────────────────────────────────────────────────────
    # ANALYSE CONSOMMATION
    # ─────────────────────────────────────────────────────────

    def analyser_consommation(
        self,
        energie: str,
        nb_mois: int = 12,
        db: Session | None = None,
    ) -> AnalyseEnergie:
        """Analyse détaillée de la consommation d'une énergie.

        Args:
            energie: Type d'énergie (electricite, gaz, eau)
            nb_mois: Nombre de mois à analyser
            db: Session DB optionnelle

        Returns:
            AnalyseEnergie avec stats et anomalies
        """
        if db is None:
            with obtenir_contexte_db() as session:
                return self._analyser_conso_impl(session, energie, nb_mois)
        return self._analyser_conso_impl(db, energie, nb_mois)

    def _analyser_conso_impl(self, db: Session, energie: str, nb_mois: int) -> AnalyseEnergie:
        """Implémentation analyse consommation."""
        config = ENERGIES.get(energie, ENERGIES["electricite"])
        date_debut = date.today() - timedelta(days=nb_mois * 30)

        # Récupérer les données
        depenses = (
            db.query(HouseExpense)
            .filter(
                HouseExpense.type_depense == energie,
                HouseExpense.date_facture >= date_debut,
            )
            .order_by(HouseExpense.date_facture)
            .all()
        )

        if not depenses:
            return AnalyseEnergie(
                periode=f"{nb_mois} derniers mois",
                energie=energie,
                consommation_totale=0,
                cout_total=Decimal("0"),
                tendance="stable",
                anomalies_detectees=["Aucune donnée disponible"],
                suggestions_economies=[],
            )

        # Calculer stats
        total_conso = sum(d.consommation or 0 for d in depenses)
        total_cout = sum(d.montant or Decimal("0") for d in depenses)

        # Détecter tendance
        if len(depenses) >= 2:
            premiere_moitie = sum(d.consommation or 0 for d in depenses[: len(depenses) // 2])
            seconde_moitie = sum(d.consommation or 0 for d in depenses[len(depenses) // 2 :])
            if seconde_moitie > premiere_moitie * 1.1:
                tendance = "hausse"
            elif seconde_moitie < premiere_moitie * 0.9:
                tendance = "baisse"
            else:
                tendance = "stable"
        else:
            tendance = "stable"

        # Détecter anomalies
        anomalies = self._detecter_anomalies(depenses, config)

        return AnalyseEnergie(
            periode=f"{nb_mois} derniers mois",
            energie=energie,
            consommation_totale=total_conso,
            cout_total=total_cout,
            tendance=tendance,
            anomalies_detectees=anomalies,
            suggestions_economies=self._suggestions_economies(energie, tendance),
        )

    def _detecter_anomalies(self, depenses: list[HouseExpense], config: dict) -> list[str]:
        """Détecte les anomalies dans les consommations."""
        anomalies = []
        if not depenses:
            return anomalies

        consos = [d.consommation for d in depenses if d.consommation]
        if not consos:
            return anomalies

        moyenne = sum(consos) / len(consos)
        moyenne_ref = config.get("conso_moyenne_mois", moyenne)

        # Pic de consommation
        for d in depenses:
            if d.consommation and d.consommation > moyenne * 1.5:
                anomalies.append(
                    f"Pic en {d.date_facture.strftime('%B %Y')}: "
                    f"{d.consommation:.0f} {config['unite']} (+50%)"
                )

        # Consommation vs moyenne nationale
        if moyenne > moyenne_ref * 1.3:
            anomalies.append(
                f"Consommation {(moyenne/moyenne_ref - 1)*100:.0f}% au-dessus de la moyenne"
            )

        return anomalies[:5]  # Max 5 anomalies

    def _suggestions_economies(self, energie: str, tendance: str) -> list[str]:
        """Génère des suggestions d'économies."""
        suggestions = {
            "electricite": [
                "Passer aux LED (économie ~80%)",
                "Débrancher les appareils en veille",
                "Utiliser des multiprises à interrupteur",
            ],
            "gaz": [
                "Baisser le chauffage de 1°C (économie ~7%)",
                "Purger les radiateurs régulièrement",
                "Programmer le thermostat selon présence",
            ],
            "eau": [
                "Installer des mousseurs sur robinets",
                "Réparer les fuites rapidement",
                "Privilégier les douches aux bains",
            ],
        }

        base = suggestions.get(energie, [])
        if tendance == "hausse":
            base.insert(0, "⚠️ Tendance à la hausse - vigilance recommandée")

        return base

    # ─────────────────────────────────────────────────────────
    # ÉCO-SCORE GAMIFIÉ
    # ─────────────────────────────────────────────────────────

    def calculer_eco_score(self, mois: date, db: Session | None = None) -> EcoScoreResult:
        """Calcule l'éco-score mensuel gamifié.

        Args:
            mois: Premier jour du mois à évaluer
            db: Session DB optionnelle

        Returns:
            EcoScoreResult avec score, badges, conseils
        """
        if db is None:
            with obtenir_contexte_db() as session:
                return self._calculer_score_impl(session, mois)
        return self._calculer_score_impl(db, mois)

    def _calculer_score_impl(self, db: Session, mois: date) -> EcoScoreResult:
        """Implémentation calcul éco-score."""
        # Récupérer consommations du mois
        debut_mois = mois.replace(day=1)
        fin_mois = (debut_mois + timedelta(days=32)).replace(day=1) - timedelta(days=1)

        depenses = (
            db.query(HouseExpense)
            .filter(
                HouseExpense.date_facture >= debut_mois,
                HouseExpense.date_facture <= fin_mois,
            )
            .all()
        )

        # Calculer score de base (0-100)
        score = 50  # Base neutre
        economies = Decimal("0")
        badges_obtenus = []

        for energie, config in ENERGIES.items():
            conso_energie = sum(d.consommation or 0 for d in depenses if d.type_depense == energie)
            moyenne = config["conso_moyenne_mois"]

            if conso_energie > 0:
                ratio = conso_energie / moyenne
                # Ajuster score selon ratio
                if ratio < 0.8:
                    score += 15
                    economies += config["prix_moyen"] * Decimal(str(moyenne - conso_energie))
                elif ratio < 1.0:
                    score += 5
                    economies += config["prix_moyen"] * Decimal(str(moyenne - conso_energie))
                elif ratio > 1.2:
                    score -= 10
                elif ratio > 1.0:
                    score -= 5

                # Vérifier badges énergie
                for badge_id, badge_def in BADGES_DEFINITIONS.items():
                    if badge_def["categorie"] in (energie, "energie"):
                        if badge_def["condition"](conso_energie, moyenne):
                            badges_obtenus.append(
                                BadgeEco(
                                    nom=badge_def["nom"],
                                    description=badge_def["description"],
                                    icone=badge_def["nom"][0],
                                    date_obtention=mois,
                                    categorie=badge_def["categorie"],
                                )
                            )

        # Limiter score entre 0 et 100
        score = max(0, min(100, score))

        # Récupérer score précédent pour comparaison
        mois_prec = (debut_mois - timedelta(days=1)).replace(day=1)
        score_prec = self._get_score_precedent(db, mois_prec)

        # Conseils d'amélioration
        conseils = []
        if score < 50:
            conseils.append("Votre consommation est au-dessus de la moyenne")
            conseils.append("Identifiez les postes les plus consommateurs")
        elif score < 70:
            conseils.append("Vous êtes dans la moyenne - continuez vos efforts!")
        else:
            conseils.append("Excellent! Vous êtes un éco-champion 🏆")

        return EcoScoreResult(
            mois=mois,
            score=score,
            score_precedent=score_prec,
            variation=score - score_prec if score_prec else None,
            streak_jours=0,  # TODO: calculer streak
            economies_euros=economies,
            badges_obtenus=badges_obtenus,
            conseils_amelioration=conseils,
            comparaison_moyenne=self._comparaison_moyenne(score),
        )

    def _get_score_precedent(self, db: Session, mois: date) -> int | None:
        """Récupère le score du mois précédent."""
        # TODO: stocker les scores en DB
        return None

    def _comparaison_moyenne(self, score: int) -> str:
        """Génère le texte de comparaison vs moyenne."""
        if score > 70:
            return f"{score - 50}% au-dessus de la moyenne nationale"
        elif score < 30:
            return f"{50 - score}% en-dessous de la moyenne nationale"
        else:
            return "Dans la moyenne nationale"

    # ─────────────────────────────────────────────────────────
    # SIMULATION ÉCONOMIES
    # ─────────────────────────────────────────────────────────

    async def simuler_economies(self, action: str, energie: str = "electricite") -> dict[str, any]:
        """Simule les économies d'une action éco.

        Args:
            action: Action envisagée (ex: "baisser chauffage 1°C")
            energie: Énergie concernée

        Returns:
            Dict avec économies estimées
        """
        prompt = f"""Pour l'action "{action}" concernant {energie}:
- Estime l'économie en % de consommation
- Calcule l'économie annuelle en euros (prix moyen France)
- Indique le temps de retour si investissement nécessaire

Format JSON: {{"economie_pct": 7, "economie_euros_an": 85, "investissement": 0, "retour_mois": 0}}"""

        try:
            response = await self.call_with_cache(
                prompt=prompt,
                system_prompt="Tu es conseiller en économies d'énergie certifié",
                max_tokens=300,
            )
            import json

            return json.loads(response)
        except Exception as e:
            logger.warning(f"Simulation économies échouée: {e}")
            return {
                "economie_pct": 0,
                "economie_euros_an": 0,
                "investissement": 0,
                "retour_mois": 0,
            }

    async def comparer_periode(
        self,
        energie: str,
        periode1: tuple[date, date],
        periode2: tuple[date, date],
        db: Session | None = None,
    ) -> dict[str, any]:
        """Compare les consommations entre deux périodes.

        Args:
            energie: Type d'énergie
            periode1: (debut, fin) première période
            periode2: (debut, fin) deuxième période
            db: Session DB optionnelle

        Returns:
            Dict avec comparaison détaillée
        """
        if db is None:
            with obtenir_contexte_db() as session:
                return self._comparer_impl(session, energie, periode1, periode2)
        return self._comparer_impl(db, energie, periode1, periode2)

    def _comparer_impl(
        self,
        db: Session,
        energie: str,
        periode1: tuple[date, date],
        periode2: tuple[date, date],
    ) -> dict[str, any]:
        """Implémentation comparaison périodes."""

        def get_conso(debut: date, fin: date) -> float:
            result = (
                db.query(func.sum(HouseExpense.consommation))
                .filter(
                    HouseExpense.type_depense == energie,
                    HouseExpense.date_facture >= debut,
                    HouseExpense.date_facture <= fin,
                )
                .scalar()
            )
            return result or 0

        conso1 = get_conso(*periode1)
        conso2 = get_conso(*periode2)

        variation = ((conso2 - conso1) / conso1 * 100) if conso1 > 0 else 0

        return {
            "periode1": {"debut": periode1[0], "fin": periode1[1], "conso": conso1},
            "periode2": {"debut": periode2[0], "fin": periode2[1], "conso": conso2},
            "variation_pct": round(variation, 1),
            "tendance": "hausse" if variation > 5 else "baisse" if variation < -5 else "stable",
        }


# ═══════════════════════════════════════════════════════════
# FACTORY
# ═══════════════════════════════════════════════════════════


def get_energie_service(client: ClientIA | None = None) -> EnergieService:
    """Factory pour obtenir le service énergie.

    Args:
        client: Client IA optionnel

    Returns:
        Instance de EnergieService
    """
    return EnergieService(client=client)
