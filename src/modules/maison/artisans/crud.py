"""Fonctions CRUD pour le module Artisans — délègue au service."""

import logging

logger = logging.getLogger(__name__)


def _get_service():
    from src.services.maison.artisans_crud_service import get_artisans_crud_service

    return get_artisans_crud_service()


def get_all_artisans(filtre_metier=None):
    return _get_service().get_all_artisans(filtre_metier=filtre_metier)


def get_artisan_by_id(artisan_id: int):
    return _get_service().get_artisan_by_id(artisan_id)


def create_artisan(data: dict):
    return _get_service().create_artisan(data)


def update_artisan(artisan_id: int, data: dict):
    return _get_service().update_artisan(artisan_id, data)


def delete_artisan(artisan_id: int):
    return _get_service().delete_artisan(artisan_id)


def get_interventions_artisan(artisan_id: int):
    return _get_service().get_interventions_artisan(artisan_id)


def create_intervention(data: dict):
    return _get_service().create_intervention(data)


def get_stats_artisans():
    return _get_service().get_stats_artisans()
