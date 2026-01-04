"""
Service Versions Recettes - Gestion Bébé & Batch

Service pour gérer les versions alternatives des recettes :
- Création/sauvegarde versions bébé
- Création/sauvegarde versions batch cooking
- Récupération versions existantes
"""
import logging
from typing import Optional

from src.core import (
    BaseService,
    obtenir_contexte_db,
    handle_errors,
    Cache,
    ErreurNonTrouve,
)
from src.core.models import VersionRecette, TypeVersionRecetteEnum

from .recette_ai_service import (
    recette_ai_service,
    VersionBebeGeneree,
    VersionBatchGeneree,
)

logger = logging.getLogger(__name__)


class RecetteVersionService(BaseService[VersionRecette]):
    """
    Service pour gérer les versions alternatives de recettes.

    Orchestre la génération IA et la sauvegarde en base.
    """

    def __init__(self):
        """Initialise le service avec cache 2h."""
        super().__init__(VersionRecette, cache_ttl=7200)

    # ═══════════════════════════════════════════════════════════
    # RÉCUPÉRATION VERSIONS
    # ═══════════════════════════════════════════════════════════

    @handle_errors(show_in_ui=False, fallback_value=None)
    def get_version_bebe(self, recette_id: int) -> Optional[VersionRecette]:
        """
        Récupère la version bébé existante.

        Args:
            recette_id: ID de la recette

        Returns:
            Version bébé ou None
        """
        with obtenir_contexte_db() as db:
            return db.query(VersionRecette).filter(
                VersionRecette.recette_base_id == recette_id,
                VersionRecette.type_version == TypeVersionRecetteEnum.BEBE.value
            ).first()

    @handle_errors(show_in_ui=False, fallback_value=None)
    def get_version_batch(self, recette_id: int) -> Optional[VersionRecette]:
        """
        Récupère la version batch cooking existante.

        Args:
            recette_id: ID de la recette

        Returns:
            Version batch ou None
        """
        with obtenir_contexte_db() as db:
            return db.query(VersionRecette).filter(
                VersionRecette.recette_base_id == recette_id,
                VersionRecette.type_version == TypeVersionRecetteEnum.BATCH_COOKING.value
            ).first()

    # ═══════════════════════════════════════════════════════════
    # GÉNÉRATION + SAUVEGARDE VERSION BÉBÉ
    # ═══════════════════════════════════════════════════════════

    @handle_errors(show_in_ui=True, fallback_value=None)
    async def generer_et_sauvegarder_version_bebe(
            self,
            recette_id: int,
            force_regeneration: bool = False
    ) -> Optional[VersionRecette]:
        """
        Génère et sauvegarde une version bébé.

        Args:
            recette_id: ID de la recette
            force_regeneration: Forcer la régénération si existe déjà

        Returns:
            Version bébé sauvegardée

        Example:
            >>> version = await service.generer_et_sauvegarder_version_bebe(42)
            >>> print(version.notes_bebe)
        """
        # Vérifier si existe déjà
        if not force_regeneration:
            existing = self.get_version_bebe(recette_id)
            if existing:
                logger.info(f"Version bébé déjà existante pour recette {recette_id}")
                return existing

        # Générer avec IA
        version_generee = await recette_ai_service.adapter_recette_bebe(recette_id)

        if not version_generee:
            logger.error(f"Échec génération version bébé pour recette {recette_id}")
            return None

        # Sauvegarder en base
        return self._sauvegarder_version_bebe(recette_id, version_generee)

    @handle_errors(show_in_ui=True, fallback_value=None)
    def _sauvegarder_version_bebe(
            self,
            recette_id: int,
            version_data: VersionBebeGeneree
    ) -> Optional[VersionRecette]:
        """Sauvegarde version bébé en base."""
        with obtenir_contexte_db() as db:
            # Supprimer ancienne version si existe
            db.query(VersionRecette).filter(
                VersionRecette.recette_base_id == recette_id,
                VersionRecette.type_version == TypeVersionRecetteEnum.BEBE.value
            ).delete()

            # Créer nouvelle version
            version = VersionRecette(
                recette_base_id=recette_id,
                type_version=TypeVersionRecetteEnum.BEBE.value,
                instructions_modifiees=version_data.instructions_modifiees,
                notes_bebe=version_data.notes_bebe,
                ingredients_modifies=version_data.ingredients_modifies,
            )

            db.add(version)
            db.commit()
            db.refresh(version)

            # Invalider cache
            Cache.invalider(dependencies=[
                f"recette_{recette_id}",
                f"version_bebe_{recette_id}"
            ])

            logger.info(f"✅ Version bébé sauvegardée (recette {recette_id})")
            return version

    # ═══════════════════════════════════════════════════════════
    # GÉNÉRATION + SAUVEGARDE VERSION BATCH
    # ═══════════════════════════════════════════════════════════

    @handle_errors(show_in_ui=True, fallback_value=None)
    async def generer_et_sauvegarder_version_batch(
            self,
            recette_id: int,
            force_regeneration: bool = False
    ) -> Optional[VersionRecette]:
        """
        Génère et sauvegarde une version batch cooking.

        Args:
            recette_id: ID de la recette
            force_regeneration: Forcer la régénération

        Returns:
            Version batch sauvegardée
        """
        # Vérifier si existe
        if not force_regeneration:
            existing = self.get_version_batch(recette_id)
            if existing:
                logger.info(f"Version batch déjà existante pour recette {recette_id}")
                return existing

        # Générer avec IA
        version_generee = await recette_ai_service.adapter_recette_batch(recette_id)

        if not version_generee:
            logger.error(f"Échec génération version batch pour recette {recette_id}")
            return None

        # Sauvegarder
        return self._sauvegarder_version_batch(recette_id, version_generee)

    @handle_errors(show_in_ui=True, fallback_value=None)
    def _sauvegarder_version_batch(
            self,
            recette_id: int,
            version_data: VersionBatchGeneree
    ) -> Optional[VersionRecette]:
        """Sauvegarde version batch en base."""
        with obtenir_contexte_db() as db:
            # Supprimer ancienne
            db.query(VersionRecette).filter(
                VersionRecette.recette_base_id == recette_id,
                VersionRecette.type_version == TypeVersionRecetteEnum.BATCH_COOKING.value
            ).delete()

            # Créer nouvelle
            version = VersionRecette(
                recette_base_id=recette_id,
                type_version=TypeVersionRecetteEnum.BATCH_COOKING.value,
                etapes_paralleles_batch=version_data.etapes_paralleles,
                temps_optimise_batch=version_data.temps_optimise,
                instructions_modifiees=version_data.conseils_batch,
            )

            db.add(version)
            db.commit()
            db.refresh(version)

            # Invalider cache
            Cache.invalider(dependencies=[
                f"recette_{recette_id}",
                f"version_batch_{recette_id}"
            ])

            logger.info(f"✅ Version batch sauvegardée (recette {recette_id})")
            return version

    # ═══════════════════════════════════════════════════════════
    # SUPPRESSION
    # ═══════════════════════════════════════════════════════════

    @handle_errors(show_in_ui=True, fallback_value=False)
    def supprimer_version(
            self,
            recette_id: int,
            type_version: str
    ) -> bool:
        """
        Supprime une version spécifique.

        Args:
            recette_id: ID de la recette
            type_version: "bébé" ou "batch_cooking"

        Returns:
            True si supprimé
        """
        with obtenir_contexte_db() as db:
            count = db.query(VersionRecette).filter(
                VersionRecette.recette_base_id == recette_id,
                VersionRecette.type_version == type_version
            ).delete()

            db.commit()

            if count > 0:
                Cache.invalider(dependencies=[
                    f"recette_{recette_id}",
                    f"version_{type_version}_{recette_id}"
                ])
                logger.info(f"Version {type_version} supprimée (recette {recette_id})")
                return True

            return False


# ═══════════════════════════════════════════════════════════
# INSTANCE SINGLETON
# ═══════════════════════════════════════════════════════════

recette_version_service = RecetteVersionService()