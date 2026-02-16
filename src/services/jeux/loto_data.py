"""
LotoDataService - Service de récupération des données Loto FDJ.

Fournit:
- Historique des tirages Loto depuis data.gouv.fr
- Statistiques par numéro (fréquence, série)
- Données pour le tracking "loi des séries"

Source: https://www.data.gouv.fr/fr/datasets/nouveau-loto-nouveau-jeu-de-la-fdj/

Règles Loto:
- 5 numéros parmi 49 (1-49)
- 1 numéro Chance parmi 10 (1-10)
- Tirages: Lundi, Mercredi, Samedi
"""

import csv
import io
import logging
from datetime import date, datetime
from typing import Any

import httpx
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# CONSTANTES
# ═══════════════════════════════════════════════════════════

# URL des données sur data.gouv.fr
DATA_GOUV_URL = "https://www.data.gouv.fr/fr/datasets/r/77e2bca4-f4c5-4f25-aab2-69a5a3a0e80f"

# Alternative: fichiers CSV directs (plus stable)
LOTO_CSV_URLS = {
    "nouveau_loto": "https://media.fdj.fr/static/csv/loto/nouveau_loto.csv",
    "loto_historique": "https://media.fdj.fr/static/csv/loto/loto_historique.csv",
}

# Nombre de numéros
NB_NUMEROS_PRINCIPAUX = 49
NB_NUMEROS_CHANCE = 10
NUMEROS_PAR_TIRAGE = 5


# ═══════════════════════════════════════════════════════════
# TYPES ET SCHÉMAS
# ═══════════════════════════════════════════════════════════


class TirageLoto(BaseModel):
    """Données d'un tirage Loto."""

    date_tirage: date
    jour_semaine: str = ""  # lundi, mercredi, samedi
    numeros: list[int] = Field(default_factory=list)  # 5 numéros principaux
    numero_chance: int = 0
    numero_complementaire: int | None = None  # Ancien Loto

    @property
    def tous_numeros(self) -> set[int]:
        """Retourne l'ensemble de tous les numéros tirés (principaux)."""
        return set(self.numeros)


class StatistiqueNumeroLoto(BaseModel):
    """Statistiques pour un numéro Loto."""

    numero: int
    type_numero: str = "principal"  # "principal" ou "chance"
    total_tirages: int = 0
    nb_sorties: int = 0
    frequence: float = 0.0  # nb_sorties / total_tirages
    frequence_theorique: float = 0.0  # 5/49 ou 1/10
    serie_actuelle: int = 0  # Tirages depuis dernière sortie
    derniere_sortie: date | None = None
    value: float = 0.0  # frequence × serie (loi des séries)


class StatistiquesGlobalesLoto(BaseModel):
    """Statistiques globales du Loto."""

    total_tirages: int = 0
    date_premier_tirage: date | None = None
    date_dernier_tirage: date | None = None
    numeros_principaux: dict[int, StatistiqueNumeroLoto] = Field(default_factory=dict)
    numeros_chance: dict[int, StatistiqueNumeroLoto] = Field(default_factory=dict)


# ═══════════════════════════════════════════════════════════
# SERVICE PRINCIPAL
# ═══════════════════════════════════════════════════════════


class LotoDataService:
    """
    Service de récupération et analyse des données Loto FDJ.

    Utilise les données ouvertes de data.gouv.fr / FDJ.
    """

    def __init__(self):
        """Initialise le service."""
        self.http_client = httpx.Client(timeout=60.0)
        self._tirages_cache: list[TirageLoto] = []

    # ─────────────────────────────────────────────────────────────────
    # RÉCUPÉRATION DES DONNÉES
    # ─────────────────────────────────────────────────────────────────

    def telecharger_historique(self, source: str = "nouveau_loto") -> list[TirageLoto]:
        """
        Télécharge l'historique des tirages depuis data.gouv.fr ou FDJ.

        Args:
            source: "nouveau_loto" ou "loto_historique"

        Returns:
            Liste de tirages triés par date croissante
        """
        url = LOTO_CSV_URLS.get(source, LOTO_CSV_URLS["nouveau_loto"])

        try:
            logger.info(f"Téléchargement données Loto depuis {url}")
            response = self.http_client.get(url)
            response.raise_for_status()

            # Parser le CSV
            tirages = self._parser_csv_fdj(response.text)

            # Trier par date croissante
            tirages.sort(key=lambda t: t.date_tirage)

            logger.info(f"Récupéré {len(tirages)} tirages Loto")
            self._tirages_cache = tirages
            return tirages

        except httpx.HTTPStatusError as e:
            logger.error(f"Erreur HTTP Loto: {e.response.status_code}")
            return []
        except httpx.TimeoutException:
            logger.error("Timeout téléchargement Loto")
            return []
        except Exception as e:
            logger.error(f"Erreur téléchargement Loto: {e}")
            return []

    def _parser_csv_fdj(self, csv_content: str) -> list[TirageLoto]:
        """
        Parse le fichier CSV FDJ.

        Format attendu (colonnes séparées par ;):
        annee_numero_de_tirage;date_de_tirage;boule_1;boule_2;boule_3;boule_4;boule_5;numero_chance;...
        """
        tirages = []

        try:
            # Détecter le séparateur
            first_line = csv_content.split("\n")[0]
            delimiter = ";" if ";" in first_line else ","

            reader = csv.DictReader(io.StringIO(csv_content), delimiter=delimiter)

            for row in reader:
                try:
                    tirage = self._parser_ligne_csv(row)
                    if tirage:
                        tirages.append(tirage)
                except Exception as e:
                    logger.debug(f"Erreur parsing ligne: {e}")
                    continue

        except Exception as e:
            logger.error(f"Erreur parsing CSV: {e}")

        return tirages

    def _parser_ligne_csv(self, row: dict) -> TirageLoto | None:
        """Parse une ligne du CSV en TirageLoto."""
        try:
            # Trouver la colonne date (différents noms possibles)
            date_str = row.get("date_de_tirage") or row.get("date") or row.get("DATE") or ""

            if not date_str:
                return None

            # Parser la date (format DD/MM/YYYY ou YYYY-MM-DD)
            if "/" in date_str:
                date_tirage = datetime.strptime(date_str, "%d/%m/%Y").date()
            else:
                date_tirage = datetime.strptime(date_str[:10], "%Y-%m-%d").date()

            # Récupérer les numéros (différents noms de colonnes possibles)
            numeros = []
            for i in range(1, 6):
                for col_name in [f"boule_{i}", f"boule{i}", f"b{i}", f"BOULE_{i}"]:
                    if col_name in row and row[col_name]:
                        numeros.append(int(row[col_name]))
                        break

            if len(numeros) < 5:
                # Essayer format alternatif (colonnes numérotées)
                numeros = []
                for col in row:
                    if col.lower().startswith("boule") and row[col]:
                        try:
                            numeros.append(int(row[col]))
                        except ValueError:
                            continue
                numeros = numeros[:5]

            # Numéro chance
            numero_chance = 0
            for col_name in ["numero_chance", "chance", "CHANCE", "numero_complementaire"]:
                if col_name in row and row[col_name]:
                    try:
                        numero_chance = int(row[col_name])
                        break
                    except ValueError:
                        continue

            # Jour de la semaine
            jours = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
            jour_semaine = jours[date_tirage.weekday()]

            return TirageLoto(
                date_tirage=date_tirage,
                jour_semaine=jour_semaine,
                numeros=numeros,
                numero_chance=numero_chance,
            )

        except Exception as e:
            logger.debug(f"Erreur parsing ligne: {e}")
            return None

    # ─────────────────────────────────────────────────────────────────
    # CALCUL DES STATISTIQUES
    # ─────────────────────────────────────────────────────────────────

    def calculer_statistiques_numero(
        self,
        numero: int,
        tirages: list[TirageLoto] | None = None,
        type_numero: str = "principal",
    ) -> StatistiqueNumeroLoto:
        """
        Calcule les statistiques d'un numéro.

        Args:
            numero: Numéro à analyser
            tirages: Liste de tirages (défaut: cache)
            type_numero: "principal" (1-49) ou "chance" (1-10)

        Returns:
            Statistiques du numéro
        """
        if tirages is None:
            tirages = self._tirages_cache

        if not tirages:
            return StatistiqueNumeroLoto(numero=numero, type_numero=type_numero)

        total_tirages = len(tirages)
        nb_sorties = 0
        derniere_sortie: date | None = None
        serie_actuelle = 0

        # Fréquence théorique
        if type_numero == "principal":
            freq_theorique = NUMEROS_PAR_TIRAGE / NB_NUMEROS_PRINCIPAUX  # 5/49 ≈ 0.102
        else:
            freq_theorique = 1 / NB_NUMEROS_CHANCE  # 1/10 = 0.1

        # Parcourir les tirages (triés par date croissante)
        for tirage in tirages:
            est_sorti = (
                numero in tirage.numeros
                if type_numero == "principal"
                else tirage.numero_chance == numero
            )

            if est_sorti:
                nb_sorties += 1
                derniere_sortie = tirage.date_tirage
                serie_actuelle = 0
            else:
                serie_actuelle += 1

        frequence = nb_sorties / total_tirages if total_tirages > 0 else 0.0
        value = frequence * serie_actuelle  # Loi des séries

        return StatistiqueNumeroLoto(
            numero=numero,
            type_numero=type_numero,
            total_tirages=total_tirages,
            nb_sorties=nb_sorties,
            frequence=round(frequence, 4),
            frequence_theorique=round(freq_theorique, 4),
            serie_actuelle=serie_actuelle,
            derniere_sortie=derniere_sortie,
            value=round(value, 2),
        )

    def calculer_toutes_statistiques(
        self, tirages: list[TirageLoto] | None = None
    ) -> StatistiquesGlobalesLoto:
        """
        Calcule les statistiques de tous les numéros.

        Args:
            tirages: Liste de tirages

        Returns:
            Statistiques globales
        """
        if tirages is None:
            tirages = self._tirages_cache

        if not tirages:
            return StatistiquesGlobalesLoto()

        # Stats numéros principaux (1-49)
        stats_principaux = {}
        for num in range(1, NB_NUMEROS_PRINCIPAUX + 1):
            stats_principaux[num] = self.calculer_statistiques_numero(num, tirages, "principal")

        # Stats numéros chance (1-10)
        stats_chance = {}
        for num in range(1, NB_NUMEROS_CHANCE + 1):
            stats_chance[num] = self.calculer_statistiques_numero(num, tirages, "chance")

        return StatistiquesGlobalesLoto(
            total_tirages=len(tirages),
            date_premier_tirage=tirages[0].date_tirage,
            date_dernier_tirage=tirages[-1].date_tirage,
            numeros_principaux=stats_principaux,
            numeros_chance=stats_chance,
        )

    def obtenir_numeros_en_retard(
        self,
        tirages: list[TirageLoto] | None = None,
        seuil_value: float = 2.0,
        type_numero: str = "principal",
    ) -> list[StatistiqueNumeroLoto]:
        """
        Retourne les numéros "en retard" selon la loi des séries.

        Args:
            tirages: Liste de tirages
            seuil_value: Seuil minimum de value (défaut: 2.0)
            type_numero: "principal" ou "chance"

        Returns:
            Liste de stats triée par value décroissante
        """
        if tirages is None:
            tirages = self._tirages_cache

        if not tirages:
            return []

        max_numero = NB_NUMEROS_PRINCIPAUX if type_numero == "principal" else NB_NUMEROS_CHANCE

        stats = []
        for num in range(1, max_numero + 1):
            stat = self.calculer_statistiques_numero(num, tirages, type_numero)
            if stat.value >= seuil_value:
                stats.append(stat)

        # Trier par value décroissante
        stats.sort(key=lambda s: s.value, reverse=True)
        return stats

    def close(self):
        """Ferme le client HTTP."""
        self.http_client.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


# ═══════════════════════════════════════════════════════════
# FACTORY
# ═══════════════════════════════════════════════════════════


def get_loto_data_service() -> LotoDataService:
    """
    Factory pour créer une instance du service.

    Returns:
        Instance LotoDataService
    """
    return LotoDataService()
