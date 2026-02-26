"""Fonctions CRUD pour le module Diagnostics — délègue au service."""

import logging

logger = logging.getLogger(__name__)


def _get_diag_service():
    from src.services.maison.diagnostics_crud_service import get_diagnostics_crud_service

    return get_diagnostics_crud_service()


def _get_estim_service():
    from src.services.maison.diagnostics_crud_service import get_estimations_crud_service

    return get_estimations_crud_service()


def get_all_diagnostics(filtre_type=None):
    return _get_diag_service().get_all_diagnostics(filtre_type=filtre_type)


def get_diagnostic_by_id(diag_id: int):
    return _get_diag_service().get_diagnostic_by_id(diag_id)


def create_diagnostic(data: dict):
    return _get_diag_service().create_diagnostic(data)


def update_diagnostic(diag_id: int, data: dict):
    return _get_diag_service().update_diagnostic(diag_id, data)


def delete_diagnostic(diag_id: int):
    return _get_diag_service().delete_diagnostic(diag_id)


def get_alertes_diagnostics(jours: int = 90):
    return _get_diag_service().get_alertes_diagnostics(jours_horizon=jours)


def get_all_estimations():
    return _get_estim_service().get_all_estimations()


def create_estimation(data: dict):
    return _get_estim_service().create_estimation(data)
