"""
Schémas Pydantic pour le service budget.

Types et modèles de données pour la gestion du budget familial.
"""

from datetime import date as date_type
from datetime import datetime
from enum import Enum, StrEnum

from pydantic import BaseModel, Field

# ID utilisateur par défaut (famille Matanne)
DEFAULT_USER_ID = "matanne"


class CategorieDepense(StrEnum):
    """Catégories de dépenses."""

    ALIMENTATION = "alimentation"
    COURSES = "courses"
    MAISON = "maison"
    SANTE = "santé"
    TRANSPORT = "transport"
    LOISIRS = "loisirs"
    VETEMENTS = "vêtements"
    ENFANT = "enfant"
    EDUCATION = "éducation"
    SERVICES = "services"
    IMPOTS = "impôts"
    EPARGNE = "épargne"
    # Factures maison (avec consommation)
    GAZ = "gaz"
    ELECTRICITE = "electricite"
    EAU = "eau"
    INTERNET = "internet"
    LOYER = "loyer"
    ASSURANCE = "assurance"
    TAXE_FONCIERE = "taxe_fonciere"
    CRECHE = "creche"
    AUTRE = "autre"


class FrequenceRecurrence(StrEnum):
    """Fréquence des dépenses récurrentes."""

    PONCTUEL = "ponctuel"
    HEBDOMADAIRE = "hebdomadaire"
    MENSUEL = "mensuel"
    TRIMESTRIEL = "trimestriel"
    ANNUEL = "annuel"


class Depense(BaseModel):
    """Une dépense."""

    id: int | None = None
    date: date_type = Field(default_factory=date_type.today)
    montant: float
    categorie: CategorieDepense
    description: str = ""
    magasin: str = ""

    # Récurrence
    est_recurrente: bool = False
    frequence: FrequenceRecurrence = FrequenceRecurrence.PONCTUEL

    # Métadonnées
    payeur: str = ""  # Qui a payé
    moyen_paiement: str = ""  # CB, espèces, etc.
    remboursable: bool = False
    rembourse: bool = False

    cree_le: datetime = Field(default_factory=datetime.now)


class FactureMaison(BaseModel):
    """Facture maison avec suivi consommation (gaz, eau, électricité)."""

    id: int | None = None
    categorie: CategorieDepense  # GAZ, ELECTRICITE, EAU, etc.
    montant: float
    consommation: float | None = None  # kWh pour élec, m³ pour gaz/eau
    unite_consommation: str = ""  # "kWh", "m³"
    mois: int  # 1-12
    annee: int
    date_facture: date_type | None = None
    fournisseur: str = ""
    numero_facture: str = ""
    note: str = ""

    @property
    def prix_unitaire(self) -> float | None:
        """Calcule le prix par unité de consommation."""
        if self.consommation and self.consommation > 0:
            return round(self.montant / self.consommation, 4)
        return None

    @property
    def periode(self) -> str:
        """Retourne la période formatée (ex: 'Janvier 2026')."""
        mois_noms = [
            "",
            "Janvier",
            "Février",
            "Mars",
            "Avril",
            "Mai",
            "Juin",
            "Juillet",
            "Août",
            "Septembre",
            "Octobre",
            "Novembre",
            "Décembre",
        ]
        return f"{mois_noms[self.mois]} {self.annee}"


class BudgetMensuel(BaseModel):
    """Budget mensuel par catégorie."""

    id: int | None = None
    mois: int  # 1-12
    annee: int
    categorie: CategorieDepense
    budget_prevu: float
    depense_reelle: float = 0.0

    @property
    def pourcentage_utilise(self) -> float:
        """Pourcentage du budget utilisé."""
        if self.budget_prevu <= 0:
            return 0.0
        return min((self.depense_reelle / self.budget_prevu) * 100, 999)

    @property
    def reste_disponible(self) -> float:
        """Montant restant disponible."""
        return max(0, self.budget_prevu - self.depense_reelle)

    @property
    def est_depasse(self) -> bool:
        """Budget dépassé ?"""
        return self.depense_reelle > self.budget_prevu


class ResumeFinancier(BaseModel):
    """Résumé financier mensuel."""

    mois: int
    annee: int

    total_depenses: float = 0.0
    total_budget: float = 0.0
    total_epargne: float = 0.0

    depenses_par_categorie: dict[str, float] = Field(default_factory=dict)
    budgets_par_categorie: dict[str, BudgetMensuel] = Field(default_factory=dict)

    # Tendances
    variation_vs_mois_precedent: float = 0.0  # %
    moyenne_6_mois: float = 0.0

    # Alertes
    categories_depassees: list[str] = Field(default_factory=list)
    categories_a_risque: list[str] = Field(default_factory=list)  # >80%


class PrevisionDepense(BaseModel):
    """Prévision de dépense."""

    categorie: CategorieDepense
    montant_prevu: float
    confiance: float = 0.0  # Score de confiance 0-1
    base_calcul: str = ""  # Explication du calcul
