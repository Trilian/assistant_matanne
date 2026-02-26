"""
Modèles SQLAlchemy pour le domaine Jeux (Paris sportifs, Loto & Euromillions)
"""

import enum
from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    JSON,
    Boolean,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, utc_now
from .mixins import CreeLeMixin, TimestampMixin

# ═══════════════════════════════════════════════════════════════════
# ENUMS
# ═══════════════════════════════════════════════════════════════════


class ResultatMatchEnum(enum.StrEnum):
    """Résultat possible d'un match"""

    VICTOIRE_DOMICILE = "1"
    NUL = "N"
    VICTOIRE_EXTERIEUR = "2"
    NON_JOUE = "non_joue"


class StatutPariEnum(enum.StrEnum):
    """Statut d'un pari"""

    EN_ATTENTE = "en_attente"
    GAGNE = "gagne"
    PERDU = "perdu"
    ANNULE = "annule"


class TypePariEnum(enum.StrEnum):
    """Type de pari"""

    RESULTAT_MATCH = "1N2"
    OVER_UNDER = "over_under"
    SCORE_EXACT = "score_exact"
    BTTS = "les_deux_marquent"  # Both Teams To Score


class ChampionnatEnum(enum.StrEnum):
    """Championnats européens suivis"""

    LIGUE_1 = "Ligue 1"
    PREMIER_LEAGUE = "Premier League"
    LA_LIGA = "La Liga"
    SERIE_A = "Serie A"
    BUNDESLIGA = "Bundesliga"
    CHAMPIONS_LEAGUE = "Champions League"
    EUROPA_LEAGUE = "Europa League"


# ═══════════════════════════════════════════════════════════════════
# MODÈLES PARIS SPORTIFS
# ═══════════════════════════════════════════════════════════════════


class Equipe(TimestampMixin, Base):
    """Équipe de football"""

    __tablename__ = "jeux_equipes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nom: Mapped[str] = mapped_column(String(100), nullable=False)
    nom_court: Mapped[str] = mapped_column(String(50), nullable=True)
    championnat: Mapped[str] = mapped_column(String(50), nullable=False)
    pays: Mapped[str] = mapped_column(String(50), nullable=True)
    logo_url: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Stats agrégées (mises à jour automatiquement)
    matchs_joues: Mapped[int] = mapped_column(Integer, default=0)
    victoires: Mapped[int] = mapped_column(Integer, default=0)
    nuls: Mapped[int] = mapped_column(Integer, default=0)
    defaites: Mapped[int] = mapped_column(Integer, default=0)
    buts_marques: Mapped[int] = mapped_column(Integer, default=0)
    buts_encaisses: Mapped[int] = mapped_column(Integer, default=0)

    # Relations
    matchs_domicile: Mapped[list["Match"]] = relationship(
        "Match", foreign_keys="Match.equipe_domicile_id", back_populates="equipe_domicile"
    )
    matchs_exterieur: Mapped[list["Match"]] = relationship(
        "Match", foreign_keys="Match.equipe_exterieur_id", back_populates="equipe_exterieur"
    )

    def __repr__(self) -> str:
        return f"<Equipe {self.nom} ({self.championnat})>"

    @property
    def forme_recente(self) -> str:
        """Retourne la forme sur les 5 derniers matchs (ex: VVNPV).

        V = Victoire, N = Nul, D = Défaite.
        Calculé dynamiquement à partir des matchs chargés.
        """
        tous_matchs = [
            *[(m, "dom") for m in self.matchs_domicile if m.joue],
            *[(m, "ext") for m in self.matchs_exterieur if m.joue],
        ]
        tous_matchs.sort(key=lambda x: x[0].date_match, reverse=True)

        forme = []
        for match, position in tous_matchs[:5]:
            if match.score_domicile is None or match.score_exterieur is None:
                continue
            if position == "dom":
                if match.score_domicile > match.score_exterieur:
                    forme.append("V")
                elif match.score_domicile < match.score_exterieur:
                    forme.append("D")
                else:
                    forme.append("N")
            else:
                if match.score_exterieur > match.score_domicile:
                    forme.append("V")
                elif match.score_exterieur < match.score_domicile:
                    forme.append("D")
                else:
                    forme.append("N")

        return "".join(forme)

    @property
    def points(self) -> int:
        """Calcule les points (3V + 1N)"""
        return self.victoires * 3 + self.nuls


class Match(TimestampMixin, Base):
    """Match de football"""

    __tablename__ = "jeux_matchs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    # Équipes
    equipe_domicile_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("jeux_equipes.id"), nullable=False
    )
    equipe_exterieur_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("jeux_equipes.id"), nullable=False
    )

    # Infos match
    championnat: Mapped[str] = mapped_column(String(50), nullable=False)
    journee: Mapped[int | None] = mapped_column(Integer, nullable=True)
    date_match: Mapped[date] = mapped_column(Date, nullable=False)
    heure: Mapped[str | None] = mapped_column(String(5), nullable=True)  # "20:45"

    # Résultat
    score_domicile: Mapped[int | None] = mapped_column(Integer, nullable=True)
    score_exterieur: Mapped[int | None] = mapped_column(Integer, nullable=True)
    resultat: Mapped[str | None] = mapped_column(String(10), nullable=True)  # "1", "N", "2"
    joue: Mapped[bool] = mapped_column(Boolean, default=False)

    # Cotes (optionnel - si on veut les tracker)
    cote_domicile: Mapped[float | None] = mapped_column(Float, nullable=True)
    cote_nul: Mapped[float | None] = mapped_column(Float, nullable=True)
    cote_exterieur: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Prédiction IA
    prediction_resultat: Mapped[str | None] = mapped_column(String(10), nullable=True)
    prediction_proba_dom: Mapped[float | None] = mapped_column(Float, nullable=True)
    prediction_proba_nul: Mapped[float | None] = mapped_column(Float, nullable=True)
    prediction_proba_ext: Mapped[float | None] = mapped_column(Float, nullable=True)
    prediction_confiance: Mapped[float | None] = mapped_column(Float, nullable=True)  # 0-100%
    prediction_raison: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relations (lazy="joined" pour éviter N+1 sur equipe.nom)
    equipe_domicile: Mapped["Equipe"] = relationship(
        "Equipe",
        foreign_keys=[equipe_domicile_id],
        back_populates="matchs_domicile",
        lazy="joined",
    )
    equipe_exterieur: Mapped["Equipe"] = relationship(
        "Equipe",
        foreign_keys=[equipe_exterieur_id],
        back_populates="matchs_exterieur",
        lazy="joined",
    )
    paris: Mapped[list["PariSportif"]] = relationship("PariSportif", back_populates="match")

    def __repr__(self) -> str:
        if self.joue:
            return f"<Match {self.equipe_domicile.nom} {self.score_domicile}-{self.score_exterieur} {self.equipe_exterieur.nom}>"
        return f"<Match {self.date_match}: DOM vs EXT>"


class PariSportif(CreeLeMixin, Base):
    """Pari sportif enregistré (réel ou virtuel)"""

    __tablename__ = "jeux_paris_sportifs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    match_id: Mapped[int] = mapped_column(Integer, ForeignKey("jeux_matchs.id"), nullable=False)

    # Détails du pari
    type_pari: Mapped[str] = mapped_column(String(30), default="1N2")  # 1N2, over_under, etc.
    prediction: Mapped[str] = mapped_column(String(20), nullable=False)  # "1", "N", "2", "over_2.5"
    cote: Mapped[float] = mapped_column(Float, nullable=False)
    mise: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), default=Decimal("0.00")
    )  # 0 = pari virtuel

    # Résultat
    statut: Mapped[str] = mapped_column(String(20), default="en_attente")
    gain: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)

    # Tracking
    est_virtuel: Mapped[bool] = mapped_column(Boolean, default=True)  # Pari simulé vs réel
    confiance_prediction: Mapped[float | None] = mapped_column(Float, nullable=True)  # Score IA
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relations
    match: Mapped["Match"] = relationship("Match", back_populates="paris")

    def __repr__(self) -> str:
        return f"<Pari {self.prediction} @ {self.cote} - {self.statut}>"


# ═══════════════════════════════════════════════════════════════════
# MODÈLES LOTO
# ═══════════════════════════════════════════════════════════════════


class TirageLoto(CreeLeMixin, Base):
    """Historique des tirages du Loto"""

    __tablename__ = "jeux_tirages_loto"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    date_tirage: Mapped[date] = mapped_column(Date, nullable=False, unique=True)

    # Numéros (5 boules + 1 numéro chance pour le Loto français)
    numero_1: Mapped[int] = mapped_column(Integer, nullable=False)
    numero_2: Mapped[int] = mapped_column(Integer, nullable=False)
    numero_3: Mapped[int] = mapped_column(Integer, nullable=False)
    numero_4: Mapped[int] = mapped_column(Integer, nullable=False)
    numero_5: Mapped[int] = mapped_column(Integer, nullable=False)
    numero_chance: Mapped[int] = mapped_column(Integer, nullable=False)  # 1-10

    # Infos jackpot
    jackpot_euros: Mapped[int | None] = mapped_column(Integer, nullable=True)
    gagnants_rang1: Mapped[int | None] = mapped_column(Integer, nullable=True)

    def __repr__(self) -> str:
        return f"<Tirage {self.date_tirage}: {self.numeros_str}>"

    @property
    def numeros(self) -> list[int]:
        """Retourne la liste des 5 numéros principaux"""
        return sorted([self.numero_1, self.numero_2, self.numero_3, self.numero_4, self.numero_5])

    @property
    def numeros_str(self) -> str:
        """Format affichage: 5-12-23-34-45 + N°8"""
        return f"{'-'.join(map(str, self.numeros))} + N°{self.numero_chance}"


class GrilleLoto(Base):
    """Grille de loto jouée (réelle ou virtuelle)"""

    __tablename__ = "jeux_grilles_loto"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tirage_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("jeux_tirages_loto.id"), nullable=True
    )

    # Numéros choisis
    numero_1: Mapped[int] = mapped_column(Integer, nullable=False)
    numero_2: Mapped[int] = mapped_column(Integer, nullable=False)
    numero_3: Mapped[int] = mapped_column(Integer, nullable=False)
    numero_4: Mapped[int] = mapped_column(Integer, nullable=False)
    numero_5: Mapped[int] = mapped_column(Integer, nullable=False)
    numero_chance: Mapped[int] = mapped_column(Integer, nullable=False)

    # Tracking
    est_virtuelle: Mapped[bool] = mapped_column(Boolean, default=True)
    source_prediction: Mapped[str] = mapped_column(
        String(50), default="manuel"
    )  # "manuel", "ia", "aleatoire"
    mise: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("2.20"))

    # Résultat (après tirage)
    numeros_trouves: Mapped[int | None] = mapped_column(Integer, nullable=True)  # 0-5
    chance_trouvee: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    gain: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    rang: Mapped[int | None] = mapped_column(Integer, nullable=True)  # 1-9 ou null

    # Méta
    date_creation: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relations
    tirage: Mapped[Optional["TirageLoto"]] = relationship("TirageLoto")

    def __repr__(self) -> str:
        return f"<Grille {self.numeros_str}>"

    @property
    def numeros(self) -> list[int]:
        return sorted([self.numero_1, self.numero_2, self.numero_3, self.numero_4, self.numero_5])

    @property
    def numeros_str(self) -> str:
        return f"{'-'.join(map(str, self.numeros))} + N°{self.numero_chance}"


class StatistiquesLoto(Base):
    """Statistiques calculées sur les tirages (cache)"""

    __tablename__ = "jeux_stats_loto"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    date_calcul: Mapped[datetime] = mapped_column(DateTime, default=utc_now)

    # Stats par numéro (JSON: {1: {freq: 123, dernier: "2024-01-01", ecart: 5}, ...})
    frequences_numeros: Mapped[dict] = mapped_column(JSON, nullable=True)
    frequences_chance: Mapped[dict] = mapped_column(JSON, nullable=True)

    # Numéros chauds/froids (top 5)
    numeros_chauds: Mapped[dict] = mapped_column(JSON, nullable=True)  # Plus fréquents
    numeros_froids: Mapped[dict] = mapped_column(JSON, nullable=True)  # Moins fréquents
    numeros_retard: Mapped[dict] = mapped_column(JSON, nullable=True)  # Plus grand écart

    # Patterns
    somme_moyenne: Mapped[float | None] = mapped_column(Float, nullable=True)
    paires_frequentes: Mapped[dict] = mapped_column(JSON, nullable=True)

    # Méta
    nb_tirages_analyses: Mapped[int] = mapped_column(Integer, default=0)


# ═══════════════════════════════════════════════════════════════════
# SUIVI GLOBAL (Bankroll & Performance)
# ═══════════════════════════════════════════════════════════════════


class HistoriqueJeux(CreeLeMixin, Base):
    """Historique global pour tracker la performance"""

    __tablename__ = "jeux_historique"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    type_jeu: Mapped[str] = mapped_column(String(20), nullable=False)  # "paris" ou "loto"

    # Cumuls du jour
    nb_paris: Mapped[int] = mapped_column(Integer, default=0)
    mises_totales: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("0.00"))
    gains_totaux: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("0.00"))
    paris_gagnes: Mapped[int] = mapped_column(Integer, default=0)
    paris_perdus: Mapped[int] = mapped_column(Integer, default=0)

    # Performance IA
    predictions_correctes: Mapped[int] = mapped_column(Integer, default=0)
    predictions_totales: Mapped[int] = mapped_column(Integer, default=0)

    @property
    def roi(self) -> float:
        """Return on Investment en %"""
        if self.mises_totales == 0:
            return 0.0
        return float((self.gains_totaux - self.mises_totales) / self.mises_totales * 100)

    @property
    def taux_reussite(self) -> float:
        """Pourcentage de paris gagnés"""
        total = self.paris_gagnes + self.paris_perdus
        if total == 0:
            return 0.0
        return self.paris_gagnes / total * 100


# ═══════════════════════════════════════════════════════════════════
# ENUMS SÉRIES
# ═══════════════════════════════════════════════════════════════════


class TypeJeuEnum(enum.StrEnum):
    """Type de jeu pour le tracking des séries"""

    PARIS = "paris"
    LOTO = "loto"
    EUROMILLIONS = "euromillions"


class TypeMarcheParisEnum(enum.StrEnum):
    """Types de marchés paris sportifs (inspiré du template Excel)"""

    # Mi-temps
    DOMICILE_MT = "domicile_mi_temps"
    NUL_MT = "nul_mi_temps"
    EXTERIEUR_MT = "exterieur_mi_temps"
    ZERO_ZERO_MT = "0-0_mi_temps"
    OVER_05_MT = "over_0.5_mi_temps"
    OVER_15_MT = "over_1.5_mi_temps"
    BTTS_MT = "btts_mi_temps"
    CLEAN_SHEET_MT = "clean_sheet_mi_temps"

    # Fin de match
    DOMICILE_FT = "domicile_fin_match"
    NUL_FT = "nul_fin_match"
    EXTERIEUR_FT = "exterieur_fin_match"
    ZERO_ZERO_FT = "0-0_fin_match"
    UNDER_15_FT = "under_1.5_fin_match"
    OVER_25_FT = "over_2.5_fin_match"
    OVER_35_FT = "over_3.5_fin_match"
    OVER_45_FT = "over_4.5_fin_match"
    BTTS_FT = "btts_fin_match"
    CLEAN_SHEET_FT = "clean_sheet_fin_match"

    # Écarts
    DOMICILE_1_BUT = "domicile_1_but_ecart"
    DOMICILE_2PLUS_BUTS = "domicile_2plus_buts_ecart"
    EXTERIEUR_1_BUT = "exterieur_1_but_ecart"
    EXTERIEUR_2PLUS_BUTS = "exterieur_2plus_buts_ecart"


# ═══════════════════════════════════════════════════════════════════
# MODÈLES SÉRIES (Loi des séries - Paris & Loto)
# ═══════════════════════════════════════════════════════════════════


class SerieJeux(CreeLeMixin, Base):
    """
    Tracking des séries pour la loi des séries.

    Pour Paris: série = nb matchs depuis dernière occurrence du marché
    Pour Loto: série = nb tirages depuis dernière sortie du numéro
    """

    __tablename__ = "jeux_series"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    # Identification
    type_jeu: Mapped[str] = mapped_column(String(20), nullable=False)  # "paris" ou "loto"
    championnat: Mapped[str | None] = mapped_column(
        String(50), nullable=True
    )  # Pour paris: "Ligue 1", pour loto: null
    marche: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # Pour paris: type marché, pour loto: numéro (1-49)

    # Statistiques
    serie_actuelle: Mapped[int] = mapped_column(Integer, default=0)  # Nb événements depuis dernier
    frequence: Mapped[float] = mapped_column(Float, default=0.0)  # Fréquence historique (0-1)
    nb_occurrences: Mapped[int] = mapped_column(Integer, default=0)  # Nb fois ce marché est arrivé
    nb_total: Mapped[int] = mapped_column(Integer, default=0)  # Nb total d'événements analysés

    # Tracking
    derniere_occurrence: Mapped[date | None] = mapped_column(Date, nullable=True)
    derniere_mise_a_jour: Mapped[datetime] = mapped_column(DateTime, default=utc_now)

    def __repr__(self) -> str:
        return f"<Serie {self.type_jeu}/{self.championnat or 'global'}/{self.marche}: {self.serie_actuelle}>"

    @property
    def value(self) -> float:
        """Calcule la value = fréquence × série (indicateur d'opportunité)"""
        return self.frequence * self.serie_actuelle

    @property
    def frequence_pourcent(self) -> float:
        """Fréquence en pourcentage"""
        return self.frequence * 100


class AlerteJeux(CreeLeMixin, Base):
    """
    Alertes d'opportunités basées sur la loi des séries.

    Créée automatiquement quand value > seuil configurable.
    """

    __tablename__ = "jeux_alertes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    # Référence à la série
    serie_id: Mapped[int] = mapped_column(Integer, ForeignKey("jeux_series.id"), nullable=False)

    # Contexte
    type_jeu: Mapped[str] = mapped_column(String(20), nullable=False)
    championnat: Mapped[str | None] = mapped_column(String(50), nullable=True)
    marche: Mapped[str] = mapped_column(String(50), nullable=False)

    # Métriques au moment de l'alerte
    value_alerte: Mapped[float] = mapped_column(Float, nullable=False)
    serie_alerte: Mapped[int] = mapped_column(Integer, nullable=False)
    frequence_alerte: Mapped[float] = mapped_column(Float, nullable=False)
    seuil_utilise: Mapped[float] = mapped_column(Float, default=2.0)

    # Statut
    notifie: Mapped[bool] = mapped_column(Boolean, default=False)
    date_notification: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Résultat (après l'événement)
    resultat_verifie: Mapped[bool] = mapped_column(Boolean, default=False)
    resultat_correct: Mapped[bool | None] = mapped_column(
        Boolean, nullable=True
    )  # True si la série s'est brisée

    # Relations
    serie: Mapped["SerieJeux"] = relationship("SerieJeux")

    def __repr__(self) -> str:
        return f"<Alerte {self.type_jeu}/{self.marche} value={self.value_alerte:.2f}>"


class ConfigurationJeux(Base):
    """
    Configuration globale pour les modules jeux.

    Stocke les seuils d'alerte, fréquences de sync, etc.
    """

    __tablename__ = "jeux_configuration"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    cle: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    valeur: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    modifie_le: Mapped[datetime] = mapped_column(DateTime, default=utc_now, onupdate=utc_now)

    def __repr__(self) -> str:
        return f"<Config {self.cle}={self.valeur}>"


# ═══════════════════════════════════════════════════════════════════
# MODÈLES EUROMILLIONS
# ═══════════════════════════════════════════════════════════════════


class TirageEuromillions(CreeLeMixin, Base):
    """Historique des tirages Euromillions"""

    __tablename__ = "jeux_tirages_euromillions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    date_tirage: Mapped[date] = mapped_column(Date, nullable=False, unique=True)

    # 5 numéros principaux (1-50)
    numero_1: Mapped[int] = mapped_column(Integer, nullable=False)
    numero_2: Mapped[int] = mapped_column(Integer, nullable=False)
    numero_3: Mapped[int] = mapped_column(Integer, nullable=False)
    numero_4: Mapped[int] = mapped_column(Integer, nullable=False)
    numero_5: Mapped[int] = mapped_column(Integer, nullable=False)

    # 2 étoiles (1-12)
    etoile_1: Mapped[int] = mapped_column(Integer, nullable=False)
    etoile_2: Mapped[int] = mapped_column(Integer, nullable=False)

    # Infos jackpot
    jackpot_euros: Mapped[int | None] = mapped_column(Integer, nullable=True)
    gagnants_rang1: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # MyMillion (code)
    code_my_million: Mapped[str | None] = mapped_column(String(20), nullable=True)

    def __repr__(self) -> str:
        return f"<TirageEuro {self.date_tirage}: {self.numeros_str}>"

    @property
    def numeros(self) -> list[int]:
        """Retourne la liste des 5 numéros principaux"""
        return sorted([self.numero_1, self.numero_2, self.numero_3, self.numero_4, self.numero_5])

    @property
    def etoiles(self) -> list[int]:
        """Retourne la liste des 2 étoiles"""
        return sorted([self.etoile_1, self.etoile_2])

    @property
    def numeros_str(self) -> str:
        """Format affichage: 5-12-23-34-45 ★1 ★9"""
        nums = "-".join(map(str, self.numeros))
        stars = " ".join(f"★{e}" for e in self.etoiles)
        return f"{nums} {stars}"


class GrilleEuromillions(Base):
    """Grille Euromillions jouée (réelle ou virtuelle)"""

    __tablename__ = "jeux_grilles_euromillions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tirage_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("jeux_tirages_euromillions.id"), nullable=True
    )

    # 5 numéros choisis (1-50)
    numero_1: Mapped[int] = mapped_column(Integer, nullable=False)
    numero_2: Mapped[int] = mapped_column(Integer, nullable=False)
    numero_3: Mapped[int] = mapped_column(Integer, nullable=False)
    numero_4: Mapped[int] = mapped_column(Integer, nullable=False)
    numero_5: Mapped[int] = mapped_column(Integer, nullable=False)

    # 2 étoiles (1-12)
    etoile_1: Mapped[int] = mapped_column(Integer, nullable=False)
    etoile_2: Mapped[int] = mapped_column(Integer, nullable=False)

    # Tracking
    est_virtuelle: Mapped[bool] = mapped_column(Boolean, default=True)
    source_prediction: Mapped[str] = mapped_column(String(50), default="manuel")
    mise: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("2.50"))

    # Résultat
    numeros_trouves: Mapped[int | None] = mapped_column(Integer, nullable=True)  # 0-5
    etoiles_trouvees: Mapped[int | None] = mapped_column(Integer, nullable=True)  # 0-2
    gain: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    rang: Mapped[int | None] = mapped_column(Integer, nullable=True)  # 1-13

    # Méta
    date_creation: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relations
    tirage: Mapped[Optional["TirageEuromillions"]] = relationship("TirageEuromillions")

    def __repr__(self) -> str:
        return f"<GrilleEuro {self.numeros_str}>"

    @property
    def numeros(self) -> list[int]:
        return sorted([self.numero_1, self.numero_2, self.numero_3, self.numero_4, self.numero_5])

    @property
    def etoiles(self) -> list[int]:
        return sorted([self.etoile_1, self.etoile_2])

    @property
    def numeros_str(self) -> str:
        nums = "-".join(map(str, self.numeros))
        stars = " ".join(f"★{e}" for e in self.etoiles)
        return f"{nums} {stars}"


class StatistiquesEuromillions(Base):
    """Statistiques calculées sur les tirages Euromillions (cache)"""

    __tablename__ = "jeux_stats_euromillions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    date_calcul: Mapped[datetime] = mapped_column(DateTime, default=utc_now)

    frequences_numeros: Mapped[dict] = mapped_column(JSON, nullable=True)
    frequences_etoiles: Mapped[dict] = mapped_column(JSON, nullable=True)

    numeros_chauds: Mapped[dict] = mapped_column(JSON, nullable=True)
    numeros_froids: Mapped[dict] = mapped_column(JSON, nullable=True)
    numeros_retard: Mapped[dict] = mapped_column(JSON, nullable=True)
    etoiles_chaudes: Mapped[dict] = mapped_column(JSON, nullable=True)
    etoiles_froides: Mapped[dict] = mapped_column(JSON, nullable=True)

    somme_moyenne: Mapped[float | None] = mapped_column(Float, nullable=True)
    paires_frequentes: Mapped[dict] = mapped_column(JSON, nullable=True)
    nb_tirages_analyses: Mapped[int] = mapped_column(Integer, default=0)


# ═══════════════════════════════════════════════════════════════════
# SUIVI DES COTES EN TEMPS RÉEL
# ═══════════════════════════════════════════════════════════════════


class CoteHistorique(CreeLeMixin, Base):
    """Historique des mouvements de cotes par bookmaker"""

    __tablename__ = "jeux_cotes_historique"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    match_id: Mapped[int] = mapped_column(Integer, ForeignKey("jeux_matchs.id"), nullable=False)

    bookmaker: Mapped[str] = mapped_column(String(100), nullable=False)
    marche: Mapped[str] = mapped_column(String(50), nullable=False)  # "1", "N", "2", "over_2.5"

    cote: Mapped[float] = mapped_column(Float, nullable=False)
    probabilite_implicite: Mapped[float | None] = mapped_column(Float, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=utc_now)

    # Relations
    match: Mapped["Match"] = relationship("Match")

    def __repr__(self) -> str:
        return f"<Cote {self.bookmaker} {self.marche}={self.cote} @ {self.timestamp}>"


# ═══════════════════════════════════════════════════════════════════
# MISE RESPONSABLE
# ═══════════════════════════════════════════════════════════════════


class MiseResponsable(CreeLeMixin, Base):
    """Suivi mensuel de la mise responsable"""

    __tablename__ = "jeux_mise_responsable"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    mois: Mapped[date] = mapped_column(Date, nullable=False)  # Premier jour du mois

    # Limites
    limite_mensuelle: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), nullable=False, default=Decimal("50.00")
    )
    mises_cumulees: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("0.00"))

    # Alertes déclenchées
    alerte_50_pct: Mapped[bool] = mapped_column(Boolean, default=False)
    alerte_75_pct: Mapped[bool] = mapped_column(Boolean, default=False)
    alerte_90_pct: Mapped[bool] = mapped_column(Boolean, default=False)
    alerte_100_pct: Mapped[bool] = mapped_column(Boolean, default=False)

    # Auto-exclusion
    auto_exclusion_jusqu_a: Mapped[date | None] = mapped_column(Date, nullable=True)

    # Cooldown
    cooldown_actif: Mapped[bool] = mapped_column(Boolean, default=False)
    cooldown_fin: Mapped[date | None] = mapped_column(Date, nullable=True)

    def __repr__(self) -> str:
        return f"<MiseResponsable {self.mois}: {self.mises_cumulees}/{self.limite_mensuelle}>"

    @property
    def pourcentage_utilise(self) -> float:
        """Pourcentage de la limite utilisée"""
        if self.limite_mensuelle == 0:
            return 100.0
        return float(self.mises_cumulees / self.limite_mensuelle * 100)

    @property
    def reste_disponible(self) -> Decimal:
        """Montant restant disponible ce mois"""
        reste = self.limite_mensuelle - self.mises_cumulees
        return max(reste, Decimal("0.00"))

    @property
    def est_bloque(self) -> bool:
        """Indique si les mises sont bloquées"""
        from datetime import date as date_type

        if self.auto_exclusion_jusqu_a and self.auto_exclusion_jusqu_a > date_type.today():
            return True
        if self.cooldown_actif and self.cooldown_fin and self.cooldown_fin > date_type.today():
            return True
        return self.mises_cumulees >= self.limite_mensuelle
