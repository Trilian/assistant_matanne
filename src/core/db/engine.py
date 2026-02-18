"""
Engine - Création et gestion de l'engine SQLAlchemy.

Fonctions pour:
- Créer l'engine PostgreSQL avec retry automatique
- Obtenir l'engine de façon sécurisée
"""

import logging
import time

import streamlit as st
from sqlalchemy import create_engine, pool, text
from sqlalchemy.exc import DatabaseError, OperationalError

from ..config import obtenir_parametres
from ..constants import DB_CONNECTION_RETRY, DB_CONNECTION_TIMEOUT
from ..errors import ErreurBaseDeDonnees

logger = logging.getLogger(__name__)


@st.cache_resource(ttl=3600)
def obtenir_moteur(nombre_tentatives: int = DB_CONNECTION_RETRY, delai_tentative: int = 2):
    """
    Crée l'engine PostgreSQL avec retry automatique.

    Args:
        nombre_tentatives: Nombre de tentatives de reconnexion
        delai_tentative: Délai entre les tentatives en secondes

    Returns:
        Engine SQLAlchemy configuré

    Raises:
        ErreurBaseDeDonnees: Si connexion impossible après toutes les tentatives
    """
    parametres = obtenir_parametres()
    derniere_erreur = None

    for tentative in range(nombre_tentatives):
        try:
            url_base = parametres.DATABASE_URL

            # Utiliser QueuePool pour de meilleures performances
            moteur = create_engine(
                url_base,
                poolclass=pool.QueuePool,
                pool_size=5,  # Connexions de base
                max_overflow=10,  # Connexions supplémentaires si nécessaire
                pool_timeout=30,  # Timeout attente connexion
                pool_recycle=1800,  # Recycler connexions après 30min
                pool_pre_ping=True,  # Vérifier connexion avant utilisation
                echo=parametres.DEBUG,
                connect_args={
                    "connect_timeout": DB_CONNECTION_TIMEOUT,
                    "options": "-c timezone=utc",
                    "sslmode": "require",
                },
            )

            # Test de connexion
            with moteur.connect() as conn:
                conn.execute(text("SELECT 1"))

            logger.info(f"[OK] Connexion DB établie (tentative {tentative + 1})")
            return moteur

        except (OperationalError, DatabaseError) as e:
            derniere_erreur = e
            logger.warning(f"[ERROR] Tentative {tentative + 1}/{nombre_tentatives} échouée: {e}")

            if tentative < nombre_tentatives - 1:
                time.sleep(delai_tentative)
                continue

    # Toutes les tentatives ont échoué
    message_erreur = (
        f"Impossible de se connecter après {nombre_tentatives} tentatives: {derniere_erreur}"
    )
    logger.error(message_erreur)
    raise ErreurBaseDeDonnees(
        message_erreur, message_utilisateur="Impossible de se connecter à la base de données"
    )


def obtenir_moteur_securise() -> object | None:
    """
    Version sécurisée qui retourne None au lieu de lever une exception.

    Returns:
        Engine ou None si erreur
    """
    try:
        return obtenir_moteur()
    except ErreurBaseDeDonnees as e:
        logger.error(f"DB non disponible: {e}")
        return None
