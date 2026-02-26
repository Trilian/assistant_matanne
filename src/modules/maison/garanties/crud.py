"""Fonctions CRUD pour le module Garanties — délègue au service."""

import logging

logger = logging.getLogger(__name__)


def _get_service():
    from src.services.maison.garanties_crud_service import get_garanties_crud_service

    return get_garanties_crud_service()


def get_all_garanties(filtre_statut=None):
    return _get_service().get_all_garanties(filtre_statut=filtre_statut)


def get_garantie_by_id(garantie_id: int):
    return _get_service().get_garantie_by_id(garantie_id)


def create_garantie(data: dict):
    return _get_service().create_garantie(data)


def update_garantie(garantie_id: int, data: dict):
    return _get_service().update_garantie(garantie_id, data)


def delete_garantie(garantie_id: int):
    return _get_service().delete_garantie(garantie_id)


def create_incident(data: dict):
    return _get_service().create_incident(data)


def get_alertes_garanties(jours: int = 60):
    return _get_service().get_alertes_garanties(jours_horizon=jours)


def get_stats_garanties():
    return _get_service().get_stats_garanties()
