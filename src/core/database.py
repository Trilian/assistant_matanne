"""
Database - Avec Système de Migration & Optimisations
"""
from contextlib import contextmanager
from typing import Generator, Optional, List
import streamlit as st
from sqlalchemy import create_engine, event, text, pool, inspect
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import OperationalError, DatabaseError
import logging
import time
from pathlib import Path

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# CONFIGURATION ENGINE
# ═══════════════════════════════════════════════════════════

class DatabaseConnectionError(Exception):
    """Erreur connexion DB personnalisée"""
    pass


@st.cache_resource(ttl=3600)
def get_engine(retry_count: int = 3, retry_delay: int = 2):
    """
    Crée l'engine PostgreSQL avec retry automatique
    """
    from src.core.config import get_settings

    settings = get_settings()
    last_error = None

    for attempt in range(retry_count):
        try:
            database_url = settings.DATABASE_URL

            engine = create_engine(
                database_url,
                poolclass=pool.NullPool,
                echo=settings.DEBUG,
                connect_args={
                    "connect_timeout": 10,
                    "options": "-c timezone=utc",
                    "sslmode": "require",
                },
                pool_pre_ping=True,
            )

            # Test connexion
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))

            logger.info(f"✅ Connexion DB établie (tentative {attempt + 1})")
            return engine

        except (OperationalError, DatabaseError) as e:
            last_error = e
            logger.warning(f"❌ Tentative {attempt + 1}/{retry_count} échouée: {e}")

            if attempt < retry_count - 1:
                time.sleep(retry_delay)
                continue

    error_msg = f"Impossible de se connecter après {retry_count} tentatives: {last_error}"
    logger.error(error_msg)
    raise DatabaseConnectionError(error_msg)


def get_engine_safe() -> Optional[object]:
    """Version safe qui retourne None au lieu de crash"""
    try:
        return get_engine()
    except DatabaseConnectionError as e:
        logger.error(f"DB non disponible: {e}")
        return None


# ═══════════════════════════════════════════════════════════
# SESSION FACTORY
# ═══════════════════════════════════════════════════════════

def get_session_factory():
    """Retourne une session factory"""
    engine = get_engine()
    return sessionmaker(autocommit=False, autoflush=False, bind=engine, expire_on_commit=False)


SessionLocal = get_session_factory()


# ═══════════════════════════════════════════════════════════
# CONTEXT MANAGERS
# ═══════════════════════════════════════════════════════════

@contextmanager
def get_db_context() -> Generator[Session, None, None]:
    """Context manager avec gestion d'erreurs robuste"""
    db = SessionLocal()

    try:
        yield db
        db.commit()

    except OperationalError as e:
        db.rollback()
        logger.error(f"❌ Erreur opérationnelle DB: {e}")
        raise DatabaseConnectionError(f"Erreur réseau/connexion: {e}")

    except DatabaseError as e:
        db.rollback()
        logger.error(f"❌ Erreur base de données: {e}")
        raise

    except Exception as e:
        db.rollback()
        logger.error(f"❌ Erreur inattendue: {e}")
        raise

    finally:
        db.close()


@contextmanager
def get_db_safe() -> Generator[Optional[Session], None, None]:
    """Version safe qui n'interrompt pas l'app"""
    try:
        with get_db_context() as db:
            yield db
    except DatabaseConnectionError:
        logger.warning("DB non disponible, fallback")
        yield None
    except Exception as e:
        logger.error(f"Erreur DB: {e}")
        yield None


# ═══════════════════════════════════════════════════════════
# SYSTÈME DE MIGRATION
# ═══════════════════════════════════════════════════════════

class MigrationManager:
    """
    Gestionnaire de migrations de schéma

    Gère versionnement et application automatique des migrations
    """

    MIGRATIONS_TABLE = "schema_migrations"

    @staticmethod
    def init_migrations_table():
        """Crée table de suivi des migrations si n'existe pas"""
        engine = get_engine()

        with engine.connect() as conn:
            conn.execute(text(f"""
                CREATE TABLE IF NOT EXISTS {MigrationManager.MIGRATIONS_TABLE} (
                    id SERIAL PRIMARY KEY,
                    version INTEGER NOT NULL UNIQUE,
                    name VARCHAR(255) NOT NULL,
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            conn.commit()

        logger.info("✅ Table migrations initialisée")

    @staticmethod
    def get_current_version() -> int:
        """Retourne version actuelle du schéma"""
        try:
            engine = get_engine()

            with engine.connect() as conn:
                result = conn.execute(text(f"""
                    SELECT MAX(version) FROM {MigrationManager.MIGRATIONS_TABLE}
                """)).scalar()

                return result if result else 0

        except Exception:
            return 0

    @staticmethod
    def apply_migration(version: int, name: str, sql: str):
        """Applique une migration"""
        engine = get_engine()

        try:
            with engine.begin() as conn:
                # Exécuter SQL migration
                conn.execute(text(sql))

                # Enregistrer migration
                conn.execute(text(f"""
                    INSERT INTO {MigrationManager.MIGRATIONS_TABLE} (version, name)
                    VALUES (:version, :name)
                """), {"version": version, "name": name})

            logger.info(f"✅ Migration v{version} appliquée: {name}")
            return True

        except Exception as e:
            logger.error(f"❌ Échec migration v{version}: {e}")
            raise

    @staticmethod
    def run_migrations():
        """Exécute toutes les migrations en attente"""
        MigrationManager.init_migrations_table()

        current_version = MigrationManager.get_current_version()
        logger.info(f"Version schéma actuelle: v{current_version}")

        # Migrations disponibles
        migrations = MigrationManager.get_available_migrations()

        # Filtrer migrations non appliquées
        pending = [m for m in migrations if m["version"] > current_version]

        if not pending:
            logger.info("✅ Aucune migration en attente")
            return

        logger.info(f"🔄 {len(pending)} migration(s) en attente")

        for migration in sorted(pending, key=lambda x: x["version"]):
            logger.info(f"Application migration v{migration['version']}: {migration['name']}")
            MigrationManager.apply_migration(
                migration["version"],
                migration["name"],
                migration["sql"]
            )

        logger.info("✅ Toutes les migrations appliquées")

    @staticmethod
    def get_available_migrations() -> List[dict]:
        """
        Retourne liste des migrations disponibles

        À personnaliser selon vos besoins (fichiers SQL, etc.)
        """
        return [
            {
                "version": 1,
                "name": "add_indexes_performance",
                "sql": MIGRATION_V1_ADD_INDEXES
            },
            {
                "version": 2,
                "name": "add_constraints_integrity",
                "sql": MIGRATION_V2_ADD_CONSTRAINTS
            },
            {
                "version": 3,
                "name": "add_unique_constraints",
                "sql": MIGRATION_V3_ADD_UNIQUE_CONSTRAINTS
            }
        ]


# ═══════════════════════════════════════════════════════════
# MIGRATIONS SQL
# ═══════════════════════════════════════════════════════════

MIGRATION_V1_ADD_INDEXES = """
-- Migration v1: Ajout index de performance

-- Recettes
CREATE INDEX IF NOT EXISTS idx_recette_saison_type ON recettes(saison, type_repas);
CREATE INDEX IF NOT EXISTS idx_recette_rapide ON recettes(est_rapide, temps_preparation);
CREATE INDEX IF NOT EXISTS idx_recette_bebe ON recettes(compatible_bebe);
CREATE INDEX IF NOT EXISTS idx_recette_created ON recettes(cree_le);
CREATE INDEX IF NOT EXISTS idx_recette_nom ON recettes(nom);
CREATE INDEX IF NOT EXISTS idx_recette_difficulte ON recettes(difficulte);

-- Ingrédients
CREATE INDEX IF NOT EXISTS idx_ingredient_nom_categorie ON ingredients(nom, categorie);
CREATE INDEX IF NOT EXISTS idx_ingredient_categorie ON ingredients(categorie);

-- Inventaire
CREATE INDEX IF NOT EXISTS idx_inventaire_stock_bas ON inventaire(quantite, quantite_min);
CREATE INDEX IF NOT EXISTS idx_inventaire_peremption ON inventaire(date_peremption);
CREATE INDEX IF NOT EXISTS idx_inventaire_emplacement ON inventaire(emplacement);
CREATE INDEX IF NOT EXISTS idx_inventaire_maj ON inventaire(derniere_maj);

-- Courses
CREATE INDEX IF NOT EXISTS idx_courses_actifs ON liste_courses(achete, priorite);
CREATE INDEX IF NOT EXISTS idx_courses_magasin ON liste_courses(magasin_cible, rayon_magasin);
CREATE INDEX IF NOT EXISTS idx_courses_priorite ON liste_courses(priorite);
CREATE INDEX IF NOT EXISTS idx_courses_created ON liste_courses(cree_le);

-- Planning
CREATE INDEX IF NOT EXISTS idx_planning_semaine_statut ON plannings_hebdomadaires(semaine_debut, statut);
CREATE INDEX IF NOT EXISTS idx_repas_planning_jour ON repas_planning(planning_id, jour_semaine);
CREATE INDEX IF NOT EXISTS idx_repas_date ON repas_planning(date);
CREATE INDEX IF NOT EXISTS idx_repas_statut ON repas_planning(statut);
CREATE INDEX IF NOT EXISTS idx_repas_type ON repas_planning(type_repas);

-- Relations
CREATE INDEX IF NOT EXISTS idx_recette_ingredient_recette ON recette_ingredients(recette_id);
CREATE INDEX IF NOT EXISTS idx_recette_ingredient_ingredient ON recette_ingredients(ingredient_id);
CREATE INDEX IF NOT EXISTS idx_etape_recette ON etapes_recette(recette_id);
CREATE INDEX IF NOT EXISTS idx_version_recette ON versions_recette(recette_base_id);
CREATE INDEX IF NOT EXISTS idx_version_type ON versions_recette(type_version);

-- Famille
CREATE INDEX IF NOT EXISTS idx_bien_etre_enfant_date ON entrees_bien_etre(enfant_id, date);
CREATE INDEX IF NOT EXISTS idx_routine_enfant ON routines(enfant_id);
CREATE INDEX IF NOT EXISTS idx_routine_active ON routines(est_active);
CREATE INDEX IF NOT EXISTS idx_tache_routine ON taches_routine(routine_id);
CREATE INDEX IF NOT EXISTS idx_tache_statut ON taches_routine(statut);

-- Maison
CREATE INDEX IF NOT EXISTS idx_projet_statut_priorite ON projets(statut, priorite);
CREATE INDEX IF NOT EXISTS idx_projet_categorie ON projets(categorie);
CREATE INDEX IF NOT EXISTS idx_tache_projet ON taches_projet(projet_id);
CREATE INDEX IF NOT EXISTS idx_jardin_arrosage ON elements_jardin(dernier_arrosage, frequence_arrosage_jours);
CREATE INDEX IF NOT EXISTS idx_jardin_categorie ON elements_jardin(categorie);
CREATE INDEX IF NOT EXISTS idx_log_jardin ON logs_jardin(element_id, date);

-- Calendrier
CREATE INDEX IF NOT EXISTS idx_evenement_date ON evenements_calendrier(date_debut);
CREATE INDEX IF NOT EXISTS idx_evenement_categorie ON evenements_calendrier(categorie);

-- Utilisateurs
CREATE INDEX IF NOT EXISTS idx_utilisateur_nom ON utilisateurs(nom_utilisateur);
CREATE INDEX IF NOT EXISTS idx_utilisateur_email ON utilisateurs(email);
"""

MIGRATION_V2_ADD_CONSTRAINTS = """
-- Migration v2: Ajout contraintes d'intégrité

-- Recettes
ALTER TABLE recettes 
  ADD CONSTRAINT IF NOT EXISTS check_temps_prep_positif 
  CHECK (temps_preparation >= 0);

ALTER TABLE recettes 
  ADD CONSTRAINT IF NOT EXISTS check_temps_cuisson_positif 
  CHECK (temps_cuisson >= 0);

ALTER TABLE recettes 
  ADD CONSTRAINT IF NOT EXISTS check_portions_valides 
  CHECK (portions > 0 AND portions <= 20);

-- Recette Ingrédients
ALTER TABLE recette_ingredients 
  ADD CONSTRAINT IF NOT EXISTS check_quantite_positive 
  CHECK (quantite > 0);

-- Étapes
ALTER TABLE etapes_recette 
  ADD CONSTRAINT IF NOT EXISTS check_ordre_positif 
  CHECK (ordre > 0);

ALTER TABLE etapes_recette 
  ADD CONSTRAINT IF NOT EXISTS check_duree_positive 
  CHECK (duree IS NULL OR duree >= 0);

-- Inventaire
ALTER TABLE inventaire 
  ADD CONSTRAINT IF NOT EXISTS check_quantite_inventaire_positive 
  CHECK (quantite >= 0);

ALTER TABLE inventaire 
  ADD CONSTRAINT IF NOT EXISTS check_seuil_positif 
  CHECK (quantite_min >= 0);

-- Courses
ALTER TABLE liste_courses 
  ADD CONSTRAINT IF NOT EXISTS check_quantite_courses_positive 
  CHECK (quantite_necessaire > 0);

-- Planning
ALTER TABLE repas_planning 
  ADD CONSTRAINT IF NOT EXISTS check_jour_valide 
  CHECK (jour_semaine >= 0 AND jour_semaine <= 6);

ALTER TABLE repas_planning 
  ADD CONSTRAINT IF NOT EXISTS check_portions_repas_valides 
  CHECK (portions > 0 AND portions <= 20);

ALTER TABLE repas_planning 
  ADD CONSTRAINT IF NOT EXISTS check_ordre_repas_positif 
  CHECK (ordre >= 0);

-- Config Planning
ALTER TABLE config_planning_utilisateur 
  ADD CONSTRAINT IF NOT EXISTS check_nb_adultes_valide 
  CHECK (nb_adultes > 0 AND nb_adultes <= 10);

ALTER TABLE config_planning_utilisateur 
  ADD CONSTRAINT IF NOT EXISTS check_nb_enfants_valide 
  CHECK (nb_enfants >= 0 AND nb_enfants <= 10);

-- Bien-être
ALTER TABLE entrees_bien_etre 
  ADD CONSTRAINT IF NOT EXISTS check_sommeil_valide 
  CHECK (heures_sommeil IS NULL OR (heures_sommeil >= 0 AND heures_sommeil <= 24));

-- Projets
ALTER TABLE projets 
  ADD CONSTRAINT IF NOT EXISTS check_progression_valide 
  CHECK (progression >= 0 AND progression <= 100);

ALTER TABLE projets 
  ADD CONSTRAINT IF NOT EXISTS check_dates_coherentes 
  CHECK (date_fin IS NULL OR date_debut IS NULL OR date_fin >= date_debut);

-- Jardin
ALTER TABLE elements_jardin 
  ADD CONSTRAINT IF NOT EXISTS check_quantite_jardin_positive 
  CHECK (quantite > 0);

ALTER TABLE elements_jardin 
  ADD CONSTRAINT IF NOT EXISTS check_frequence_arrosage_positive 
  CHECK (frequence_arrosage_jours > 0);

-- Événements
ALTER TABLE evenements_calendrier 
  ADD CONSTRAINT IF NOT EXISTS check_dates_evenement_coherentes 
  CHECK (date_fin IS NULL OR date_fin >= date_debut);
"""

MIGRATION_V3_ADD_UNIQUE_CONSTRAINTS = """
-- Migration v3: Ajout contraintes d'unicité

-- Éviter doublons ingrédient dans recette
ALTER TABLE recette_ingredients 
  ADD CONSTRAINT IF NOT EXISTS uq_recette_ingredient 
  UNIQUE (recette_id, ingredient_id);

-- Éviter doublons ordre dans recette
ALTER TABLE etapes_recette 
  ADD CONSTRAINT IF NOT EXISTS uq_recette_ordre 
  UNIQUE (recette_id, ordre);

-- Une seule version de chaque type par recette
ALTER TABLE versions_recette 
  ADD CONSTRAINT IF NOT EXISTS uq_recette_version_type 
  UNIQUE (recette_base_id, type_version);

-- Un seul article inventaire par ingrédient
ALTER TABLE inventaire 
  ADD CONSTRAINT IF NOT EXISTS uq_inventaire_ingredient 
  UNIQUE (ingredient_id);

-- Une seule semaine par planning
ALTER TABLE plannings_hebdomadaires 
  ADD CONSTRAINT IF NOT EXISTS uq_planning_semaine 
  UNIQUE (semaine_debut);

-- Éviter doublons repas dans planning
ALTER TABLE repas_planning 
  ADD CONSTRAINT IF NOT EXISTS uq_planning_jour_type_ordre 
  UNIQUE (planning_id, jour_semaine, type_repas, ordre);

-- Une seule config par utilisateur
ALTER TABLE config_planning_utilisateur 
  ADD CONSTRAINT IF NOT EXISTS uq_config_utilisateur 
  UNIQUE (utilisateur_id);
"""


# ═══════════════════════════════════════════════════════════
# VÉRIFICATIONS
# ═══════════════════════════════════════════════════════════

@st.cache_data(ttl=60)
def check_connection() -> tuple[bool, str]:
    """Vérifie connexion avec message d'erreur"""
    try:
        engine = get_engine_safe()
        if not engine:
            return False, "Engine non disponible"

        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))

        return True, "Connexion OK"

    except DatabaseConnectionError as e:
        return False, f"Erreur connexion: {str(e)}"

    except Exception as e:
        logger.error(f"❌ Test connexion échoué: {e}")
        return False, f"Erreur: {str(e)}"


@st.cache_data(ttl=300)
def get_db_info() -> dict:
    """Retourne infos DB"""
    try:
        engine = get_engine()

        with engine.connect() as conn:
            result = conn.execute(
                text("""
                SELECT 
                    version() as version,
                    current_database() as database,
                    current_user as user,
                    pg_size_pretty(pg_database_size(current_database())) as size
            """)
            ).fetchone()

            from src.core.config import get_settings
            settings = get_settings()
            db_url = settings.DATABASE_URL

            host = "unknown"
            if "@" in db_url:
                host = db_url.split("@")[1].split(":")[0]

            return {
                "status": "connected",
                "version": result[0].split(",")[0],
                "database": result[1],
                "user": result[2],
                "size": result[3],
                "host": host,
                "schema_version": MigrationManager.get_current_version(),
                "error": None,
            }

    except Exception as e:
        logger.error(f"get_db_info error: {e}")
        return {
            "status": "error",
            "error": str(e),
            "version": None,
            "database": None,
            "user": None,
            "schema_version": 0
        }


# ═══════════════════════════════════════════════════════════
# INITIALISATION
# ═══════════════════════════════════════════════════════════

def init_database(run_migrations: bool = True):
    """
    Initialise la base de données

    Args:
        run_migrations: Si True, exécute les migrations automatiquement
    """
    from src.core.config import get_settings
    settings = get_settings()

    if settings.is_production():
        logger.info("Mode production: vérification schéma uniquement")

    try:
        engine = get_engine()

        # Vérifier connexion
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))

        logger.info("✅ Connexion DB OK")

        # Exécuter migrations si demandé
        if run_migrations:
            logger.info("🔄 Exécution migrations...")
            MigrationManager.run_migrations()

        return True

    except Exception as e:
        logger.error(f"❌ Erreur initialisation DB: {e}")
        return False


def create_all_tables():
    """
    Crée toutes les tables (dev/setup uniquement)

    ATTENTION: Ne pas appeler en production
    """
    from src.core.config import get_settings
    settings = get_settings()

    if settings.is_production():
        logger.warning("create_all_tables ignoré en production")
        return

    try:
        from src.core.models import Base
        engine = get_engine()
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Tables créées/vérifiées")

    except Exception as e:
        logger.error(f"Erreur création tables: {e}")
        raise


# ═══════════════════════════════════════════════════════════
# MAINTENANCE
# ═══════════════════════════════════════════════════════════

def health_check() -> dict:
    """Health check complet de la DB"""
    try:
        engine = get_engine()

        with engine.connect() as conn:
            active_conns = conn.execute(
                text("""
                SELECT count(*) 
                FROM pg_stat_activity 
                WHERE state = 'active'
            """)
            ).scalar()

            db_size = conn.execute(
                text("SELECT pg_database_size(current_database())")
            ).scalar()

            return {
                "healthy": True,
                "active_connections": active_conns,
                "database_size_bytes": db_size,
                "schema_version": MigrationManager.get_current_version(),
                "timestamp": time.time(),
            }

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "healthy": False,
            "error": str(e),
            "timestamp": time.time()
        }


def vacuum_database():
    """Optimise la base (VACUUM)"""
    try:
        engine = get_engine()

        with engine.connect() as conn:
            conn.execution_options(isolation_level="AUTOCOMMIT")
            conn.execute(text("VACUUM ANALYZE"))

        logger.info("✅ VACUUM ANALYZE exécuté")

    except Exception as e:
        logger.error(f"Erreur VACUUM: {e}")