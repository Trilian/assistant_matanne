"""Fonctions CRUD pour le module Nuisibles."""

import logging

logger = logging.getLogger(__name__)


def _get_service():
    from src.services.maison.extensions_crud_service import get_nuisibles_crud_service

    return get_nuisibles_crud_service()


def get_all_traitements(filtre_type=None):
    return _get_service().get_all_traitements(filtre_type=filtre_type)


def get_traitement_by_id(traitement_id: int):
    return _get_service().get_traitement_by_id(traitement_id)


def create_traitement(data: dict):
    return _get_service().create_traitement(data)


def update_traitement(traitement_id: int, data: dict):
    return _get_service().update_traitement(traitement_id, data)


def delete_traitement(traitement_id: int):
    return _get_service().delete_traitement(traitement_id)
