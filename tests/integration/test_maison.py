# -*- coding: utf-8 -*-
"""
Tests d'integration pour le module Maison.
"""

import pytest
from datetime import date, timedelta

from src.core.models import (
    Project,
    ProjectTask,
    GardenItem,
    GardenLog,
)


@pytest.mark.integration
class TestWorkflowProjets:
    """Tests du workflow de gestion des projets."""

    def test_creer_projet_complet(self, int_db):
        """Creer un nouveau projet avec taches."""
        projet = Project(
            nom="Installer etageres garage",
            description="Monter des etageres dans le garage",
            priorite="moyenne",
            statut="planifie",
            date_debut=date.today() + timedelta(days=7),
            date_fin_prevue=date.today() + timedelta(days=14),
        )
        int_db.add(projet)
        int_db.flush()
        
        taches = [
            ProjectTask(project_id=projet.id, nom="Acheter materiel", statut="a_faire"),
            ProjectTask(project_id=projet.id, nom="Preparer mur", statut="a_faire"),
            ProjectTask(project_id=projet.id, nom="Monter etageres", statut="a_faire"),
        ]
        for tache in taches:
            int_db.add(tache)
        
        int_db.commit()
        
        projet_db = int_db.query(Project).filter_by(nom="Installer etageres garage").first()
        assert projet_db is not None
        
        taches_db = int_db.query(ProjectTask).filter_by(project_id=projet_db.id).all()
        assert len(taches_db) == 3

    def test_avancer_projet(self, int_db, projets_maison):
        """Faire avancer un projet."""
        projet = projets_maison[0]
        
        tache = int_db.query(ProjectTask).filter_by(
            project_id=projet.id,
            statut="en_cours"
        ).first()
        
        if tache:
            tache.statut = "termine"
            int_db.commit()
            
            tache_db = int_db.query(ProjectTask).filter_by(id=tache.id).first()
            assert tache_db.statut == "termine"

    def test_calculer_avancement(self, int_db, projets_maison):
        """Calculer le pourcentage d'avancement."""
        projet = projets_maison[0]
        
        taches = int_db.query(ProjectTask).filter_by(project_id=projet.id).all()
        
        if taches:
            terminees = len([t for t in taches if t.statut == "termine"])
            pourcentage = (terminees / len(taches)) * 100
            
            assert 0 <= pourcentage <= 100

    def test_filtrer_projets_par_statut(self, int_db, projets_maison):
        """Filtrer les projets par statut."""
        projets_en_cours = int_db.query(Project).filter_by(statut="en_cours").all()
        
        assert len(projets_en_cours) >= 1


@pytest.mark.integration
class TestWorkflowPotager:
    """Tests du workflow de gestion du potager."""

    def test_ajouter_plante(self, int_db):
        """Ajouter une nouvelle plante au potager."""
        plante = GardenItem(
            nom="Fraisiers",
            type="fruit",
            location="Potager est",
            date_plantation=date.today(),
        )
        int_db.add(plante)
        int_db.commit()
        
        plante_db = int_db.query(GardenItem).filter_by(nom="Fraisiers").first()
        assert plante_db is not None
        assert plante_db.date_plantation == date.today()

    def test_ajouter_entree_journal_jardin(self, int_db, potager_base):
        """Ajouter une entree au journal de jardin."""
        plante = potager_base[0]
        
        log = GardenLog(
            garden_item_id=plante.id,
            date=date.today(),
            action="arrosage",
            notes="Arrosage abondant apres journee chaude",
        )
        int_db.add(log)
        int_db.commit()
        
        log_db = int_db.query(GardenLog).filter_by(garden_item_id=plante.id).first()
        assert log_db is not None
        assert log_db.action == "arrosage"

    def test_historique_entretien_plante(self, int_db, potager_base):
        """Consulter l'historique d'entretien d'une plante."""
        plante = potager_base[0]
        
        for i in range(3):
            log = GardenLog(
                garden_item_id=plante.id,
                date=date.today() - timedelta(days=i),
                action="arrosage",
                notes=f"Entretien jour {i}",
            )
            int_db.add(log)
        
        int_db.commit()
        
        historique = int_db.query(GardenLog).filter_by(
            garden_item_id=plante.id
        ).order_by(GardenLog.date.desc()).all()
        
        assert len(historique) >= 3

    def test_filtrer_plantes_par_type(self, int_db, potager_base):
        """Filtrer les plantes par type."""
        legumes = int_db.query(GardenItem).filter_by(type="legume").all()
        
        assert len(legumes) >= 1


@pytest.mark.integration
class TestStatistiquesMaison:
    """Tests des statistiques du module maison."""

    def test_compter_projets_par_statut(self, int_db, projets_maison):
        """Compter les projets par statut."""
        statuts = {}
        
        projets = int_db.query(Project).all()
        for projet in projets:
            statuts[projet.statut] = statuts.get(projet.statut, 0) + 1
        
        assert len(statuts) >= 1

    def test_compter_taches_par_statut(self, int_db, projets_maison):
        """Compter les taches par statut."""
        taches = int_db.query(ProjectTask).all()
        
        statuts = {}
        for tache in taches:
            statuts[tache.statut] = statuts.get(tache.statut, 0) + 1
        
        assert len(statuts) >= 1

    def test_compter_plantes_par_emplacement(self, int_db, potager_base):
        """Compter les plantes par emplacement."""
        emplacements = {}
        
        plantes = int_db.query(GardenItem).all()
        for plante in plantes:
            emp = plante.location or "non_defini"
            emplacements[emp] = emplacements.get(emp, 0) + 1
        
        assert len(emplacements) >= 1

