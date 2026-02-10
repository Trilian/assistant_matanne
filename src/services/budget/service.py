"""
Service de suivi du budget familial.

Fonctionnalités:
- CRUD dépenses
- Gestion des budgets mensuels (persistés en DB)
- Calcul des statistiques
- Prévisions
- Alertes dépassement
"""

import logging
from datetime import date as date_type
from decimal import Decimal

from sqlalchemy import extract
from sqlalchemy.orm import Session

from src.core.database import obtenir_contexte_db
from src.core.decorators import avec_session_db, avec_cache
from src.core.models import FamilyBudget, BudgetMensuelDB

from .schemas import (
    CategorieDepense,
    FrequenceRecurrence,
    Depense,
    FactureMaison,
    BudgetMensuel,
    ResumeFinancier,
    PrevisionDepense,
    DEFAULT_USER_ID,
)

logger = logging.getLogger(__name__)


class BudgetService:
    """
    Service de gestion du budget familial.
    
    Fonctionnalités:
    - CRUD dépenses
    - Gestion des budgets mensuels
    - Calcul des statistiques
    - Prévisions
    - Alertes dépassement
    """
    
    # Budgets par défaut suggérés (pour une famille)
    BUDGETS_DEFAUT = {
        CategorieDepense.ALIMENTATION: 600,
        CategorieDepense.COURSES: 200,
        CategorieDepense.MAISON: 300,
        CategorieDepense.SANTE: 100,
        CategorieDepense.TRANSPORT: 200,
        CategorieDepense.LOISIRS: 150,
        CategorieDepense.VETEMENTS: 100,
        CategorieDepense.ENFANT: 200,
        CategorieDepense.SERVICES: 150,
    }
    
    def __init__(self):
        """Initialise le service."""
        self._depenses_cache: dict[str, list[Depense]] = {}
    
    # ═══════════════════════════════════════════════════════════
    # GESTION DES DÉPENSES
    # ═══════════════════════════════════════════════════════════
    
    @avec_session_db
    def ajouter_depense(self, depense: Depense, db: Session = None) -> Depense:
        """
        Ajoute une nouvelle dépense.
        
        Args:
            depense: Dépense à ajouter
            db: Session DB
            
        Returns:
            Dépense créée avec ID
        """
        # Créer l'entrée FamilyBudget
        budget_entry = FamilyBudget(
            date=depense.date,
            montant=depense.montant,
            categorie=depense.categorie.value,
            description=depense.description,
            magasin=depense.magasin,
            est_recurrent=depense.est_recurrente,
            frequence_recurrence=depense.frequence.value if depense.est_recurrente else None,
        )
        
        db.add(budget_entry)
        db.commit()
        db.refresh(budget_entry)
        
        depense.id = budget_entry.id
        
        logger.info(f"Dépense ajoutée: {depense.montant}€ ({depense.categorie.value})")
        
        # Vérifier si budget dépassé
        self._verifier_alertes_budget(depense.date.month, depense.date.year, db)
        
        return depense
    
    @avec_session_db
    def modifier_depense(self, depense_id: int, updates: dict, db: Session = None) -> bool:
        """Modifie une dépense existante."""
        entry = db.query(FamilyBudget).filter(FamilyBudget.id == depense_id).first()
        
        if not entry:
            return False
        
        for key, value in updates.items():
            if hasattr(entry, key):
                setattr(entry, key, value)
        
        db.commit()
        return True
    
    @avec_session_db
    def supprimer_depense(self, depense_id: int, db: Session = None) -> bool:
        """Supprime une dépense."""
        entry = db.query(FamilyBudget).filter(FamilyBudget.id == depense_id).first()
        
        if not entry:
            return False
        
        db.delete(entry)
        db.commit()
        return True
    
    @avec_cache(ttl=300)
    @avec_session_db
    def get_depenses_mois(
        self,
        mois: int,
        annee: int,
        categorie: CategorieDepense | None = None,
        db: Session = None,
    ) -> list[Depense]:
        """
        Récupère les dépenses d'un mois.
        
        Args:
            mois: Mois (1-12)
            annee: Année
            categorie: Filtrer par catégorie (optionnel)
            db: Session DB
            
        Returns:
            Liste des dépenses
        """
        query = db.query(FamilyBudget).filter(
            extract('month', FamilyBudget.date) == mois,
            extract('year', FamilyBudget.date) == annee,
        )
        
        if categorie:
            query = query.filter(FamilyBudget.categorie == categorie.value)
        
        entries = query.order_by(FamilyBudget.date.desc()).all()
        
        return [
            Depense(
                id=e.id,
                date=e.date,
                montant=float(e.montant),
                categorie=CategorieDepense(e.categorie) if e.categorie in [c.value for c in CategorieDepense] else CategorieDepense.AUTRE,
                description=e.description or "",
            )
            for e in entries
        ]
    
    # ═══════════════════════════════════════════════════════════
    # GESTION DES BUDGETS (PERSISTÉ EN DB)
    # ═══════════════════════════════════════════════════════════
    
    @avec_session_db
    def definir_budget(
        self,
        categorie: CategorieDepense,
        montant: float,
        mois: int | None = None,
        annee: int | None = None,
        user_id: str = DEFAULT_USER_ID,
        db: Session = None,
    ):
        """
        Définit le budget pour une catégorie (persisté en DB).
        
        Args:
            categorie: Catégorie de dépense
            montant: Budget mensuel
            mois: Mois spécifique (optionnel, défaut = mois courant)
            annee: Année spécifique (optionnel, défaut = année courante)
            user_id: ID utilisateur
            db: Session DB
        """
        mois = mois or date_type.today().month
        annee = annee or date_type.today().year
        
        # Date du premier jour du mois
        date_mois = date_type(annee, mois, 1)
        
        # Chercher ou créer le budget mensuel
        budget_db = db.query(BudgetMensuelDB).filter(
            BudgetMensuelDB.mois == date_mois,
            BudgetMensuelDB.user_id == user_id,
        ).first()
        
        if not budget_db:
            budget_db = BudgetMensuelDB(
                mois=date_mois,
                user_id=user_id,
                budgets_par_categorie={},
            )
            db.add(budget_db)
        
        # Mettre à jour le budget de la catégorie
        budgets = budget_db.budgets_par_categorie or {}
        budgets[categorie.value] = montant
        budget_db.budgets_par_categorie = budgets
        
        # Recalculer le total
        budget_db.budget_total = Decimal(str(sum(budgets.values())))
        
        db.commit()
        logger.info(f"✅ Budget défini: {categorie.value} = {montant}€ ({mois}/{annee})")
    
    @avec_session_db
    def get_budget(
        self,
        categorie: CategorieDepense,
        mois: int | None = None,
        annee: int | None = None,
        user_id: str = DEFAULT_USER_ID,
        db: Session = None,
    ) -> float:
        """Récupère le budget d'une catégorie depuis la DB."""
        mois = mois or date_type.today().month
        annee = annee or date_type.today().year
        date_mois = date_type(annee, mois, 1)
        
        budget_db = db.query(BudgetMensuelDB).filter(
            BudgetMensuelDB.mois == date_mois,
            BudgetMensuelDB.user_id == user_id,
        ).first()
        
        if budget_db and budget_db.budgets_par_categorie:
            return budget_db.budgets_par_categorie.get(
                categorie.value, 
                self.BUDGETS_DEFAUT.get(categorie, 0)
            )
        
        return self.BUDGETS_DEFAUT.get(categorie, 0)
    
    @avec_session_db
    def get_tous_budgets(
        self,
        mois: int | None = None,
        annee: int | None = None,
        user_id: str = DEFAULT_USER_ID,
        db: Session = None,
    ) -> dict[CategorieDepense, float]:
        """Récupère tous les budgets du mois depuis la DB."""
        mois = mois or date_type.today().month
        annee = annee or date_type.today().year
        date_mois = date_type(annee, mois, 1)
        
        budget_db = db.query(BudgetMensuelDB).filter(
            BudgetMensuelDB.mois == date_mois,
            BudgetMensuelDB.user_id == user_id,
        ).first()
        
        budgets_db = budget_db.budgets_par_categorie if budget_db else {}
        
        result = {}
        for cat in CategorieDepense:
            if budgets_db and cat.value in budgets_db:
                result[cat] = budgets_db[cat.value]
            elif cat in self.BUDGETS_DEFAUT:
                result[cat] = self.BUDGETS_DEFAUT[cat]
        
        return result
    
    @avec_session_db
    def definir_budgets_batch(
        self,
        budgets: dict[CategorieDepense, float],
        mois: int | None = None,
        annee: int | None = None,
        user_id: str = DEFAULT_USER_ID,
        db: Session = None,
    ):
        """
        Définit plusieurs budgets en une fois.
        
        Args:
            budgets: Dict catégorie → montant
            mois: Mois
            annee: Année
            user_id: ID utilisateur
            db: Session DB
        """
        mois = mois or date_type.today().month
        annee = annee or date_type.today().year
        date_mois = date_type(annee, mois, 1)
        
        budget_db = db.query(BudgetMensuelDB).filter(
            BudgetMensuelDB.mois == date_mois,
            BudgetMensuelDB.user_id == user_id,
        ).first()
        
        if not budget_db:
            budget_db = BudgetMensuelDB(
                mois=date_mois,
                user_id=user_id,
                budgets_par_categorie={},
            )
            db.add(budget_db)
        
        # Mettre à jour tous les budgets
        budgets_dict = budget_db.budgets_par_categorie or {}
        for cat, montant in budgets.items():
            budgets_dict[cat.value] = montant
        
        budget_db.budgets_par_categorie = budgets_dict
        budget_db.budget_total = Decimal(str(sum(budgets_dict.values())))
        
        db.commit()
        logger.info(f"✅ {len(budgets)} budgets définis pour {mois}/{annee}")
    
    # ═══════════════════════════════════════════════════════════
    # STATISTIQUES ET ANALYSES
    # ═══════════════════════════════════════════════════════════
    
    @avec_cache(ttl=600)
    @avec_session_db
    def get_resume_mensuel(
        self,
        mois: int | None = None,
        annee: int | None = None,
        db: Session = None,
    ) -> ResumeFinancier:
        """
        Génère un résumé financier du mois.
        
        Args:
            mois: Mois (défaut = mois courant)
            annee: Année (défaut = année courante)
            db: Session DB
            
        Returns:
            Résumé financier complet
        """
        mois = mois or date_type.today().month
        annee = annee or date_type.today().year
        
        resume = ResumeFinancier(mois=mois, annee=annee)
        
        # Récupérer les dépenses du mois
        depenses = self.get_depenses_mois(mois, annee, db=db)
        
        # Total et par catégorie
        for dep in depenses:
            resume.total_depenses += dep.montant
            cat_key = dep.categorie.value
            resume.depenses_par_categorie[cat_key] = \
                resume.depenses_par_categorie.get(cat_key, 0) + dep.montant
        
        # Budgets
        budgets = self.get_tous_budgets(mois, annee, db=db)
        for cat, budget_montant in budgets.items():
            depense_cat = resume.depenses_par_categorie.get(cat.value, 0)
            
            budget = BudgetMensuel(
                mois=mois,
                annee=annee,
                categorie=cat,
                budget_prevu=budget_montant,
                depense_reelle=depense_cat,
            )
            
            resume.budgets_par_categorie[cat.value] = budget
            resume.total_budget += budget_montant
            
            # Alertes
            if budget.est_depasse:
                resume.categories_depassees.append(cat.value)
            elif budget.pourcentage_utilise > 80:
                resume.categories_a_risque.append(cat.value)
        
        # Variation vs mois précédent
        mois_prec = mois - 1 if mois > 1 else 12
        annee_prec = annee if mois > 1 else annee - 1
        depenses_prec = self.get_depenses_mois(mois_prec, annee_prec, db=db)
        total_prec = sum(d.montant for d in depenses_prec)
        
        if total_prec > 0:
            resume.variation_vs_mois_precedent = \
                ((resume.total_depenses - total_prec) / total_prec) * 100
        
        # Moyenne 6 mois
        totaux_6_mois = []
        for i in range(6):
            m = mois - i if mois - i > 0 else 12 + (mois - i)
            a = annee if mois - i > 0 else annee - 1
            deps = self.get_depenses_mois(m, a, db=db)
            totaux_6_mois.append(sum(d.montant for d in deps))
        
        resume.moyenne_6_mois = sum(totaux_6_mois) / len(totaux_6_mois) if totaux_6_mois else 0
        
        return resume
    
    @avec_session_db
    def get_tendances(
        self,
        nb_mois: int = 6,
        db: Session = None,
    ) -> dict[str, list[float]]:
        """
        Récupère les tendances de dépenses sur plusieurs mois.
        
        Args:
            nb_mois: Nombre de mois à analyser
            db: Session DB
            
        Returns:
            Dict avec les tendances par catégorie
        """
        tendances = {cat.value: [] for cat in CategorieDepense}
        tendances["total"] = []
        tendances["mois"] = []
        
        aujourd_hui = date_type.today()
        
        for i in range(nb_mois - 1, -1, -1):
            # Calculer le mois
            mois_delta = aujourd_hui.month - i
            if mois_delta <= 0:
                mois = 12 + mois_delta
                annee = aujourd_hui.year - 1
            else:
                mois = mois_delta
                annee = aujourd_hui.year
            
            tendances["mois"].append(f"{mois:02d}/{annee}")
            
            # Récupérer les dépenses
            depenses = self.get_depenses_mois(mois, annee, db=db)
            
            # Totaux par catégorie
            totaux_cat = {cat.value: 0.0 for cat in CategorieDepense}
            total_mois = 0.0
            
            for dep in depenses:
                totaux_cat[dep.categorie.value] += dep.montant
                total_mois += dep.montant
            
            for cat in CategorieDepense:
                tendances[cat.value].append(totaux_cat[cat.value])
            
            tendances["total"].append(total_mois)
        
        return tendances
    
    def prevoir_depenses(
        self,
        mois_cible: int,
        annee_cible: int,
    ) -> list[PrevisionDepense]:
        """
        Prédit les dépenses pour un mois futur.
        
        Args:
            mois_cible: Mois cible
            annee_cible: Année cible
            
        Returns:
            Liste des prévisions par catégorie
        """
        previsions = []
        
        # Récupérer l'historique
        with obtenir_contexte_db() as db:
            tendances = self.get_tendances(nb_mois=6, db=db)
        
        for cat in CategorieDepense:
            valeurs = tendances.get(cat.value, [])
            
            if not valeurs or all(v == 0 for v in valeurs):
                continue
            
            # Moyenne simple pondérée (plus récent = plus de poids)
            poids = [1, 1.2, 1.4, 1.6, 1.8, 2.0][:len(valeurs)]
            moyenne_ponderee = sum(v * p for v, p in zip(valeurs, poids)) / sum(poids)
            
            # Tendance (croissance ou décroissance)
            if len(valeurs) >= 3:
                tendance = (valeurs[-1] - valeurs[0]) / len(valeurs)
            else:
                tendance = 0
            
            montant_prevu = max(0, moyenne_ponderee + tendance)
            
            # Score de confiance basé sur la variance
            if len(valeurs) >= 3:
                variance = sum((v - moyenne_ponderee) ** 2 for v in valeurs) / len(valeurs)
                confiance = max(0, 1 - (variance / (moyenne_ponderee ** 2 + 1)))
            else:
                confiance = 0.5
            
            previsions.append(PrevisionDepense(
                categorie=cat,
                montant_prevu=round(montant_prevu, 2),
                confiance=round(confiance, 2),
                base_calcul=f"Moyenne pondérée sur {len(valeurs)} mois",
            ))
        
        return sorted(previsions, key=lambda p: p.montant_prevu, reverse=True)
    
    # ═══════════════════════════════════════════════════════════
    # ALERTES
    # ═══════════════════════════════════════════════════════════
    
    def _verifier_alertes_budget(self, mois: int, annee: int, db: Session):
        """Vérifie et génère les alertes de budget."""
        budgets = self.get_tous_budgets(mois, annee, db=db)
        depenses = self.get_depenses_mois(mois, annee, db=db)
        
        # Calculer les totaux par catégorie
        totaux = {}
        for dep in depenses:
            totaux[dep.categorie] = totaux.get(dep.categorie, 0) + dep.montant
        
        alertes = []
        
        for cat, budget in budgets.items():
            depense = totaux.get(cat, 0)
            pourcentage = (depense / budget * 100) if budget > 0 else 0
            
            if pourcentage >= 100:
                alertes.append({
                    "type": "danger",
                    "categorie": cat.value,
                    "message": f"Budget {cat.value} dépassé! ({depense:.0f}€ / {budget:.0f}€)",
                    "pourcentage": pourcentage,
                })
            elif pourcentage >= 80:
                alertes.append({
                    "type": "warning",
                    "categorie": cat.value,
                    "message": f"Budget {cat.value} à {pourcentage:.0f}%",
                    "pourcentage": pourcentage,
                })
        
        # Stocker les alertes (sans dépendance Streamlit)
        self._derniers_alertes = alertes
        return alertes

    # ═══════════════════════════════════════════════════════════
    # GESTION DES FACTURES MAISON (gaz, eau, électricité)
    # ═══════════════════════════════════════════════════════════
    
    @avec_session_db
    def ajouter_facture_maison(self, facture: FactureMaison, db: Session = None) -> FactureMaison:
        """
        Ajoute une facture maison avec suivi consommation.
        Utilise la table house_expenses si disponible, sinon FamilyBudget.
        
        Args:
            facture: Facture à ajouter
            db: Session DB
            
        Returns:
            Facture créée avec ID
        """
        try:
            # Essayer d'utiliser house_expenses (table dédiée factures)
            from src.core.models import HouseExpense
            
            entry = HouseExpense(
                categorie=facture.categorie.value,
                montant=facture.montant,
                consommation=facture.consommation,
                mois=facture.mois,
                annee=facture.annee,
                date_facture=facture.date_facture,
                fournisseur=facture.fournisseur,
                numero_facture=facture.numero_facture,
                note=facture.note,
            )
            db.add(entry)
            db.commit()
            db.refresh(entry)
            
            facture.id = entry.id
            logger.info(f"✅ Facture {facture.categorie.value} ajoutée: {facture.montant}€")
            return facture
            
        except Exception as e:
            logger.warning(f"Table house_expenses indisponible, fallback vers FamilyBudget: {e}")
            
            # Fallback: utiliser FamilyBudget
            date_facture = facture.date_facture or date_type(facture.annee, facture.mois, 1)
            
            entry = FamilyBudget(
                date=date_facture,
                montant=facture.montant,
                categorie=facture.categorie.value,
                description=f"Facture {facture.fournisseur} - {facture.consommation} {facture.unite_consommation}",
                est_recurrent=True,
                frequence_recurrence=FrequenceRecurrence.MENSUEL.value,
            )
            db.add(entry)
            db.commit()
            
            facture.id = entry.id
            return facture
    
    @avec_cache(ttl=300)
    @avec_session_db
    def get_factures_maison(
        self,
        categorie: CategorieDepense | None = None,
        annee: int | None = None,
        db: Session = None,
    ) -> list[FactureMaison]:
        """
        Récupère les factures maison avec consommation.
        
        Args:
            categorie: Filtrer par catégorie (GAZ, ELECTRICITE, EAU...)
            annee: Filtrer par année
            db: Session DB
            
        Returns:
            Liste des factures
        """
        try:
            from src.core.models import HouseExpense
            
            query = db.query(HouseExpense)
            
            if categorie:
                query = query.filter(HouseExpense.categorie == categorie.value)
            if annee:
                query = query.filter(HouseExpense.annee == annee)
            
            entries = query.order_by(
                HouseExpense.annee.desc(),
                HouseExpense.mois.desc()
            ).all()
            
            return [
                FactureMaison(
                    id=e.id,
                    categorie=CategorieDepense(e.categorie),
                    montant=float(e.montant),
                    consommation=float(e.consommation) if e.consommation else None,
                    unite_consommation="kWh" if e.categorie == "electricite" else "m³",
                    mois=e.mois,
                    annee=e.annee,
                    date_facture=e.date_facture,
                    fournisseur=e.fournisseur or "",
                    numero_facture=e.numero_facture or "",
                    note=e.note or "",
                )
                for e in entries
            ]
            
        except Exception as e:
            logger.warning(f"Table house_expenses indisponible: {e}")
            return []
    
    def get_evolution_consommation(
        self,
        categorie: CategorieDepense,
        nb_mois: int = 12,
    ) -> list[dict]:
        """
        Retourne l'évolution de la consommation sur les derniers mois.
        Utile pour les graphiques.
        
        Args:
            categorie: GAZ, ELECTRICITE, ou EAU
            nb_mois: Nombre de mois à afficher
            
        Returns:
            Liste de {mois, annee, consommation, montant, prix_unitaire}
        """
        factures = self.get_factures_maison(categorie=categorie)
        
        # Trier par date et limiter
        factures_triees = sorted(
            factures,
            key=lambda f: (f.annee, f.mois),
            reverse=True
        )[:nb_mois]
        
        return [
            {
                "periode": f.periode,
                "mois": f.mois,
                "annee": f.annee,
                "consommation": f.consommation,
                "montant": f.montant,
                "prix_unitaire": f.prix_unitaire,
            }
            for f in reversed(factures_triees)  # Ordre chronologique
        ]


# ═══════════════════════════════════════════════════════════
# FACTORY
# ═══════════════════════════════════════════════════════════


_budget_service: BudgetService | None = None


def get_budget_service() -> BudgetService:
    """Factory pour le service budget."""
    global _budget_service
    if _budget_service is None:
        _budget_service = BudgetService()
    return _budget_service

