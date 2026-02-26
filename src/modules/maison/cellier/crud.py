"""Fonctions CRUD pour le module Cellier — délègue au service."""

import logging

logger = logging.getLogger(__name__)


def _get_service():
    from src.services.maison.cellier_crud_service import get_cellier_crud_service

    return get_cellier_crud_service()


def get_all_articles(filtre_categorie=None):
    return _get_service().get_all_articles(filtre_categorie=filtre_categorie)


def get_article_by_id(article_id: int):
    return _get_service().get_article_by_id(article_id)


def create_article(data: dict):
    return _get_service().create_article(data)


def update_article(article_id: int, data: dict):
    return _get_service().update_article(article_id, data)


def delete_article(article_id: int):
    return _get_service().delete_article(article_id)


def ajuster_quantite(article_id: int, delta: int):
    return _get_service().ajuster_quantite(article_id, delta)


def get_alertes_peremption(jours: int = 30):
    return _get_service().get_alertes_peremption(jours=jours)


def get_alertes_stock():
    return _get_service().get_alertes_stock()


def get_stats_cellier():
    return _get_service().get_stats_cellier()
