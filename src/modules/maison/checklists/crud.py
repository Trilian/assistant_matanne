"""Fonctions CRUD pour le module Checklists — délègue au service."""

import logging

logger = logging.getLogger(__name__)


def _get_service():
    from src.services.maison.checklists_crud_service import get_checklists_crud_service

    return get_checklists_crud_service()


def get_all_checklists():
    return _get_service().get_all_checklists()


def get_checklist_by_id(checklist_id: int):
    return _get_service().get_checklist_by_id(checklist_id)


def create_checklist(data: dict):
    return _get_service().create_checklist(data)


def create_from_template(template_key: str, nom: str = "", date_depart=None):
    return _get_service().create_from_template(template_key, nom, date_depart)


def delete_checklist(checklist_id: int):
    return _get_service().delete_checklist(checklist_id)


def toggle_item(item_id: int):
    return _get_service().toggle_item(item_id)


def add_item(data: dict):
    return _get_service().add_item(data)
