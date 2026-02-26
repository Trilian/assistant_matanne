"""Fonctions CRUD pour le module Contrats — délègue au service."""

import logging

logger = logging.getLogger(__name__)


def _get_service():
    from src.services.maison.contrats_crud_service import get_contrats_crud_service

    return get_contrats_crud_service()


def get_all_contrats(filtre_type=None, filtre_statut=None):
    return _get_service().get_all_contrats(filtre_type=filtre_type, filtre_statut=filtre_statut)


def get_contrat_by_id(contrat_id: int):
    return _get_service().get_contrat_by_id(contrat_id)


def create_contrat(data: dict):
    return _get_service().create_contrat(data)


def update_contrat(contrat_id: int, data: dict):
    return _get_service().update_contrat(contrat_id, data)


def delete_contrat(contrat_id: int):
    return _get_service().delete_contrat(contrat_id)


def get_alertes_contrats(jours_horizon: int = 60):
    return _get_service().get_alertes_contrats(jours_horizon=jours_horizon)


def get_resume_financier():
    return _get_service().get_resume_financier()
