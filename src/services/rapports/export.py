"""
Service Export PDF.

Export de recettes, planning et courses en PDF.
Renommé depuis pdf_export.py avec nommage français.
"""

import logging
from datetime import datetime, timedelta
from io import BytesIO

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from sqlalchemy.orm import joinedload

from src.core.database import obtenir_contexte_db
from src.core.decorators import avec_gestion_erreurs
from src.core.models import (
    Recette, RecetteIngredient,
    Planning, Repas, ArticleCourses
)
from src.services.rapports.types import (
    DonneesRecettePDF, DonneesPlanningPDF, DonneesCoursesPDF,
    RecettePDFData, PlanningPDFData, CoursesPDFData  # Alias compat
)

logger = logging.getLogger(__name__)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# SERVICE EXPORT PDF
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class ServiceExportPDF:
    """
    Service d'export PDF pour recettes, planning et courses.
    
    Renommé depuis PDFExportService.
    """

    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._configurer_styles()

    def _configurer_styles(self):
        """Configure les styles personnalisés."""
        self.styles.add(ParagraphStyle(
            name='TitreRecette',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=12,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#2E7D32')
        ))
        self.styles.add(ParagraphStyle(
            name='SousTitre',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceBefore=12,
            spaceAfter=6,
            textColor=colors.HexColor('#1565C0')
        ))
        self.styles.add(ParagraphStyle(
            name='Etape',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceBefore=4,
            spaceAfter=4,
            leftIndent=20
        ))

    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # EXPORT RECETTE
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

    @avec_gestion_erreurs()
    def exporter_recette(self, recette_id: int) -> BytesIO:
        """
        Exporte une recette en PDF.
        
        Args:
            recette_id: ID de la recette
            
        Returns:
            BytesIO contenant le PDF
        """
        with obtenir_contexte_db() as db:
            recette = db.query(Recette).options(
                joinedload(Recette.ingredients).joinedload(RecetteIngredient.ingredient),
                joinedload(Recette.etapes)
            ).filter(Recette.id == recette_id).first()
            
            if not recette:
                raise ValueError(f"Recette {recette_id} non trouvée")
            
            data = DonneesRecettePDF(
                id=recette.id,
                nom=recette.nom,
                description=recette.description or "",
                temps_preparation=recette.temps_preparation or 0,
                temps_cuisson=recette.temps_cuisson or 0,
                portions=recette.portions or 4,
                difficulte=recette.difficulte or "facile",
                ingredients=[
                    {
                        "nom": ri.ingredient.nom if ri.ingredient else "Inconnu",
                        "quantite": ri.quantite or 0,
                        "unite": ri.unite or ""
                    }
                    for ri in recette.ingredients
                ],
                etapes=[e.description for e in sorted(recette.etapes, key=lambda x: x.ordre)],
                tags=recette.tags if hasattr(recette, 'tags') and recette.tags else []
            )
            
            return self._generer_pdf_recette(data)

    def _generer_pdf_recette(self, data: DonneesRecettePDF) -> BytesIO:
        """Génère le PDF d'une recette."""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=2*cm, bottomMargin=2*cm)
        story = []
        
        # Titre
        story.append(Paragraph(f"ðŸ½ï¸ {data.nom}", self.styles['TitreRecette']))
        story.append(Spacer(1, 12))
        
        # Description
        if data.description:
            story.append(Paragraph(data.description, self.styles['Normal']))
            story.append(Spacer(1, 12))
        
        # Infos pratiques
        infos_data = [
            ["â±ï¸ Préparation", f"{data.temps_preparation} min"],
            ["ðŸ”¥ Cuisson", f"{data.temps_cuisson} min"],
            ["ðŸ‘¥ Portions", str(data.portions)],
            ["ðŸ“Š Difficulté", data.difficulte.capitalize()]
        ]
        infos_table = Table(infos_data, colWidths=[4*cm, 3*cm])
        infos_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#E8F5E9')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        story.append(infos_table)
        story.append(Spacer(1, 20))
        
        # Ingrédients
        story.append(Paragraph("ðŸ¥• Ingrédients", self.styles['SousTitre']))
        for ing in data.ingredients:
            quantite = f"{ing['quantite']} {ing['unite']}" if ing['quantite'] else ""
            story.append(Paragraph(f"â€¢ {ing['nom']} {quantite}".strip(), self.styles['Normal']))
        story.append(Spacer(1, 12))
        
        # Étapes
        story.append(Paragraph("ðŸ“ Préparation", self.styles['SousTitre']))
        for i, etape in enumerate(data.etapes, 1):
            story.append(Paragraph(f"{i}. {etape}", self.styles['Etape']))
        
        # Tags
        if data.tags:
            story.append(Spacer(1, 20))
            tags_str = " | ".join(f"#{tag}" for tag in data.tags)
            story.append(Paragraph(f"Tags: {tags_str}", self.styles['Normal']))
        
        # Pied de page
        story.append(Spacer(1, 30))
        story.append(Paragraph(
            f"Généré par Assistant Matanne - {datetime.now().strftime('%d/%m/%Y')}",
            ParagraphStyle(name='Footer', parent=self.styles['Normal'], fontSize=8, textColor=colors.grey, alignment=TA_CENTER)
        ))
        
        doc.build(story)
        buffer.seek(0)
        return buffer

    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # EXPORT PLANNING
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

    @avec_gestion_erreurs()
    def exporter_planning_semaine(self, planning_id: int, date_debut: datetime = None) -> BytesIO:
        """
        Exporte un planning de semaine en PDF.
        
        Args:
            planning_id: ID du planning
            date_debut: Date de début de semaine (défaut: semaine courante)
            
        Returns:
            BytesIO contenant le PDF
        """
        if not date_debut:
            date_debut = datetime.now() - timedelta(days=datetime.now().weekday())
        
        date_fin = date_debut + timedelta(days=6)
        
        with obtenir_contexte_db() as db:
            planning = db.query(Planning).options(
                joinedload(Planning.repas).joinedload(Repas.recette)
            ).filter(Planning.id == planning_id).first()
            
            if not planning:
                raise ValueError(f"Planning {planning_id} non trouvé")
            
            # Organiser les repas par jour
            repas_par_jour = {}
            jours_semaine = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
            
            for repas in planning.repas:
                if repas.date and date_debut.date() <= repas.date <= date_fin.date():
                    jour_idx = (repas.date - date_debut.date()).days
                    jour_nom = jours_semaine[jour_idx] if 0 <= jour_idx < 7 else "Autre"
                    
                    if jour_nom not in repas_par_jour:
                        repas_par_jour[jour_nom] = []
                    
                    repas_par_jour[jour_nom].append({
                        "type": repas.type_repas or "repas",
                        "recette": repas.recette.nom if repas.recette else "Non défini",
                        "notes": repas.notes or ""
                    })
            
            data = DonneesPlanningPDF(
                semaine_debut=date_debut,
                semaine_fin=date_fin,
                repas_par_jour=repas_par_jour,
                total_repas=sum(len(r) for r in repas_par_jour.values())
            )
            
            return self._generer_pdf_planning(data, planning.nom or "Planning")

    def _generer_pdf_planning(self, data: DonneesPlanningPDF, nom_planning: str) -> BytesIO:
        """Génère le PDF d'un planning."""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=2*cm, bottomMargin=2*cm)
        story = []
        
        # Titre
        story.append(Paragraph(f"ðŸ“… {nom_planning}", self.styles['TitreRecette']))
        story.append(Paragraph(
            f"Semaine du {data.semaine_debut.strftime('%d/%m')} au {data.semaine_fin.strftime('%d/%m/%Y')}",
            ParagraphStyle(name='DateRange', parent=self.styles['Normal'], alignment=TA_CENTER, fontSize=12)
        ))
        story.append(Spacer(1, 20))
        
        # Tableau planning
        jours_semaine = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
        table_data = [["Jour", "Déjeuner", "Dîner"]]
        
        for jour in jours_semaine:
            repas_jour = data.repas_par_jour.get(jour, [])
            dejeuner = next((r["recette"] for r in repas_jour if "déj" in r["type"].lower()), "-")
            diner = next((r["recette"] for r in repas_jour if "dîn" in r["type"].lower() or "din" in r["type"].lower()), "-")
            table_data.append([jour, dejeuner, diner])
        
        table = Table(table_data, colWidths=[3*cm, 6*cm, 6*cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1565C0')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F5F5F5')]),
        ]))
        story.append(table)
        
        # Stats
        story.append(Spacer(1, 20))
        story.append(Paragraph(f"Total repas planifiés: {data.total_repas}", self.styles['Normal']))
        
        # Pied de page
        story.append(Spacer(1, 30))
        story.append(Paragraph(
            f"Généré par Assistant Matanne - {datetime.now().strftime('%d/%m/%Y %H:%M')}",
            ParagraphStyle(name='Footer', parent=self.styles['Normal'], fontSize=8, textColor=colors.grey, alignment=TA_CENTER)
        ))
        
        doc.build(story)
        buffer.seek(0)
        return buffer

    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # EXPORT LISTE COURSES
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

    @avec_gestion_erreurs()
    def exporter_liste_courses(self) -> BytesIO:
        """
        Exporte la liste de courses actuelle en PDF.
        
        Returns:
            BytesIO contenant le PDF
        """
        with obtenir_contexte_db() as db:
            articles = db.query(ArticleCourses).filter(
                ArticleCourses.achete == False
            ).order_by(ArticleCourses.categorie, ArticleCourses.nom).all()
            
            # Organiser par catégorie
            par_categorie = {}
            for article in articles:
                cat = article.categorie or "Autre"
                if cat not in par_categorie:
                    par_categorie[cat] = []
                par_categorie[cat].append({
                    "nom": article.nom,
                    "quantite": article.quantite or 1,
                    "unite": article.unite or "",
                    "urgent": article.urgent or False
                })
            
            data = DonneesCoursesPDF(
                articles=[{"nom": a.nom, "quantite": a.quantite, "categorie": a.categorie} for a in articles],
                total_articles=len(articles),
                par_categorie=par_categorie
            )
            
            return self._generer_pdf_courses(data)

    def _generer_pdf_courses(self, data: DonneesCoursesPDF) -> BytesIO:
        """Génère le PDF de la liste de courses."""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=2*cm, bottomMargin=2*cm)
        story = []
        
        # Titre
        story.append(Paragraph("ðŸ›’ Liste de Courses", self.styles['TitreRecette']))
        story.append(Paragraph(
            f"Générée le {data.date_export.strftime('%d/%m/%Y Ã  %H:%M')}",
            ParagraphStyle(name='Date', parent=self.styles['Normal'], alignment=TA_CENTER, fontSize=10, textColor=colors.grey)
        ))
        story.append(Spacer(1, 20))
        
        # Emojis par catégorie
        emojis_categories = {
            "fruits_legumes": "ðŸ¥¬",
            "viande": "ðŸ¥©",
            "poisson": "ðŸŸ",
            "produits_laitiers": "ðŸ§€",
            "epicerie": "ðŸ¥«",
            "surgeles": "ðŸ§Š",
            "boissons": "ðŸ¥¤",
            "hygiene": "ðŸ§´",
            "autre": "ðŸ“¦"
        }
        
        for categorie, articles in data.par_categorie.items():
            emoji = emojis_categories.get(categorie.lower(), "ðŸ“¦")
            story.append(Paragraph(f"{emoji} {categorie.replace('_', ' ').title()}", self.styles['SousTitre']))
            
            for article in articles:
                prefix = "ðŸ”´ " if article.get("urgent") else "â˜ "
                quantite = f" ({article['quantite']} {article['unite']})" if article['quantite'] else ""
                story.append(Paragraph(f"{prefix}{article['nom']}{quantite}", self.styles['Normal']))
            
            story.append(Spacer(1, 10))
        
        # Total
        story.append(Spacer(1, 10))
        story.append(Paragraph(f"ðŸ“Š Total: {data.total_articles} articles", self.styles['Normal']))
        
        # Pied de page
        story.append(Spacer(1, 30))
        story.append(Paragraph(
            "Assistant Matanne - Imprimez et cochez au fur et Ã  mesure !",
            ParagraphStyle(name='Footer', parent=self.styles['Normal'], fontSize=8, textColor=colors.grey, alignment=TA_CENTER)
        ))
        
        doc.build(story)
        buffer.seek(0)
        return buffer

    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # ALIAS MÉTHODES RÉTROCOMPATIBILITÉ
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    
    # Alias méthode privée anglais
    _setup_custom_styles = _configurer_styles


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# SINGLETON
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

_service_export_pdf: ServiceExportPDF | None = None


def obtenir_service_export_pdf() -> ServiceExportPDF:
    """Factory pour obtenir le service d'export PDF."""
    global _service_export_pdf
    if _service_export_pdf is None:
        _service_export_pdf = ServiceExportPDF()
    return _service_export_pdf


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# ALIAS RÉTROCOMPATIBILITÉ
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

PDFExportService = ServiceExportPDF
get_pdf_export_service = obtenir_service_export_pdf


__all__ = [
    # Français
    "ServiceExportPDF",
    "obtenir_service_export_pdf",
    # Alias rétrocompatibilité
    "PDFExportService",
    "get_pdf_export_service",
]
