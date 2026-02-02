"""
Service Génération Rapports PDF

✅ Rapports hebdo stocks
✅ Rapports budget/dépenses
✅ Analyse gaspillage
✅ Export professionnel
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, Any
from io import BytesIO

from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

from src.core.cache import Cache
from src.core.database import obtenir_contexte_db
from src.core.decorators import with_db_session, with_cache, with_error_handling
from src.core.errors_base import ErreurValidation, ErreurNonTrouve
from src.core.models import ArticleInventaire, Recette, HistoriqueRecette, HistoriqueInventaire, Planning, Repas, RecetteIngredient
from src.services.types import BaseService

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════
# SCHÉMAS PYDANTIC
# ═══════════════════════════════════════════════════════════


class RapportStocks(BaseModel):
    """Données pour rapport stocks"""
    date_rapport: datetime = Field(default_factory=datetime.now)
    periode_jours: int = Field(7, ge=1, le=365)
    articles_total: int = 0
    articles_faible_stock: list[dict] = Field(default_factory=list)
    articles_perimes: list[dict] = Field(default_factory=list)
    valeur_stock_total: float = 0.0
    categories_resumee: dict = Field(default_factory=dict)


class RapportBudget(BaseModel):
    """Données pour rapport budget"""
    date_rapport: datetime = Field(default_factory=datetime.now)
    periode_jours: int = Field(30, ge=1, le=365)
    depenses_total: float = 0.0
    depenses_par_categorie: dict = Field(default_factory=dict)
    evolution_semaine: list[dict] = Field(default_factory=list)
    articles_couteux: list[dict] = Field(default_factory=list)


class AnalyseGaspillage(BaseModel):
    """Données pour analyse gaspillage"""
    date_rapport: datetime = Field(default_factory=datetime.now)
    periode_jours: int = Field(30, ge=1, le=365)
    articles_perimes_total: int = 0
    valeur_perdue: float = 0.0
    categories_gaspillage: dict = Field(default_factory=dict)
    recommandations: list[str] = Field(default_factory=list)
    articles_perimes_detail: list[dict] = Field(default_factory=list)


class RapportPlanning(BaseModel):
    """Données pour rapport planning hebdomadaire"""
    date_rapport: datetime = Field(default_factory=datetime.now)
    planning_id: int = 0
    nom_planning: str = ""
    semaine_debut: datetime | None = None
    semaine_fin: datetime | None = None
    repas_par_jour: dict = Field(default_factory=dict)  # {date: [{repas}]}
    total_repas: int = 0
    liste_courses_estimee: list[dict] = Field(default_factory=list)


# ═══════════════════════════════════════════════════════════
# SERVICE RAPPORTS PDF
# ═══════════════════════════════════════════════════════════


class RapportsPDFService(BaseService[ArticleInventaire]):
    """
    Service pour générer des rapports PDF.
    
    Fonctionnalités:
    - Rapport hebdo stocks
    - Rapport budget/dépenses
    - Analyse gaspillage
    - Export professionnel
    """

    def __init__(self):
        super().__init__(ArticleInventaire, cache_ttl=3600)
        # Cache est statique, pas besoin d'instancier
        self.cache_ttl = 3600

    # ═══════════════════════════════════════════════════════════
    # RAPPORT STOCKS
    # ═══════════════════════════════════════════════════════════

    @with_db_session
    def generer_donnees_rapport_stocks(
        self,
        periode_jours: int = 7,
        session: Session = None
    ) -> RapportStocks:
        """
        Collecte les données pour rapport stocks.
        
        Args:
            periode_jours: Nombre de jours à analyser
            session: Session DB
            
        Returns:
            Données structurées du rapport
        """
        rapport = RapportStocks(periode_jours=periode_jours)
        
        # Récupérer tous les articles
        articles = session.query(ArticleInventaire).all()
        rapport.articles_total = len(articles)
        
        # Catégoriser
        categories = {}
        valeur_total = 0.0
        articles_faible = []
        articles_perimes = []
        
        maintenant = datetime.now()
        
        for article in articles:
            # Valeur stock
            if article.prix_unitaire:
                valeur = article.quantite * article.prix_unitaire
                valeur_total += valeur
            
            # Catégories
            if article.categorie not in categories:
                categories[article.categorie] = {
                    "quantite": 0,
                    "valeur": 0.0,
                    "articles": 0
                }
            categories[article.categorie]["quantite"] += article.quantite
            categories[article.categorie]["articles"] += 1
            if article.prix_unitaire:
                categories[article.categorie]["valeur"] += article.quantite * article.prix_unitaire
            
            # Stock faible
            if article.quantite < article.quantite_min and article.quantite > 0:
                articles_faible.append({
                    "nom": article.nom,
                    "quantite": article.quantite,
                    "quantite_min": article.quantite_min,
                    "unite": article.unite,
                    "emplacement": article.emplacement
                })
            
            # Périmés
            if article.date_peremption and article.date_peremption < maintenant:
                jours_ecart = (maintenant - article.date_peremption).days
                articles_perimes.append({
                    "nom": article.nom,
                    "date_peremption": article.date_peremption,
                    "jours_perime": jours_ecart,
                    "quantite": article.quantite,
                    "unite": article.unite
                })
        
        rapport.articles_faible_stock = sorted(
            articles_faible,
            key=lambda x: x["quantite"] / x["quantite_min"] if x["quantite_min"] > 0 else 0
        )
        rapport.articles_perimes = sorted(
            articles_perimes,
            key=lambda x: x["jours_perime"],
            reverse=True
        )
        rapport.valeur_stock_total = valeur_total
        rapport.categories_resumee = categories
        
        return rapport

    @with_db_session
    def generer_pdf_rapport_stocks(
        self,
        periode_jours: int = 7,
        session: Session = None
    ) -> BytesIO:
        """
        Génère un PDF du rapport stocks.
        
        Args:
            periode_jours: Nombre de jours
            session: Session DB
            
        Returns:
            Fichier PDF en BytesIO
        """
        donnees = self.generer_donnees_rapport_stocks(periode_jours, session)
        
        # Créer le PDF
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2E7D32'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#1976D2'),
            spaceAfter=12,
            spaceBefore=12
        )
        
        # Contenu
        elements = []
        
        # Titre
        elements.append(Paragraph(
            "📊 RAPPORT STOCKS HEBDOMADAIRE",
            title_style
        ))
        elements.append(Paragraph(
            f"Généré le {donnees.date_rapport.strftime('%d/%m/%Y à %H:%M')}",
            styles['Normal']
        ))
        elements.append(Spacer(1, 0.3*inch))
        
        # Résumé général
        elements.append(Paragraph(
            "🔍 RÉSUMÉ GÉNÉRAL",
            heading_style
        ))
        summary_data = [
            ["Métrique", "Valeur"],
            [f"Total articles en stock", str(donnees.articles_total)],
            [f"Valeur stock total", f"€{donnees.valeur_stock_total:.2f}"],
            [f"Articles faible stock", str(len(donnees.articles_faible_stock))],
            [f"Articles périmés", str(len(donnees.articles_perimes))]
        ]
        
        summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E7D32')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
        ]))
        elements.append(summary_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Articles faible stock
        if donnees.articles_faible_stock:
            elements.append(Paragraph(
                "⚠️ ARTICLES EN FAIBLE STOCK",
                heading_style
            ))
            stock_data = [["Article", "Quantité", "Minimum", "Unité", "Emplacement"]]
            for article in donnees.articles_faible_stock[:10]:
                stock_data.append([
                    article["nom"][:30],
                    f"{article['quantite']}",
                    f"{article['quantite_min']}",
                    article["unite"],
                    article["emplacement"]
                ])
            
            stock_table = Table(stock_data, colWidths=[1.8*inch, 1*inch, 1*inch, 0.8*inch, 1.2*inch])
            stock_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#FF9800')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#FFF3E0')])
            ]))
            elements.append(stock_table)
            elements.append(Spacer(1, 0.2*inch))
        
        # Articles périmés
        if donnees.articles_perimes:
            elements.append(Paragraph(
                "❌ ARTICLES PÉRIMÉS",
                heading_style
            ))
            perimes_data = [["Article", "Date péremption", "Jours écart", "Quantité"]]
            for article in donnees.articles_perimes[:10]:
                perimes_data.append([
                    article["nom"][:30],
                    article["date_peremption"].strftime('%d/%m/%Y'),
                    f"{article['jours_perime']} j",
                    f"{article['quantite']} {article['unite']}"
                ])
            
            perimes_table = Table(perimes_data, colWidths=[2*inch, 1.5*inch, 1.2*inch, 1.3*inch])
            perimes_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#D32F2F')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#FFEBEE')])
            ]))
            elements.append(perimes_table)
            elements.append(Spacer(1, 0.2*inch))
        
        # Catégories
        if donnees.categories_resumee:
            elements.append(PageBreak())
            elements.append(Paragraph(
                "📦 RÉSUMÉ PAR CATÉGORIE",
                heading_style
            ))
            cat_data = [["Catégorie", "Articles", "Quantité", "Valeur €"]]
            for cat, data in donnees.categories_resumee.items():
                cat_data.append([
                    cat,
                    str(data["articles"]),
                    f"{data['quantite']}",
                    f"{data['valeur']:.2f}"
                ])
            
            cat_table = Table(cat_data, colWidths=[2*inch, 1.2*inch, 1.2*inch, 1.6*inch])
            cat_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1976D2')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightblue])
            ]))
            elements.append(cat_table)
        
        # Générer le PDF
        doc.build(elements)
        buffer.seek(0)
        
        return buffer

    # ═══════════════════════════════════════════════════════════
    # RAPPORT BUDGET
    # ═══════════════════════════════════════════════════════════

    @with_db_session
    def generer_donnees_rapport_budget(
        self,
        periode_jours: int = 30,
        session: Session = None
    ) -> RapportBudget:
        """
        Collecte les données pour rapport budget.
        
        Args:
            periode_jours: Nombre de jours à analyser
            session: Session DB
            
        Returns:
            Données structurées
        """
        rapport = RapportBudget(periode_jours=periode_jours)
        
        # TODO: Implémenter avec historique d'achats si disponible
        # Pour maintenant, calculer à partir du stock actuel
        
        articles = session.query(ArticleInventaire).all()
        depenses_par_cat = {}
        articles_couteux = []
        
        for article in articles:
            if article.prix_unitaire:
                cout = article.quantite * article.prix_unitaire
                rapport.depenses_total += cout
                
                if article.categorie not in depenses_par_cat:
                    depenses_par_cat[article.categorie] = 0.0
                depenses_par_cat[article.categorie] += cout
                
                if cout > 10:  # Articles coûteux
                    articles_couteux.append({
                        "nom": article.nom,
                        "quantite": article.quantite,
                        "unite": article.unite,
                        "prix_unitaire": article.prix_unitaire,
                        "cout_total": cout,
                        "categorie": article.categorie
                    })
        
        rapport.depenses_par_categorie = depenses_par_cat
        rapport.articles_couteux = sorted(
            articles_couteux,
            key=lambda x: x["cout_total"],
            reverse=True
        )[:10]
        
        return rapport

    @with_db_session
    def generer_pdf_rapport_budget(
        self,
        periode_jours: int = 30,
        session: Session = None
    ) -> BytesIO:
        """
        Génère un PDF du rapport budget.
        
        Args:
            periode_jours: Nombre de jours
            session: Session DB
            
        Returns:
            Fichier PDF en BytesIO
        """
        donnees = self.generer_donnees_rapport_budget(periode_jours, session)
        
        # Créer le PDF
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#D32F2F'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#1976D2'),
            spaceAfter=12,
            spaceBefore=12
        )
        
        # Contenu
        elements = []
        
        # Titre
        elements.append(Paragraph(
            "💰 RAPPORT BUDGET/DÉPENSES",
            title_style
        ))
        elements.append(Paragraph(
            f"Généré le {donnees.date_rapport.strftime('%d/%m/%Y à %H:%M')}",
            styles['Normal']
        ))
        elements.append(Spacer(1, 0.3*inch))
        
        # Résumé
        elements.append(Paragraph(
            "💵 RÉSUMÉ FINANCIER",
            heading_style
        ))
        summary_data = [
            ["Métrique", "Valeur"],
            ["Dépenses totales", f"€{donnees.depenses_total:.2f}"],
            ["Période analysée", f"{donnees.periode_jours} jours"],
            ["Articles coûteux", str(len(donnees.articles_couteux))]
        ]
        
        summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#D32F2F')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightyellow),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
        ]))
        elements.append(summary_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Dépenses par catégorie
        if donnees.depenses_par_categorie:
            elements.append(Paragraph(
                "📊 DÉPENSES PAR CATÉGORIE",
                heading_style
            ))
            cat_data = [["Catégorie", "Montant €", "% du total"]]
            for cat, montant in sorted(
                donnees.depenses_par_categorie.items(),
                key=lambda x: x[1],
                reverse=True
            ):
                pct = (montant / donnees.depenses_total * 100) if donnees.depenses_total > 0 else 0
                cat_data.append([cat, f"€{montant:.2f}", f"{pct:.1f}%"])
            
            cat_table = Table(cat_data, colWidths=[2.5*inch, 1.5*inch, 1.5*inch])
            cat_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1976D2')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightblue])
            ]))
            elements.append(cat_table)
            elements.append(Spacer(1, 0.2*inch))
        
        # Articles coûteux
        if donnees.articles_couteux:
            elements.append(Paragraph(
                "⭐ ARTICLES LES PLUS COÛTEUX",
                heading_style
            ))
            costly_data = [["Article", "Catégorie", "Quantité", "Coût total €"]]
            for article in donnees.articles_couteux[:10]:
                costly_data.append([
                    article["nom"][:25],
                    article["categorie"],
                    f"{article['quantite']} {article['unite']}",
                    f"€{article['cout_total']:.2f}"
                ])
            
            costly_table = Table(costly_data, colWidths=[1.8*inch, 1.5*inch, 1.5*inch, 1.2*inch])
            costly_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F57F17')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#FFF3E0')])
            ]))
            elements.append(costly_table)
        
        # Générer le PDF
        doc.build(elements)
        buffer.seek(0)
        
        return buffer

    # ═══════════════════════════════════════════════════════════
    # ANALYSE GASPILLAGE
    # ═══════════════════════════════════════════════════════════

    @with_db_session
    def generer_analyse_gaspillage(
        self,
        periode_jours: int = 30,
        session: Session = None
    ) -> AnalyseGaspillage:
        """
        Analyse le gaspillage (articles périmés, etc).
        
        Args:
            periode_jours: Nombre de jours à analyser
            session: Session DB
            
        Returns:
            Analyse détaillée
        """
        analyse = AnalyseGaspillage(periode_jours=periode_jours)
        
        articles = session.query(ArticleInventaire).all()
        maintenant = datetime.now()
        gaspillage_par_cat = {}
        
        for article in articles:
            # Articles périmés
            if article.date_peremption and article.date_peremption < maintenant:
                analyse.articles_perimes_total += 1
                
                if article.prix_unitaire:
                    valeur_perdue = article.quantite * article.prix_unitaire
                    analyse.valeur_perdue += valeur_perdue
                
                # Par catégorie
                if article.categorie not in gaspillage_par_cat:
                    gaspillage_par_cat[article.categorie] = {"articles": 0, "valeur": 0.0}
                gaspillage_par_cat[article.categorie]["articles"] += 1
                if article.prix_unitaire:
                    gaspillage_par_cat[article.categorie]["valeur"] += valeur_perdue
                
                # Détail
                analyse.articles_perimes_detail.append({
                    "nom": article.nom,
                    "date_peremption": article.date_peremption,
                    "jours_perime": (maintenant - article.date_peremption).days,
                    "quantite": article.quantite,
                    "unite": article.unite,
                    "valeur_perdue": article.prix_unitaire * article.quantite if article.prix_unitaire else 0
                })
        
        analyse.categories_gaspillage = gaspillage_par_cat
        
        # Recommandations
        analyse.recommandations = []
        if analyse.articles_perimes_total > 5:
            analyse.recommandations.append(
                "⚠️ Gaspillage important détecté: améliorer la planification des achats"
            )
        if analyse.valeur_perdue > 50:
            analyse.recommandations.append(
                f"💰 Valeur perdue: €{analyse.valeur_perdue:.2f} - Optimiser l'inventaire"
            )
        if analyse.articles_perimes_detail:
            analyse.recommandations.append(
                "📅 Mettre en place un FIFO (First In First Out) strict"
            )
        
        return analyse

    @with_db_session
    def generer_pdf_analyse_gaspillage(
        self,
        periode_jours: int = 30,
        session: Session = None
    ) -> BytesIO:
        """
        Génère un PDF de l'analyse gaspillage.
        
        Args:
            periode_jours: Nombre de jours
            session: Session DB
            
        Returns:
            Fichier PDF en BytesIO
        """
        analyse = self.generer_analyse_gaspillage(periode_jours, session)
        
        # Créer le PDF
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#E91E63'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#1976D2'),
            spaceAfter=12,
            spaceBefore=12
        )
        
        # Contenu
        elements = []
        
        # Titre
        elements.append(Paragraph(
            "🗑️ ANALYSE GASPILLAGE",
            title_style
        ))
        elements.append(Paragraph(
            f"Généré le {analyse.date_rapport.strftime('%d/%m/%Y à %H:%M')}",
            styles['Normal']
        ))
        elements.append(Spacer(1, 0.3*inch))
        
        # Résumé
        elements.append(Paragraph(
            "📊 RÉSUMÉ GASPILLAGE",
            heading_style
        ))
        summary_data = [
            ["Métrique", "Valeur"],
            ["Articles périmés", str(analyse.articles_perimes_total)],
            ["Valeur perdue", f"€{analyse.valeur_perdue:.2f}"],
            ["Moyenne par article", f"€{analyse.valeur_perdue/max(analyse.articles_perimes_total, 1):.2f}"]
        ]
        
        summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E91E63')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#FCE4EC')),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
        ]))
        elements.append(summary_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Recommandations
        if analyse.recommandations:
            elements.append(Paragraph(
                "💡 RECOMMANDATIONS",
                heading_style
            ))
            for rec in analyse.recommandations:
                elements.append(Paragraph(f"• {rec}", styles['Normal']))
            elements.append(Spacer(1, 0.2*inch))
        
        # Articles périmés détail
        if analyse.articles_perimes_detail:
            elements.append(Paragraph(
                "❌ ARTICLES PÉRIMÉS DÉTAIL",
                heading_style
            ))
            
            detail_data = [["Article", "Périmé depuis", "Quantité", "Valeur perdue"]]
            for article in analyse.articles_perimes_detail[:15]:
                detail_data.append([
                    article["nom"][:25],
                    f"{article['jours_perime']} j",
                    f"{article['quantite']} {article['unite']}",
                    f"€{article['valeur_perdue']:.2f}"
                ])
            
            detail_table = Table(detail_data, colWidths=[1.8*inch, 1.2*inch, 1.2*inch, 1.8*inch])
            detail_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#C62828')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#FFEBEE')])
            ]))
            elements.append(detail_table)
            elements.append(Spacer(1, 0.2*inch))
        
        # Gaspillage par catégorie
        if analyse.categories_gaspillage:
            elements.append(PageBreak())
            elements.append(Paragraph(
                "📦 GASPILLAGE PAR CATÉGORIE",
                heading_style
            ))
            
            cat_data = [["Catégorie", "Articles", "Valeur perdue"]]
            for cat, data in sorted(
                analyse.categories_gaspillage.items(),
                key=lambda x: x[1]["valeur"],
                reverse=True
            ):
                cat_data.append([
                    cat,
                    str(data["articles"]),
                    f"€{data['valeur']:.2f}"
                ])
            
            cat_table = Table(cat_data, colWidths=[2.5*inch, 1.5*inch, 1.5*inch])
            cat_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F57F17')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#FFF3E0')])
            ]))
            elements.append(cat_table)
        
        # Générer le PDF
        doc.build(elements)
        buffer.seek(0)
        
        return buffer

    # ═══════════════════════════════════════════════════════════
    # UTILITAIRES
    # ═══════════════════════════════════════════════════════════

    def telecharger_rapport_pdf(
        self,
        type_rapport: str,
        periode_jours: int = 30
    ) -> tuple[BytesIO, str]:
        """
        Prépare un rapport pour téléchargement.
        
        Args:
            type_rapport: 'stocks', 'budget' ou 'gaspillage'
            periode_jours: Période à analyser
            
        Returns:
            (BytesIO, filename)
        """
        now = datetime.now()
        
        if type_rapport == "stocks":
            pdf = self.generer_pdf_rapport_stocks(7)  # Toujours hebdo
            filename = f"rapport_stocks_{now.strftime('%Y%m%d_%H%M%S')}.pdf"
        
        elif type_rapport == "budget":
            pdf = self.generer_pdf_rapport_budget(periode_jours)
            filename = f"rapport_budget_{now.strftime('%Y%m%d_%H%M%S')}.pdf"
        
        elif type_rapport == "gaspillage":
            pdf = self.generer_pdf_analyse_gaspillage(periode_jours)
            filename = f"analyse_gaspillage_{now.strftime('%Y%m%d_%H%M%S')}.pdf"
        
        else:
            raise ErreurValidation(f"Type de rapport inconnu: {type_rapport}")
        
        return pdf, filename

    # ═══════════════════════════════════════════════════════════
    # RAPPORT PLANNING REPAS
    # ═══════════════════════════════════════════════════════════

    @with_db_session
    def generer_donnees_rapport_planning(
        self,
        planning_id: int,
        session: Session = None
    ) -> RapportPlanning:
        """
        Collecte les données pour rapport planning.
        
        Args:
            planning_id: ID du planning
            session: Session DB
            
        Returns:
            Données structurées du rapport
        """
        from sqlalchemy.orm import selectinload
        
        # Eager loading pour éviter N+1 queries
        planning = (
            session.query(Planning)
            .options(
                selectinload(Planning.repas)
                .selectinload(Repas.recette)
                .selectinload(Recette.ingredients)
                .selectinload(RecetteIngredient.ingredient)
            )
            .filter_by(id=planning_id)
            .first()
        )
        
        if not planning:
            raise ErreurNonTrouve(f"Planning {planning_id} non trouvé")
        
        rapport = RapportPlanning(
            planning_id=planning.id,
            nom_planning=planning.nom,
            semaine_debut=planning.semaine_debut,
            semaine_fin=planning.semaine_fin,
        )
        
        # Organiser les repas par jour
        repas_par_jour = {}
        ingredients_needed = {}
        
        for repas in planning.repas:
            date_str = repas.date_repas.strftime('%Y-%m-%d')
            
            if date_str not in repas_par_jour:
                repas_par_jour[date_str] = []
            
            repas_info = {
                "type": repas.type_repas,
                "recette_nom": repas.recette.nom if repas.recette else "Repas libre",
                "portions": repas.portion_ajustee or (repas.recette.portions if repas.recette else 2),
                "prepare": repas.prepare,
                "notes": repas.notes,
            }
            repas_par_jour[date_str].append(repas_info)
            rapport.total_repas += 1
            
            # Collecter ingrédients pour liste courses
            if repas.recette and hasattr(repas.recette, 'ingredients'):
                for ri in repas.recette.ingredients:
                    if ri.ingredient:
                        nom = ri.ingredient.nom
                        if nom not in ingredients_needed:
                            ingredients_needed[nom] = {
                                "nom": nom,
                                "quantite": 0,
                                "unite": ri.unite or ri.ingredient.unite_defaut or "unité",
                            }
                        ingredients_needed[nom]["quantite"] += ri.quantite or 0
        
        rapport.repas_par_jour = repas_par_jour
        rapport.liste_courses_estimee = list(ingredients_needed.values())
        
        return rapport

    @with_db_session
    def generer_pdf_rapport_planning(
        self,
        planning_id: int,
        session: Session = None
    ) -> BytesIO:
        """
        Génère un PDF du planning de repas.
        
        Args:
            planning_id: ID du planning
            session: Session DB
            
        Returns:
            Fichier PDF en BytesIO
        """
        donnees = self.generer_donnees_rapport_planning(planning_id, session)
        
        # Créer le PDF
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=1.5*cm,
            leftMargin=1.5*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'PlanningTitle',
            parent=styles['Heading1'],
            fontSize=22,
            textColor=colors.HexColor('#4CAF50'),
            spaceAfter=20,
            alignment=TA_CENTER
        )
        subtitle_style = ParagraphStyle(
            'PlanningSubtitle',
            parent=styles['Normal'],
            fontSize=12,
            textColor=colors.HexColor('#666666'),
            spaceAfter=20,
            alignment=TA_CENTER
        )
        day_style = ParagraphStyle(
            'DayHeader',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#1976D2'),
            spaceAfter=8,
            spaceBefore=15
        )
        meal_style = ParagraphStyle(
            'MealStyle',
            parent=styles['Normal'],
            fontSize=10,
            leftIndent=20
        )
        
        elements = []
        
        # En-tête
        elements.append(Paragraph(
            f"🍽️ {donnees.nom_planning}",
            title_style
        ))
        
        date_range = ""
        if donnees.semaine_debut and donnees.semaine_fin:
            date_range = f"Du {donnees.semaine_debut.strftime('%d/%m/%Y')} au {donnees.semaine_fin.strftime('%d/%m/%Y')}"
        elements.append(Paragraph(date_range, subtitle_style))
        elements.append(Spacer(1, 0.2*inch))
        
        # Statistiques rapides
        stats_data = [
            ["📊 Statistiques", ""],
            ["Total repas planifiés", str(donnees.total_repas)],
            ["Ingrédients nécessaires", str(len(donnees.liste_courses_estimee))],
        ]
        stats_table = Table(stats_data, colWidths=[3*inch, 2*inch])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4CAF50')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#E8F5E9')])
        ]))
        elements.append(stats_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Planning jour par jour
        elements.append(Paragraph("📅 PLANNING DE LA SEMAINE", day_style))
        elements.append(Spacer(1, 0.1*inch))
        
        jours_fr = {
            0: "Lundi", 1: "Mardi", 2: "Mercredi", 3: "Jeudi",
            4: "Vendredi", 5: "Samedi", 6: "Dimanche"
        }
        
        type_repas_emoji = {
            "petit_déjeuner": "🌅",
            "déjeuner": "☀️",
            "goûter": "🍪",
            "dîner": "🌙",
        }
        
        for date_str in sorted(donnees.repas_par_jour.keys()):
            repas_jour = donnees.repas_par_jour[date_str]
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            jour_nom = jours_fr.get(date_obj.weekday(), "")
            
            # Tableau pour ce jour
            day_data = [[f"📆 {jour_nom} {date_obj.strftime('%d/%m')}", "Recette", "Portions", "Status"]]
            
            for repas in sorted(repas_jour, key=lambda x: ["petit_déjeuner", "déjeuner", "goûter", "dîner"].index(x["type"]) if x["type"] in ["petit_déjeuner", "déjeuner", "goûter", "dîner"] else 99):
                emoji = type_repas_emoji.get(repas["type"], "🍴")
                status = "✅" if repas["prepare"] else "⏳"
                day_data.append([
                    f"{emoji} {repas['type'].replace('_', ' ').title()}",
                    repas["recette_nom"][:25],
                    str(repas["portions"]),
                    status
                ])
            
            day_table = Table(day_data, colWidths=[2*inch, 2.5*inch, 1*inch, 0.8*inch])
            day_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2196F3')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (2, 0), (3, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#E3F2FD')])
            ]))
            elements.append(day_table)
            elements.append(Spacer(1, 0.15*inch))
        
        # Liste des courses
        if donnees.liste_courses_estimee:
            elements.append(PageBreak())
            elements.append(Paragraph("🛒 LISTE DE COURSES ESTIMÉE", day_style))
            elements.append(Spacer(1, 0.1*inch))
            
            courses_data = [["Ingrédient", "Quantité", "Unité"]]
            for ing in sorted(donnees.liste_courses_estimee, key=lambda x: x["nom"]):
                courses_data.append([
                    ing["nom"][:30],
                    f"{ing['quantite']:.0f}" if ing["quantite"] else "-",
                    ing["unite"]
                ])
            
            courses_table = Table(courses_data, colWidths=[3*inch, 1.5*inch, 1.5*inch])
            courses_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#FF9800')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#FFF3E0')])
            ]))
            elements.append(courses_table)
        
        # Footer
        elements.append(Spacer(1, 0.5*inch))
        elements.append(Paragraph(
            f"Généré le {donnees.date_rapport.strftime('%d/%m/%Y à %H:%M')} • Assistant Matanne 🏠",
            ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, textColor=colors.grey, alignment=TA_CENTER)
        ))
        
        # Générer le PDF
        doc.build(elements)
        buffer.seek(0)
        
        return buffer

    def telecharger_rapport_planning(
        self,
        planning_id: int
    ) -> tuple[BytesIO, str]:
        """
        Prépare un rapport planning pour téléchargement.
        
        Args:
            planning_id: ID du planning
            
        Returns:
            (BytesIO, filename)
        """
        now = datetime.now()
        pdf = self.generer_pdf_rapport_planning(planning_id)
        filename = f"planning_semaine_{now.strftime('%Y%m%d_%H%M%S')}.pdf"
        return pdf, filename
