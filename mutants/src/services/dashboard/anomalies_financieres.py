"""Service IA - detection d'anomalies de depenses (IA3)."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import date
from typing import Any

from pydantic import BaseModel, Field

from src.core.ai import obtenir_client_ia
from src.core.db import obtenir_contexte_db
from src.services.core.base import BaseAIService
from src.services.core.registry import service_factory
from typing import Annotated
from typing import Callable
from typing import ClassVar

MutantDict = Annotated[dict[str, Callable], "Mutant"] # type: ignore


def _mutmut_trampoline(orig, mutants, call_args, call_kwargs, self_arg = None): # type: ignore
    """Forward call to original or mutated function, depending on the environment"""
    import os # type: ignore
    mutant_under_test = os.environ['MUTANT_UNDER_TEST'] # type: ignore
    if mutant_under_test == 'fail': # type: ignore
        from mutmut.__main__ import MutmutProgrammaticFailException # type: ignore
        raise MutmutProgrammaticFailException('Failed programmatically')       # type: ignore
    elif mutant_under_test == 'stats': # type: ignore
        from mutmut.__main__ import record_trampoline_hit # type: ignore
        record_trampoline_hit(orig.__module__ + '.' + orig.__name__) # type: ignore
        # (for class methods, orig is bound and thus does not need the explicit self argument)
        result = orig(*call_args, **call_kwargs) # type: ignore
        return result # type: ignore
    prefix = orig.__module__ + '.' + orig.__name__ + '__mutmut_' # type: ignore
    if not mutant_under_test.startswith(prefix): # type: ignore
        result = orig(*call_args, **call_kwargs) # type: ignore
        return result # type: ignore
    mutant_name = mutant_under_test.rpartition('.')[-1] # type: ignore
    if self_arg is not None: # type: ignore
        # call to a class method where self is not bound
        result = mutants[mutant_name](self_arg, *call_args, **call_kwargs) # type: ignore
    else:
        result = mutants[mutant_name](*call_args, **call_kwargs) # type: ignore
    return result # type: ignore


@dataclass
class MoisRef:
    annee: int
    mois: int


class ResumeAnomaliesIA(BaseModel):
    """Sortie IA courte pour widget dashboard."""

    resume: str = ""
    recommandations: list[str] = Field(default_factory=list)


class ServiceAnomaliesFinancieres(BaseAIService):
    """Compare mois courant vs N-1/N-2 et detecte les variations anormales."""

    def __init__(self) -> None:
        args = []# type: ignore
        kwargs = {}# type: ignore
        return _mutmut_trampoline(object.__getattribute__(self, 'xǁServiceAnomaliesFinancieresǁ__init____mutmut_orig'), object.__getattribute__(self, 'xǁServiceAnomaliesFinancieresǁ__init____mutmut_mutants'), args, kwargs, self)

    def xǁServiceAnomaliesFinancieresǁ__init____mutmut_orig(self) -> None:
        super().__init__(
            client=obtenir_client_ia(),
            cache_prefix="anomalies_financieres",
            default_ttl=1800,
            service_name="anomalies_financieres",
        )

    def xǁServiceAnomaliesFinancieresǁ__init____mutmut_1(self) -> None:
        super().__init__(
            client=None,
            cache_prefix="anomalies_financieres",
            default_ttl=1800,
            service_name="anomalies_financieres",
        )

    def xǁServiceAnomaliesFinancieresǁ__init____mutmut_2(self) -> None:
        super().__init__(
            client=obtenir_client_ia(),
            cache_prefix=None,
            default_ttl=1800,
            service_name="anomalies_financieres",
        )

    def xǁServiceAnomaliesFinancieresǁ__init____mutmut_3(self) -> None:
        super().__init__(
            client=obtenir_client_ia(),
            cache_prefix="anomalies_financieres",
            default_ttl=None,
            service_name="anomalies_financieres",
        )

    def xǁServiceAnomaliesFinancieresǁ__init____mutmut_4(self) -> None:
        super().__init__(
            client=obtenir_client_ia(),
            cache_prefix="anomalies_financieres",
            default_ttl=1800,
            service_name=None,
        )

    def xǁServiceAnomaliesFinancieresǁ__init____mutmut_5(self) -> None:
        super().__init__(
            cache_prefix="anomalies_financieres",
            default_ttl=1800,
            service_name="anomalies_financieres",
        )

    def xǁServiceAnomaliesFinancieresǁ__init____mutmut_6(self) -> None:
        super().__init__(
            client=obtenir_client_ia(),
            default_ttl=1800,
            service_name="anomalies_financieres",
        )

    def xǁServiceAnomaliesFinancieresǁ__init____mutmut_7(self) -> None:
        super().__init__(
            client=obtenir_client_ia(),
            cache_prefix="anomalies_financieres",
            service_name="anomalies_financieres",
        )

    def xǁServiceAnomaliesFinancieresǁ__init____mutmut_8(self) -> None:
        super().__init__(
            client=obtenir_client_ia(),
            cache_prefix="anomalies_financieres",
            default_ttl=1800,
            )

    def xǁServiceAnomaliesFinancieresǁ__init____mutmut_9(self) -> None:
        super().__init__(
            client=obtenir_client_ia(),
            cache_prefix="XXanomalies_financieresXX",
            default_ttl=1800,
            service_name="anomalies_financieres",
        )

    def xǁServiceAnomaliesFinancieresǁ__init____mutmut_10(self) -> None:
        super().__init__(
            client=obtenir_client_ia(),
            cache_prefix="ANOMALIES_FINANCIERES",
            default_ttl=1800,
            service_name="anomalies_financieres",
        )

    def xǁServiceAnomaliesFinancieresǁ__init____mutmut_11(self) -> None:
        super().__init__(
            client=obtenir_client_ia(),
            cache_prefix="anomalies_financieres",
            default_ttl=1801,
            service_name="anomalies_financieres",
        )

    def xǁServiceAnomaliesFinancieresǁ__init____mutmut_12(self) -> None:
        super().__init__(
            client=obtenir_client_ia(),
            cache_prefix="anomalies_financieres",
            default_ttl=1800,
            service_name="XXanomalies_financieresXX",
        )

    def xǁServiceAnomaliesFinancieresǁ__init____mutmut_13(self) -> None:
        super().__init__(
            client=obtenir_client_ia(),
            cache_prefix="anomalies_financieres",
            default_ttl=1800,
            service_name="ANOMALIES_FINANCIERES",
        )
    
    xǁServiceAnomaliesFinancieresǁ__init____mutmut_mutants : ClassVar[MutantDict] = { # type: ignore
    'xǁServiceAnomaliesFinancieresǁ__init____mutmut_1': xǁServiceAnomaliesFinancieresǁ__init____mutmut_1, 
        'xǁServiceAnomaliesFinancieresǁ__init____mutmut_2': xǁServiceAnomaliesFinancieresǁ__init____mutmut_2, 
        'xǁServiceAnomaliesFinancieresǁ__init____mutmut_3': xǁServiceAnomaliesFinancieresǁ__init____mutmut_3, 
        'xǁServiceAnomaliesFinancieresǁ__init____mutmut_4': xǁServiceAnomaliesFinancieresǁ__init____mutmut_4, 
        'xǁServiceAnomaliesFinancieresǁ__init____mutmut_5': xǁServiceAnomaliesFinancieresǁ__init____mutmut_5, 
        'xǁServiceAnomaliesFinancieresǁ__init____mutmut_6': xǁServiceAnomaliesFinancieresǁ__init____mutmut_6, 
        'xǁServiceAnomaliesFinancieresǁ__init____mutmut_7': xǁServiceAnomaliesFinancieresǁ__init____mutmut_7, 
        'xǁServiceAnomaliesFinancieresǁ__init____mutmut_8': xǁServiceAnomaliesFinancieresǁ__init____mutmut_8, 
        'xǁServiceAnomaliesFinancieresǁ__init____mutmut_9': xǁServiceAnomaliesFinancieresǁ__init____mutmut_9, 
        'xǁServiceAnomaliesFinancieresǁ__init____mutmut_10': xǁServiceAnomaliesFinancieresǁ__init____mutmut_10, 
        'xǁServiceAnomaliesFinancieresǁ__init____mutmut_11': xǁServiceAnomaliesFinancieresǁ__init____mutmut_11, 
        'xǁServiceAnomaliesFinancieresǁ__init____mutmut_12': xǁServiceAnomaliesFinancieresǁ__init____mutmut_12, 
        'xǁServiceAnomaliesFinancieresǁ__init____mutmut_13': xǁServiceAnomaliesFinancieresǁ__init____mutmut_13
    }
    xǁServiceAnomaliesFinancieresǁ__init____mutmut_orig.__name__ = 'xǁServiceAnomaliesFinancieresǁ__init__'

    @staticmethod
    def _mois_precedents(ref: date) -> list[MoisRef]:
        courant = MoisRef(annee=ref.year, mois=ref.month)
        mois_1 = ref.month - 1
        annee_1 = ref.year
        if mois_1 == 0:
            mois_1 = 12
            annee_1 -= 1

        mois_2 = mois_1 - 1
        annee_2 = annee_1
        if mois_2 == 0:
            mois_2 = 12
            annee_2 -= 1

        return [courant, MoisRef(annee_1, mois_1), MoisRef(annee_2, mois_2)]

    @staticmethod
    def _normaliser_categorie(categorie: str | None) -> str:
        cat = (categorie or "autre").strip().lower()
        if any(k in cat for k in ("course", "aliment", "supermarche", "epicer")):
            return "courses"
        if any(k in cat for k in ("energie", "electric", "gaz", "eau", "chauffage")):
            return "energie"
        if any(k in cat for k in ("loisir", "sortie", "jeu", "culture", "restaurant")):
            return "loisirs"
        return cat or "autre"

    def _collecter_depenses(self, reference: date | None = None) -> dict[str, dict[str, float]]:
        args = [reference]# type: ignore
        kwargs = {}# type: ignore
        return _mutmut_trampoline(object.__getattribute__(self, 'xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_orig'), object.__getattribute__(self, 'xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_mutants'), args, kwargs, self)

    def xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_orig(self, reference: date | None = None) -> dict[str, dict[str, float]]:
        """Collecte les montants par categorie normalisee sur mois courant, N-1, N-2."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)

        result: dict[str, dict[str, float]] = {
            f"{m.annee:04d}-{m.mois:02d}": defaultdict(float) for m in mois_refs
        }

        with obtenir_contexte_db() as session:
            from sqlalchemy import extract, func
            from src.core.models import BudgetFamille
            from src.core.models.finances import DepenseMaison

            for m in mois_refs:
                key = f"{m.annee:04d}-{m.mois:02d}"

                dep_famille = (
                    session.query(BudgetFamille.categorie, func.sum(BudgetFamille.montant))
                    .filter(
                        extract("year", BudgetFamille.date) == m.annee,
                        extract("month", BudgetFamille.date) == m.mois,
                    )
                    .group_by(BudgetFamille.categorie)
                    .all()
                )
                for categorie, montant in dep_famille:
                    result[key][self._normaliser_categorie(categorie)] += float(montant or 0.0)

                dep_maison = (
                    session.query(DepenseMaison.categorie, func.sum(DepenseMaison.montant))
                    .filter(DepenseMaison.annee == m.annee, DepenseMaison.mois == m.mois)
                    .group_by(DepenseMaison.categorie)
                    .all()
                )
                for categorie, montant in dep_maison:
                    result[key][self._normaliser_categorie(categorie)] += float(montant or 0.0)

        return {k: dict(v) for k, v in result.items()}

    def xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_1(self, reference: date | None = None) -> dict[str, dict[str, float]]:
        """Collecte les montants par categorie normalisee sur mois courant, N-1, N-2."""
        ref = None
        mois_refs = self._mois_precedents(ref)

        result: dict[str, dict[str, float]] = {
            f"{m.annee:04d}-{m.mois:02d}": defaultdict(float) for m in mois_refs
        }

        with obtenir_contexte_db() as session:
            from sqlalchemy import extract, func
            from src.core.models import BudgetFamille
            from src.core.models.finances import DepenseMaison

            for m in mois_refs:
                key = f"{m.annee:04d}-{m.mois:02d}"

                dep_famille = (
                    session.query(BudgetFamille.categorie, func.sum(BudgetFamille.montant))
                    .filter(
                        extract("year", BudgetFamille.date) == m.annee,
                        extract("month", BudgetFamille.date) == m.mois,
                    )
                    .group_by(BudgetFamille.categorie)
                    .all()
                )
                for categorie, montant in dep_famille:
                    result[key][self._normaliser_categorie(categorie)] += float(montant or 0.0)

                dep_maison = (
                    session.query(DepenseMaison.categorie, func.sum(DepenseMaison.montant))
                    .filter(DepenseMaison.annee == m.annee, DepenseMaison.mois == m.mois)
                    .group_by(DepenseMaison.categorie)
                    .all()
                )
                for categorie, montant in dep_maison:
                    result[key][self._normaliser_categorie(categorie)] += float(montant or 0.0)

        return {k: dict(v) for k, v in result.items()}

    def xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_2(self, reference: date | None = None) -> dict[str, dict[str, float]]:
        """Collecte les montants par categorie normalisee sur mois courant, N-1, N-2."""
        ref = reference and date.today()
        mois_refs = self._mois_precedents(ref)

        result: dict[str, dict[str, float]] = {
            f"{m.annee:04d}-{m.mois:02d}": defaultdict(float) for m in mois_refs
        }

        with obtenir_contexte_db() as session:
            from sqlalchemy import extract, func
            from src.core.models import BudgetFamille
            from src.core.models.finances import DepenseMaison

            for m in mois_refs:
                key = f"{m.annee:04d}-{m.mois:02d}"

                dep_famille = (
                    session.query(BudgetFamille.categorie, func.sum(BudgetFamille.montant))
                    .filter(
                        extract("year", BudgetFamille.date) == m.annee,
                        extract("month", BudgetFamille.date) == m.mois,
                    )
                    .group_by(BudgetFamille.categorie)
                    .all()
                )
                for categorie, montant in dep_famille:
                    result[key][self._normaliser_categorie(categorie)] += float(montant or 0.0)

                dep_maison = (
                    session.query(DepenseMaison.categorie, func.sum(DepenseMaison.montant))
                    .filter(DepenseMaison.annee == m.annee, DepenseMaison.mois == m.mois)
                    .group_by(DepenseMaison.categorie)
                    .all()
                )
                for categorie, montant in dep_maison:
                    result[key][self._normaliser_categorie(categorie)] += float(montant or 0.0)

        return {k: dict(v) for k, v in result.items()}

    def xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_3(self, reference: date | None = None) -> dict[str, dict[str, float]]:
        """Collecte les montants par categorie normalisee sur mois courant, N-1, N-2."""
        ref = reference or date.today()
        mois_refs = None

        result: dict[str, dict[str, float]] = {
            f"{m.annee:04d}-{m.mois:02d}": defaultdict(float) for m in mois_refs
        }

        with obtenir_contexte_db() as session:
            from sqlalchemy import extract, func
            from src.core.models import BudgetFamille
            from src.core.models.finances import DepenseMaison

            for m in mois_refs:
                key = f"{m.annee:04d}-{m.mois:02d}"

                dep_famille = (
                    session.query(BudgetFamille.categorie, func.sum(BudgetFamille.montant))
                    .filter(
                        extract("year", BudgetFamille.date) == m.annee,
                        extract("month", BudgetFamille.date) == m.mois,
                    )
                    .group_by(BudgetFamille.categorie)
                    .all()
                )
                for categorie, montant in dep_famille:
                    result[key][self._normaliser_categorie(categorie)] += float(montant or 0.0)

                dep_maison = (
                    session.query(DepenseMaison.categorie, func.sum(DepenseMaison.montant))
                    .filter(DepenseMaison.annee == m.annee, DepenseMaison.mois == m.mois)
                    .group_by(DepenseMaison.categorie)
                    .all()
                )
                for categorie, montant in dep_maison:
                    result[key][self._normaliser_categorie(categorie)] += float(montant or 0.0)

        return {k: dict(v) for k, v in result.items()}

    def xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_4(self, reference: date | None = None) -> dict[str, dict[str, float]]:
        """Collecte les montants par categorie normalisee sur mois courant, N-1, N-2."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(None)

        result: dict[str, dict[str, float]] = {
            f"{m.annee:04d}-{m.mois:02d}": defaultdict(float) for m in mois_refs
        }

        with obtenir_contexte_db() as session:
            from sqlalchemy import extract, func
            from src.core.models import BudgetFamille
            from src.core.models.finances import DepenseMaison

            for m in mois_refs:
                key = f"{m.annee:04d}-{m.mois:02d}"

                dep_famille = (
                    session.query(BudgetFamille.categorie, func.sum(BudgetFamille.montant))
                    .filter(
                        extract("year", BudgetFamille.date) == m.annee,
                        extract("month", BudgetFamille.date) == m.mois,
                    )
                    .group_by(BudgetFamille.categorie)
                    .all()
                )
                for categorie, montant in dep_famille:
                    result[key][self._normaliser_categorie(categorie)] += float(montant or 0.0)

                dep_maison = (
                    session.query(DepenseMaison.categorie, func.sum(DepenseMaison.montant))
                    .filter(DepenseMaison.annee == m.annee, DepenseMaison.mois == m.mois)
                    .group_by(DepenseMaison.categorie)
                    .all()
                )
                for categorie, montant in dep_maison:
                    result[key][self._normaliser_categorie(categorie)] += float(montant or 0.0)

        return {k: dict(v) for k, v in result.items()}

    def xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_5(self, reference: date | None = None) -> dict[str, dict[str, float]]:
        """Collecte les montants par categorie normalisee sur mois courant, N-1, N-2."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)

        result: dict[str, dict[str, float]] = None

        with obtenir_contexte_db() as session:
            from sqlalchemy import extract, func
            from src.core.models import BudgetFamille
            from src.core.models.finances import DepenseMaison

            for m in mois_refs:
                key = f"{m.annee:04d}-{m.mois:02d}"

                dep_famille = (
                    session.query(BudgetFamille.categorie, func.sum(BudgetFamille.montant))
                    .filter(
                        extract("year", BudgetFamille.date) == m.annee,
                        extract("month", BudgetFamille.date) == m.mois,
                    )
                    .group_by(BudgetFamille.categorie)
                    .all()
                )
                for categorie, montant in dep_famille:
                    result[key][self._normaliser_categorie(categorie)] += float(montant or 0.0)

                dep_maison = (
                    session.query(DepenseMaison.categorie, func.sum(DepenseMaison.montant))
                    .filter(DepenseMaison.annee == m.annee, DepenseMaison.mois == m.mois)
                    .group_by(DepenseMaison.categorie)
                    .all()
                )
                for categorie, montant in dep_maison:
                    result[key][self._normaliser_categorie(categorie)] += float(montant or 0.0)

        return {k: dict(v) for k, v in result.items()}

    def xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_6(self, reference: date | None = None) -> dict[str, dict[str, float]]:
        """Collecte les montants par categorie normalisee sur mois courant, N-1, N-2."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)

        result: dict[str, dict[str, float]] = {
            f"{m.annee:04d}-{m.mois:02d}": defaultdict(None) for m in mois_refs
        }

        with obtenir_contexte_db() as session:
            from sqlalchemy import extract, func
            from src.core.models import BudgetFamille
            from src.core.models.finances import DepenseMaison

            for m in mois_refs:
                key = f"{m.annee:04d}-{m.mois:02d}"

                dep_famille = (
                    session.query(BudgetFamille.categorie, func.sum(BudgetFamille.montant))
                    .filter(
                        extract("year", BudgetFamille.date) == m.annee,
                        extract("month", BudgetFamille.date) == m.mois,
                    )
                    .group_by(BudgetFamille.categorie)
                    .all()
                )
                for categorie, montant in dep_famille:
                    result[key][self._normaliser_categorie(categorie)] += float(montant or 0.0)

                dep_maison = (
                    session.query(DepenseMaison.categorie, func.sum(DepenseMaison.montant))
                    .filter(DepenseMaison.annee == m.annee, DepenseMaison.mois == m.mois)
                    .group_by(DepenseMaison.categorie)
                    .all()
                )
                for categorie, montant in dep_maison:
                    result[key][self._normaliser_categorie(categorie)] += float(montant or 0.0)

        return {k: dict(v) for k, v in result.items()}

    def xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_7(self, reference: date | None = None) -> dict[str, dict[str, float]]:
        """Collecte les montants par categorie normalisee sur mois courant, N-1, N-2."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)

        result: dict[str, dict[str, float]] = {
            f"{m.annee:04d}-{m.mois:02d}": defaultdict(float) for m in mois_refs
        }

        with obtenir_contexte_db() as session:
            from sqlalchemy import extract, func
            from src.core.models import BudgetFamille
            from src.core.models.finances import DepenseMaison

            for m in mois_refs:
                key = None

                dep_famille = (
                    session.query(BudgetFamille.categorie, func.sum(BudgetFamille.montant))
                    .filter(
                        extract("year", BudgetFamille.date) == m.annee,
                        extract("month", BudgetFamille.date) == m.mois,
                    )
                    .group_by(BudgetFamille.categorie)
                    .all()
                )
                for categorie, montant in dep_famille:
                    result[key][self._normaliser_categorie(categorie)] += float(montant or 0.0)

                dep_maison = (
                    session.query(DepenseMaison.categorie, func.sum(DepenseMaison.montant))
                    .filter(DepenseMaison.annee == m.annee, DepenseMaison.mois == m.mois)
                    .group_by(DepenseMaison.categorie)
                    .all()
                )
                for categorie, montant in dep_maison:
                    result[key][self._normaliser_categorie(categorie)] += float(montant or 0.0)

        return {k: dict(v) for k, v in result.items()}

    def xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_8(self, reference: date | None = None) -> dict[str, dict[str, float]]:
        """Collecte les montants par categorie normalisee sur mois courant, N-1, N-2."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)

        result: dict[str, dict[str, float]] = {
            f"{m.annee:04d}-{m.mois:02d}": defaultdict(float) for m in mois_refs
        }

        with obtenir_contexte_db() as session:
            from sqlalchemy import extract, func
            from src.core.models import BudgetFamille
            from src.core.models.finances import DepenseMaison

            for m in mois_refs:
                key = f"{m.annee:04d}-{m.mois:02d}"

                dep_famille = None
                for categorie, montant in dep_famille:
                    result[key][self._normaliser_categorie(categorie)] += float(montant or 0.0)

                dep_maison = (
                    session.query(DepenseMaison.categorie, func.sum(DepenseMaison.montant))
                    .filter(DepenseMaison.annee == m.annee, DepenseMaison.mois == m.mois)
                    .group_by(DepenseMaison.categorie)
                    .all()
                )
                for categorie, montant in dep_maison:
                    result[key][self._normaliser_categorie(categorie)] += float(montant or 0.0)

        return {k: dict(v) for k, v in result.items()}

    def xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_9(self, reference: date | None = None) -> dict[str, dict[str, float]]:
        """Collecte les montants par categorie normalisee sur mois courant, N-1, N-2."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)

        result: dict[str, dict[str, float]] = {
            f"{m.annee:04d}-{m.mois:02d}": defaultdict(float) for m in mois_refs
        }

        with obtenir_contexte_db() as session:
            from sqlalchemy import extract, func
            from src.core.models import BudgetFamille
            from src.core.models.finances import DepenseMaison

            for m in mois_refs:
                key = f"{m.annee:04d}-{m.mois:02d}"

                dep_famille = (
                    session.query(BudgetFamille.categorie, func.sum(BudgetFamille.montant))
                    .filter(
                        extract("year", BudgetFamille.date) == m.annee,
                        extract("month", BudgetFamille.date) == m.mois,
                    )
                    .group_by(None)
                    .all()
                )
                for categorie, montant in dep_famille:
                    result[key][self._normaliser_categorie(categorie)] += float(montant or 0.0)

                dep_maison = (
                    session.query(DepenseMaison.categorie, func.sum(DepenseMaison.montant))
                    .filter(DepenseMaison.annee == m.annee, DepenseMaison.mois == m.mois)
                    .group_by(DepenseMaison.categorie)
                    .all()
                )
                for categorie, montant in dep_maison:
                    result[key][self._normaliser_categorie(categorie)] += float(montant or 0.0)

        return {k: dict(v) for k, v in result.items()}

    def xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_10(self, reference: date | None = None) -> dict[str, dict[str, float]]:
        """Collecte les montants par categorie normalisee sur mois courant, N-1, N-2."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)

        result: dict[str, dict[str, float]] = {
            f"{m.annee:04d}-{m.mois:02d}": defaultdict(float) for m in mois_refs
        }

        with obtenir_contexte_db() as session:
            from sqlalchemy import extract, func
            from src.core.models import BudgetFamille
            from src.core.models.finances import DepenseMaison

            for m in mois_refs:
                key = f"{m.annee:04d}-{m.mois:02d}"

                dep_famille = (
                    session.query(BudgetFamille.categorie, func.sum(BudgetFamille.montant))
                    .filter(
                        None,
                        extract("month", BudgetFamille.date) == m.mois,
                    )
                    .group_by(BudgetFamille.categorie)
                    .all()
                )
                for categorie, montant in dep_famille:
                    result[key][self._normaliser_categorie(categorie)] += float(montant or 0.0)

                dep_maison = (
                    session.query(DepenseMaison.categorie, func.sum(DepenseMaison.montant))
                    .filter(DepenseMaison.annee == m.annee, DepenseMaison.mois == m.mois)
                    .group_by(DepenseMaison.categorie)
                    .all()
                )
                for categorie, montant in dep_maison:
                    result[key][self._normaliser_categorie(categorie)] += float(montant or 0.0)

        return {k: dict(v) for k, v in result.items()}

    def xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_11(self, reference: date | None = None) -> dict[str, dict[str, float]]:
        """Collecte les montants par categorie normalisee sur mois courant, N-1, N-2."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)

        result: dict[str, dict[str, float]] = {
            f"{m.annee:04d}-{m.mois:02d}": defaultdict(float) for m in mois_refs
        }

        with obtenir_contexte_db() as session:
            from sqlalchemy import extract, func
            from src.core.models import BudgetFamille
            from src.core.models.finances import DepenseMaison

            for m in mois_refs:
                key = f"{m.annee:04d}-{m.mois:02d}"

                dep_famille = (
                    session.query(BudgetFamille.categorie, func.sum(BudgetFamille.montant))
                    .filter(
                        extract("year", BudgetFamille.date) == m.annee,
                        None,
                    )
                    .group_by(BudgetFamille.categorie)
                    .all()
                )
                for categorie, montant in dep_famille:
                    result[key][self._normaliser_categorie(categorie)] += float(montant or 0.0)

                dep_maison = (
                    session.query(DepenseMaison.categorie, func.sum(DepenseMaison.montant))
                    .filter(DepenseMaison.annee == m.annee, DepenseMaison.mois == m.mois)
                    .group_by(DepenseMaison.categorie)
                    .all()
                )
                for categorie, montant in dep_maison:
                    result[key][self._normaliser_categorie(categorie)] += float(montant or 0.0)

        return {k: dict(v) for k, v in result.items()}

    def xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_12(self, reference: date | None = None) -> dict[str, dict[str, float]]:
        """Collecte les montants par categorie normalisee sur mois courant, N-1, N-2."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)

        result: dict[str, dict[str, float]] = {
            f"{m.annee:04d}-{m.mois:02d}": defaultdict(float) for m in mois_refs
        }

        with obtenir_contexte_db() as session:
            from sqlalchemy import extract, func
            from src.core.models import BudgetFamille
            from src.core.models.finances import DepenseMaison

            for m in mois_refs:
                key = f"{m.annee:04d}-{m.mois:02d}"

                dep_famille = (
                    session.query(BudgetFamille.categorie, func.sum(BudgetFamille.montant))
                    .filter(
                        extract("month", BudgetFamille.date) == m.mois,
                    )
                    .group_by(BudgetFamille.categorie)
                    .all()
                )
                for categorie, montant in dep_famille:
                    result[key][self._normaliser_categorie(categorie)] += float(montant or 0.0)

                dep_maison = (
                    session.query(DepenseMaison.categorie, func.sum(DepenseMaison.montant))
                    .filter(DepenseMaison.annee == m.annee, DepenseMaison.mois == m.mois)
                    .group_by(DepenseMaison.categorie)
                    .all()
                )
                for categorie, montant in dep_maison:
                    result[key][self._normaliser_categorie(categorie)] += float(montant or 0.0)

        return {k: dict(v) for k, v in result.items()}

    def xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_13(self, reference: date | None = None) -> dict[str, dict[str, float]]:
        """Collecte les montants par categorie normalisee sur mois courant, N-1, N-2."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)

        result: dict[str, dict[str, float]] = {
            f"{m.annee:04d}-{m.mois:02d}": defaultdict(float) for m in mois_refs
        }

        with obtenir_contexte_db() as session:
            from sqlalchemy import extract, func
            from src.core.models import BudgetFamille
            from src.core.models.finances import DepenseMaison

            for m in mois_refs:
                key = f"{m.annee:04d}-{m.mois:02d}"

                dep_famille = (
                    session.query(BudgetFamille.categorie, func.sum(BudgetFamille.montant))
                    .filter(
                        extract("year", BudgetFamille.date) == m.annee,
                        )
                    .group_by(BudgetFamille.categorie)
                    .all()
                )
                for categorie, montant in dep_famille:
                    result[key][self._normaliser_categorie(categorie)] += float(montant or 0.0)

                dep_maison = (
                    session.query(DepenseMaison.categorie, func.sum(DepenseMaison.montant))
                    .filter(DepenseMaison.annee == m.annee, DepenseMaison.mois == m.mois)
                    .group_by(DepenseMaison.categorie)
                    .all()
                )
                for categorie, montant in dep_maison:
                    result[key][self._normaliser_categorie(categorie)] += float(montant or 0.0)

        return {k: dict(v) for k, v in result.items()}

    def xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_14(self, reference: date | None = None) -> dict[str, dict[str, float]]:
        """Collecte les montants par categorie normalisee sur mois courant, N-1, N-2."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)

        result: dict[str, dict[str, float]] = {
            f"{m.annee:04d}-{m.mois:02d}": defaultdict(float) for m in mois_refs
        }

        with obtenir_contexte_db() as session:
            from sqlalchemy import extract, func
            from src.core.models import BudgetFamille
            from src.core.models.finances import DepenseMaison

            for m in mois_refs:
                key = f"{m.annee:04d}-{m.mois:02d}"

                dep_famille = (
                    session.query(None, func.sum(BudgetFamille.montant))
                    .filter(
                        extract("year", BudgetFamille.date) == m.annee,
                        extract("month", BudgetFamille.date) == m.mois,
                    )
                    .group_by(BudgetFamille.categorie)
                    .all()
                )
                for categorie, montant in dep_famille:
                    result[key][self._normaliser_categorie(categorie)] += float(montant or 0.0)

                dep_maison = (
                    session.query(DepenseMaison.categorie, func.sum(DepenseMaison.montant))
                    .filter(DepenseMaison.annee == m.annee, DepenseMaison.mois == m.mois)
                    .group_by(DepenseMaison.categorie)
                    .all()
                )
                for categorie, montant in dep_maison:
                    result[key][self._normaliser_categorie(categorie)] += float(montant or 0.0)

        return {k: dict(v) for k, v in result.items()}

    def xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_15(self, reference: date | None = None) -> dict[str, dict[str, float]]:
        """Collecte les montants par categorie normalisee sur mois courant, N-1, N-2."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)

        result: dict[str, dict[str, float]] = {
            f"{m.annee:04d}-{m.mois:02d}": defaultdict(float) for m in mois_refs
        }

        with obtenir_contexte_db() as session:
            from sqlalchemy import extract, func
            from src.core.models import BudgetFamille
            from src.core.models.finances import DepenseMaison

            for m in mois_refs:
                key = f"{m.annee:04d}-{m.mois:02d}"

                dep_famille = (
                    session.query(BudgetFamille.categorie, None)
                    .filter(
                        extract("year", BudgetFamille.date) == m.annee,
                        extract("month", BudgetFamille.date) == m.mois,
                    )
                    .group_by(BudgetFamille.categorie)
                    .all()
                )
                for categorie, montant in dep_famille:
                    result[key][self._normaliser_categorie(categorie)] += float(montant or 0.0)

                dep_maison = (
                    session.query(DepenseMaison.categorie, func.sum(DepenseMaison.montant))
                    .filter(DepenseMaison.annee == m.annee, DepenseMaison.mois == m.mois)
                    .group_by(DepenseMaison.categorie)
                    .all()
                )
                for categorie, montant in dep_maison:
                    result[key][self._normaliser_categorie(categorie)] += float(montant or 0.0)

        return {k: dict(v) for k, v in result.items()}

    def xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_16(self, reference: date | None = None) -> dict[str, dict[str, float]]:
        """Collecte les montants par categorie normalisee sur mois courant, N-1, N-2."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)

        result: dict[str, dict[str, float]] = {
            f"{m.annee:04d}-{m.mois:02d}": defaultdict(float) for m in mois_refs
        }

        with obtenir_contexte_db() as session:
            from sqlalchemy import extract, func
            from src.core.models import BudgetFamille
            from src.core.models.finances import DepenseMaison

            for m in mois_refs:
                key = f"{m.annee:04d}-{m.mois:02d}"

                dep_famille = (
                    session.query(func.sum(BudgetFamille.montant))
                    .filter(
                        extract("year", BudgetFamille.date) == m.annee,
                        extract("month", BudgetFamille.date) == m.mois,
                    )
                    .group_by(BudgetFamille.categorie)
                    .all()
                )
                for categorie, montant in dep_famille:
                    result[key][self._normaliser_categorie(categorie)] += float(montant or 0.0)

                dep_maison = (
                    session.query(DepenseMaison.categorie, func.sum(DepenseMaison.montant))
                    .filter(DepenseMaison.annee == m.annee, DepenseMaison.mois == m.mois)
                    .group_by(DepenseMaison.categorie)
                    .all()
                )
                for categorie, montant in dep_maison:
                    result[key][self._normaliser_categorie(categorie)] += float(montant or 0.0)

        return {k: dict(v) for k, v in result.items()}

    def xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_17(self, reference: date | None = None) -> dict[str, dict[str, float]]:
        """Collecte les montants par categorie normalisee sur mois courant, N-1, N-2."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)

        result: dict[str, dict[str, float]] = {
            f"{m.annee:04d}-{m.mois:02d}": defaultdict(float) for m in mois_refs
        }

        with obtenir_contexte_db() as session:
            from sqlalchemy import extract, func
            from src.core.models import BudgetFamille
            from src.core.models.finances import DepenseMaison

            for m in mois_refs:
                key = f"{m.annee:04d}-{m.mois:02d}"

                dep_famille = (
                    session.query(BudgetFamille.categorie, )
                    .filter(
                        extract("year", BudgetFamille.date) == m.annee,
                        extract("month", BudgetFamille.date) == m.mois,
                    )
                    .group_by(BudgetFamille.categorie)
                    .all()
                )
                for categorie, montant in dep_famille:
                    result[key][self._normaliser_categorie(categorie)] += float(montant or 0.0)

                dep_maison = (
                    session.query(DepenseMaison.categorie, func.sum(DepenseMaison.montant))
                    .filter(DepenseMaison.annee == m.annee, DepenseMaison.mois == m.mois)
                    .group_by(DepenseMaison.categorie)
                    .all()
                )
                for categorie, montant in dep_maison:
                    result[key][self._normaliser_categorie(categorie)] += float(montant or 0.0)

        return {k: dict(v) for k, v in result.items()}

    def xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_18(self, reference: date | None = None) -> dict[str, dict[str, float]]:
        """Collecte les montants par categorie normalisee sur mois courant, N-1, N-2."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)

        result: dict[str, dict[str, float]] = {
            f"{m.annee:04d}-{m.mois:02d}": defaultdict(float) for m in mois_refs
        }

        with obtenir_contexte_db() as session:
            from sqlalchemy import extract, func
            from src.core.models import BudgetFamille
            from src.core.models.finances import DepenseMaison

            for m in mois_refs:
                key = f"{m.annee:04d}-{m.mois:02d}"

                dep_famille = (
                    session.query(BudgetFamille.categorie, func.sum(None))
                    .filter(
                        extract("year", BudgetFamille.date) == m.annee,
                        extract("month", BudgetFamille.date) == m.mois,
                    )
                    .group_by(BudgetFamille.categorie)
                    .all()
                )
                for categorie, montant in dep_famille:
                    result[key][self._normaliser_categorie(categorie)] += float(montant or 0.0)

                dep_maison = (
                    session.query(DepenseMaison.categorie, func.sum(DepenseMaison.montant))
                    .filter(DepenseMaison.annee == m.annee, DepenseMaison.mois == m.mois)
                    .group_by(DepenseMaison.categorie)
                    .all()
                )
                for categorie, montant in dep_maison:
                    result[key][self._normaliser_categorie(categorie)] += float(montant or 0.0)

        return {k: dict(v) for k, v in result.items()}

    def xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_19(self, reference: date | None = None) -> dict[str, dict[str, float]]:
        """Collecte les montants par categorie normalisee sur mois courant, N-1, N-2."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)

        result: dict[str, dict[str, float]] = {
            f"{m.annee:04d}-{m.mois:02d}": defaultdict(float) for m in mois_refs
        }

        with obtenir_contexte_db() as session:
            from sqlalchemy import extract, func
            from src.core.models import BudgetFamille
            from src.core.models.finances import DepenseMaison

            for m in mois_refs:
                key = f"{m.annee:04d}-{m.mois:02d}"

                dep_famille = (
                    session.query(BudgetFamille.categorie, func.sum(BudgetFamille.montant))
                    .filter(
                        extract(None, BudgetFamille.date) == m.annee,
                        extract("month", BudgetFamille.date) == m.mois,
                    )
                    .group_by(BudgetFamille.categorie)
                    .all()
                )
                for categorie, montant in dep_famille:
                    result[key][self._normaliser_categorie(categorie)] += float(montant or 0.0)

                dep_maison = (
                    session.query(DepenseMaison.categorie, func.sum(DepenseMaison.montant))
                    .filter(DepenseMaison.annee == m.annee, DepenseMaison.mois == m.mois)
                    .group_by(DepenseMaison.categorie)
                    .all()
                )
                for categorie, montant in dep_maison:
                    result[key][self._normaliser_categorie(categorie)] += float(montant or 0.0)

        return {k: dict(v) for k, v in result.items()}

    def xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_20(self, reference: date | None = None) -> dict[str, dict[str, float]]:
        """Collecte les montants par categorie normalisee sur mois courant, N-1, N-2."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)

        result: dict[str, dict[str, float]] = {
            f"{m.annee:04d}-{m.mois:02d}": defaultdict(float) for m in mois_refs
        }

        with obtenir_contexte_db() as session:
            from sqlalchemy import extract, func
            from src.core.models import BudgetFamille
            from src.core.models.finances import DepenseMaison

            for m in mois_refs:
                key = f"{m.annee:04d}-{m.mois:02d}"

                dep_famille = (
                    session.query(BudgetFamille.categorie, func.sum(BudgetFamille.montant))
                    .filter(
                        extract("year", None) == m.annee,
                        extract("month", BudgetFamille.date) == m.mois,
                    )
                    .group_by(BudgetFamille.categorie)
                    .all()
                )
                for categorie, montant in dep_famille:
                    result[key][self._normaliser_categorie(categorie)] += float(montant or 0.0)

                dep_maison = (
                    session.query(DepenseMaison.categorie, func.sum(DepenseMaison.montant))
                    .filter(DepenseMaison.annee == m.annee, DepenseMaison.mois == m.mois)
                    .group_by(DepenseMaison.categorie)
                    .all()
                )
                for categorie, montant in dep_maison:
                    result[key][self._normaliser_categorie(categorie)] += float(montant or 0.0)

        return {k: dict(v) for k, v in result.items()}

    def xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_21(self, reference: date | None = None) -> dict[str, dict[str, float]]:
        """Collecte les montants par categorie normalisee sur mois courant, N-1, N-2."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)

        result: dict[str, dict[str, float]] = {
            f"{m.annee:04d}-{m.mois:02d}": defaultdict(float) for m in mois_refs
        }

        with obtenir_contexte_db() as session:
            from sqlalchemy import extract, func
            from src.core.models import BudgetFamille
            from src.core.models.finances import DepenseMaison

            for m in mois_refs:
                key = f"{m.annee:04d}-{m.mois:02d}"

                dep_famille = (
                    session.query(BudgetFamille.categorie, func.sum(BudgetFamille.montant))
                    .filter(
                        extract(BudgetFamille.date) == m.annee,
                        extract("month", BudgetFamille.date) == m.mois,
                    )
                    .group_by(BudgetFamille.categorie)
                    .all()
                )
                for categorie, montant in dep_famille:
                    result[key][self._normaliser_categorie(categorie)] += float(montant or 0.0)

                dep_maison = (
                    session.query(DepenseMaison.categorie, func.sum(DepenseMaison.montant))
                    .filter(DepenseMaison.annee == m.annee, DepenseMaison.mois == m.mois)
                    .group_by(DepenseMaison.categorie)
                    .all()
                )
                for categorie, montant in dep_maison:
                    result[key][self._normaliser_categorie(categorie)] += float(montant or 0.0)

        return {k: dict(v) for k, v in result.items()}

    def xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_22(self, reference: date | None = None) -> dict[str, dict[str, float]]:
        """Collecte les montants par categorie normalisee sur mois courant, N-1, N-2."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)

        result: dict[str, dict[str, float]] = {
            f"{m.annee:04d}-{m.mois:02d}": defaultdict(float) for m in mois_refs
        }

        with obtenir_contexte_db() as session:
            from sqlalchemy import extract, func
            from src.core.models import BudgetFamille
            from src.core.models.finances import DepenseMaison

            for m in mois_refs:
                key = f"{m.annee:04d}-{m.mois:02d}"

                dep_famille = (
                    session.query(BudgetFamille.categorie, func.sum(BudgetFamille.montant))
                    .filter(
                        extract("year", ) == m.annee,
                        extract("month", BudgetFamille.date) == m.mois,
                    )
                    .group_by(BudgetFamille.categorie)
                    .all()
                )
                for categorie, montant in dep_famille:
                    result[key][self._normaliser_categorie(categorie)] += float(montant or 0.0)

                dep_maison = (
                    session.query(DepenseMaison.categorie, func.sum(DepenseMaison.montant))
                    .filter(DepenseMaison.annee == m.annee, DepenseMaison.mois == m.mois)
                    .group_by(DepenseMaison.categorie)
                    .all()
                )
                for categorie, montant in dep_maison:
                    result[key][self._normaliser_categorie(categorie)] += float(montant or 0.0)

        return {k: dict(v) for k, v in result.items()}

    def xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_23(self, reference: date | None = None) -> dict[str, dict[str, float]]:
        """Collecte les montants par categorie normalisee sur mois courant, N-1, N-2."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)

        result: dict[str, dict[str, float]] = {
            f"{m.annee:04d}-{m.mois:02d}": defaultdict(float) for m in mois_refs
        }

        with obtenir_contexte_db() as session:
            from sqlalchemy import extract, func
            from src.core.models import BudgetFamille
            from src.core.models.finances import DepenseMaison

            for m in mois_refs:
                key = f"{m.annee:04d}-{m.mois:02d}"

                dep_famille = (
                    session.query(BudgetFamille.categorie, func.sum(BudgetFamille.montant))
                    .filter(
                        extract("XXyearXX", BudgetFamille.date) == m.annee,
                        extract("month", BudgetFamille.date) == m.mois,
                    )
                    .group_by(BudgetFamille.categorie)
                    .all()
                )
                for categorie, montant in dep_famille:
                    result[key][self._normaliser_categorie(categorie)] += float(montant or 0.0)

                dep_maison = (
                    session.query(DepenseMaison.categorie, func.sum(DepenseMaison.montant))
                    .filter(DepenseMaison.annee == m.annee, DepenseMaison.mois == m.mois)
                    .group_by(DepenseMaison.categorie)
                    .all()
                )
                for categorie, montant in dep_maison:
                    result[key][self._normaliser_categorie(categorie)] += float(montant or 0.0)

        return {k: dict(v) for k, v in result.items()}

    def xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_24(self, reference: date | None = None) -> dict[str, dict[str, float]]:
        """Collecte les montants par categorie normalisee sur mois courant, N-1, N-2."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)

        result: dict[str, dict[str, float]] = {
            f"{m.annee:04d}-{m.mois:02d}": defaultdict(float) for m in mois_refs
        }

        with obtenir_contexte_db() as session:
            from sqlalchemy import extract, func
            from src.core.models import BudgetFamille
            from src.core.models.finances import DepenseMaison

            for m in mois_refs:
                key = f"{m.annee:04d}-{m.mois:02d}"

                dep_famille = (
                    session.query(BudgetFamille.categorie, func.sum(BudgetFamille.montant))
                    .filter(
                        extract("YEAR", BudgetFamille.date) == m.annee,
                        extract("month", BudgetFamille.date) == m.mois,
                    )
                    .group_by(BudgetFamille.categorie)
                    .all()
                )
                for categorie, montant in dep_famille:
                    result[key][self._normaliser_categorie(categorie)] += float(montant or 0.0)

                dep_maison = (
                    session.query(DepenseMaison.categorie, func.sum(DepenseMaison.montant))
                    .filter(DepenseMaison.annee == m.annee, DepenseMaison.mois == m.mois)
                    .group_by(DepenseMaison.categorie)
                    .all()
                )
                for categorie, montant in dep_maison:
                    result[key][self._normaliser_categorie(categorie)] += float(montant or 0.0)

        return {k: dict(v) for k, v in result.items()}

    def xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_25(self, reference: date | None = None) -> dict[str, dict[str, float]]:
        """Collecte les montants par categorie normalisee sur mois courant, N-1, N-2."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)

        result: dict[str, dict[str, float]] = {
            f"{m.annee:04d}-{m.mois:02d}": defaultdict(float) for m in mois_refs
        }

        with obtenir_contexte_db() as session:
            from sqlalchemy import extract, func
            from src.core.models import BudgetFamille
            from src.core.models.finances import DepenseMaison

            for m in mois_refs:
                key = f"{m.annee:04d}-{m.mois:02d}"

                dep_famille = (
                    session.query(BudgetFamille.categorie, func.sum(BudgetFamille.montant))
                    .filter(
                        extract("year", BudgetFamille.date) != m.annee,
                        extract("month", BudgetFamille.date) == m.mois,
                    )
                    .group_by(BudgetFamille.categorie)
                    .all()
                )
                for categorie, montant in dep_famille:
                    result[key][self._normaliser_categorie(categorie)] += float(montant or 0.0)

                dep_maison = (
                    session.query(DepenseMaison.categorie, func.sum(DepenseMaison.montant))
                    .filter(DepenseMaison.annee == m.annee, DepenseMaison.mois == m.mois)
                    .group_by(DepenseMaison.categorie)
                    .all()
                )
                for categorie, montant in dep_maison:
                    result[key][self._normaliser_categorie(categorie)] += float(montant or 0.0)

        return {k: dict(v) for k, v in result.items()}

    def xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_26(self, reference: date | None = None) -> dict[str, dict[str, float]]:
        """Collecte les montants par categorie normalisee sur mois courant, N-1, N-2."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)

        result: dict[str, dict[str, float]] = {
            f"{m.annee:04d}-{m.mois:02d}": defaultdict(float) for m in mois_refs
        }

        with obtenir_contexte_db() as session:
            from sqlalchemy import extract, func
            from src.core.models import BudgetFamille
            from src.core.models.finances import DepenseMaison

            for m in mois_refs:
                key = f"{m.annee:04d}-{m.mois:02d}"

                dep_famille = (
                    session.query(BudgetFamille.categorie, func.sum(BudgetFamille.montant))
                    .filter(
                        extract("year", BudgetFamille.date) == m.annee,
                        extract(None, BudgetFamille.date) == m.mois,
                    )
                    .group_by(BudgetFamille.categorie)
                    .all()
                )
                for categorie, montant in dep_famille:
                    result[key][self._normaliser_categorie(categorie)] += float(montant or 0.0)

                dep_maison = (
                    session.query(DepenseMaison.categorie, func.sum(DepenseMaison.montant))
                    .filter(DepenseMaison.annee == m.annee, DepenseMaison.mois == m.mois)
                    .group_by(DepenseMaison.categorie)
                    .all()
                )
                for categorie, montant in dep_maison:
                    result[key][self._normaliser_categorie(categorie)] += float(montant or 0.0)

        return {k: dict(v) for k, v in result.items()}

    def xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_27(self, reference: date | None = None) -> dict[str, dict[str, float]]:
        """Collecte les montants par categorie normalisee sur mois courant, N-1, N-2."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)

        result: dict[str, dict[str, float]] = {
            f"{m.annee:04d}-{m.mois:02d}": defaultdict(float) for m in mois_refs
        }

        with obtenir_contexte_db() as session:
            from sqlalchemy import extract, func
            from src.core.models import BudgetFamille
            from src.core.models.finances import DepenseMaison

            for m in mois_refs:
                key = f"{m.annee:04d}-{m.mois:02d}"

                dep_famille = (
                    session.query(BudgetFamille.categorie, func.sum(BudgetFamille.montant))
                    .filter(
                        extract("year", BudgetFamille.date) == m.annee,
                        extract("month", None) == m.mois,
                    )
                    .group_by(BudgetFamille.categorie)
                    .all()
                )
                for categorie, montant in dep_famille:
                    result[key][self._normaliser_categorie(categorie)] += float(montant or 0.0)

                dep_maison = (
                    session.query(DepenseMaison.categorie, func.sum(DepenseMaison.montant))
                    .filter(DepenseMaison.annee == m.annee, DepenseMaison.mois == m.mois)
                    .group_by(DepenseMaison.categorie)
                    .all()
                )
                for categorie, montant in dep_maison:
                    result[key][self._normaliser_categorie(categorie)] += float(montant or 0.0)

        return {k: dict(v) for k, v in result.items()}

    def xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_28(self, reference: date | None = None) -> dict[str, dict[str, float]]:
        """Collecte les montants par categorie normalisee sur mois courant, N-1, N-2."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)

        result: dict[str, dict[str, float]] = {
            f"{m.annee:04d}-{m.mois:02d}": defaultdict(float) for m in mois_refs
        }

        with obtenir_contexte_db() as session:
            from sqlalchemy import extract, func
            from src.core.models import BudgetFamille
            from src.core.models.finances import DepenseMaison

            for m in mois_refs:
                key = f"{m.annee:04d}-{m.mois:02d}"

                dep_famille = (
                    session.query(BudgetFamille.categorie, func.sum(BudgetFamille.montant))
                    .filter(
                        extract("year", BudgetFamille.date) == m.annee,
                        extract(BudgetFamille.date) == m.mois,
                    )
                    .group_by(BudgetFamille.categorie)
                    .all()
                )
                for categorie, montant in dep_famille:
                    result[key][self._normaliser_categorie(categorie)] += float(montant or 0.0)

                dep_maison = (
                    session.query(DepenseMaison.categorie, func.sum(DepenseMaison.montant))
                    .filter(DepenseMaison.annee == m.annee, DepenseMaison.mois == m.mois)
                    .group_by(DepenseMaison.categorie)
                    .all()
                )
                for categorie, montant in dep_maison:
                    result[key][self._normaliser_categorie(categorie)] += float(montant or 0.0)

        return {k: dict(v) for k, v in result.items()}

    def xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_29(self, reference: date | None = None) -> dict[str, dict[str, float]]:
        """Collecte les montants par categorie normalisee sur mois courant, N-1, N-2."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)

        result: dict[str, dict[str, float]] = {
            f"{m.annee:04d}-{m.mois:02d}": defaultdict(float) for m in mois_refs
        }

        with obtenir_contexte_db() as session:
            from sqlalchemy import extract, func
            from src.core.models import BudgetFamille
            from src.core.models.finances import DepenseMaison

            for m in mois_refs:
                key = f"{m.annee:04d}-{m.mois:02d}"

                dep_famille = (
                    session.query(BudgetFamille.categorie, func.sum(BudgetFamille.montant))
                    .filter(
                        extract("year", BudgetFamille.date) == m.annee,
                        extract("month", ) == m.mois,
                    )
                    .group_by(BudgetFamille.categorie)
                    .all()
                )
                for categorie, montant in dep_famille:
                    result[key][self._normaliser_categorie(categorie)] += float(montant or 0.0)

                dep_maison = (
                    session.query(DepenseMaison.categorie, func.sum(DepenseMaison.montant))
                    .filter(DepenseMaison.annee == m.annee, DepenseMaison.mois == m.mois)
                    .group_by(DepenseMaison.categorie)
                    .all()
                )
                for categorie, montant in dep_maison:
                    result[key][self._normaliser_categorie(categorie)] += float(montant or 0.0)

        return {k: dict(v) for k, v in result.items()}

    def xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_30(self, reference: date | None = None) -> dict[str, dict[str, float]]:
        """Collecte les montants par categorie normalisee sur mois courant, N-1, N-2."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)

        result: dict[str, dict[str, float]] = {
            f"{m.annee:04d}-{m.mois:02d}": defaultdict(float) for m in mois_refs
        }

        with obtenir_contexte_db() as session:
            from sqlalchemy import extract, func
            from src.core.models import BudgetFamille
            from src.core.models.finances import DepenseMaison

            for m in mois_refs:
                key = f"{m.annee:04d}-{m.mois:02d}"

                dep_famille = (
                    session.query(BudgetFamille.categorie, func.sum(BudgetFamille.montant))
                    .filter(
                        extract("year", BudgetFamille.date) == m.annee,
                        extract("XXmonthXX", BudgetFamille.date) == m.mois,
                    )
                    .group_by(BudgetFamille.categorie)
                    .all()
                )
                for categorie, montant in dep_famille:
                    result[key][self._normaliser_categorie(categorie)] += float(montant or 0.0)

                dep_maison = (
                    session.query(DepenseMaison.categorie, func.sum(DepenseMaison.montant))
                    .filter(DepenseMaison.annee == m.annee, DepenseMaison.mois == m.mois)
                    .group_by(DepenseMaison.categorie)
                    .all()
                )
                for categorie, montant in dep_maison:
                    result[key][self._normaliser_categorie(categorie)] += float(montant or 0.0)

        return {k: dict(v) for k, v in result.items()}

    def xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_31(self, reference: date | None = None) -> dict[str, dict[str, float]]:
        """Collecte les montants par categorie normalisee sur mois courant, N-1, N-2."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)

        result: dict[str, dict[str, float]] = {
            f"{m.annee:04d}-{m.mois:02d}": defaultdict(float) for m in mois_refs
        }

        with obtenir_contexte_db() as session:
            from sqlalchemy import extract, func
            from src.core.models import BudgetFamille
            from src.core.models.finances import DepenseMaison

            for m in mois_refs:
                key = f"{m.annee:04d}-{m.mois:02d}"

                dep_famille = (
                    session.query(BudgetFamille.categorie, func.sum(BudgetFamille.montant))
                    .filter(
                        extract("year", BudgetFamille.date) == m.annee,
                        extract("MONTH", BudgetFamille.date) == m.mois,
                    )
                    .group_by(BudgetFamille.categorie)
                    .all()
                )
                for categorie, montant in dep_famille:
                    result[key][self._normaliser_categorie(categorie)] += float(montant or 0.0)

                dep_maison = (
                    session.query(DepenseMaison.categorie, func.sum(DepenseMaison.montant))
                    .filter(DepenseMaison.annee == m.annee, DepenseMaison.mois == m.mois)
                    .group_by(DepenseMaison.categorie)
                    .all()
                )
                for categorie, montant in dep_maison:
                    result[key][self._normaliser_categorie(categorie)] += float(montant or 0.0)

        return {k: dict(v) for k, v in result.items()}

    def xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_32(self, reference: date | None = None) -> dict[str, dict[str, float]]:
        """Collecte les montants par categorie normalisee sur mois courant, N-1, N-2."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)

        result: dict[str, dict[str, float]] = {
            f"{m.annee:04d}-{m.mois:02d}": defaultdict(float) for m in mois_refs
        }

        with obtenir_contexte_db() as session:
            from sqlalchemy import extract, func
            from src.core.models import BudgetFamille
            from src.core.models.finances import DepenseMaison

            for m in mois_refs:
                key = f"{m.annee:04d}-{m.mois:02d}"

                dep_famille = (
                    session.query(BudgetFamille.categorie, func.sum(BudgetFamille.montant))
                    .filter(
                        extract("year", BudgetFamille.date) == m.annee,
                        extract("month", BudgetFamille.date) != m.mois,
                    )
                    .group_by(BudgetFamille.categorie)
                    .all()
                )
                for categorie, montant in dep_famille:
                    result[key][self._normaliser_categorie(categorie)] += float(montant or 0.0)

                dep_maison = (
                    session.query(DepenseMaison.categorie, func.sum(DepenseMaison.montant))
                    .filter(DepenseMaison.annee == m.annee, DepenseMaison.mois == m.mois)
                    .group_by(DepenseMaison.categorie)
                    .all()
                )
                for categorie, montant in dep_maison:
                    result[key][self._normaliser_categorie(categorie)] += float(montant or 0.0)

        return {k: dict(v) for k, v in result.items()}

    def xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_33(self, reference: date | None = None) -> dict[str, dict[str, float]]:
        """Collecte les montants par categorie normalisee sur mois courant, N-1, N-2."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)

        result: dict[str, dict[str, float]] = {
            f"{m.annee:04d}-{m.mois:02d}": defaultdict(float) for m in mois_refs
        }

        with obtenir_contexte_db() as session:
            from sqlalchemy import extract, func
            from src.core.models import BudgetFamille
            from src.core.models.finances import DepenseMaison

            for m in mois_refs:
                key = f"{m.annee:04d}-{m.mois:02d}"

                dep_famille = (
                    session.query(BudgetFamille.categorie, func.sum(BudgetFamille.montant))
                    .filter(
                        extract("year", BudgetFamille.date) == m.annee,
                        extract("month", BudgetFamille.date) == m.mois,
                    )
                    .group_by(BudgetFamille.categorie)
                    .all()
                )
                for categorie, montant in dep_famille:
                    result[key][self._normaliser_categorie(categorie)] = float(montant or 0.0)

                dep_maison = (
                    session.query(DepenseMaison.categorie, func.sum(DepenseMaison.montant))
                    .filter(DepenseMaison.annee == m.annee, DepenseMaison.mois == m.mois)
                    .group_by(DepenseMaison.categorie)
                    .all()
                )
                for categorie, montant in dep_maison:
                    result[key][self._normaliser_categorie(categorie)] += float(montant or 0.0)

        return {k: dict(v) for k, v in result.items()}

    def xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_34(self, reference: date | None = None) -> dict[str, dict[str, float]]:
        """Collecte les montants par categorie normalisee sur mois courant, N-1, N-2."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)

        result: dict[str, dict[str, float]] = {
            f"{m.annee:04d}-{m.mois:02d}": defaultdict(float) for m in mois_refs
        }

        with obtenir_contexte_db() as session:
            from sqlalchemy import extract, func
            from src.core.models import BudgetFamille
            from src.core.models.finances import DepenseMaison

            for m in mois_refs:
                key = f"{m.annee:04d}-{m.mois:02d}"

                dep_famille = (
                    session.query(BudgetFamille.categorie, func.sum(BudgetFamille.montant))
                    .filter(
                        extract("year", BudgetFamille.date) == m.annee,
                        extract("month", BudgetFamille.date) == m.mois,
                    )
                    .group_by(BudgetFamille.categorie)
                    .all()
                )
                for categorie, montant in dep_famille:
                    result[key][self._normaliser_categorie(categorie)] -= float(montant or 0.0)

                dep_maison = (
                    session.query(DepenseMaison.categorie, func.sum(DepenseMaison.montant))
                    .filter(DepenseMaison.annee == m.annee, DepenseMaison.mois == m.mois)
                    .group_by(DepenseMaison.categorie)
                    .all()
                )
                for categorie, montant in dep_maison:
                    result[key][self._normaliser_categorie(categorie)] += float(montant or 0.0)

        return {k: dict(v) for k, v in result.items()}

    def xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_35(self, reference: date | None = None) -> dict[str, dict[str, float]]:
        """Collecte les montants par categorie normalisee sur mois courant, N-1, N-2."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)

        result: dict[str, dict[str, float]] = {
            f"{m.annee:04d}-{m.mois:02d}": defaultdict(float) for m in mois_refs
        }

        with obtenir_contexte_db() as session:
            from sqlalchemy import extract, func
            from src.core.models import BudgetFamille
            from src.core.models.finances import DepenseMaison

            for m in mois_refs:
                key = f"{m.annee:04d}-{m.mois:02d}"

                dep_famille = (
                    session.query(BudgetFamille.categorie, func.sum(BudgetFamille.montant))
                    .filter(
                        extract("year", BudgetFamille.date) == m.annee,
                        extract("month", BudgetFamille.date) == m.mois,
                    )
                    .group_by(BudgetFamille.categorie)
                    .all()
                )
                for categorie, montant in dep_famille:
                    result[key][self._normaliser_categorie(None)] += float(montant or 0.0)

                dep_maison = (
                    session.query(DepenseMaison.categorie, func.sum(DepenseMaison.montant))
                    .filter(DepenseMaison.annee == m.annee, DepenseMaison.mois == m.mois)
                    .group_by(DepenseMaison.categorie)
                    .all()
                )
                for categorie, montant in dep_maison:
                    result[key][self._normaliser_categorie(categorie)] += float(montant or 0.0)

        return {k: dict(v) for k, v in result.items()}

    def xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_36(self, reference: date | None = None) -> dict[str, dict[str, float]]:
        """Collecte les montants par categorie normalisee sur mois courant, N-1, N-2."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)

        result: dict[str, dict[str, float]] = {
            f"{m.annee:04d}-{m.mois:02d}": defaultdict(float) for m in mois_refs
        }

        with obtenir_contexte_db() as session:
            from sqlalchemy import extract, func
            from src.core.models import BudgetFamille
            from src.core.models.finances import DepenseMaison

            for m in mois_refs:
                key = f"{m.annee:04d}-{m.mois:02d}"

                dep_famille = (
                    session.query(BudgetFamille.categorie, func.sum(BudgetFamille.montant))
                    .filter(
                        extract("year", BudgetFamille.date) == m.annee,
                        extract("month", BudgetFamille.date) == m.mois,
                    )
                    .group_by(BudgetFamille.categorie)
                    .all()
                )
                for categorie, montant in dep_famille:
                    result[key][self._normaliser_categorie(categorie)] += float(None)

                dep_maison = (
                    session.query(DepenseMaison.categorie, func.sum(DepenseMaison.montant))
                    .filter(DepenseMaison.annee == m.annee, DepenseMaison.mois == m.mois)
                    .group_by(DepenseMaison.categorie)
                    .all()
                )
                for categorie, montant in dep_maison:
                    result[key][self._normaliser_categorie(categorie)] += float(montant or 0.0)

        return {k: dict(v) for k, v in result.items()}

    def xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_37(self, reference: date | None = None) -> dict[str, dict[str, float]]:
        """Collecte les montants par categorie normalisee sur mois courant, N-1, N-2."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)

        result: dict[str, dict[str, float]] = {
            f"{m.annee:04d}-{m.mois:02d}": defaultdict(float) for m in mois_refs
        }

        with obtenir_contexte_db() as session:
            from sqlalchemy import extract, func
            from src.core.models import BudgetFamille
            from src.core.models.finances import DepenseMaison

            for m in mois_refs:
                key = f"{m.annee:04d}-{m.mois:02d}"

                dep_famille = (
                    session.query(BudgetFamille.categorie, func.sum(BudgetFamille.montant))
                    .filter(
                        extract("year", BudgetFamille.date) == m.annee,
                        extract("month", BudgetFamille.date) == m.mois,
                    )
                    .group_by(BudgetFamille.categorie)
                    .all()
                )
                for categorie, montant in dep_famille:
                    result[key][self._normaliser_categorie(categorie)] += float(montant and 0.0)

                dep_maison = (
                    session.query(DepenseMaison.categorie, func.sum(DepenseMaison.montant))
                    .filter(DepenseMaison.annee == m.annee, DepenseMaison.mois == m.mois)
                    .group_by(DepenseMaison.categorie)
                    .all()
                )
                for categorie, montant in dep_maison:
                    result[key][self._normaliser_categorie(categorie)] += float(montant or 0.0)

        return {k: dict(v) for k, v in result.items()}

    def xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_38(self, reference: date | None = None) -> dict[str, dict[str, float]]:
        """Collecte les montants par categorie normalisee sur mois courant, N-1, N-2."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)

        result: dict[str, dict[str, float]] = {
            f"{m.annee:04d}-{m.mois:02d}": defaultdict(float) for m in mois_refs
        }

        with obtenir_contexte_db() as session:
            from sqlalchemy import extract, func
            from src.core.models import BudgetFamille
            from src.core.models.finances import DepenseMaison

            for m in mois_refs:
                key = f"{m.annee:04d}-{m.mois:02d}"

                dep_famille = (
                    session.query(BudgetFamille.categorie, func.sum(BudgetFamille.montant))
                    .filter(
                        extract("year", BudgetFamille.date) == m.annee,
                        extract("month", BudgetFamille.date) == m.mois,
                    )
                    .group_by(BudgetFamille.categorie)
                    .all()
                )
                for categorie, montant in dep_famille:
                    result[key][self._normaliser_categorie(categorie)] += float(montant or 1.0)

                dep_maison = (
                    session.query(DepenseMaison.categorie, func.sum(DepenseMaison.montant))
                    .filter(DepenseMaison.annee == m.annee, DepenseMaison.mois == m.mois)
                    .group_by(DepenseMaison.categorie)
                    .all()
                )
                for categorie, montant in dep_maison:
                    result[key][self._normaliser_categorie(categorie)] += float(montant or 0.0)

        return {k: dict(v) for k, v in result.items()}

    def xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_39(self, reference: date | None = None) -> dict[str, dict[str, float]]:
        """Collecte les montants par categorie normalisee sur mois courant, N-1, N-2."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)

        result: dict[str, dict[str, float]] = {
            f"{m.annee:04d}-{m.mois:02d}": defaultdict(float) for m in mois_refs
        }

        with obtenir_contexte_db() as session:
            from sqlalchemy import extract, func
            from src.core.models import BudgetFamille
            from src.core.models.finances import DepenseMaison

            for m in mois_refs:
                key = f"{m.annee:04d}-{m.mois:02d}"

                dep_famille = (
                    session.query(BudgetFamille.categorie, func.sum(BudgetFamille.montant))
                    .filter(
                        extract("year", BudgetFamille.date) == m.annee,
                        extract("month", BudgetFamille.date) == m.mois,
                    )
                    .group_by(BudgetFamille.categorie)
                    .all()
                )
                for categorie, montant in dep_famille:
                    result[key][self._normaliser_categorie(categorie)] += float(montant or 0.0)

                dep_maison = None
                for categorie, montant in dep_maison:
                    result[key][self._normaliser_categorie(categorie)] += float(montant or 0.0)

        return {k: dict(v) for k, v in result.items()}

    def xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_40(self, reference: date | None = None) -> dict[str, dict[str, float]]:
        """Collecte les montants par categorie normalisee sur mois courant, N-1, N-2."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)

        result: dict[str, dict[str, float]] = {
            f"{m.annee:04d}-{m.mois:02d}": defaultdict(float) for m in mois_refs
        }

        with obtenir_contexte_db() as session:
            from sqlalchemy import extract, func
            from src.core.models import BudgetFamille
            from src.core.models.finances import DepenseMaison

            for m in mois_refs:
                key = f"{m.annee:04d}-{m.mois:02d}"

                dep_famille = (
                    session.query(BudgetFamille.categorie, func.sum(BudgetFamille.montant))
                    .filter(
                        extract("year", BudgetFamille.date) == m.annee,
                        extract("month", BudgetFamille.date) == m.mois,
                    )
                    .group_by(BudgetFamille.categorie)
                    .all()
                )
                for categorie, montant in dep_famille:
                    result[key][self._normaliser_categorie(categorie)] += float(montant or 0.0)

                dep_maison = (
                    session.query(DepenseMaison.categorie, func.sum(DepenseMaison.montant))
                    .filter(DepenseMaison.annee == m.annee, DepenseMaison.mois == m.mois)
                    .group_by(None)
                    .all()
                )
                for categorie, montant in dep_maison:
                    result[key][self._normaliser_categorie(categorie)] += float(montant or 0.0)

        return {k: dict(v) for k, v in result.items()}

    def xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_41(self, reference: date | None = None) -> dict[str, dict[str, float]]:
        """Collecte les montants par categorie normalisee sur mois courant, N-1, N-2."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)

        result: dict[str, dict[str, float]] = {
            f"{m.annee:04d}-{m.mois:02d}": defaultdict(float) for m in mois_refs
        }

        with obtenir_contexte_db() as session:
            from sqlalchemy import extract, func
            from src.core.models import BudgetFamille
            from src.core.models.finances import DepenseMaison

            for m in mois_refs:
                key = f"{m.annee:04d}-{m.mois:02d}"

                dep_famille = (
                    session.query(BudgetFamille.categorie, func.sum(BudgetFamille.montant))
                    .filter(
                        extract("year", BudgetFamille.date) == m.annee,
                        extract("month", BudgetFamille.date) == m.mois,
                    )
                    .group_by(BudgetFamille.categorie)
                    .all()
                )
                for categorie, montant in dep_famille:
                    result[key][self._normaliser_categorie(categorie)] += float(montant or 0.0)

                dep_maison = (
                    session.query(DepenseMaison.categorie, func.sum(DepenseMaison.montant))
                    .filter(None, DepenseMaison.mois == m.mois)
                    .group_by(DepenseMaison.categorie)
                    .all()
                )
                for categorie, montant in dep_maison:
                    result[key][self._normaliser_categorie(categorie)] += float(montant or 0.0)

        return {k: dict(v) for k, v in result.items()}

    def xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_42(self, reference: date | None = None) -> dict[str, dict[str, float]]:
        """Collecte les montants par categorie normalisee sur mois courant, N-1, N-2."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)

        result: dict[str, dict[str, float]] = {
            f"{m.annee:04d}-{m.mois:02d}": defaultdict(float) for m in mois_refs
        }

        with obtenir_contexte_db() as session:
            from sqlalchemy import extract, func
            from src.core.models import BudgetFamille
            from src.core.models.finances import DepenseMaison

            for m in mois_refs:
                key = f"{m.annee:04d}-{m.mois:02d}"

                dep_famille = (
                    session.query(BudgetFamille.categorie, func.sum(BudgetFamille.montant))
                    .filter(
                        extract("year", BudgetFamille.date) == m.annee,
                        extract("month", BudgetFamille.date) == m.mois,
                    )
                    .group_by(BudgetFamille.categorie)
                    .all()
                )
                for categorie, montant in dep_famille:
                    result[key][self._normaliser_categorie(categorie)] += float(montant or 0.0)

                dep_maison = (
                    session.query(DepenseMaison.categorie, func.sum(DepenseMaison.montant))
                    .filter(DepenseMaison.annee == m.annee, None)
                    .group_by(DepenseMaison.categorie)
                    .all()
                )
                for categorie, montant in dep_maison:
                    result[key][self._normaliser_categorie(categorie)] += float(montant or 0.0)

        return {k: dict(v) for k, v in result.items()}

    def xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_43(self, reference: date | None = None) -> dict[str, dict[str, float]]:
        """Collecte les montants par categorie normalisee sur mois courant, N-1, N-2."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)

        result: dict[str, dict[str, float]] = {
            f"{m.annee:04d}-{m.mois:02d}": defaultdict(float) for m in mois_refs
        }

        with obtenir_contexte_db() as session:
            from sqlalchemy import extract, func
            from src.core.models import BudgetFamille
            from src.core.models.finances import DepenseMaison

            for m in mois_refs:
                key = f"{m.annee:04d}-{m.mois:02d}"

                dep_famille = (
                    session.query(BudgetFamille.categorie, func.sum(BudgetFamille.montant))
                    .filter(
                        extract("year", BudgetFamille.date) == m.annee,
                        extract("month", BudgetFamille.date) == m.mois,
                    )
                    .group_by(BudgetFamille.categorie)
                    .all()
                )
                for categorie, montant in dep_famille:
                    result[key][self._normaliser_categorie(categorie)] += float(montant or 0.0)

                dep_maison = (
                    session.query(DepenseMaison.categorie, func.sum(DepenseMaison.montant))
                    .filter(DepenseMaison.mois == m.mois)
                    .group_by(DepenseMaison.categorie)
                    .all()
                )
                for categorie, montant in dep_maison:
                    result[key][self._normaliser_categorie(categorie)] += float(montant or 0.0)

        return {k: dict(v) for k, v in result.items()}

    def xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_44(self, reference: date | None = None) -> dict[str, dict[str, float]]:
        """Collecte les montants par categorie normalisee sur mois courant, N-1, N-2."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)

        result: dict[str, dict[str, float]] = {
            f"{m.annee:04d}-{m.mois:02d}": defaultdict(float) for m in mois_refs
        }

        with obtenir_contexte_db() as session:
            from sqlalchemy import extract, func
            from src.core.models import BudgetFamille
            from src.core.models.finances import DepenseMaison

            for m in mois_refs:
                key = f"{m.annee:04d}-{m.mois:02d}"

                dep_famille = (
                    session.query(BudgetFamille.categorie, func.sum(BudgetFamille.montant))
                    .filter(
                        extract("year", BudgetFamille.date) == m.annee,
                        extract("month", BudgetFamille.date) == m.mois,
                    )
                    .group_by(BudgetFamille.categorie)
                    .all()
                )
                for categorie, montant in dep_famille:
                    result[key][self._normaliser_categorie(categorie)] += float(montant or 0.0)

                dep_maison = (
                    session.query(DepenseMaison.categorie, func.sum(DepenseMaison.montant))
                    .filter(DepenseMaison.annee == m.annee, )
                    .group_by(DepenseMaison.categorie)
                    .all()
                )
                for categorie, montant in dep_maison:
                    result[key][self._normaliser_categorie(categorie)] += float(montant or 0.0)

        return {k: dict(v) for k, v in result.items()}

    def xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_45(self, reference: date | None = None) -> dict[str, dict[str, float]]:
        """Collecte les montants par categorie normalisee sur mois courant, N-1, N-2."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)

        result: dict[str, dict[str, float]] = {
            f"{m.annee:04d}-{m.mois:02d}": defaultdict(float) for m in mois_refs
        }

        with obtenir_contexte_db() as session:
            from sqlalchemy import extract, func
            from src.core.models import BudgetFamille
            from src.core.models.finances import DepenseMaison

            for m in mois_refs:
                key = f"{m.annee:04d}-{m.mois:02d}"

                dep_famille = (
                    session.query(BudgetFamille.categorie, func.sum(BudgetFamille.montant))
                    .filter(
                        extract("year", BudgetFamille.date) == m.annee,
                        extract("month", BudgetFamille.date) == m.mois,
                    )
                    .group_by(BudgetFamille.categorie)
                    .all()
                )
                for categorie, montant in dep_famille:
                    result[key][self._normaliser_categorie(categorie)] += float(montant or 0.0)

                dep_maison = (
                    session.query(None, func.sum(DepenseMaison.montant))
                    .filter(DepenseMaison.annee == m.annee, DepenseMaison.mois == m.mois)
                    .group_by(DepenseMaison.categorie)
                    .all()
                )
                for categorie, montant in dep_maison:
                    result[key][self._normaliser_categorie(categorie)] += float(montant or 0.0)

        return {k: dict(v) for k, v in result.items()}

    def xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_46(self, reference: date | None = None) -> dict[str, dict[str, float]]:
        """Collecte les montants par categorie normalisee sur mois courant, N-1, N-2."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)

        result: dict[str, dict[str, float]] = {
            f"{m.annee:04d}-{m.mois:02d}": defaultdict(float) for m in mois_refs
        }

        with obtenir_contexte_db() as session:
            from sqlalchemy import extract, func
            from src.core.models import BudgetFamille
            from src.core.models.finances import DepenseMaison

            for m in mois_refs:
                key = f"{m.annee:04d}-{m.mois:02d}"

                dep_famille = (
                    session.query(BudgetFamille.categorie, func.sum(BudgetFamille.montant))
                    .filter(
                        extract("year", BudgetFamille.date) == m.annee,
                        extract("month", BudgetFamille.date) == m.mois,
                    )
                    .group_by(BudgetFamille.categorie)
                    .all()
                )
                for categorie, montant in dep_famille:
                    result[key][self._normaliser_categorie(categorie)] += float(montant or 0.0)

                dep_maison = (
                    session.query(DepenseMaison.categorie, None)
                    .filter(DepenseMaison.annee == m.annee, DepenseMaison.mois == m.mois)
                    .group_by(DepenseMaison.categorie)
                    .all()
                )
                for categorie, montant in dep_maison:
                    result[key][self._normaliser_categorie(categorie)] += float(montant or 0.0)

        return {k: dict(v) for k, v in result.items()}

    def xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_47(self, reference: date | None = None) -> dict[str, dict[str, float]]:
        """Collecte les montants par categorie normalisee sur mois courant, N-1, N-2."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)

        result: dict[str, dict[str, float]] = {
            f"{m.annee:04d}-{m.mois:02d}": defaultdict(float) for m in mois_refs
        }

        with obtenir_contexte_db() as session:
            from sqlalchemy import extract, func
            from src.core.models import BudgetFamille
            from src.core.models.finances import DepenseMaison

            for m in mois_refs:
                key = f"{m.annee:04d}-{m.mois:02d}"

                dep_famille = (
                    session.query(BudgetFamille.categorie, func.sum(BudgetFamille.montant))
                    .filter(
                        extract("year", BudgetFamille.date) == m.annee,
                        extract("month", BudgetFamille.date) == m.mois,
                    )
                    .group_by(BudgetFamille.categorie)
                    .all()
                )
                for categorie, montant in dep_famille:
                    result[key][self._normaliser_categorie(categorie)] += float(montant or 0.0)

                dep_maison = (
                    session.query(func.sum(DepenseMaison.montant))
                    .filter(DepenseMaison.annee == m.annee, DepenseMaison.mois == m.mois)
                    .group_by(DepenseMaison.categorie)
                    .all()
                )
                for categorie, montant in dep_maison:
                    result[key][self._normaliser_categorie(categorie)] += float(montant or 0.0)

        return {k: dict(v) for k, v in result.items()}

    def xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_48(self, reference: date | None = None) -> dict[str, dict[str, float]]:
        """Collecte les montants par categorie normalisee sur mois courant, N-1, N-2."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)

        result: dict[str, dict[str, float]] = {
            f"{m.annee:04d}-{m.mois:02d}": defaultdict(float) for m in mois_refs
        }

        with obtenir_contexte_db() as session:
            from sqlalchemy import extract, func
            from src.core.models import BudgetFamille
            from src.core.models.finances import DepenseMaison

            for m in mois_refs:
                key = f"{m.annee:04d}-{m.mois:02d}"

                dep_famille = (
                    session.query(BudgetFamille.categorie, func.sum(BudgetFamille.montant))
                    .filter(
                        extract("year", BudgetFamille.date) == m.annee,
                        extract("month", BudgetFamille.date) == m.mois,
                    )
                    .group_by(BudgetFamille.categorie)
                    .all()
                )
                for categorie, montant in dep_famille:
                    result[key][self._normaliser_categorie(categorie)] += float(montant or 0.0)

                dep_maison = (
                    session.query(DepenseMaison.categorie, )
                    .filter(DepenseMaison.annee == m.annee, DepenseMaison.mois == m.mois)
                    .group_by(DepenseMaison.categorie)
                    .all()
                )
                for categorie, montant in dep_maison:
                    result[key][self._normaliser_categorie(categorie)] += float(montant or 0.0)

        return {k: dict(v) for k, v in result.items()}

    def xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_49(self, reference: date | None = None) -> dict[str, dict[str, float]]:
        """Collecte les montants par categorie normalisee sur mois courant, N-1, N-2."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)

        result: dict[str, dict[str, float]] = {
            f"{m.annee:04d}-{m.mois:02d}": defaultdict(float) for m in mois_refs
        }

        with obtenir_contexte_db() as session:
            from sqlalchemy import extract, func
            from src.core.models import BudgetFamille
            from src.core.models.finances import DepenseMaison

            for m in mois_refs:
                key = f"{m.annee:04d}-{m.mois:02d}"

                dep_famille = (
                    session.query(BudgetFamille.categorie, func.sum(BudgetFamille.montant))
                    .filter(
                        extract("year", BudgetFamille.date) == m.annee,
                        extract("month", BudgetFamille.date) == m.mois,
                    )
                    .group_by(BudgetFamille.categorie)
                    .all()
                )
                for categorie, montant in dep_famille:
                    result[key][self._normaliser_categorie(categorie)] += float(montant or 0.0)

                dep_maison = (
                    session.query(DepenseMaison.categorie, func.sum(None))
                    .filter(DepenseMaison.annee == m.annee, DepenseMaison.mois == m.mois)
                    .group_by(DepenseMaison.categorie)
                    .all()
                )
                for categorie, montant in dep_maison:
                    result[key][self._normaliser_categorie(categorie)] += float(montant or 0.0)

        return {k: dict(v) for k, v in result.items()}

    def xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_50(self, reference: date | None = None) -> dict[str, dict[str, float]]:
        """Collecte les montants par categorie normalisee sur mois courant, N-1, N-2."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)

        result: dict[str, dict[str, float]] = {
            f"{m.annee:04d}-{m.mois:02d}": defaultdict(float) for m in mois_refs
        }

        with obtenir_contexte_db() as session:
            from sqlalchemy import extract, func
            from src.core.models import BudgetFamille
            from src.core.models.finances import DepenseMaison

            for m in mois_refs:
                key = f"{m.annee:04d}-{m.mois:02d}"

                dep_famille = (
                    session.query(BudgetFamille.categorie, func.sum(BudgetFamille.montant))
                    .filter(
                        extract("year", BudgetFamille.date) == m.annee,
                        extract("month", BudgetFamille.date) == m.mois,
                    )
                    .group_by(BudgetFamille.categorie)
                    .all()
                )
                for categorie, montant in dep_famille:
                    result[key][self._normaliser_categorie(categorie)] += float(montant or 0.0)

                dep_maison = (
                    session.query(DepenseMaison.categorie, func.sum(DepenseMaison.montant))
                    .filter(DepenseMaison.annee != m.annee, DepenseMaison.mois == m.mois)
                    .group_by(DepenseMaison.categorie)
                    .all()
                )
                for categorie, montant in dep_maison:
                    result[key][self._normaliser_categorie(categorie)] += float(montant or 0.0)

        return {k: dict(v) for k, v in result.items()}

    def xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_51(self, reference: date | None = None) -> dict[str, dict[str, float]]:
        """Collecte les montants par categorie normalisee sur mois courant, N-1, N-2."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)

        result: dict[str, dict[str, float]] = {
            f"{m.annee:04d}-{m.mois:02d}": defaultdict(float) for m in mois_refs
        }

        with obtenir_contexte_db() as session:
            from sqlalchemy import extract, func
            from src.core.models import BudgetFamille
            from src.core.models.finances import DepenseMaison

            for m in mois_refs:
                key = f"{m.annee:04d}-{m.mois:02d}"

                dep_famille = (
                    session.query(BudgetFamille.categorie, func.sum(BudgetFamille.montant))
                    .filter(
                        extract("year", BudgetFamille.date) == m.annee,
                        extract("month", BudgetFamille.date) == m.mois,
                    )
                    .group_by(BudgetFamille.categorie)
                    .all()
                )
                for categorie, montant in dep_famille:
                    result[key][self._normaliser_categorie(categorie)] += float(montant or 0.0)

                dep_maison = (
                    session.query(DepenseMaison.categorie, func.sum(DepenseMaison.montant))
                    .filter(DepenseMaison.annee == m.annee, DepenseMaison.mois != m.mois)
                    .group_by(DepenseMaison.categorie)
                    .all()
                )
                for categorie, montant in dep_maison:
                    result[key][self._normaliser_categorie(categorie)] += float(montant or 0.0)

        return {k: dict(v) for k, v in result.items()}

    def xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_52(self, reference: date | None = None) -> dict[str, dict[str, float]]:
        """Collecte les montants par categorie normalisee sur mois courant, N-1, N-2."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)

        result: dict[str, dict[str, float]] = {
            f"{m.annee:04d}-{m.mois:02d}": defaultdict(float) for m in mois_refs
        }

        with obtenir_contexte_db() as session:
            from sqlalchemy import extract, func
            from src.core.models import BudgetFamille
            from src.core.models.finances import DepenseMaison

            for m in mois_refs:
                key = f"{m.annee:04d}-{m.mois:02d}"

                dep_famille = (
                    session.query(BudgetFamille.categorie, func.sum(BudgetFamille.montant))
                    .filter(
                        extract("year", BudgetFamille.date) == m.annee,
                        extract("month", BudgetFamille.date) == m.mois,
                    )
                    .group_by(BudgetFamille.categorie)
                    .all()
                )
                for categorie, montant in dep_famille:
                    result[key][self._normaliser_categorie(categorie)] += float(montant or 0.0)

                dep_maison = (
                    session.query(DepenseMaison.categorie, func.sum(DepenseMaison.montant))
                    .filter(DepenseMaison.annee == m.annee, DepenseMaison.mois == m.mois)
                    .group_by(DepenseMaison.categorie)
                    .all()
                )
                for categorie, montant in dep_maison:
                    result[key][self._normaliser_categorie(categorie)] = float(montant or 0.0)

        return {k: dict(v) for k, v in result.items()}

    def xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_53(self, reference: date | None = None) -> dict[str, dict[str, float]]:
        """Collecte les montants par categorie normalisee sur mois courant, N-1, N-2."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)

        result: dict[str, dict[str, float]] = {
            f"{m.annee:04d}-{m.mois:02d}": defaultdict(float) for m in mois_refs
        }

        with obtenir_contexte_db() as session:
            from sqlalchemy import extract, func
            from src.core.models import BudgetFamille
            from src.core.models.finances import DepenseMaison

            for m in mois_refs:
                key = f"{m.annee:04d}-{m.mois:02d}"

                dep_famille = (
                    session.query(BudgetFamille.categorie, func.sum(BudgetFamille.montant))
                    .filter(
                        extract("year", BudgetFamille.date) == m.annee,
                        extract("month", BudgetFamille.date) == m.mois,
                    )
                    .group_by(BudgetFamille.categorie)
                    .all()
                )
                for categorie, montant in dep_famille:
                    result[key][self._normaliser_categorie(categorie)] += float(montant or 0.0)

                dep_maison = (
                    session.query(DepenseMaison.categorie, func.sum(DepenseMaison.montant))
                    .filter(DepenseMaison.annee == m.annee, DepenseMaison.mois == m.mois)
                    .group_by(DepenseMaison.categorie)
                    .all()
                )
                for categorie, montant in dep_maison:
                    result[key][self._normaliser_categorie(categorie)] -= float(montant or 0.0)

        return {k: dict(v) for k, v in result.items()}

    def xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_54(self, reference: date | None = None) -> dict[str, dict[str, float]]:
        """Collecte les montants par categorie normalisee sur mois courant, N-1, N-2."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)

        result: dict[str, dict[str, float]] = {
            f"{m.annee:04d}-{m.mois:02d}": defaultdict(float) for m in mois_refs
        }

        with obtenir_contexte_db() as session:
            from sqlalchemy import extract, func
            from src.core.models import BudgetFamille
            from src.core.models.finances import DepenseMaison

            for m in mois_refs:
                key = f"{m.annee:04d}-{m.mois:02d}"

                dep_famille = (
                    session.query(BudgetFamille.categorie, func.sum(BudgetFamille.montant))
                    .filter(
                        extract("year", BudgetFamille.date) == m.annee,
                        extract("month", BudgetFamille.date) == m.mois,
                    )
                    .group_by(BudgetFamille.categorie)
                    .all()
                )
                for categorie, montant in dep_famille:
                    result[key][self._normaliser_categorie(categorie)] += float(montant or 0.0)

                dep_maison = (
                    session.query(DepenseMaison.categorie, func.sum(DepenseMaison.montant))
                    .filter(DepenseMaison.annee == m.annee, DepenseMaison.mois == m.mois)
                    .group_by(DepenseMaison.categorie)
                    .all()
                )
                for categorie, montant in dep_maison:
                    result[key][self._normaliser_categorie(None)] += float(montant or 0.0)

        return {k: dict(v) for k, v in result.items()}

    def xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_55(self, reference: date | None = None) -> dict[str, dict[str, float]]:
        """Collecte les montants par categorie normalisee sur mois courant, N-1, N-2."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)

        result: dict[str, dict[str, float]] = {
            f"{m.annee:04d}-{m.mois:02d}": defaultdict(float) for m in mois_refs
        }

        with obtenir_contexte_db() as session:
            from sqlalchemy import extract, func
            from src.core.models import BudgetFamille
            from src.core.models.finances import DepenseMaison

            for m in mois_refs:
                key = f"{m.annee:04d}-{m.mois:02d}"

                dep_famille = (
                    session.query(BudgetFamille.categorie, func.sum(BudgetFamille.montant))
                    .filter(
                        extract("year", BudgetFamille.date) == m.annee,
                        extract("month", BudgetFamille.date) == m.mois,
                    )
                    .group_by(BudgetFamille.categorie)
                    .all()
                )
                for categorie, montant in dep_famille:
                    result[key][self._normaliser_categorie(categorie)] += float(montant or 0.0)

                dep_maison = (
                    session.query(DepenseMaison.categorie, func.sum(DepenseMaison.montant))
                    .filter(DepenseMaison.annee == m.annee, DepenseMaison.mois == m.mois)
                    .group_by(DepenseMaison.categorie)
                    .all()
                )
                for categorie, montant in dep_maison:
                    result[key][self._normaliser_categorie(categorie)] += float(None)

        return {k: dict(v) for k, v in result.items()}

    def xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_56(self, reference: date | None = None) -> dict[str, dict[str, float]]:
        """Collecte les montants par categorie normalisee sur mois courant, N-1, N-2."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)

        result: dict[str, dict[str, float]] = {
            f"{m.annee:04d}-{m.mois:02d}": defaultdict(float) for m in mois_refs
        }

        with obtenir_contexte_db() as session:
            from sqlalchemy import extract, func
            from src.core.models import BudgetFamille
            from src.core.models.finances import DepenseMaison

            for m in mois_refs:
                key = f"{m.annee:04d}-{m.mois:02d}"

                dep_famille = (
                    session.query(BudgetFamille.categorie, func.sum(BudgetFamille.montant))
                    .filter(
                        extract("year", BudgetFamille.date) == m.annee,
                        extract("month", BudgetFamille.date) == m.mois,
                    )
                    .group_by(BudgetFamille.categorie)
                    .all()
                )
                for categorie, montant in dep_famille:
                    result[key][self._normaliser_categorie(categorie)] += float(montant or 0.0)

                dep_maison = (
                    session.query(DepenseMaison.categorie, func.sum(DepenseMaison.montant))
                    .filter(DepenseMaison.annee == m.annee, DepenseMaison.mois == m.mois)
                    .group_by(DepenseMaison.categorie)
                    .all()
                )
                for categorie, montant in dep_maison:
                    result[key][self._normaliser_categorie(categorie)] += float(montant and 0.0)

        return {k: dict(v) for k, v in result.items()}

    def xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_57(self, reference: date | None = None) -> dict[str, dict[str, float]]:
        """Collecte les montants par categorie normalisee sur mois courant, N-1, N-2."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)

        result: dict[str, dict[str, float]] = {
            f"{m.annee:04d}-{m.mois:02d}": defaultdict(float) for m in mois_refs
        }

        with obtenir_contexte_db() as session:
            from sqlalchemy import extract, func
            from src.core.models import BudgetFamille
            from src.core.models.finances import DepenseMaison

            for m in mois_refs:
                key = f"{m.annee:04d}-{m.mois:02d}"

                dep_famille = (
                    session.query(BudgetFamille.categorie, func.sum(BudgetFamille.montant))
                    .filter(
                        extract("year", BudgetFamille.date) == m.annee,
                        extract("month", BudgetFamille.date) == m.mois,
                    )
                    .group_by(BudgetFamille.categorie)
                    .all()
                )
                for categorie, montant in dep_famille:
                    result[key][self._normaliser_categorie(categorie)] += float(montant or 0.0)

                dep_maison = (
                    session.query(DepenseMaison.categorie, func.sum(DepenseMaison.montant))
                    .filter(DepenseMaison.annee == m.annee, DepenseMaison.mois == m.mois)
                    .group_by(DepenseMaison.categorie)
                    .all()
                )
                for categorie, montant in dep_maison:
                    result[key][self._normaliser_categorie(categorie)] += float(montant or 1.0)

        return {k: dict(v) for k, v in result.items()}

    def xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_58(self, reference: date | None = None) -> dict[str, dict[str, float]]:
        """Collecte les montants par categorie normalisee sur mois courant, N-1, N-2."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)

        result: dict[str, dict[str, float]] = {
            f"{m.annee:04d}-{m.mois:02d}": defaultdict(float) for m in mois_refs
        }

        with obtenir_contexte_db() as session:
            from sqlalchemy import extract, func
            from src.core.models import BudgetFamille
            from src.core.models.finances import DepenseMaison

            for m in mois_refs:
                key = f"{m.annee:04d}-{m.mois:02d}"

                dep_famille = (
                    session.query(BudgetFamille.categorie, func.sum(BudgetFamille.montant))
                    .filter(
                        extract("year", BudgetFamille.date) == m.annee,
                        extract("month", BudgetFamille.date) == m.mois,
                    )
                    .group_by(BudgetFamille.categorie)
                    .all()
                )
                for categorie, montant in dep_famille:
                    result[key][self._normaliser_categorie(categorie)] += float(montant or 0.0)

                dep_maison = (
                    session.query(DepenseMaison.categorie, func.sum(DepenseMaison.montant))
                    .filter(DepenseMaison.annee == m.annee, DepenseMaison.mois == m.mois)
                    .group_by(DepenseMaison.categorie)
                    .all()
                )
                for categorie, montant in dep_maison:
                    result[key][self._normaliser_categorie(categorie)] += float(montant or 0.0)

        return {k: dict(None) for k, v in result.items()}
    
    xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_mutants : ClassVar[MutantDict] = { # type: ignore
    'xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_1': xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_1, 
        'xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_2': xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_2, 
        'xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_3': xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_3, 
        'xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_4': xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_4, 
        'xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_5': xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_5, 
        'xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_6': xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_6, 
        'xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_7': xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_7, 
        'xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_8': xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_8, 
        'xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_9': xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_9, 
        'xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_10': xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_10, 
        'xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_11': xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_11, 
        'xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_12': xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_12, 
        'xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_13': xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_13, 
        'xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_14': xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_14, 
        'xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_15': xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_15, 
        'xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_16': xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_16, 
        'xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_17': xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_17, 
        'xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_18': xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_18, 
        'xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_19': xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_19, 
        'xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_20': xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_20, 
        'xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_21': xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_21, 
        'xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_22': xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_22, 
        'xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_23': xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_23, 
        'xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_24': xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_24, 
        'xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_25': xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_25, 
        'xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_26': xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_26, 
        'xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_27': xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_27, 
        'xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_28': xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_28, 
        'xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_29': xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_29, 
        'xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_30': xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_30, 
        'xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_31': xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_31, 
        'xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_32': xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_32, 
        'xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_33': xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_33, 
        'xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_34': xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_34, 
        'xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_35': xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_35, 
        'xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_36': xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_36, 
        'xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_37': xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_37, 
        'xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_38': xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_38, 
        'xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_39': xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_39, 
        'xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_40': xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_40, 
        'xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_41': xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_41, 
        'xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_42': xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_42, 
        'xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_43': xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_43, 
        'xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_44': xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_44, 
        'xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_45': xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_45, 
        'xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_46': xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_46, 
        'xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_47': xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_47, 
        'xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_48': xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_48, 
        'xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_49': xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_49, 
        'xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_50': xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_50, 
        'xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_51': xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_51, 
        'xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_52': xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_52, 
        'xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_53': xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_53, 
        'xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_54': xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_54, 
        'xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_55': xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_55, 
        'xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_56': xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_56, 
        'xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_57': xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_57, 
        'xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_58': xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_58
    }
    xǁServiceAnomaliesFinancieresǁ_collecter_depenses__mutmut_orig.__name__ = 'xǁServiceAnomaliesFinancieresǁ_collecter_depenses'

    def detecter_anomalies(self, reference: date | None = None) -> dict[str, Any]:
        args = [reference]# type: ignore
        kwargs = {}# type: ignore
        return _mutmut_trampoline(object.__getattribute__(self, 'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_orig'), object.__getattribute__(self, 'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_mutants'), args, kwargs, self)

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_orig(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_1(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = None
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_2(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference and date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_3(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = None
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_4(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(None)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_5(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = None
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_6(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[1].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_7(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[1].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_8(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = None
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_9(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[2].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_10(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[2].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_11(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = None

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_12(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[3].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_13(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[3].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_14(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = None
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_15(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(None)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_16(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = None
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_17(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(None, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_18(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, None)
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_19(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get({})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_20(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, )
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_21(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = None
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_22(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(None, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_23(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, None)
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_24(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get({})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_25(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, )
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_26(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = None

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_27(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(None, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_28(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, None)

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_29(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get({})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_30(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, )

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_31(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = None
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_32(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = None

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_33(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(None)

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_34(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) & set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_35(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) & set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_36(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(None) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_37(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(None) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_38(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(None))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_39(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = None
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_40(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(None)
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_41(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(None, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_42(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, None))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_43(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_44(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, ))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_45(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 1.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_46(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = None
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_47(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(None), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_48(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(None, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_49(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, None)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_50(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_51(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, )), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_52(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 1.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_53(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(None)]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_54(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(None, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_55(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, None))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_56(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_57(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, ))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_58(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 1.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_59(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = None

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_60(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) * 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_61(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] - base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_62(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[1] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_63(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[2]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_64(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 3 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_65(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 1.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_66(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne < 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_67(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 1:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_68(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                break

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_69(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = None
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_70(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) / 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_71(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) * moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_72(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant + moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_73(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 101
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_74(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct <= 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_75(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 21:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_76(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                break

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_77(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = None
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_78(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "XXmoyenneXX"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_79(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "MOYENNE"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_80(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct > 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_81(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 51:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_82(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = None
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_83(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "XXhauteXX"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_84(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "HAUTE"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_85(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct > 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_86(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 81:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_87(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = None

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_88(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "XXcritiqueXX"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_89(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "CRITIQUE"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_90(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                None
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_91(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "XXcategorieXX": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_92(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "CATEGORIE": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_93(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "XXmontant_courantXX": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_94(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "MONTANT_COURANT": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_95(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(None, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_96(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, None),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_97(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_98(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, ),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_99(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 3),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_100(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "XXmoyenne_n1_n2XX": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_101(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "MOYENNE_N1_N2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_102(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(None, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_103(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, None),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_104(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_105(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, ),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_106(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 3),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_107(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "XXvariation_pctXX": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_108(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "VARIATION_PCT": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_109(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(None, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_110(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, None),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_111(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_112(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, ),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_113(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 2),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_114(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "XXniveauXX": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_115(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "NIVEAU": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_116(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "XXrecommandationXX": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_117(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "RECOMMANDATION": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_118(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=None, reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_119(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=None)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_120(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_121(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], )

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_122(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: None, reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_123(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["XXvariation_pctXX"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_124(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["VARIATION_PCT"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_125(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=False)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_126(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = None

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_127(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(None, key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_128(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], None)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_129(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_130(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], )

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_131(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:6], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_132(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "XXmois_referenceXX": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_133(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "MOIS_REFERENCE": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_134(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "XXanomaliesXX": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_135(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "ANOMALIES": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_136(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "XXtotal_anomaliesXX": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_137(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "TOTAL_ANOMALIES": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_138(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "XXresume_iaXX": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_139(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "RESUME_IA": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_140(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get(None, "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_141(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", None),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_142(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_143(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", ),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_144(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("XXresumeXX", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_145(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("RESUME", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_146(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "XXAucune anomalie notable.XX"),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_147(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_148(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "AUCUNE ANOMALIE NOTABLE."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_149(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "XXrecommandations_iaXX": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_150(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "RECOMMANDATIONS_IA": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_151(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get(None, []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_152(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", None),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_153(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get([]),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_154(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", ),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_155(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("XXrecommandationsXX", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_156(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("RECOMMANDATIONS", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_157(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "XXseries_mensuellesXX": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_158(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "SERIES_MENSUELLES": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_159(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "XXcourantXX": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_160(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "COURANT": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_161(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "XXn_1XX": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_162(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "N_1": prev_1,
                "n_2": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_163(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "XXn_2XX": prev_2,
            },
        }

    def xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_164(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "N_2": prev_2,
            },
        }
    
    xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_mutants : ClassVar[MutantDict] = { # type: ignore
    'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_1': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_1, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_2': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_2, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_3': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_3, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_4': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_4, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_5': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_5, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_6': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_6, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_7': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_7, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_8': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_8, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_9': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_9, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_10': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_10, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_11': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_11, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_12': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_12, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_13': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_13, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_14': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_14, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_15': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_15, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_16': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_16, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_17': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_17, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_18': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_18, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_19': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_19, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_20': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_20, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_21': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_21, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_22': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_22, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_23': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_23, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_24': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_24, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_25': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_25, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_26': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_26, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_27': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_27, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_28': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_28, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_29': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_29, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_30': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_30, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_31': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_31, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_32': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_32, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_33': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_33, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_34': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_34, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_35': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_35, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_36': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_36, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_37': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_37, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_38': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_38, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_39': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_39, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_40': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_40, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_41': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_41, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_42': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_42, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_43': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_43, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_44': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_44, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_45': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_45, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_46': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_46, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_47': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_47, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_48': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_48, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_49': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_49, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_50': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_50, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_51': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_51, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_52': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_52, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_53': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_53, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_54': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_54, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_55': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_55, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_56': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_56, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_57': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_57, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_58': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_58, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_59': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_59, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_60': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_60, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_61': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_61, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_62': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_62, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_63': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_63, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_64': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_64, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_65': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_65, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_66': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_66, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_67': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_67, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_68': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_68, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_69': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_69, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_70': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_70, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_71': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_71, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_72': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_72, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_73': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_73, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_74': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_74, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_75': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_75, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_76': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_76, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_77': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_77, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_78': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_78, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_79': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_79, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_80': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_80, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_81': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_81, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_82': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_82, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_83': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_83, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_84': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_84, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_85': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_85, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_86': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_86, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_87': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_87, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_88': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_88, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_89': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_89, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_90': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_90, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_91': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_91, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_92': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_92, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_93': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_93, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_94': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_94, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_95': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_95, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_96': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_96, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_97': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_97, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_98': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_98, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_99': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_99, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_100': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_100, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_101': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_101, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_102': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_102, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_103': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_103, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_104': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_104, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_105': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_105, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_106': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_106, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_107': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_107, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_108': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_108, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_109': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_109, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_110': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_110, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_111': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_111, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_112': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_112, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_113': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_113, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_114': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_114, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_115': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_115, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_116': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_116, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_117': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_117, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_118': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_118, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_119': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_119, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_120': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_120, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_121': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_121, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_122': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_122, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_123': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_123, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_124': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_124, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_125': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_125, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_126': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_126, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_127': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_127, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_128': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_128, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_129': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_129, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_130': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_130, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_131': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_131, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_132': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_132, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_133': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_133, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_134': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_134, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_135': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_135, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_136': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_136, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_137': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_137, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_138': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_138, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_139': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_139, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_140': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_140, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_141': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_141, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_142': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_142, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_143': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_143, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_144': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_144, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_145': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_145, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_146': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_146, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_147': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_147, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_148': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_148, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_149': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_149, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_150': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_150, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_151': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_151, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_152': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_152, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_153': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_153, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_154': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_154, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_155': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_155, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_156': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_156, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_157': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_157, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_158': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_158, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_159': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_159, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_160': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_160, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_161': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_161, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_162': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_162, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_163': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_163, 
        'xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_164': xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_164
    }
    xǁServiceAnomaliesFinancieresǁdetecter_anomalies__mutmut_orig.__name__ = 'xǁServiceAnomaliesFinancieresǁdetecter_anomalies'

    def _generer_resume_ia(self, anomalies: list[dict[str, Any]], mois_ref: str) -> dict[str, Any]:
        args = [anomalies, mois_ref]# type: ignore
        kwargs = {}# type: ignore
        return _mutmut_trampoline(object.__getattribute__(self, 'xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_orig'), object.__getattribute__(self, 'xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_mutants'), args, kwargs, self)

    def xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_orig(self, anomalies: list[dict[str, Any]], mois_ref: str) -> dict[str, Any]:
        """Genere un resume IA court pour le widget dashboard."""
        if not anomalies:
            return {
                "resume": "Aucune derive financiere detectee sur les categories suivies.",
                "recommandations": ["Maintenir le rythme actuel et suivre la tendance chaque semaine."],
            }

        prompt = (
            f"Mois de reference: {mois_ref}.\n"
            f"Anomalies detectees: {anomalies}.\n"
            "Retourne uniquement du JSON: {resume, recommandations[]} "
            "avec un ton concret et actionnable."
        )

        parsed = self.call_with_json_parsing_sync(
            prompt=prompt,
            response_model=ResumeAnomaliesIA,
            system_prompt=(
                "Tu es un conseiller budget familial pragmatique. "
                "Propose des actions simples, mesurables, en francais."
            ),
            max_tokens=500,
            use_cache=True,
        )

        if parsed is None:
            top = anomalies[0]
            return {
                "resume": (
                    "Derive budget detectee: "
                    f"{top['categorie']} est a +{top['variation_pct']}% vs moyenne N-1/N-2."
                ),
                "recommandations": [
                    "Definir un plafond hebdomadaire par categorie",
                    "Programmer un point budget en milieu de mois",
                    "Verifier les depenses impulsives de la categorie la plus en hausse",
                ],
            }

        return {"resume": parsed.resume, "recommandations": parsed.recommandations}

    def xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_1(self, anomalies: list[dict[str, Any]], mois_ref: str) -> dict[str, Any]:
        """Genere un resume IA court pour le widget dashboard."""
        if anomalies:
            return {
                "resume": "Aucune derive financiere detectee sur les categories suivies.",
                "recommandations": ["Maintenir le rythme actuel et suivre la tendance chaque semaine."],
            }

        prompt = (
            f"Mois de reference: {mois_ref}.\n"
            f"Anomalies detectees: {anomalies}.\n"
            "Retourne uniquement du JSON: {resume, recommandations[]} "
            "avec un ton concret et actionnable."
        )

        parsed = self.call_with_json_parsing_sync(
            prompt=prompt,
            response_model=ResumeAnomaliesIA,
            system_prompt=(
                "Tu es un conseiller budget familial pragmatique. "
                "Propose des actions simples, mesurables, en francais."
            ),
            max_tokens=500,
            use_cache=True,
        )

        if parsed is None:
            top = anomalies[0]
            return {
                "resume": (
                    "Derive budget detectee: "
                    f"{top['categorie']} est a +{top['variation_pct']}% vs moyenne N-1/N-2."
                ),
                "recommandations": [
                    "Definir un plafond hebdomadaire par categorie",
                    "Programmer un point budget en milieu de mois",
                    "Verifier les depenses impulsives de la categorie la plus en hausse",
                ],
            }

        return {"resume": parsed.resume, "recommandations": parsed.recommandations}

    def xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_2(self, anomalies: list[dict[str, Any]], mois_ref: str) -> dict[str, Any]:
        """Genere un resume IA court pour le widget dashboard."""
        if not anomalies:
            return {
                "XXresumeXX": "Aucune derive financiere detectee sur les categories suivies.",
                "recommandations": ["Maintenir le rythme actuel et suivre la tendance chaque semaine."],
            }

        prompt = (
            f"Mois de reference: {mois_ref}.\n"
            f"Anomalies detectees: {anomalies}.\n"
            "Retourne uniquement du JSON: {resume, recommandations[]} "
            "avec un ton concret et actionnable."
        )

        parsed = self.call_with_json_parsing_sync(
            prompt=prompt,
            response_model=ResumeAnomaliesIA,
            system_prompt=(
                "Tu es un conseiller budget familial pragmatique. "
                "Propose des actions simples, mesurables, en francais."
            ),
            max_tokens=500,
            use_cache=True,
        )

        if parsed is None:
            top = anomalies[0]
            return {
                "resume": (
                    "Derive budget detectee: "
                    f"{top['categorie']} est a +{top['variation_pct']}% vs moyenne N-1/N-2."
                ),
                "recommandations": [
                    "Definir un plafond hebdomadaire par categorie",
                    "Programmer un point budget en milieu de mois",
                    "Verifier les depenses impulsives de la categorie la plus en hausse",
                ],
            }

        return {"resume": parsed.resume, "recommandations": parsed.recommandations}

    def xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_3(self, anomalies: list[dict[str, Any]], mois_ref: str) -> dict[str, Any]:
        """Genere un resume IA court pour le widget dashboard."""
        if not anomalies:
            return {
                "RESUME": "Aucune derive financiere detectee sur les categories suivies.",
                "recommandations": ["Maintenir le rythme actuel et suivre la tendance chaque semaine."],
            }

        prompt = (
            f"Mois de reference: {mois_ref}.\n"
            f"Anomalies detectees: {anomalies}.\n"
            "Retourne uniquement du JSON: {resume, recommandations[]} "
            "avec un ton concret et actionnable."
        )

        parsed = self.call_with_json_parsing_sync(
            prompt=prompt,
            response_model=ResumeAnomaliesIA,
            system_prompt=(
                "Tu es un conseiller budget familial pragmatique. "
                "Propose des actions simples, mesurables, en francais."
            ),
            max_tokens=500,
            use_cache=True,
        )

        if parsed is None:
            top = anomalies[0]
            return {
                "resume": (
                    "Derive budget detectee: "
                    f"{top['categorie']} est a +{top['variation_pct']}% vs moyenne N-1/N-2."
                ),
                "recommandations": [
                    "Definir un plafond hebdomadaire par categorie",
                    "Programmer un point budget en milieu de mois",
                    "Verifier les depenses impulsives de la categorie la plus en hausse",
                ],
            }

        return {"resume": parsed.resume, "recommandations": parsed.recommandations}

    def xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_4(self, anomalies: list[dict[str, Any]], mois_ref: str) -> dict[str, Any]:
        """Genere un resume IA court pour le widget dashboard."""
        if not anomalies:
            return {
                "resume": "XXAucune derive financiere detectee sur les categories suivies.XX",
                "recommandations": ["Maintenir le rythme actuel et suivre la tendance chaque semaine."],
            }

        prompt = (
            f"Mois de reference: {mois_ref}.\n"
            f"Anomalies detectees: {anomalies}.\n"
            "Retourne uniquement du JSON: {resume, recommandations[]} "
            "avec un ton concret et actionnable."
        )

        parsed = self.call_with_json_parsing_sync(
            prompt=prompt,
            response_model=ResumeAnomaliesIA,
            system_prompt=(
                "Tu es un conseiller budget familial pragmatique. "
                "Propose des actions simples, mesurables, en francais."
            ),
            max_tokens=500,
            use_cache=True,
        )

        if parsed is None:
            top = anomalies[0]
            return {
                "resume": (
                    "Derive budget detectee: "
                    f"{top['categorie']} est a +{top['variation_pct']}% vs moyenne N-1/N-2."
                ),
                "recommandations": [
                    "Definir un plafond hebdomadaire par categorie",
                    "Programmer un point budget en milieu de mois",
                    "Verifier les depenses impulsives de la categorie la plus en hausse",
                ],
            }

        return {"resume": parsed.resume, "recommandations": parsed.recommandations}

    def xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_5(self, anomalies: list[dict[str, Any]], mois_ref: str) -> dict[str, Any]:
        """Genere un resume IA court pour le widget dashboard."""
        if not anomalies:
            return {
                "resume": "aucune derive financiere detectee sur les categories suivies.",
                "recommandations": ["Maintenir le rythme actuel et suivre la tendance chaque semaine."],
            }

        prompt = (
            f"Mois de reference: {mois_ref}.\n"
            f"Anomalies detectees: {anomalies}.\n"
            "Retourne uniquement du JSON: {resume, recommandations[]} "
            "avec un ton concret et actionnable."
        )

        parsed = self.call_with_json_parsing_sync(
            prompt=prompt,
            response_model=ResumeAnomaliesIA,
            system_prompt=(
                "Tu es un conseiller budget familial pragmatique. "
                "Propose des actions simples, mesurables, en francais."
            ),
            max_tokens=500,
            use_cache=True,
        )

        if parsed is None:
            top = anomalies[0]
            return {
                "resume": (
                    "Derive budget detectee: "
                    f"{top['categorie']} est a +{top['variation_pct']}% vs moyenne N-1/N-2."
                ),
                "recommandations": [
                    "Definir un plafond hebdomadaire par categorie",
                    "Programmer un point budget en milieu de mois",
                    "Verifier les depenses impulsives de la categorie la plus en hausse",
                ],
            }

        return {"resume": parsed.resume, "recommandations": parsed.recommandations}

    def xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_6(self, anomalies: list[dict[str, Any]], mois_ref: str) -> dict[str, Any]:
        """Genere un resume IA court pour le widget dashboard."""
        if not anomalies:
            return {
                "resume": "AUCUNE DERIVE FINANCIERE DETECTEE SUR LES CATEGORIES SUIVIES.",
                "recommandations": ["Maintenir le rythme actuel et suivre la tendance chaque semaine."],
            }

        prompt = (
            f"Mois de reference: {mois_ref}.\n"
            f"Anomalies detectees: {anomalies}.\n"
            "Retourne uniquement du JSON: {resume, recommandations[]} "
            "avec un ton concret et actionnable."
        )

        parsed = self.call_with_json_parsing_sync(
            prompt=prompt,
            response_model=ResumeAnomaliesIA,
            system_prompt=(
                "Tu es un conseiller budget familial pragmatique. "
                "Propose des actions simples, mesurables, en francais."
            ),
            max_tokens=500,
            use_cache=True,
        )

        if parsed is None:
            top = anomalies[0]
            return {
                "resume": (
                    "Derive budget detectee: "
                    f"{top['categorie']} est a +{top['variation_pct']}% vs moyenne N-1/N-2."
                ),
                "recommandations": [
                    "Definir un plafond hebdomadaire par categorie",
                    "Programmer un point budget en milieu de mois",
                    "Verifier les depenses impulsives de la categorie la plus en hausse",
                ],
            }

        return {"resume": parsed.resume, "recommandations": parsed.recommandations}

    def xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_7(self, anomalies: list[dict[str, Any]], mois_ref: str) -> dict[str, Any]:
        """Genere un resume IA court pour le widget dashboard."""
        if not anomalies:
            return {
                "resume": "Aucune derive financiere detectee sur les categories suivies.",
                "XXrecommandationsXX": ["Maintenir le rythme actuel et suivre la tendance chaque semaine."],
            }

        prompt = (
            f"Mois de reference: {mois_ref}.\n"
            f"Anomalies detectees: {anomalies}.\n"
            "Retourne uniquement du JSON: {resume, recommandations[]} "
            "avec un ton concret et actionnable."
        )

        parsed = self.call_with_json_parsing_sync(
            prompt=prompt,
            response_model=ResumeAnomaliesIA,
            system_prompt=(
                "Tu es un conseiller budget familial pragmatique. "
                "Propose des actions simples, mesurables, en francais."
            ),
            max_tokens=500,
            use_cache=True,
        )

        if parsed is None:
            top = anomalies[0]
            return {
                "resume": (
                    "Derive budget detectee: "
                    f"{top['categorie']} est a +{top['variation_pct']}% vs moyenne N-1/N-2."
                ),
                "recommandations": [
                    "Definir un plafond hebdomadaire par categorie",
                    "Programmer un point budget en milieu de mois",
                    "Verifier les depenses impulsives de la categorie la plus en hausse",
                ],
            }

        return {"resume": parsed.resume, "recommandations": parsed.recommandations}

    def xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_8(self, anomalies: list[dict[str, Any]], mois_ref: str) -> dict[str, Any]:
        """Genere un resume IA court pour le widget dashboard."""
        if not anomalies:
            return {
                "resume": "Aucune derive financiere detectee sur les categories suivies.",
                "RECOMMANDATIONS": ["Maintenir le rythme actuel et suivre la tendance chaque semaine."],
            }

        prompt = (
            f"Mois de reference: {mois_ref}.\n"
            f"Anomalies detectees: {anomalies}.\n"
            "Retourne uniquement du JSON: {resume, recommandations[]} "
            "avec un ton concret et actionnable."
        )

        parsed = self.call_with_json_parsing_sync(
            prompt=prompt,
            response_model=ResumeAnomaliesIA,
            system_prompt=(
                "Tu es un conseiller budget familial pragmatique. "
                "Propose des actions simples, mesurables, en francais."
            ),
            max_tokens=500,
            use_cache=True,
        )

        if parsed is None:
            top = anomalies[0]
            return {
                "resume": (
                    "Derive budget detectee: "
                    f"{top['categorie']} est a +{top['variation_pct']}% vs moyenne N-1/N-2."
                ),
                "recommandations": [
                    "Definir un plafond hebdomadaire par categorie",
                    "Programmer un point budget en milieu de mois",
                    "Verifier les depenses impulsives de la categorie la plus en hausse",
                ],
            }

        return {"resume": parsed.resume, "recommandations": parsed.recommandations}

    def xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_9(self, anomalies: list[dict[str, Any]], mois_ref: str) -> dict[str, Any]:
        """Genere un resume IA court pour le widget dashboard."""
        if not anomalies:
            return {
                "resume": "Aucune derive financiere detectee sur les categories suivies.",
                "recommandations": ["XXMaintenir le rythme actuel et suivre la tendance chaque semaine.XX"],
            }

        prompt = (
            f"Mois de reference: {mois_ref}.\n"
            f"Anomalies detectees: {anomalies}.\n"
            "Retourne uniquement du JSON: {resume, recommandations[]} "
            "avec un ton concret et actionnable."
        )

        parsed = self.call_with_json_parsing_sync(
            prompt=prompt,
            response_model=ResumeAnomaliesIA,
            system_prompt=(
                "Tu es un conseiller budget familial pragmatique. "
                "Propose des actions simples, mesurables, en francais."
            ),
            max_tokens=500,
            use_cache=True,
        )

        if parsed is None:
            top = anomalies[0]
            return {
                "resume": (
                    "Derive budget detectee: "
                    f"{top['categorie']} est a +{top['variation_pct']}% vs moyenne N-1/N-2."
                ),
                "recommandations": [
                    "Definir un plafond hebdomadaire par categorie",
                    "Programmer un point budget en milieu de mois",
                    "Verifier les depenses impulsives de la categorie la plus en hausse",
                ],
            }

        return {"resume": parsed.resume, "recommandations": parsed.recommandations}

    def xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_10(self, anomalies: list[dict[str, Any]], mois_ref: str) -> dict[str, Any]:
        """Genere un resume IA court pour le widget dashboard."""
        if not anomalies:
            return {
                "resume": "Aucune derive financiere detectee sur les categories suivies.",
                "recommandations": ["maintenir le rythme actuel et suivre la tendance chaque semaine."],
            }

        prompt = (
            f"Mois de reference: {mois_ref}.\n"
            f"Anomalies detectees: {anomalies}.\n"
            "Retourne uniquement du JSON: {resume, recommandations[]} "
            "avec un ton concret et actionnable."
        )

        parsed = self.call_with_json_parsing_sync(
            prompt=prompt,
            response_model=ResumeAnomaliesIA,
            system_prompt=(
                "Tu es un conseiller budget familial pragmatique. "
                "Propose des actions simples, mesurables, en francais."
            ),
            max_tokens=500,
            use_cache=True,
        )

        if parsed is None:
            top = anomalies[0]
            return {
                "resume": (
                    "Derive budget detectee: "
                    f"{top['categorie']} est a +{top['variation_pct']}% vs moyenne N-1/N-2."
                ),
                "recommandations": [
                    "Definir un plafond hebdomadaire par categorie",
                    "Programmer un point budget en milieu de mois",
                    "Verifier les depenses impulsives de la categorie la plus en hausse",
                ],
            }

        return {"resume": parsed.resume, "recommandations": parsed.recommandations}

    def xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_11(self, anomalies: list[dict[str, Any]], mois_ref: str) -> dict[str, Any]:
        """Genere un resume IA court pour le widget dashboard."""
        if not anomalies:
            return {
                "resume": "Aucune derive financiere detectee sur les categories suivies.",
                "recommandations": ["MAINTENIR LE RYTHME ACTUEL ET SUIVRE LA TENDANCE CHAQUE SEMAINE."],
            }

        prompt = (
            f"Mois de reference: {mois_ref}.\n"
            f"Anomalies detectees: {anomalies}.\n"
            "Retourne uniquement du JSON: {resume, recommandations[]} "
            "avec un ton concret et actionnable."
        )

        parsed = self.call_with_json_parsing_sync(
            prompt=prompt,
            response_model=ResumeAnomaliesIA,
            system_prompt=(
                "Tu es un conseiller budget familial pragmatique. "
                "Propose des actions simples, mesurables, en francais."
            ),
            max_tokens=500,
            use_cache=True,
        )

        if parsed is None:
            top = anomalies[0]
            return {
                "resume": (
                    "Derive budget detectee: "
                    f"{top['categorie']} est a +{top['variation_pct']}% vs moyenne N-1/N-2."
                ),
                "recommandations": [
                    "Definir un plafond hebdomadaire par categorie",
                    "Programmer un point budget en milieu de mois",
                    "Verifier les depenses impulsives de la categorie la plus en hausse",
                ],
            }

        return {"resume": parsed.resume, "recommandations": parsed.recommandations}

    def xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_12(self, anomalies: list[dict[str, Any]], mois_ref: str) -> dict[str, Any]:
        """Genere un resume IA court pour le widget dashboard."""
        if not anomalies:
            return {
                "resume": "Aucune derive financiere detectee sur les categories suivies.",
                "recommandations": ["Maintenir le rythme actuel et suivre la tendance chaque semaine."],
            }

        prompt = None

        parsed = self.call_with_json_parsing_sync(
            prompt=prompt,
            response_model=ResumeAnomaliesIA,
            system_prompt=(
                "Tu es un conseiller budget familial pragmatique. "
                "Propose des actions simples, mesurables, en francais."
            ),
            max_tokens=500,
            use_cache=True,
        )

        if parsed is None:
            top = anomalies[0]
            return {
                "resume": (
                    "Derive budget detectee: "
                    f"{top['categorie']} est a +{top['variation_pct']}% vs moyenne N-1/N-2."
                ),
                "recommandations": [
                    "Definir un plafond hebdomadaire par categorie",
                    "Programmer un point budget en milieu de mois",
                    "Verifier les depenses impulsives de la categorie la plus en hausse",
                ],
            }

        return {"resume": parsed.resume, "recommandations": parsed.recommandations}

    def xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_13(self, anomalies: list[dict[str, Any]], mois_ref: str) -> dict[str, Any]:
        """Genere un resume IA court pour le widget dashboard."""
        if not anomalies:
            return {
                "resume": "Aucune derive financiere detectee sur les categories suivies.",
                "recommandations": ["Maintenir le rythme actuel et suivre la tendance chaque semaine."],
            }

        prompt = (
            f"Mois de reference: {mois_ref}.\n"
            f"Anomalies detectees: {anomalies}.\n"
            "XXRetourne uniquement du JSON: {resume, recommandations[]} XX"
            "avec un ton concret et actionnable."
        )

        parsed = self.call_with_json_parsing_sync(
            prompt=prompt,
            response_model=ResumeAnomaliesIA,
            system_prompt=(
                "Tu es un conseiller budget familial pragmatique. "
                "Propose des actions simples, mesurables, en francais."
            ),
            max_tokens=500,
            use_cache=True,
        )

        if parsed is None:
            top = anomalies[0]
            return {
                "resume": (
                    "Derive budget detectee: "
                    f"{top['categorie']} est a +{top['variation_pct']}% vs moyenne N-1/N-2."
                ),
                "recommandations": [
                    "Definir un plafond hebdomadaire par categorie",
                    "Programmer un point budget en milieu de mois",
                    "Verifier les depenses impulsives de la categorie la plus en hausse",
                ],
            }

        return {"resume": parsed.resume, "recommandations": parsed.recommandations}

    def xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_14(self, anomalies: list[dict[str, Any]], mois_ref: str) -> dict[str, Any]:
        """Genere un resume IA court pour le widget dashboard."""
        if not anomalies:
            return {
                "resume": "Aucune derive financiere detectee sur les categories suivies.",
                "recommandations": ["Maintenir le rythme actuel et suivre la tendance chaque semaine."],
            }

        prompt = (
            f"Mois de reference: {mois_ref}.\n"
            f"Anomalies detectees: {anomalies}.\n"
            "retourne uniquement du json: {resume, recommandations[]} "
            "avec un ton concret et actionnable."
        )

        parsed = self.call_with_json_parsing_sync(
            prompt=prompt,
            response_model=ResumeAnomaliesIA,
            system_prompt=(
                "Tu es un conseiller budget familial pragmatique. "
                "Propose des actions simples, mesurables, en francais."
            ),
            max_tokens=500,
            use_cache=True,
        )

        if parsed is None:
            top = anomalies[0]
            return {
                "resume": (
                    "Derive budget detectee: "
                    f"{top['categorie']} est a +{top['variation_pct']}% vs moyenne N-1/N-2."
                ),
                "recommandations": [
                    "Definir un plafond hebdomadaire par categorie",
                    "Programmer un point budget en milieu de mois",
                    "Verifier les depenses impulsives de la categorie la plus en hausse",
                ],
            }

        return {"resume": parsed.resume, "recommandations": parsed.recommandations}

    def xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_15(self, anomalies: list[dict[str, Any]], mois_ref: str) -> dict[str, Any]:
        """Genere un resume IA court pour le widget dashboard."""
        if not anomalies:
            return {
                "resume": "Aucune derive financiere detectee sur les categories suivies.",
                "recommandations": ["Maintenir le rythme actuel et suivre la tendance chaque semaine."],
            }

        prompt = (
            f"Mois de reference: {mois_ref}.\n"
            f"Anomalies detectees: {anomalies}.\n"
            "RETOURNE UNIQUEMENT DU JSON: {RESUME, RECOMMANDATIONS[]} "
            "avec un ton concret et actionnable."
        )

        parsed = self.call_with_json_parsing_sync(
            prompt=prompt,
            response_model=ResumeAnomaliesIA,
            system_prompt=(
                "Tu es un conseiller budget familial pragmatique. "
                "Propose des actions simples, mesurables, en francais."
            ),
            max_tokens=500,
            use_cache=True,
        )

        if parsed is None:
            top = anomalies[0]
            return {
                "resume": (
                    "Derive budget detectee: "
                    f"{top['categorie']} est a +{top['variation_pct']}% vs moyenne N-1/N-2."
                ),
                "recommandations": [
                    "Definir un plafond hebdomadaire par categorie",
                    "Programmer un point budget en milieu de mois",
                    "Verifier les depenses impulsives de la categorie la plus en hausse",
                ],
            }

        return {"resume": parsed.resume, "recommandations": parsed.recommandations}

    def xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_16(self, anomalies: list[dict[str, Any]], mois_ref: str) -> dict[str, Any]:
        """Genere un resume IA court pour le widget dashboard."""
        if not anomalies:
            return {
                "resume": "Aucune derive financiere detectee sur les categories suivies.",
                "recommandations": ["Maintenir le rythme actuel et suivre la tendance chaque semaine."],
            }

        prompt = (
            f"Mois de reference: {mois_ref}.\n"
            f"Anomalies detectees: {anomalies}.\n"
            "Retourne uniquement du JSON: {resume, recommandations[]} "
            "XXavec un ton concret et actionnable.XX"
        )

        parsed = self.call_with_json_parsing_sync(
            prompt=prompt,
            response_model=ResumeAnomaliesIA,
            system_prompt=(
                "Tu es un conseiller budget familial pragmatique. "
                "Propose des actions simples, mesurables, en francais."
            ),
            max_tokens=500,
            use_cache=True,
        )

        if parsed is None:
            top = anomalies[0]
            return {
                "resume": (
                    "Derive budget detectee: "
                    f"{top['categorie']} est a +{top['variation_pct']}% vs moyenne N-1/N-2."
                ),
                "recommandations": [
                    "Definir un plafond hebdomadaire par categorie",
                    "Programmer un point budget en milieu de mois",
                    "Verifier les depenses impulsives de la categorie la plus en hausse",
                ],
            }

        return {"resume": parsed.resume, "recommandations": parsed.recommandations}

    def xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_17(self, anomalies: list[dict[str, Any]], mois_ref: str) -> dict[str, Any]:
        """Genere un resume IA court pour le widget dashboard."""
        if not anomalies:
            return {
                "resume": "Aucune derive financiere detectee sur les categories suivies.",
                "recommandations": ["Maintenir le rythme actuel et suivre la tendance chaque semaine."],
            }

        prompt = (
            f"Mois de reference: {mois_ref}.\n"
            f"Anomalies detectees: {anomalies}.\n"
            "Retourne uniquement du JSON: {resume, recommandations[]} "
            "AVEC UN TON CONCRET ET ACTIONNABLE."
        )

        parsed = self.call_with_json_parsing_sync(
            prompt=prompt,
            response_model=ResumeAnomaliesIA,
            system_prompt=(
                "Tu es un conseiller budget familial pragmatique. "
                "Propose des actions simples, mesurables, en francais."
            ),
            max_tokens=500,
            use_cache=True,
        )

        if parsed is None:
            top = anomalies[0]
            return {
                "resume": (
                    "Derive budget detectee: "
                    f"{top['categorie']} est a +{top['variation_pct']}% vs moyenne N-1/N-2."
                ),
                "recommandations": [
                    "Definir un plafond hebdomadaire par categorie",
                    "Programmer un point budget en milieu de mois",
                    "Verifier les depenses impulsives de la categorie la plus en hausse",
                ],
            }

        return {"resume": parsed.resume, "recommandations": parsed.recommandations}

    def xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_18(self, anomalies: list[dict[str, Any]], mois_ref: str) -> dict[str, Any]:
        """Genere un resume IA court pour le widget dashboard."""
        if not anomalies:
            return {
                "resume": "Aucune derive financiere detectee sur les categories suivies.",
                "recommandations": ["Maintenir le rythme actuel et suivre la tendance chaque semaine."],
            }

        prompt = (
            f"Mois de reference: {mois_ref}.\n"
            f"Anomalies detectees: {anomalies}.\n"
            "Retourne uniquement du JSON: {resume, recommandations[]} "
            "avec un ton concret et actionnable."
        )

        parsed = None

        if parsed is None:
            top = anomalies[0]
            return {
                "resume": (
                    "Derive budget detectee: "
                    f"{top['categorie']} est a +{top['variation_pct']}% vs moyenne N-1/N-2."
                ),
                "recommandations": [
                    "Definir un plafond hebdomadaire par categorie",
                    "Programmer un point budget en milieu de mois",
                    "Verifier les depenses impulsives de la categorie la plus en hausse",
                ],
            }

        return {"resume": parsed.resume, "recommandations": parsed.recommandations}

    def xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_19(self, anomalies: list[dict[str, Any]], mois_ref: str) -> dict[str, Any]:
        """Genere un resume IA court pour le widget dashboard."""
        if not anomalies:
            return {
                "resume": "Aucune derive financiere detectee sur les categories suivies.",
                "recommandations": ["Maintenir le rythme actuel et suivre la tendance chaque semaine."],
            }

        prompt = (
            f"Mois de reference: {mois_ref}.\n"
            f"Anomalies detectees: {anomalies}.\n"
            "Retourne uniquement du JSON: {resume, recommandations[]} "
            "avec un ton concret et actionnable."
        )

        parsed = self.call_with_json_parsing_sync(
            prompt=None,
            response_model=ResumeAnomaliesIA,
            system_prompt=(
                "Tu es un conseiller budget familial pragmatique. "
                "Propose des actions simples, mesurables, en francais."
            ),
            max_tokens=500,
            use_cache=True,
        )

        if parsed is None:
            top = anomalies[0]
            return {
                "resume": (
                    "Derive budget detectee: "
                    f"{top['categorie']} est a +{top['variation_pct']}% vs moyenne N-1/N-2."
                ),
                "recommandations": [
                    "Definir un plafond hebdomadaire par categorie",
                    "Programmer un point budget en milieu de mois",
                    "Verifier les depenses impulsives de la categorie la plus en hausse",
                ],
            }

        return {"resume": parsed.resume, "recommandations": parsed.recommandations}

    def xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_20(self, anomalies: list[dict[str, Any]], mois_ref: str) -> dict[str, Any]:
        """Genere un resume IA court pour le widget dashboard."""
        if not anomalies:
            return {
                "resume": "Aucune derive financiere detectee sur les categories suivies.",
                "recommandations": ["Maintenir le rythme actuel et suivre la tendance chaque semaine."],
            }

        prompt = (
            f"Mois de reference: {mois_ref}.\n"
            f"Anomalies detectees: {anomalies}.\n"
            "Retourne uniquement du JSON: {resume, recommandations[]} "
            "avec un ton concret et actionnable."
        )

        parsed = self.call_with_json_parsing_sync(
            prompt=prompt,
            response_model=None,
            system_prompt=(
                "Tu es un conseiller budget familial pragmatique. "
                "Propose des actions simples, mesurables, en francais."
            ),
            max_tokens=500,
            use_cache=True,
        )

        if parsed is None:
            top = anomalies[0]
            return {
                "resume": (
                    "Derive budget detectee: "
                    f"{top['categorie']} est a +{top['variation_pct']}% vs moyenne N-1/N-2."
                ),
                "recommandations": [
                    "Definir un plafond hebdomadaire par categorie",
                    "Programmer un point budget en milieu de mois",
                    "Verifier les depenses impulsives de la categorie la plus en hausse",
                ],
            }

        return {"resume": parsed.resume, "recommandations": parsed.recommandations}

    def xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_21(self, anomalies: list[dict[str, Any]], mois_ref: str) -> dict[str, Any]:
        """Genere un resume IA court pour le widget dashboard."""
        if not anomalies:
            return {
                "resume": "Aucune derive financiere detectee sur les categories suivies.",
                "recommandations": ["Maintenir le rythme actuel et suivre la tendance chaque semaine."],
            }

        prompt = (
            f"Mois de reference: {mois_ref}.\n"
            f"Anomalies detectees: {anomalies}.\n"
            "Retourne uniquement du JSON: {resume, recommandations[]} "
            "avec un ton concret et actionnable."
        )

        parsed = self.call_with_json_parsing_sync(
            prompt=prompt,
            response_model=ResumeAnomaliesIA,
            system_prompt=None,
            max_tokens=500,
            use_cache=True,
        )

        if parsed is None:
            top = anomalies[0]
            return {
                "resume": (
                    "Derive budget detectee: "
                    f"{top['categorie']} est a +{top['variation_pct']}% vs moyenne N-1/N-2."
                ),
                "recommandations": [
                    "Definir un plafond hebdomadaire par categorie",
                    "Programmer un point budget en milieu de mois",
                    "Verifier les depenses impulsives de la categorie la plus en hausse",
                ],
            }

        return {"resume": parsed.resume, "recommandations": parsed.recommandations}

    def xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_22(self, anomalies: list[dict[str, Any]], mois_ref: str) -> dict[str, Any]:
        """Genere un resume IA court pour le widget dashboard."""
        if not anomalies:
            return {
                "resume": "Aucune derive financiere detectee sur les categories suivies.",
                "recommandations": ["Maintenir le rythme actuel et suivre la tendance chaque semaine."],
            }

        prompt = (
            f"Mois de reference: {mois_ref}.\n"
            f"Anomalies detectees: {anomalies}.\n"
            "Retourne uniquement du JSON: {resume, recommandations[]} "
            "avec un ton concret et actionnable."
        )

        parsed = self.call_with_json_parsing_sync(
            prompt=prompt,
            response_model=ResumeAnomaliesIA,
            system_prompt=(
                "Tu es un conseiller budget familial pragmatique. "
                "Propose des actions simples, mesurables, en francais."
            ),
            max_tokens=None,
            use_cache=True,
        )

        if parsed is None:
            top = anomalies[0]
            return {
                "resume": (
                    "Derive budget detectee: "
                    f"{top['categorie']} est a +{top['variation_pct']}% vs moyenne N-1/N-2."
                ),
                "recommandations": [
                    "Definir un plafond hebdomadaire par categorie",
                    "Programmer un point budget en milieu de mois",
                    "Verifier les depenses impulsives de la categorie la plus en hausse",
                ],
            }

        return {"resume": parsed.resume, "recommandations": parsed.recommandations}

    def xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_23(self, anomalies: list[dict[str, Any]], mois_ref: str) -> dict[str, Any]:
        """Genere un resume IA court pour le widget dashboard."""
        if not anomalies:
            return {
                "resume": "Aucune derive financiere detectee sur les categories suivies.",
                "recommandations": ["Maintenir le rythme actuel et suivre la tendance chaque semaine."],
            }

        prompt = (
            f"Mois de reference: {mois_ref}.\n"
            f"Anomalies detectees: {anomalies}.\n"
            "Retourne uniquement du JSON: {resume, recommandations[]} "
            "avec un ton concret et actionnable."
        )

        parsed = self.call_with_json_parsing_sync(
            prompt=prompt,
            response_model=ResumeAnomaliesIA,
            system_prompt=(
                "Tu es un conseiller budget familial pragmatique. "
                "Propose des actions simples, mesurables, en francais."
            ),
            max_tokens=500,
            use_cache=None,
        )

        if parsed is None:
            top = anomalies[0]
            return {
                "resume": (
                    "Derive budget detectee: "
                    f"{top['categorie']} est a +{top['variation_pct']}% vs moyenne N-1/N-2."
                ),
                "recommandations": [
                    "Definir un plafond hebdomadaire par categorie",
                    "Programmer un point budget en milieu de mois",
                    "Verifier les depenses impulsives de la categorie la plus en hausse",
                ],
            }

        return {"resume": parsed.resume, "recommandations": parsed.recommandations}

    def xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_24(self, anomalies: list[dict[str, Any]], mois_ref: str) -> dict[str, Any]:
        """Genere un resume IA court pour le widget dashboard."""
        if not anomalies:
            return {
                "resume": "Aucune derive financiere detectee sur les categories suivies.",
                "recommandations": ["Maintenir le rythme actuel et suivre la tendance chaque semaine."],
            }

        prompt = (
            f"Mois de reference: {mois_ref}.\n"
            f"Anomalies detectees: {anomalies}.\n"
            "Retourne uniquement du JSON: {resume, recommandations[]} "
            "avec un ton concret et actionnable."
        )

        parsed = self.call_with_json_parsing_sync(
            response_model=ResumeAnomaliesIA,
            system_prompt=(
                "Tu es un conseiller budget familial pragmatique. "
                "Propose des actions simples, mesurables, en francais."
            ),
            max_tokens=500,
            use_cache=True,
        )

        if parsed is None:
            top = anomalies[0]
            return {
                "resume": (
                    "Derive budget detectee: "
                    f"{top['categorie']} est a +{top['variation_pct']}% vs moyenne N-1/N-2."
                ),
                "recommandations": [
                    "Definir un plafond hebdomadaire par categorie",
                    "Programmer un point budget en milieu de mois",
                    "Verifier les depenses impulsives de la categorie la plus en hausse",
                ],
            }

        return {"resume": parsed.resume, "recommandations": parsed.recommandations}

    def xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_25(self, anomalies: list[dict[str, Any]], mois_ref: str) -> dict[str, Any]:
        """Genere un resume IA court pour le widget dashboard."""
        if not anomalies:
            return {
                "resume": "Aucune derive financiere detectee sur les categories suivies.",
                "recommandations": ["Maintenir le rythme actuel et suivre la tendance chaque semaine."],
            }

        prompt = (
            f"Mois de reference: {mois_ref}.\n"
            f"Anomalies detectees: {anomalies}.\n"
            "Retourne uniquement du JSON: {resume, recommandations[]} "
            "avec un ton concret et actionnable."
        )

        parsed = self.call_with_json_parsing_sync(
            prompt=prompt,
            system_prompt=(
                "Tu es un conseiller budget familial pragmatique. "
                "Propose des actions simples, mesurables, en francais."
            ),
            max_tokens=500,
            use_cache=True,
        )

        if parsed is None:
            top = anomalies[0]
            return {
                "resume": (
                    "Derive budget detectee: "
                    f"{top['categorie']} est a +{top['variation_pct']}% vs moyenne N-1/N-2."
                ),
                "recommandations": [
                    "Definir un plafond hebdomadaire par categorie",
                    "Programmer un point budget en milieu de mois",
                    "Verifier les depenses impulsives de la categorie la plus en hausse",
                ],
            }

        return {"resume": parsed.resume, "recommandations": parsed.recommandations}

    def xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_26(self, anomalies: list[dict[str, Any]], mois_ref: str) -> dict[str, Any]:
        """Genere un resume IA court pour le widget dashboard."""
        if not anomalies:
            return {
                "resume": "Aucune derive financiere detectee sur les categories suivies.",
                "recommandations": ["Maintenir le rythme actuel et suivre la tendance chaque semaine."],
            }

        prompt = (
            f"Mois de reference: {mois_ref}.\n"
            f"Anomalies detectees: {anomalies}.\n"
            "Retourne uniquement du JSON: {resume, recommandations[]} "
            "avec un ton concret et actionnable."
        )

        parsed = self.call_with_json_parsing_sync(
            prompt=prompt,
            response_model=ResumeAnomaliesIA,
            max_tokens=500,
            use_cache=True,
        )

        if parsed is None:
            top = anomalies[0]
            return {
                "resume": (
                    "Derive budget detectee: "
                    f"{top['categorie']} est a +{top['variation_pct']}% vs moyenne N-1/N-2."
                ),
                "recommandations": [
                    "Definir un plafond hebdomadaire par categorie",
                    "Programmer un point budget en milieu de mois",
                    "Verifier les depenses impulsives de la categorie la plus en hausse",
                ],
            }

        return {"resume": parsed.resume, "recommandations": parsed.recommandations}

    def xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_27(self, anomalies: list[dict[str, Any]], mois_ref: str) -> dict[str, Any]:
        """Genere un resume IA court pour le widget dashboard."""
        if not anomalies:
            return {
                "resume": "Aucune derive financiere detectee sur les categories suivies.",
                "recommandations": ["Maintenir le rythme actuel et suivre la tendance chaque semaine."],
            }

        prompt = (
            f"Mois de reference: {mois_ref}.\n"
            f"Anomalies detectees: {anomalies}.\n"
            "Retourne uniquement du JSON: {resume, recommandations[]} "
            "avec un ton concret et actionnable."
        )

        parsed = self.call_with_json_parsing_sync(
            prompt=prompt,
            response_model=ResumeAnomaliesIA,
            system_prompt=(
                "Tu es un conseiller budget familial pragmatique. "
                "Propose des actions simples, mesurables, en francais."
            ),
            use_cache=True,
        )

        if parsed is None:
            top = anomalies[0]
            return {
                "resume": (
                    "Derive budget detectee: "
                    f"{top['categorie']} est a +{top['variation_pct']}% vs moyenne N-1/N-2."
                ),
                "recommandations": [
                    "Definir un plafond hebdomadaire par categorie",
                    "Programmer un point budget en milieu de mois",
                    "Verifier les depenses impulsives de la categorie la plus en hausse",
                ],
            }

        return {"resume": parsed.resume, "recommandations": parsed.recommandations}

    def xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_28(self, anomalies: list[dict[str, Any]], mois_ref: str) -> dict[str, Any]:
        """Genere un resume IA court pour le widget dashboard."""
        if not anomalies:
            return {
                "resume": "Aucune derive financiere detectee sur les categories suivies.",
                "recommandations": ["Maintenir le rythme actuel et suivre la tendance chaque semaine."],
            }

        prompt = (
            f"Mois de reference: {mois_ref}.\n"
            f"Anomalies detectees: {anomalies}.\n"
            "Retourne uniquement du JSON: {resume, recommandations[]} "
            "avec un ton concret et actionnable."
        )

        parsed = self.call_with_json_parsing_sync(
            prompt=prompt,
            response_model=ResumeAnomaliesIA,
            system_prompt=(
                "Tu es un conseiller budget familial pragmatique. "
                "Propose des actions simples, mesurables, en francais."
            ),
            max_tokens=500,
            )

        if parsed is None:
            top = anomalies[0]
            return {
                "resume": (
                    "Derive budget detectee: "
                    f"{top['categorie']} est a +{top['variation_pct']}% vs moyenne N-1/N-2."
                ),
                "recommandations": [
                    "Definir un plafond hebdomadaire par categorie",
                    "Programmer un point budget en milieu de mois",
                    "Verifier les depenses impulsives de la categorie la plus en hausse",
                ],
            }

        return {"resume": parsed.resume, "recommandations": parsed.recommandations}

    def xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_29(self, anomalies: list[dict[str, Any]], mois_ref: str) -> dict[str, Any]:
        """Genere un resume IA court pour le widget dashboard."""
        if not anomalies:
            return {
                "resume": "Aucune derive financiere detectee sur les categories suivies.",
                "recommandations": ["Maintenir le rythme actuel et suivre la tendance chaque semaine."],
            }

        prompt = (
            f"Mois de reference: {mois_ref}.\n"
            f"Anomalies detectees: {anomalies}.\n"
            "Retourne uniquement du JSON: {resume, recommandations[]} "
            "avec un ton concret et actionnable."
        )

        parsed = self.call_with_json_parsing_sync(
            prompt=prompt,
            response_model=ResumeAnomaliesIA,
            system_prompt=(
                "XXTu es un conseiller budget familial pragmatique. XX"
                "Propose des actions simples, mesurables, en francais."
            ),
            max_tokens=500,
            use_cache=True,
        )

        if parsed is None:
            top = anomalies[0]
            return {
                "resume": (
                    "Derive budget detectee: "
                    f"{top['categorie']} est a +{top['variation_pct']}% vs moyenne N-1/N-2."
                ),
                "recommandations": [
                    "Definir un plafond hebdomadaire par categorie",
                    "Programmer un point budget en milieu de mois",
                    "Verifier les depenses impulsives de la categorie la plus en hausse",
                ],
            }

        return {"resume": parsed.resume, "recommandations": parsed.recommandations}

    def xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_30(self, anomalies: list[dict[str, Any]], mois_ref: str) -> dict[str, Any]:
        """Genere un resume IA court pour le widget dashboard."""
        if not anomalies:
            return {
                "resume": "Aucune derive financiere detectee sur les categories suivies.",
                "recommandations": ["Maintenir le rythme actuel et suivre la tendance chaque semaine."],
            }

        prompt = (
            f"Mois de reference: {mois_ref}.\n"
            f"Anomalies detectees: {anomalies}.\n"
            "Retourne uniquement du JSON: {resume, recommandations[]} "
            "avec un ton concret et actionnable."
        )

        parsed = self.call_with_json_parsing_sync(
            prompt=prompt,
            response_model=ResumeAnomaliesIA,
            system_prompt=(
                "tu es un conseiller budget familial pragmatique. "
                "Propose des actions simples, mesurables, en francais."
            ),
            max_tokens=500,
            use_cache=True,
        )

        if parsed is None:
            top = anomalies[0]
            return {
                "resume": (
                    "Derive budget detectee: "
                    f"{top['categorie']} est a +{top['variation_pct']}% vs moyenne N-1/N-2."
                ),
                "recommandations": [
                    "Definir un plafond hebdomadaire par categorie",
                    "Programmer un point budget en milieu de mois",
                    "Verifier les depenses impulsives de la categorie la plus en hausse",
                ],
            }

        return {"resume": parsed.resume, "recommandations": parsed.recommandations}

    def xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_31(self, anomalies: list[dict[str, Any]], mois_ref: str) -> dict[str, Any]:
        """Genere un resume IA court pour le widget dashboard."""
        if not anomalies:
            return {
                "resume": "Aucune derive financiere detectee sur les categories suivies.",
                "recommandations": ["Maintenir le rythme actuel et suivre la tendance chaque semaine."],
            }

        prompt = (
            f"Mois de reference: {mois_ref}.\n"
            f"Anomalies detectees: {anomalies}.\n"
            "Retourne uniquement du JSON: {resume, recommandations[]} "
            "avec un ton concret et actionnable."
        )

        parsed = self.call_with_json_parsing_sync(
            prompt=prompt,
            response_model=ResumeAnomaliesIA,
            system_prompt=(
                "TU ES UN CONSEILLER BUDGET FAMILIAL PRAGMATIQUE. "
                "Propose des actions simples, mesurables, en francais."
            ),
            max_tokens=500,
            use_cache=True,
        )

        if parsed is None:
            top = anomalies[0]
            return {
                "resume": (
                    "Derive budget detectee: "
                    f"{top['categorie']} est a +{top['variation_pct']}% vs moyenne N-1/N-2."
                ),
                "recommandations": [
                    "Definir un plafond hebdomadaire par categorie",
                    "Programmer un point budget en milieu de mois",
                    "Verifier les depenses impulsives de la categorie la plus en hausse",
                ],
            }

        return {"resume": parsed.resume, "recommandations": parsed.recommandations}

    def xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_32(self, anomalies: list[dict[str, Any]], mois_ref: str) -> dict[str, Any]:
        """Genere un resume IA court pour le widget dashboard."""
        if not anomalies:
            return {
                "resume": "Aucune derive financiere detectee sur les categories suivies.",
                "recommandations": ["Maintenir le rythme actuel et suivre la tendance chaque semaine."],
            }

        prompt = (
            f"Mois de reference: {mois_ref}.\n"
            f"Anomalies detectees: {anomalies}.\n"
            "Retourne uniquement du JSON: {resume, recommandations[]} "
            "avec un ton concret et actionnable."
        )

        parsed = self.call_with_json_parsing_sync(
            prompt=prompt,
            response_model=ResumeAnomaliesIA,
            system_prompt=(
                "Tu es un conseiller budget familial pragmatique. "
                "XXPropose des actions simples, mesurables, en francais.XX"
            ),
            max_tokens=500,
            use_cache=True,
        )

        if parsed is None:
            top = anomalies[0]
            return {
                "resume": (
                    "Derive budget detectee: "
                    f"{top['categorie']} est a +{top['variation_pct']}% vs moyenne N-1/N-2."
                ),
                "recommandations": [
                    "Definir un plafond hebdomadaire par categorie",
                    "Programmer un point budget en milieu de mois",
                    "Verifier les depenses impulsives de la categorie la plus en hausse",
                ],
            }

        return {"resume": parsed.resume, "recommandations": parsed.recommandations}

    def xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_33(self, anomalies: list[dict[str, Any]], mois_ref: str) -> dict[str, Any]:
        """Genere un resume IA court pour le widget dashboard."""
        if not anomalies:
            return {
                "resume": "Aucune derive financiere detectee sur les categories suivies.",
                "recommandations": ["Maintenir le rythme actuel et suivre la tendance chaque semaine."],
            }

        prompt = (
            f"Mois de reference: {mois_ref}.\n"
            f"Anomalies detectees: {anomalies}.\n"
            "Retourne uniquement du JSON: {resume, recommandations[]} "
            "avec un ton concret et actionnable."
        )

        parsed = self.call_with_json_parsing_sync(
            prompt=prompt,
            response_model=ResumeAnomaliesIA,
            system_prompt=(
                "Tu es un conseiller budget familial pragmatique. "
                "propose des actions simples, mesurables, en francais."
            ),
            max_tokens=500,
            use_cache=True,
        )

        if parsed is None:
            top = anomalies[0]
            return {
                "resume": (
                    "Derive budget detectee: "
                    f"{top['categorie']} est a +{top['variation_pct']}% vs moyenne N-1/N-2."
                ),
                "recommandations": [
                    "Definir un plafond hebdomadaire par categorie",
                    "Programmer un point budget en milieu de mois",
                    "Verifier les depenses impulsives de la categorie la plus en hausse",
                ],
            }

        return {"resume": parsed.resume, "recommandations": parsed.recommandations}

    def xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_34(self, anomalies: list[dict[str, Any]], mois_ref: str) -> dict[str, Any]:
        """Genere un resume IA court pour le widget dashboard."""
        if not anomalies:
            return {
                "resume": "Aucune derive financiere detectee sur les categories suivies.",
                "recommandations": ["Maintenir le rythme actuel et suivre la tendance chaque semaine."],
            }

        prompt = (
            f"Mois de reference: {mois_ref}.\n"
            f"Anomalies detectees: {anomalies}.\n"
            "Retourne uniquement du JSON: {resume, recommandations[]} "
            "avec un ton concret et actionnable."
        )

        parsed = self.call_with_json_parsing_sync(
            prompt=prompt,
            response_model=ResumeAnomaliesIA,
            system_prompt=(
                "Tu es un conseiller budget familial pragmatique. "
                "PROPOSE DES ACTIONS SIMPLES, MESURABLES, EN FRANCAIS."
            ),
            max_tokens=500,
            use_cache=True,
        )

        if parsed is None:
            top = anomalies[0]
            return {
                "resume": (
                    "Derive budget detectee: "
                    f"{top['categorie']} est a +{top['variation_pct']}% vs moyenne N-1/N-2."
                ),
                "recommandations": [
                    "Definir un plafond hebdomadaire par categorie",
                    "Programmer un point budget en milieu de mois",
                    "Verifier les depenses impulsives de la categorie la plus en hausse",
                ],
            }

        return {"resume": parsed.resume, "recommandations": parsed.recommandations}

    def xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_35(self, anomalies: list[dict[str, Any]], mois_ref: str) -> dict[str, Any]:
        """Genere un resume IA court pour le widget dashboard."""
        if not anomalies:
            return {
                "resume": "Aucune derive financiere detectee sur les categories suivies.",
                "recommandations": ["Maintenir le rythme actuel et suivre la tendance chaque semaine."],
            }

        prompt = (
            f"Mois de reference: {mois_ref}.\n"
            f"Anomalies detectees: {anomalies}.\n"
            "Retourne uniquement du JSON: {resume, recommandations[]} "
            "avec un ton concret et actionnable."
        )

        parsed = self.call_with_json_parsing_sync(
            prompt=prompt,
            response_model=ResumeAnomaliesIA,
            system_prompt=(
                "Tu es un conseiller budget familial pragmatique. "
                "Propose des actions simples, mesurables, en francais."
            ),
            max_tokens=501,
            use_cache=True,
        )

        if parsed is None:
            top = anomalies[0]
            return {
                "resume": (
                    "Derive budget detectee: "
                    f"{top['categorie']} est a +{top['variation_pct']}% vs moyenne N-1/N-2."
                ),
                "recommandations": [
                    "Definir un plafond hebdomadaire par categorie",
                    "Programmer un point budget en milieu de mois",
                    "Verifier les depenses impulsives de la categorie la plus en hausse",
                ],
            }

        return {"resume": parsed.resume, "recommandations": parsed.recommandations}

    def xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_36(self, anomalies: list[dict[str, Any]], mois_ref: str) -> dict[str, Any]:
        """Genere un resume IA court pour le widget dashboard."""
        if not anomalies:
            return {
                "resume": "Aucune derive financiere detectee sur les categories suivies.",
                "recommandations": ["Maintenir le rythme actuel et suivre la tendance chaque semaine."],
            }

        prompt = (
            f"Mois de reference: {mois_ref}.\n"
            f"Anomalies detectees: {anomalies}.\n"
            "Retourne uniquement du JSON: {resume, recommandations[]} "
            "avec un ton concret et actionnable."
        )

        parsed = self.call_with_json_parsing_sync(
            prompt=prompt,
            response_model=ResumeAnomaliesIA,
            system_prompt=(
                "Tu es un conseiller budget familial pragmatique. "
                "Propose des actions simples, mesurables, en francais."
            ),
            max_tokens=500,
            use_cache=False,
        )

        if parsed is None:
            top = anomalies[0]
            return {
                "resume": (
                    "Derive budget detectee: "
                    f"{top['categorie']} est a +{top['variation_pct']}% vs moyenne N-1/N-2."
                ),
                "recommandations": [
                    "Definir un plafond hebdomadaire par categorie",
                    "Programmer un point budget en milieu de mois",
                    "Verifier les depenses impulsives de la categorie la plus en hausse",
                ],
            }

        return {"resume": parsed.resume, "recommandations": parsed.recommandations}

    def xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_37(self, anomalies: list[dict[str, Any]], mois_ref: str) -> dict[str, Any]:
        """Genere un resume IA court pour le widget dashboard."""
        if not anomalies:
            return {
                "resume": "Aucune derive financiere detectee sur les categories suivies.",
                "recommandations": ["Maintenir le rythme actuel et suivre la tendance chaque semaine."],
            }

        prompt = (
            f"Mois de reference: {mois_ref}.\n"
            f"Anomalies detectees: {anomalies}.\n"
            "Retourne uniquement du JSON: {resume, recommandations[]} "
            "avec un ton concret et actionnable."
        )

        parsed = self.call_with_json_parsing_sync(
            prompt=prompt,
            response_model=ResumeAnomaliesIA,
            system_prompt=(
                "Tu es un conseiller budget familial pragmatique. "
                "Propose des actions simples, mesurables, en francais."
            ),
            max_tokens=500,
            use_cache=True,
        )

        if parsed is not None:
            top = anomalies[0]
            return {
                "resume": (
                    "Derive budget detectee: "
                    f"{top['categorie']} est a +{top['variation_pct']}% vs moyenne N-1/N-2."
                ),
                "recommandations": [
                    "Definir un plafond hebdomadaire par categorie",
                    "Programmer un point budget en milieu de mois",
                    "Verifier les depenses impulsives de la categorie la plus en hausse",
                ],
            }

        return {"resume": parsed.resume, "recommandations": parsed.recommandations}

    def xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_38(self, anomalies: list[dict[str, Any]], mois_ref: str) -> dict[str, Any]:
        """Genere un resume IA court pour le widget dashboard."""
        if not anomalies:
            return {
                "resume": "Aucune derive financiere detectee sur les categories suivies.",
                "recommandations": ["Maintenir le rythme actuel et suivre la tendance chaque semaine."],
            }

        prompt = (
            f"Mois de reference: {mois_ref}.\n"
            f"Anomalies detectees: {anomalies}.\n"
            "Retourne uniquement du JSON: {resume, recommandations[]} "
            "avec un ton concret et actionnable."
        )

        parsed = self.call_with_json_parsing_sync(
            prompt=prompt,
            response_model=ResumeAnomaliesIA,
            system_prompt=(
                "Tu es un conseiller budget familial pragmatique. "
                "Propose des actions simples, mesurables, en francais."
            ),
            max_tokens=500,
            use_cache=True,
        )

        if parsed is None:
            top = None
            return {
                "resume": (
                    "Derive budget detectee: "
                    f"{top['categorie']} est a +{top['variation_pct']}% vs moyenne N-1/N-2."
                ),
                "recommandations": [
                    "Definir un plafond hebdomadaire par categorie",
                    "Programmer un point budget en milieu de mois",
                    "Verifier les depenses impulsives de la categorie la plus en hausse",
                ],
            }

        return {"resume": parsed.resume, "recommandations": parsed.recommandations}

    def xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_39(self, anomalies: list[dict[str, Any]], mois_ref: str) -> dict[str, Any]:
        """Genere un resume IA court pour le widget dashboard."""
        if not anomalies:
            return {
                "resume": "Aucune derive financiere detectee sur les categories suivies.",
                "recommandations": ["Maintenir le rythme actuel et suivre la tendance chaque semaine."],
            }

        prompt = (
            f"Mois de reference: {mois_ref}.\n"
            f"Anomalies detectees: {anomalies}.\n"
            "Retourne uniquement du JSON: {resume, recommandations[]} "
            "avec un ton concret et actionnable."
        )

        parsed = self.call_with_json_parsing_sync(
            prompt=prompt,
            response_model=ResumeAnomaliesIA,
            system_prompt=(
                "Tu es un conseiller budget familial pragmatique. "
                "Propose des actions simples, mesurables, en francais."
            ),
            max_tokens=500,
            use_cache=True,
        )

        if parsed is None:
            top = anomalies[1]
            return {
                "resume": (
                    "Derive budget detectee: "
                    f"{top['categorie']} est a +{top['variation_pct']}% vs moyenne N-1/N-2."
                ),
                "recommandations": [
                    "Definir un plafond hebdomadaire par categorie",
                    "Programmer un point budget en milieu de mois",
                    "Verifier les depenses impulsives de la categorie la plus en hausse",
                ],
            }

        return {"resume": parsed.resume, "recommandations": parsed.recommandations}

    def xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_40(self, anomalies: list[dict[str, Any]], mois_ref: str) -> dict[str, Any]:
        """Genere un resume IA court pour le widget dashboard."""
        if not anomalies:
            return {
                "resume": "Aucune derive financiere detectee sur les categories suivies.",
                "recommandations": ["Maintenir le rythme actuel et suivre la tendance chaque semaine."],
            }

        prompt = (
            f"Mois de reference: {mois_ref}.\n"
            f"Anomalies detectees: {anomalies}.\n"
            "Retourne uniquement du JSON: {resume, recommandations[]} "
            "avec un ton concret et actionnable."
        )

        parsed = self.call_with_json_parsing_sync(
            prompt=prompt,
            response_model=ResumeAnomaliesIA,
            system_prompt=(
                "Tu es un conseiller budget familial pragmatique. "
                "Propose des actions simples, mesurables, en francais."
            ),
            max_tokens=500,
            use_cache=True,
        )

        if parsed is None:
            top = anomalies[0]
            return {
                "XXresumeXX": (
                    "Derive budget detectee: "
                    f"{top['categorie']} est a +{top['variation_pct']}% vs moyenne N-1/N-2."
                ),
                "recommandations": [
                    "Definir un plafond hebdomadaire par categorie",
                    "Programmer un point budget en milieu de mois",
                    "Verifier les depenses impulsives de la categorie la plus en hausse",
                ],
            }

        return {"resume": parsed.resume, "recommandations": parsed.recommandations}

    def xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_41(self, anomalies: list[dict[str, Any]], mois_ref: str) -> dict[str, Any]:
        """Genere un resume IA court pour le widget dashboard."""
        if not anomalies:
            return {
                "resume": "Aucune derive financiere detectee sur les categories suivies.",
                "recommandations": ["Maintenir le rythme actuel et suivre la tendance chaque semaine."],
            }

        prompt = (
            f"Mois de reference: {mois_ref}.\n"
            f"Anomalies detectees: {anomalies}.\n"
            "Retourne uniquement du JSON: {resume, recommandations[]} "
            "avec un ton concret et actionnable."
        )

        parsed = self.call_with_json_parsing_sync(
            prompt=prompt,
            response_model=ResumeAnomaliesIA,
            system_prompt=(
                "Tu es un conseiller budget familial pragmatique. "
                "Propose des actions simples, mesurables, en francais."
            ),
            max_tokens=500,
            use_cache=True,
        )

        if parsed is None:
            top = anomalies[0]
            return {
                "RESUME": (
                    "Derive budget detectee: "
                    f"{top['categorie']} est a +{top['variation_pct']}% vs moyenne N-1/N-2."
                ),
                "recommandations": [
                    "Definir un plafond hebdomadaire par categorie",
                    "Programmer un point budget en milieu de mois",
                    "Verifier les depenses impulsives de la categorie la plus en hausse",
                ],
            }

        return {"resume": parsed.resume, "recommandations": parsed.recommandations}

    def xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_42(self, anomalies: list[dict[str, Any]], mois_ref: str) -> dict[str, Any]:
        """Genere un resume IA court pour le widget dashboard."""
        if not anomalies:
            return {
                "resume": "Aucune derive financiere detectee sur les categories suivies.",
                "recommandations": ["Maintenir le rythme actuel et suivre la tendance chaque semaine."],
            }

        prompt = (
            f"Mois de reference: {mois_ref}.\n"
            f"Anomalies detectees: {anomalies}.\n"
            "Retourne uniquement du JSON: {resume, recommandations[]} "
            "avec un ton concret et actionnable."
        )

        parsed = self.call_with_json_parsing_sync(
            prompt=prompt,
            response_model=ResumeAnomaliesIA,
            system_prompt=(
                "Tu es un conseiller budget familial pragmatique. "
                "Propose des actions simples, mesurables, en francais."
            ),
            max_tokens=500,
            use_cache=True,
        )

        if parsed is None:
            top = anomalies[0]
            return {
                "resume": (
                    "XXDerive budget detectee: XX"
                    f"{top['categorie']} est a +{top['variation_pct']}% vs moyenne N-1/N-2."
                ),
                "recommandations": [
                    "Definir un plafond hebdomadaire par categorie",
                    "Programmer un point budget en milieu de mois",
                    "Verifier les depenses impulsives de la categorie la plus en hausse",
                ],
            }

        return {"resume": parsed.resume, "recommandations": parsed.recommandations}

    def xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_43(self, anomalies: list[dict[str, Any]], mois_ref: str) -> dict[str, Any]:
        """Genere un resume IA court pour le widget dashboard."""
        if not anomalies:
            return {
                "resume": "Aucune derive financiere detectee sur les categories suivies.",
                "recommandations": ["Maintenir le rythme actuel et suivre la tendance chaque semaine."],
            }

        prompt = (
            f"Mois de reference: {mois_ref}.\n"
            f"Anomalies detectees: {anomalies}.\n"
            "Retourne uniquement du JSON: {resume, recommandations[]} "
            "avec un ton concret et actionnable."
        )

        parsed = self.call_with_json_parsing_sync(
            prompt=prompt,
            response_model=ResumeAnomaliesIA,
            system_prompt=(
                "Tu es un conseiller budget familial pragmatique. "
                "Propose des actions simples, mesurables, en francais."
            ),
            max_tokens=500,
            use_cache=True,
        )

        if parsed is None:
            top = anomalies[0]
            return {
                "resume": (
                    "derive budget detectee: "
                    f"{top['categorie']} est a +{top['variation_pct']}% vs moyenne N-1/N-2."
                ),
                "recommandations": [
                    "Definir un plafond hebdomadaire par categorie",
                    "Programmer un point budget en milieu de mois",
                    "Verifier les depenses impulsives de la categorie la plus en hausse",
                ],
            }

        return {"resume": parsed.resume, "recommandations": parsed.recommandations}

    def xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_44(self, anomalies: list[dict[str, Any]], mois_ref: str) -> dict[str, Any]:
        """Genere un resume IA court pour le widget dashboard."""
        if not anomalies:
            return {
                "resume": "Aucune derive financiere detectee sur les categories suivies.",
                "recommandations": ["Maintenir le rythme actuel et suivre la tendance chaque semaine."],
            }

        prompt = (
            f"Mois de reference: {mois_ref}.\n"
            f"Anomalies detectees: {anomalies}.\n"
            "Retourne uniquement du JSON: {resume, recommandations[]} "
            "avec un ton concret et actionnable."
        )

        parsed = self.call_with_json_parsing_sync(
            prompt=prompt,
            response_model=ResumeAnomaliesIA,
            system_prompt=(
                "Tu es un conseiller budget familial pragmatique. "
                "Propose des actions simples, mesurables, en francais."
            ),
            max_tokens=500,
            use_cache=True,
        )

        if parsed is None:
            top = anomalies[0]
            return {
                "resume": (
                    "DERIVE BUDGET DETECTEE: "
                    f"{top['categorie']} est a +{top['variation_pct']}% vs moyenne N-1/N-2."
                ),
                "recommandations": [
                    "Definir un plafond hebdomadaire par categorie",
                    "Programmer un point budget en milieu de mois",
                    "Verifier les depenses impulsives de la categorie la plus en hausse",
                ],
            }

        return {"resume": parsed.resume, "recommandations": parsed.recommandations}

    def xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_45(self, anomalies: list[dict[str, Any]], mois_ref: str) -> dict[str, Any]:
        """Genere un resume IA court pour le widget dashboard."""
        if not anomalies:
            return {
                "resume": "Aucune derive financiere detectee sur les categories suivies.",
                "recommandations": ["Maintenir le rythme actuel et suivre la tendance chaque semaine."],
            }

        prompt = (
            f"Mois de reference: {mois_ref}.\n"
            f"Anomalies detectees: {anomalies}.\n"
            "Retourne uniquement du JSON: {resume, recommandations[]} "
            "avec un ton concret et actionnable."
        )

        parsed = self.call_with_json_parsing_sync(
            prompt=prompt,
            response_model=ResumeAnomaliesIA,
            system_prompt=(
                "Tu es un conseiller budget familial pragmatique. "
                "Propose des actions simples, mesurables, en francais."
            ),
            max_tokens=500,
            use_cache=True,
        )

        if parsed is None:
            top = anomalies[0]
            return {
                "resume": (
                    "Derive budget detectee: "
                    f"{top['XXcategorieXX']} est a +{top['variation_pct']}% vs moyenne N-1/N-2."
                ),
                "recommandations": [
                    "Definir un plafond hebdomadaire par categorie",
                    "Programmer un point budget en milieu de mois",
                    "Verifier les depenses impulsives de la categorie la plus en hausse",
                ],
            }

        return {"resume": parsed.resume, "recommandations": parsed.recommandations}

    def xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_46(self, anomalies: list[dict[str, Any]], mois_ref: str) -> dict[str, Any]:
        """Genere un resume IA court pour le widget dashboard."""
        if not anomalies:
            return {
                "resume": "Aucune derive financiere detectee sur les categories suivies.",
                "recommandations": ["Maintenir le rythme actuel et suivre la tendance chaque semaine."],
            }

        prompt = (
            f"Mois de reference: {mois_ref}.\n"
            f"Anomalies detectees: {anomalies}.\n"
            "Retourne uniquement du JSON: {resume, recommandations[]} "
            "avec un ton concret et actionnable."
        )

        parsed = self.call_with_json_parsing_sync(
            prompt=prompt,
            response_model=ResumeAnomaliesIA,
            system_prompt=(
                "Tu es un conseiller budget familial pragmatique. "
                "Propose des actions simples, mesurables, en francais."
            ),
            max_tokens=500,
            use_cache=True,
        )

        if parsed is None:
            top = anomalies[0]
            return {
                "resume": (
                    "Derive budget detectee: "
                    f"{top['CATEGORIE']} est a +{top['variation_pct']}% vs moyenne N-1/N-2."
                ),
                "recommandations": [
                    "Definir un plafond hebdomadaire par categorie",
                    "Programmer un point budget en milieu de mois",
                    "Verifier les depenses impulsives de la categorie la plus en hausse",
                ],
            }

        return {"resume": parsed.resume, "recommandations": parsed.recommandations}

    def xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_47(self, anomalies: list[dict[str, Any]], mois_ref: str) -> dict[str, Any]:
        """Genere un resume IA court pour le widget dashboard."""
        if not anomalies:
            return {
                "resume": "Aucune derive financiere detectee sur les categories suivies.",
                "recommandations": ["Maintenir le rythme actuel et suivre la tendance chaque semaine."],
            }

        prompt = (
            f"Mois de reference: {mois_ref}.\n"
            f"Anomalies detectees: {anomalies}.\n"
            "Retourne uniquement du JSON: {resume, recommandations[]} "
            "avec un ton concret et actionnable."
        )

        parsed = self.call_with_json_parsing_sync(
            prompt=prompt,
            response_model=ResumeAnomaliesIA,
            system_prompt=(
                "Tu es un conseiller budget familial pragmatique. "
                "Propose des actions simples, mesurables, en francais."
            ),
            max_tokens=500,
            use_cache=True,
        )

        if parsed is None:
            top = anomalies[0]
            return {
                "resume": (
                    "Derive budget detectee: "
                    f"{top['categorie']} est a +{top['XXvariation_pctXX']}% vs moyenne N-1/N-2."
                ),
                "recommandations": [
                    "Definir un plafond hebdomadaire par categorie",
                    "Programmer un point budget en milieu de mois",
                    "Verifier les depenses impulsives de la categorie la plus en hausse",
                ],
            }

        return {"resume": parsed.resume, "recommandations": parsed.recommandations}

    def xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_48(self, anomalies: list[dict[str, Any]], mois_ref: str) -> dict[str, Any]:
        """Genere un resume IA court pour le widget dashboard."""
        if not anomalies:
            return {
                "resume": "Aucune derive financiere detectee sur les categories suivies.",
                "recommandations": ["Maintenir le rythme actuel et suivre la tendance chaque semaine."],
            }

        prompt = (
            f"Mois de reference: {mois_ref}.\n"
            f"Anomalies detectees: {anomalies}.\n"
            "Retourne uniquement du JSON: {resume, recommandations[]} "
            "avec un ton concret et actionnable."
        )

        parsed = self.call_with_json_parsing_sync(
            prompt=prompt,
            response_model=ResumeAnomaliesIA,
            system_prompt=(
                "Tu es un conseiller budget familial pragmatique. "
                "Propose des actions simples, mesurables, en francais."
            ),
            max_tokens=500,
            use_cache=True,
        )

        if parsed is None:
            top = anomalies[0]
            return {
                "resume": (
                    "Derive budget detectee: "
                    f"{top['categorie']} est a +{top['VARIATION_PCT']}% vs moyenne N-1/N-2."
                ),
                "recommandations": [
                    "Definir un plafond hebdomadaire par categorie",
                    "Programmer un point budget en milieu de mois",
                    "Verifier les depenses impulsives de la categorie la plus en hausse",
                ],
            }

        return {"resume": parsed.resume, "recommandations": parsed.recommandations}

    def xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_49(self, anomalies: list[dict[str, Any]], mois_ref: str) -> dict[str, Any]:
        """Genere un resume IA court pour le widget dashboard."""
        if not anomalies:
            return {
                "resume": "Aucune derive financiere detectee sur les categories suivies.",
                "recommandations": ["Maintenir le rythme actuel et suivre la tendance chaque semaine."],
            }

        prompt = (
            f"Mois de reference: {mois_ref}.\n"
            f"Anomalies detectees: {anomalies}.\n"
            "Retourne uniquement du JSON: {resume, recommandations[]} "
            "avec un ton concret et actionnable."
        )

        parsed = self.call_with_json_parsing_sync(
            prompt=prompt,
            response_model=ResumeAnomaliesIA,
            system_prompt=(
                "Tu es un conseiller budget familial pragmatique. "
                "Propose des actions simples, mesurables, en francais."
            ),
            max_tokens=500,
            use_cache=True,
        )

        if parsed is None:
            top = anomalies[0]
            return {
                "resume": (
                    "Derive budget detectee: "
                    f"{top['categorie']} est a +{top['variation_pct']}% vs moyenne N-1/N-2."
                ),
                "XXrecommandationsXX": [
                    "Definir un plafond hebdomadaire par categorie",
                    "Programmer un point budget en milieu de mois",
                    "Verifier les depenses impulsives de la categorie la plus en hausse",
                ],
            }

        return {"resume": parsed.resume, "recommandations": parsed.recommandations}

    def xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_50(self, anomalies: list[dict[str, Any]], mois_ref: str) -> dict[str, Any]:
        """Genere un resume IA court pour le widget dashboard."""
        if not anomalies:
            return {
                "resume": "Aucune derive financiere detectee sur les categories suivies.",
                "recommandations": ["Maintenir le rythme actuel et suivre la tendance chaque semaine."],
            }

        prompt = (
            f"Mois de reference: {mois_ref}.\n"
            f"Anomalies detectees: {anomalies}.\n"
            "Retourne uniquement du JSON: {resume, recommandations[]} "
            "avec un ton concret et actionnable."
        )

        parsed = self.call_with_json_parsing_sync(
            prompt=prompt,
            response_model=ResumeAnomaliesIA,
            system_prompt=(
                "Tu es un conseiller budget familial pragmatique. "
                "Propose des actions simples, mesurables, en francais."
            ),
            max_tokens=500,
            use_cache=True,
        )

        if parsed is None:
            top = anomalies[0]
            return {
                "resume": (
                    "Derive budget detectee: "
                    f"{top['categorie']} est a +{top['variation_pct']}% vs moyenne N-1/N-2."
                ),
                "RECOMMANDATIONS": [
                    "Definir un plafond hebdomadaire par categorie",
                    "Programmer un point budget en milieu de mois",
                    "Verifier les depenses impulsives de la categorie la plus en hausse",
                ],
            }

        return {"resume": parsed.resume, "recommandations": parsed.recommandations}

    def xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_51(self, anomalies: list[dict[str, Any]], mois_ref: str) -> dict[str, Any]:
        """Genere un resume IA court pour le widget dashboard."""
        if not anomalies:
            return {
                "resume": "Aucune derive financiere detectee sur les categories suivies.",
                "recommandations": ["Maintenir le rythme actuel et suivre la tendance chaque semaine."],
            }

        prompt = (
            f"Mois de reference: {mois_ref}.\n"
            f"Anomalies detectees: {anomalies}.\n"
            "Retourne uniquement du JSON: {resume, recommandations[]} "
            "avec un ton concret et actionnable."
        )

        parsed = self.call_with_json_parsing_sync(
            prompt=prompt,
            response_model=ResumeAnomaliesIA,
            system_prompt=(
                "Tu es un conseiller budget familial pragmatique. "
                "Propose des actions simples, mesurables, en francais."
            ),
            max_tokens=500,
            use_cache=True,
        )

        if parsed is None:
            top = anomalies[0]
            return {
                "resume": (
                    "Derive budget detectee: "
                    f"{top['categorie']} est a +{top['variation_pct']}% vs moyenne N-1/N-2."
                ),
                "recommandations": [
                    "XXDefinir un plafond hebdomadaire par categorieXX",
                    "Programmer un point budget en milieu de mois",
                    "Verifier les depenses impulsives de la categorie la plus en hausse",
                ],
            }

        return {"resume": parsed.resume, "recommandations": parsed.recommandations}

    def xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_52(self, anomalies: list[dict[str, Any]], mois_ref: str) -> dict[str, Any]:
        """Genere un resume IA court pour le widget dashboard."""
        if not anomalies:
            return {
                "resume": "Aucune derive financiere detectee sur les categories suivies.",
                "recommandations": ["Maintenir le rythme actuel et suivre la tendance chaque semaine."],
            }

        prompt = (
            f"Mois de reference: {mois_ref}.\n"
            f"Anomalies detectees: {anomalies}.\n"
            "Retourne uniquement du JSON: {resume, recommandations[]} "
            "avec un ton concret et actionnable."
        )

        parsed = self.call_with_json_parsing_sync(
            prompt=prompt,
            response_model=ResumeAnomaliesIA,
            system_prompt=(
                "Tu es un conseiller budget familial pragmatique. "
                "Propose des actions simples, mesurables, en francais."
            ),
            max_tokens=500,
            use_cache=True,
        )

        if parsed is None:
            top = anomalies[0]
            return {
                "resume": (
                    "Derive budget detectee: "
                    f"{top['categorie']} est a +{top['variation_pct']}% vs moyenne N-1/N-2."
                ),
                "recommandations": [
                    "definir un plafond hebdomadaire par categorie",
                    "Programmer un point budget en milieu de mois",
                    "Verifier les depenses impulsives de la categorie la plus en hausse",
                ],
            }

        return {"resume": parsed.resume, "recommandations": parsed.recommandations}

    def xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_53(self, anomalies: list[dict[str, Any]], mois_ref: str) -> dict[str, Any]:
        """Genere un resume IA court pour le widget dashboard."""
        if not anomalies:
            return {
                "resume": "Aucune derive financiere detectee sur les categories suivies.",
                "recommandations": ["Maintenir le rythme actuel et suivre la tendance chaque semaine."],
            }

        prompt = (
            f"Mois de reference: {mois_ref}.\n"
            f"Anomalies detectees: {anomalies}.\n"
            "Retourne uniquement du JSON: {resume, recommandations[]} "
            "avec un ton concret et actionnable."
        )

        parsed = self.call_with_json_parsing_sync(
            prompt=prompt,
            response_model=ResumeAnomaliesIA,
            system_prompt=(
                "Tu es un conseiller budget familial pragmatique. "
                "Propose des actions simples, mesurables, en francais."
            ),
            max_tokens=500,
            use_cache=True,
        )

        if parsed is None:
            top = anomalies[0]
            return {
                "resume": (
                    "Derive budget detectee: "
                    f"{top['categorie']} est a +{top['variation_pct']}% vs moyenne N-1/N-2."
                ),
                "recommandations": [
                    "DEFINIR UN PLAFOND HEBDOMADAIRE PAR CATEGORIE",
                    "Programmer un point budget en milieu de mois",
                    "Verifier les depenses impulsives de la categorie la plus en hausse",
                ],
            }

        return {"resume": parsed.resume, "recommandations": parsed.recommandations}

    def xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_54(self, anomalies: list[dict[str, Any]], mois_ref: str) -> dict[str, Any]:
        """Genere un resume IA court pour le widget dashboard."""
        if not anomalies:
            return {
                "resume": "Aucune derive financiere detectee sur les categories suivies.",
                "recommandations": ["Maintenir le rythme actuel et suivre la tendance chaque semaine."],
            }

        prompt = (
            f"Mois de reference: {mois_ref}.\n"
            f"Anomalies detectees: {anomalies}.\n"
            "Retourne uniquement du JSON: {resume, recommandations[]} "
            "avec un ton concret et actionnable."
        )

        parsed = self.call_with_json_parsing_sync(
            prompt=prompt,
            response_model=ResumeAnomaliesIA,
            system_prompt=(
                "Tu es un conseiller budget familial pragmatique. "
                "Propose des actions simples, mesurables, en francais."
            ),
            max_tokens=500,
            use_cache=True,
        )

        if parsed is None:
            top = anomalies[0]
            return {
                "resume": (
                    "Derive budget detectee: "
                    f"{top['categorie']} est a +{top['variation_pct']}% vs moyenne N-1/N-2."
                ),
                "recommandations": [
                    "Definir un plafond hebdomadaire par categorie",
                    "XXProgrammer un point budget en milieu de moisXX",
                    "Verifier les depenses impulsives de la categorie la plus en hausse",
                ],
            }

        return {"resume": parsed.resume, "recommandations": parsed.recommandations}

    def xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_55(self, anomalies: list[dict[str, Any]], mois_ref: str) -> dict[str, Any]:
        """Genere un resume IA court pour le widget dashboard."""
        if not anomalies:
            return {
                "resume": "Aucune derive financiere detectee sur les categories suivies.",
                "recommandations": ["Maintenir le rythme actuel et suivre la tendance chaque semaine."],
            }

        prompt = (
            f"Mois de reference: {mois_ref}.\n"
            f"Anomalies detectees: {anomalies}.\n"
            "Retourne uniquement du JSON: {resume, recommandations[]} "
            "avec un ton concret et actionnable."
        )

        parsed = self.call_with_json_parsing_sync(
            prompt=prompt,
            response_model=ResumeAnomaliesIA,
            system_prompt=(
                "Tu es un conseiller budget familial pragmatique. "
                "Propose des actions simples, mesurables, en francais."
            ),
            max_tokens=500,
            use_cache=True,
        )

        if parsed is None:
            top = anomalies[0]
            return {
                "resume": (
                    "Derive budget detectee: "
                    f"{top['categorie']} est a +{top['variation_pct']}% vs moyenne N-1/N-2."
                ),
                "recommandations": [
                    "Definir un plafond hebdomadaire par categorie",
                    "programmer un point budget en milieu de mois",
                    "Verifier les depenses impulsives de la categorie la plus en hausse",
                ],
            }

        return {"resume": parsed.resume, "recommandations": parsed.recommandations}

    def xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_56(self, anomalies: list[dict[str, Any]], mois_ref: str) -> dict[str, Any]:
        """Genere un resume IA court pour le widget dashboard."""
        if not anomalies:
            return {
                "resume": "Aucune derive financiere detectee sur les categories suivies.",
                "recommandations": ["Maintenir le rythme actuel et suivre la tendance chaque semaine."],
            }

        prompt = (
            f"Mois de reference: {mois_ref}.\n"
            f"Anomalies detectees: {anomalies}.\n"
            "Retourne uniquement du JSON: {resume, recommandations[]} "
            "avec un ton concret et actionnable."
        )

        parsed = self.call_with_json_parsing_sync(
            prompt=prompt,
            response_model=ResumeAnomaliesIA,
            system_prompt=(
                "Tu es un conseiller budget familial pragmatique. "
                "Propose des actions simples, mesurables, en francais."
            ),
            max_tokens=500,
            use_cache=True,
        )

        if parsed is None:
            top = anomalies[0]
            return {
                "resume": (
                    "Derive budget detectee: "
                    f"{top['categorie']} est a +{top['variation_pct']}% vs moyenne N-1/N-2."
                ),
                "recommandations": [
                    "Definir un plafond hebdomadaire par categorie",
                    "PROGRAMMER UN POINT BUDGET EN MILIEU DE MOIS",
                    "Verifier les depenses impulsives de la categorie la plus en hausse",
                ],
            }

        return {"resume": parsed.resume, "recommandations": parsed.recommandations}

    def xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_57(self, anomalies: list[dict[str, Any]], mois_ref: str) -> dict[str, Any]:
        """Genere un resume IA court pour le widget dashboard."""
        if not anomalies:
            return {
                "resume": "Aucune derive financiere detectee sur les categories suivies.",
                "recommandations": ["Maintenir le rythme actuel et suivre la tendance chaque semaine."],
            }

        prompt = (
            f"Mois de reference: {mois_ref}.\n"
            f"Anomalies detectees: {anomalies}.\n"
            "Retourne uniquement du JSON: {resume, recommandations[]} "
            "avec un ton concret et actionnable."
        )

        parsed = self.call_with_json_parsing_sync(
            prompt=prompt,
            response_model=ResumeAnomaliesIA,
            system_prompt=(
                "Tu es un conseiller budget familial pragmatique. "
                "Propose des actions simples, mesurables, en francais."
            ),
            max_tokens=500,
            use_cache=True,
        )

        if parsed is None:
            top = anomalies[0]
            return {
                "resume": (
                    "Derive budget detectee: "
                    f"{top['categorie']} est a +{top['variation_pct']}% vs moyenne N-1/N-2."
                ),
                "recommandations": [
                    "Definir un plafond hebdomadaire par categorie",
                    "Programmer un point budget en milieu de mois",
                    "XXVerifier les depenses impulsives de la categorie la plus en hausseXX",
                ],
            }

        return {"resume": parsed.resume, "recommandations": parsed.recommandations}

    def xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_58(self, anomalies: list[dict[str, Any]], mois_ref: str) -> dict[str, Any]:
        """Genere un resume IA court pour le widget dashboard."""
        if not anomalies:
            return {
                "resume": "Aucune derive financiere detectee sur les categories suivies.",
                "recommandations": ["Maintenir le rythme actuel et suivre la tendance chaque semaine."],
            }

        prompt = (
            f"Mois de reference: {mois_ref}.\n"
            f"Anomalies detectees: {anomalies}.\n"
            "Retourne uniquement du JSON: {resume, recommandations[]} "
            "avec un ton concret et actionnable."
        )

        parsed = self.call_with_json_parsing_sync(
            prompt=prompt,
            response_model=ResumeAnomaliesIA,
            system_prompt=(
                "Tu es un conseiller budget familial pragmatique. "
                "Propose des actions simples, mesurables, en francais."
            ),
            max_tokens=500,
            use_cache=True,
        )

        if parsed is None:
            top = anomalies[0]
            return {
                "resume": (
                    "Derive budget detectee: "
                    f"{top['categorie']} est a +{top['variation_pct']}% vs moyenne N-1/N-2."
                ),
                "recommandations": [
                    "Definir un plafond hebdomadaire par categorie",
                    "Programmer un point budget en milieu de mois",
                    "verifier les depenses impulsives de la categorie la plus en hausse",
                ],
            }

        return {"resume": parsed.resume, "recommandations": parsed.recommandations}

    def xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_59(self, anomalies: list[dict[str, Any]], mois_ref: str) -> dict[str, Any]:
        """Genere un resume IA court pour le widget dashboard."""
        if not anomalies:
            return {
                "resume": "Aucune derive financiere detectee sur les categories suivies.",
                "recommandations": ["Maintenir le rythme actuel et suivre la tendance chaque semaine."],
            }

        prompt = (
            f"Mois de reference: {mois_ref}.\n"
            f"Anomalies detectees: {anomalies}.\n"
            "Retourne uniquement du JSON: {resume, recommandations[]} "
            "avec un ton concret et actionnable."
        )

        parsed = self.call_with_json_parsing_sync(
            prompt=prompt,
            response_model=ResumeAnomaliesIA,
            system_prompt=(
                "Tu es un conseiller budget familial pragmatique. "
                "Propose des actions simples, mesurables, en francais."
            ),
            max_tokens=500,
            use_cache=True,
        )

        if parsed is None:
            top = anomalies[0]
            return {
                "resume": (
                    "Derive budget detectee: "
                    f"{top['categorie']} est a +{top['variation_pct']}% vs moyenne N-1/N-2."
                ),
                "recommandations": [
                    "Definir un plafond hebdomadaire par categorie",
                    "Programmer un point budget en milieu de mois",
                    "VERIFIER LES DEPENSES IMPULSIVES DE LA CATEGORIE LA PLUS EN HAUSSE",
                ],
            }

        return {"resume": parsed.resume, "recommandations": parsed.recommandations}

    def xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_60(self, anomalies: list[dict[str, Any]], mois_ref: str) -> dict[str, Any]:
        """Genere un resume IA court pour le widget dashboard."""
        if not anomalies:
            return {
                "resume": "Aucune derive financiere detectee sur les categories suivies.",
                "recommandations": ["Maintenir le rythme actuel et suivre la tendance chaque semaine."],
            }

        prompt = (
            f"Mois de reference: {mois_ref}.\n"
            f"Anomalies detectees: {anomalies}.\n"
            "Retourne uniquement du JSON: {resume, recommandations[]} "
            "avec un ton concret et actionnable."
        )

        parsed = self.call_with_json_parsing_sync(
            prompt=prompt,
            response_model=ResumeAnomaliesIA,
            system_prompt=(
                "Tu es un conseiller budget familial pragmatique. "
                "Propose des actions simples, mesurables, en francais."
            ),
            max_tokens=500,
            use_cache=True,
        )

        if parsed is None:
            top = anomalies[0]
            return {
                "resume": (
                    "Derive budget detectee: "
                    f"{top['categorie']} est a +{top['variation_pct']}% vs moyenne N-1/N-2."
                ),
                "recommandations": [
                    "Definir un plafond hebdomadaire par categorie",
                    "Programmer un point budget en milieu de mois",
                    "Verifier les depenses impulsives de la categorie la plus en hausse",
                ],
            }

        return {"XXresumeXX": parsed.resume, "recommandations": parsed.recommandations}

    def xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_61(self, anomalies: list[dict[str, Any]], mois_ref: str) -> dict[str, Any]:
        """Genere un resume IA court pour le widget dashboard."""
        if not anomalies:
            return {
                "resume": "Aucune derive financiere detectee sur les categories suivies.",
                "recommandations": ["Maintenir le rythme actuel et suivre la tendance chaque semaine."],
            }

        prompt = (
            f"Mois de reference: {mois_ref}.\n"
            f"Anomalies detectees: {anomalies}.\n"
            "Retourne uniquement du JSON: {resume, recommandations[]} "
            "avec un ton concret et actionnable."
        )

        parsed = self.call_with_json_parsing_sync(
            prompt=prompt,
            response_model=ResumeAnomaliesIA,
            system_prompt=(
                "Tu es un conseiller budget familial pragmatique. "
                "Propose des actions simples, mesurables, en francais."
            ),
            max_tokens=500,
            use_cache=True,
        )

        if parsed is None:
            top = anomalies[0]
            return {
                "resume": (
                    "Derive budget detectee: "
                    f"{top['categorie']} est a +{top['variation_pct']}% vs moyenne N-1/N-2."
                ),
                "recommandations": [
                    "Definir un plafond hebdomadaire par categorie",
                    "Programmer un point budget en milieu de mois",
                    "Verifier les depenses impulsives de la categorie la plus en hausse",
                ],
            }

        return {"RESUME": parsed.resume, "recommandations": parsed.recommandations}

    def xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_62(self, anomalies: list[dict[str, Any]], mois_ref: str) -> dict[str, Any]:
        """Genere un resume IA court pour le widget dashboard."""
        if not anomalies:
            return {
                "resume": "Aucune derive financiere detectee sur les categories suivies.",
                "recommandations": ["Maintenir le rythme actuel et suivre la tendance chaque semaine."],
            }

        prompt = (
            f"Mois de reference: {mois_ref}.\n"
            f"Anomalies detectees: {anomalies}.\n"
            "Retourne uniquement du JSON: {resume, recommandations[]} "
            "avec un ton concret et actionnable."
        )

        parsed = self.call_with_json_parsing_sync(
            prompt=prompt,
            response_model=ResumeAnomaliesIA,
            system_prompt=(
                "Tu es un conseiller budget familial pragmatique. "
                "Propose des actions simples, mesurables, en francais."
            ),
            max_tokens=500,
            use_cache=True,
        )

        if parsed is None:
            top = anomalies[0]
            return {
                "resume": (
                    "Derive budget detectee: "
                    f"{top['categorie']} est a +{top['variation_pct']}% vs moyenne N-1/N-2."
                ),
                "recommandations": [
                    "Definir un plafond hebdomadaire par categorie",
                    "Programmer un point budget en milieu de mois",
                    "Verifier les depenses impulsives de la categorie la plus en hausse",
                ],
            }

        return {"resume": parsed.resume, "XXrecommandationsXX": parsed.recommandations}

    def xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_63(self, anomalies: list[dict[str, Any]], mois_ref: str) -> dict[str, Any]:
        """Genere un resume IA court pour le widget dashboard."""
        if not anomalies:
            return {
                "resume": "Aucune derive financiere detectee sur les categories suivies.",
                "recommandations": ["Maintenir le rythme actuel et suivre la tendance chaque semaine."],
            }

        prompt = (
            f"Mois de reference: {mois_ref}.\n"
            f"Anomalies detectees: {anomalies}.\n"
            "Retourne uniquement du JSON: {resume, recommandations[]} "
            "avec un ton concret et actionnable."
        )

        parsed = self.call_with_json_parsing_sync(
            prompt=prompt,
            response_model=ResumeAnomaliesIA,
            system_prompt=(
                "Tu es un conseiller budget familial pragmatique. "
                "Propose des actions simples, mesurables, en francais."
            ),
            max_tokens=500,
            use_cache=True,
        )

        if parsed is None:
            top = anomalies[0]
            return {
                "resume": (
                    "Derive budget detectee: "
                    f"{top['categorie']} est a +{top['variation_pct']}% vs moyenne N-1/N-2."
                ),
                "recommandations": [
                    "Definir un plafond hebdomadaire par categorie",
                    "Programmer un point budget en milieu de mois",
                    "Verifier les depenses impulsives de la categorie la plus en hausse",
                ],
            }

        return {"resume": parsed.resume, "RECOMMANDATIONS": parsed.recommandations}
    
    xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_mutants : ClassVar[MutantDict] = { # type: ignore
    'xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_1': xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_1, 
        'xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_2': xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_2, 
        'xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_3': xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_3, 
        'xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_4': xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_4, 
        'xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_5': xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_5, 
        'xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_6': xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_6, 
        'xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_7': xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_7, 
        'xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_8': xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_8, 
        'xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_9': xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_9, 
        'xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_10': xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_10, 
        'xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_11': xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_11, 
        'xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_12': xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_12, 
        'xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_13': xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_13, 
        'xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_14': xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_14, 
        'xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_15': xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_15, 
        'xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_16': xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_16, 
        'xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_17': xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_17, 
        'xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_18': xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_18, 
        'xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_19': xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_19, 
        'xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_20': xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_20, 
        'xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_21': xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_21, 
        'xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_22': xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_22, 
        'xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_23': xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_23, 
        'xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_24': xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_24, 
        'xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_25': xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_25, 
        'xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_26': xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_26, 
        'xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_27': xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_27, 
        'xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_28': xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_28, 
        'xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_29': xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_29, 
        'xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_30': xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_30, 
        'xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_31': xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_31, 
        'xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_32': xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_32, 
        'xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_33': xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_33, 
        'xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_34': xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_34, 
        'xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_35': xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_35, 
        'xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_36': xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_36, 
        'xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_37': xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_37, 
        'xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_38': xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_38, 
        'xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_39': xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_39, 
        'xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_40': xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_40, 
        'xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_41': xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_41, 
        'xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_42': xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_42, 
        'xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_43': xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_43, 
        'xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_44': xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_44, 
        'xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_45': xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_45, 
        'xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_46': xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_46, 
        'xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_47': xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_47, 
        'xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_48': xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_48, 
        'xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_49': xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_49, 
        'xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_50': xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_50, 
        'xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_51': xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_51, 
        'xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_52': xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_52, 
        'xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_53': xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_53, 
        'xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_54': xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_54, 
        'xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_55': xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_55, 
        'xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_56': xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_56, 
        'xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_57': xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_57, 
        'xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_58': xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_58, 
        'xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_59': xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_59, 
        'xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_60': xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_60, 
        'xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_61': xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_61, 
        'xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_62': xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_62, 
        'xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_63': xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_63
    }
    xǁServiceAnomaliesFinancieresǁ_generer_resume_ia__mutmut_orig.__name__ = 'xǁServiceAnomaliesFinancieresǁ_generer_resume_ia'


@service_factory("anomalies_financieres", tags={"dashboard", "budget", "ia"})
def obtenir_service_anomalies_financieres() -> ServiceAnomaliesFinancieres:
    """Factory singleton du service anomalies financieres."""
    return ServiceAnomaliesFinancieres()


get_anomalies_financieres_service = obtenir_service_anomalies_financieres
