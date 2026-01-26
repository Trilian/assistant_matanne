"""
Service de suivi du budget familial.

Fonctionnalités:
- Suivi des dépenses par catégorie
- Budget mensuel avec alertes
- Analyse des tendances
- Prévisions basées sur l'historique
- Rapports et graphiques
- Intégration avec les courses
"""

import logging
from datetime import datetime, date, timedelta
from decimal import Decimal
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field
from sqlalchemy import func, extract
from sqlalchemy.orm import Session

from src.core.database import obtenir_contexte_db
from src.core.decorators import with_db_session, with_cache
from src.core.models import FamilyBudget

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# TYPES ET SCHÉMAS
# ═══════════════════════════════════════════════════════════


class CategorieDepense(str, Enum):
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
    AUTRE = "autre"


class FrequenceRecurrence(str, Enum):
    """Fréquence des dépenses récurrentes."""
    PONCTUEL = "ponctuel"
    HEBDOMADAIRE = "hebdomadaire"
    MENSUEL = "mensuel"
    TRIMESTRIEL = "trimestriel"
    ANNUEL = "annuel"


class Depense(BaseModel):
    """Une dépense."""
    
    id: int | None = None
    date: date = Field(default_factory=date.today)
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


# ═══════════════════════════════════════════════════════════
# SERVICE BUDGET
# ═══════════════════════════════════════════════════════════


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
    
    @with_db_session
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
            magasin=depense.magasin if hasattr(FamilyBudget, 'magasin') else None,
            est_recurrent=depense.est_recurrente,
        )
        
        db.add(budget_entry)
        db.commit()
        db.refresh(budget_entry)
        
        depense.id = budget_entry.id
        
        logger.info(f"Dépense ajoutée: {depense.montant}€ ({depense.categorie.value})")
        
        # Vérifier si budget dépassé
        self._verifier_alertes_budget(depense.date.month, depense.date.year, db)
        
        return depense
    
    @with_db_session
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
    
    @with_db_session
    def supprimer_depense(self, depense_id: int, db: Session = None) -> bool:
        """Supprime une dépense."""
        entry = db.query(FamilyBudget).filter(FamilyBudget.id == depense_id).first()
        
        if not entry:
            return False
        
        db.delete(entry)
        db.commit()
        return True
    
    @with_cache(ttl=300)
    @with_db_session
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
    # GESTION DES BUDGETS
    # ═══════════════════════════════════════════════════════════
    
    def definir_budget(
        self,
        categorie: CategorieDepense,
        montant: float,
        mois: int | None = None,
        annee: int | None = None,
    ):
        """
        Définit le budget pour une catégorie.
        
        Args:
            categorie: Catégorie de dépense
            montant: Budget mensuel
            mois: Mois spécifique (optionnel, défaut = mois courant)
            annee: Année spécifique (optionnel, défaut = année courante)
        """
        mois = mois or date.today().month
        annee = annee or date.today().year
        
        # Stocker en session (pour persistance simple)
        import streamlit as st
        
        key = f"budget_{annee}_{mois}"
        if key not in st.session_state:
            st.session_state[key] = {}
        
        st.session_state[key][categorie.value] = montant
        
        logger.info(f"Budget défini: {categorie.value} = {montant}€ ({mois}/{annee})")
    
    def get_budget(
        self,
        categorie: CategorieDepense,
        mois: int | None = None,
        annee: int | None = None,
    ) -> float:
        """Récupère le budget d'une catégorie."""
        mois = mois or date.today().month
        annee = annee or date.today().year
        
        import streamlit as st
        
        key = f"budget_{annee}_{mois}"
        budgets = st.session_state.get(key, {})
        
        return budgets.get(categorie.value, self.BUDGETS_DEFAUT.get(categorie, 0))
    
    def get_tous_budgets(
        self,
        mois: int | None = None,
        annee: int | None = None,
    ) -> dict[CategorieDepense, float]:
        """Récupère tous les budgets du mois."""
        mois = mois or date.today().month
        annee = annee or date.today().year
        
        import streamlit as st
        
        key = f"budget_{annee}_{mois}"
        budgets_session = st.session_state.get(key, {})
        
        result = {}
        for cat in CategorieDepense:
            if cat.value in budgets_session:
                result[cat] = budgets_session[cat.value]
            elif cat in self.BUDGETS_DEFAUT:
                result[cat] = self.BUDGETS_DEFAUT[cat]
        
        return result
    
    # ═══════════════════════════════════════════════════════════
    # STATISTIQUES ET ANALYSES
    # ═══════════════════════════════════════════════════════════
    
    @with_cache(ttl=600)
    @with_db_session
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
        mois = mois or date.today().month
        annee = annee or date.today().year
        
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
        budgets = self.get_tous_budgets(mois, annee)
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
    
    @with_db_session
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
        
        aujourd_hui = date.today()
        
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
        import streamlit as st
        
        budgets = self.get_tous_budgets(mois, annee)
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
        
        if alertes:
            st.session_state["budget_alertes"] = alertes


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


# ═══════════════════════════════════════════════════════════
# COMPOSANT UI STREAMLIT
# ═══════════════════════════════════════════════════════════


def render_budget_dashboard():
    """Affiche le tableau de bord budget dans Streamlit."""
    import streamlit as st
    import plotly.express as px
    import plotly.graph_objects as go
    
    st.subheader("💰 Budget Familial")
    
    service = get_budget_service()
    
    # Sélecteur de période
    col1, col2 = st.columns([2, 1])
    with col1:
        aujourd_hui = date.today()
        mois_options = [
            (f"{m:02d}/{aujourd_hui.year}", m, aujourd_hui.year)
            for m in range(1, 13)
        ]
        mois_select = st.selectbox(
            "Période",
            options=mois_options,
            index=aujourd_hui.month - 1,
            format_func=lambda x: x[0],
            key="budget_mois"
        )
        _, mois, annee = mois_select
    
    # Récupérer le résumé
    resume = service.get_resume_mensuel(mois, annee)
    
    # Alertes
    if resume.categories_depassees:
        st.error(f"⚠️ Budgets dépassés: {', '.join(resume.categories_depassees)}")
    if resume.categories_a_risque:
        st.warning(f"⚡ À surveiller (>80%): {', '.join(resume.categories_a_risque)}")
    
    # Métriques principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "💸 Dépenses",
            f"{resume.total_depenses:.0f}€",
            delta=f"{resume.variation_vs_mois_precedent:+.1f}% vs mois préc.",
            delta_color="inverse"
        )
    
    with col2:
        st.metric(
            "📊 Budget Total",
            f"{resume.total_budget:.0f}€"
        )
    
    with col3:
        reste = resume.total_budget - resume.total_depenses
        st.metric(
            "💵 Reste",
            f"{reste:.0f}€",
            delta="OK" if reste >= 0 else "Dépassé!",
            delta_color="normal" if reste >= 0 else "inverse"
        )
    
    with col4:
        st.metric(
            "📈 Moyenne 6 mois",
            f"{resume.moyenne_6_mois:.0f}€"
        )
    
    st.markdown("---")
    
    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Vue d'ensemble", "➕ Ajouter", "📈 Tendances", "⚙️ Budgets"])
    
    with tab1:
        # Graphique dépenses par catégorie
        if resume.depenses_par_categorie:
            col_chart1, col_chart2 = st.columns(2)
            
            with col_chart1:
                # Camembert
                fig_pie = px.pie(
                    values=list(resume.depenses_par_categorie.values()),
                    names=list(resume.depenses_par_categorie.keys()),
                    title="Répartition des dépenses",
                    hole=0.4,
                )
                fig_pie.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig_pie, use_container_width=True)
            
            with col_chart2:
                # Barres budget vs dépenses
                categories = []
                budgets_vals = []
                depenses_vals = []
                
                for cat_key, budget in resume.budgets_par_categorie.items():
                    categories.append(cat_key)
                    budgets_vals.append(budget.budget_prevu)
                    depenses_vals.append(budget.depense_reelle)
                
                fig_bar = go.Figure(data=[
                    go.Bar(name='Budget', x=categories, y=budgets_vals, marker_color='lightblue'),
                    go.Bar(name='Dépensé', x=categories, y=depenses_vals, marker_color='coral'),
                ])
                fig_bar.update_layout(
                    title="Budget vs Dépenses",
                    barmode='group',
                    xaxis_tickangle=-45
                )
                st.plotly_chart(fig_bar, use_container_width=True)
        
        # Liste des dépenses récentes
        st.markdown("### 📝 Dernières dépenses")
        depenses = service.get_depenses_mois(mois, annee)
        
        if depenses:
            for dep in depenses[:10]:
                col_d1, col_d2, col_d3 = st.columns([2, 3, 1])
                with col_d1:
                    st.caption(dep.date.strftime("%d/%m"))
                with col_d2:
                    st.write(f"**{dep.categorie.value}** - {dep.description or 'Sans description'}")
                with col_d3:
                    st.write(f"**{dep.montant:.0f}€**")
        else:
            st.info("Aucune dépense ce mois-ci")
    
    with tab2:
        # Formulaire d'ajout de dépense
        st.markdown("### ➕ Nouvelle dépense")
        
        with st.form("add_expense_form"):
            col_f1, col_f2 = st.columns(2)
            
            with col_f1:
                montant = st.number_input("Montant (€)", min_value=0.0, step=1.0, key="expense_amount")
                categorie = st.selectbox(
                    "Catégorie",
                    options=list(CategorieDepense),
                    format_func=lambda x: x.value.title(),
                    key="expense_cat"
                )
            
            with col_f2:
                date_depense = st.date_input("Date", value=date.today(), key="expense_date")
                description = st.text_input("Description", key="expense_desc")
            
            magasin = st.text_input("Magasin (optionnel)", key="expense_shop")
            
            est_recurrente = st.checkbox("Dépense récurrente", key="expense_recurring")
            
            if st.form_submit_button("💾 Enregistrer", type="primary", use_container_width=True):
                if montant > 0:
                    depense = Depense(
                        date=date_depense,
                        montant=montant,
                        categorie=categorie,
                        description=description,
                        magasin=magasin,
                        est_recurrente=est_recurrente,
                    )
                    
                    service.ajouter_depense(depense)
                    st.success(f"✅ Dépense de {montant}€ ajoutée!")
                    st.rerun()
                else:
                    st.error("Le montant doit être supérieur à 0")
    
    with tab3:
        # Graphique de tendances
        st.markdown("### 📈 Évolution sur 6 mois")
        
        tendances = service.get_tendances(nb_mois=6)
        
        if tendances.get("mois"):
            fig_trend = go.Figure()
            
            fig_trend.add_trace(go.Scatter(
                x=tendances["mois"],
                y=tendances["total"],
                mode='lines+markers',
                name='Total',
                line=dict(width=3, color='blue'),
            ))
            
            # Top 3 catégories
            moyennes_cat = {
                cat: sum(tendances.get(cat.value, [])) / max(1, len(tendances.get(cat.value, [])))
                for cat in CategorieDepense
            }
            top_cats = sorted(moyennes_cat.items(), key=lambda x: x[1], reverse=True)[:3]
            
            colors = ['green', 'orange', 'red']
            for i, (cat, _) in enumerate(top_cats):
                if tendances.get(cat.value):
                    fig_trend.add_trace(go.Scatter(
                        x=tendances["mois"],
                        y=tendances[cat.value],
                        mode='lines',
                        name=cat.value.title(),
                        line=dict(dash='dash', color=colors[i]),
                    ))
            
            fig_trend.update_layout(
                title="Évolution des dépenses",
                xaxis_title="Mois",
                yaxis_title="Montant (€)",
                hovermode='x unified',
            )
            
            st.plotly_chart(fig_trend, use_container_width=True)
        
        # Prévisions
        st.markdown("### 🔮 Prévisions mois prochain")
        mois_prochain = mois + 1 if mois < 12 else 1
        annee_prochain = annee if mois < 12 else annee + 1
        
        previsions = service.prevoir_depenses(mois_prochain, annee_prochain)
        
        if previsions:
            total_prevu = sum(p.montant_prevu for p in previsions)
            st.metric("Total prévu", f"{total_prevu:.0f}€")
            
            for prev in previsions[:5]:
                col_p1, col_p2, col_p3 = st.columns([2, 2, 1])
                with col_p1:
                    st.write(f"**{prev.categorie.value.title()}**")
                with col_p2:
                    st.write(f"{prev.montant_prevu:.0f}€")
                with col_p3:
                    confiance_color = "🟢" if prev.confiance > 0.7 else "🟡" if prev.confiance > 0.4 else "🔴"
                    st.write(f"{confiance_color} {prev.confiance:.0%}")
    
    with tab4:
        # Configuration des budgets
        st.markdown("### ⚙️ Définir les budgets mensuels")
        
        budgets_actuels = service.get_tous_budgets(mois, annee)
        
        with st.form("budget_config_form"):
            cols = st.columns(3)
            
            new_budgets = {}
            for i, cat in enumerate(CategorieDepense):
                if cat == CategorieDepense.AUTRE:
                    continue
                
                with cols[i % 3]:
                    budget_actuel = budgets_actuels.get(cat, service.BUDGETS_DEFAUT.get(cat, 0))
                    new_budgets[cat] = st.number_input(
                        f"{cat.value.title()}",
                        min_value=0.0,
                        value=float(budget_actuel),
                        step=10.0,
                        key=f"budget_{cat.value}"
                    )
            
            if st.form_submit_button("💾 Enregistrer les budgets", use_container_width=True):
                for cat, montant in new_budgets.items():
                    service.definir_budget(cat, montant, mois, annee)
                
                st.success("✅ Budgets mis à jour!")
                st.rerun()
