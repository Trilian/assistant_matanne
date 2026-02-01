"""
Modèles SQLAlchemy pour le domaine Jeux (Paris sportifs & Loto)
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List

from sqlalchemy import String, Integer, Float, Boolean, Date, DateTime, Text, ForeignKey, JSON, Numeric, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from src.core.models.base import Base


# ═══════════════════════════════════════════════════════════════════
# ENUMS
# ═══════════════════════════════════════════════════════════════════

class ResultatMatchEnum(str, enum.Enum):
    """Résultat possible d'un match"""
    VICTOIRE_DOMICILE = "1"
    NUL = "N"
    VICTOIRE_EXTERIEUR = "2"
    NON_JOUE = "non_joue"


class StatutPariEnum(str, enum.Enum):
    """Statut d'un pari"""
    EN_ATTENTE = "en_attente"
    GAGNE = "gagne"
    PERDU = "perdu"
    ANNULE = "annule"


class TypePariEnum(str, enum.Enum):
    """Type de pari"""
    RESULTAT_MATCH = "1N2"
    OVER_UNDER = "over_under"
    SCORE_EXACT = "score_exact"
    BTTS = "les_deux_marquent"  # Both Teams To Score


class ChampionnatEnum(str, enum.Enum):
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

class Equipe(Base):
    """Équipe de football"""
    __tablename__ = "jeux_equipes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nom: Mapped[str] = mapped_column(String(100), nullable=False)
    nom_court: Mapped[str] = mapped_column(String(50), nullable=True)
    championnat: Mapped[str] = mapped_column(String(50), nullable=False)
    pays: Mapped[str] = mapped_column(String(50), nullable=True)
    logo_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Stats agrégées (mises à jour automatiquement)
    matchs_joues: Mapped[int] = mapped_column(Integer, default=0)
    victoires: Mapped[int] = mapped_column(Integer, default=0)
    nuls: Mapped[int] = mapped_column(Integer, default=0)
    defaites: Mapped[int] = mapped_column(Integer, default=0)
    buts_marques: Mapped[int] = mapped_column(Integer, default=0)
    buts_encaisses: Mapped[int] = mapped_column(Integer, default=0)
    
    # Méta
    cree_le: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    modifie_le: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relations
    matchs_domicile: Mapped[List["Match"]] = relationship(
        "Match", foreign_keys="Match.equipe_domicile_id", back_populates="equipe_domicile"
    )
    matchs_exterieur: Mapped[List["Match"]] = relationship(
        "Match", foreign_keys="Match.equipe_exterieur_id", back_populates="equipe_exterieur"
    )

    def __repr__(self) -> str:
        return f"<Equipe {self.nom} ({self.championnat})>"

    @property
    def forme_recente(self) -> str:
        """Retourne la forme sur les 5 derniers matchs (ex: VVNPV)"""
        # Sera calculé dynamiquement
        return ""
    
    @property
    def points(self) -> int:
        """Calcule les points (3V + 1N)"""
        return self.victoires * 3 + self.nuls


class Match(Base):
    """Match de football"""
    __tablename__ = "jeux_matchs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    
    # Équipes
    equipe_domicile_id: Mapped[int] = mapped_column(Integer, ForeignKey("jeux_equipes.id"), nullable=False)
    equipe_exterieur_id: Mapped[int] = mapped_column(Integer, ForeignKey("jeux_equipes.id"), nullable=False)
    
    # Infos match
    championnat: Mapped[str] = mapped_column(String(50), nullable=False)
    journee: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    date_match: Mapped[date] = mapped_column(Date, nullable=False)
    heure: Mapped[Optional[str]] = mapped_column(String(5), nullable=True)  # "20:45"
    
    # Résultat
    score_domicile: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    score_exterieur: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    resultat: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)  # "1", "N", "2"
    joue: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Cotes (optionnel - si on veut les tracker)
    cote_domicile: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    cote_nul: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    cote_exterieur: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Prédiction IA
    prediction_resultat: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    prediction_proba_dom: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    prediction_proba_nul: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    prediction_proba_ext: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    prediction_confiance: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # 0-100%
    prediction_raison: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Méta
    cree_le: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    modifie_le: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relations
    equipe_domicile: Mapped["Equipe"] = relationship("Equipe", foreign_keys=[equipe_domicile_id], back_populates="matchs_domicile")
    equipe_exterieur: Mapped["Equipe"] = relationship("Equipe", foreign_keys=[equipe_exterieur_id], back_populates="matchs_exterieur")
    paris: Mapped[List["PariSportif"]] = relationship("PariSportif", back_populates="match")

    def __repr__(self) -> str:
        if self.joue:
            return f"<Match {self.equipe_domicile.nom} {self.score_domicile}-{self.score_exterieur} {self.equipe_exterieur.nom}>"
        return f"<Match {self.date_match}: DOM vs EXT>"


class PariSportif(Base):
    """Pari sportif enregistré (réel ou virtuel)"""
    __tablename__ = "jeux_paris_sportifs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    match_id: Mapped[int] = mapped_column(Integer, ForeignKey("jeux_matchs.id"), nullable=False)
    
    # Détails du pari
    type_pari: Mapped[str] = mapped_column(String(30), default="1N2")  # 1N2, over_under, etc.
    prediction: Mapped[str] = mapped_column(String(20), nullable=False)  # "1", "N", "2", "over_2.5"
    cote: Mapped[float] = mapped_column(Float, nullable=False)
    mise: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("0.00"))  # 0 = pari virtuel
    
    # Résultat
    statut: Mapped[str] = mapped_column(String(20), default="en_attente")
    gain: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    
    # Tracking
    est_virtuel: Mapped[bool] = mapped_column(Boolean, default=True)  # Pari simulé vs réel
    confiance_prediction: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # Score IA
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Méta
    cree_le: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relations
    match: Mapped["Match"] = relationship("Match", back_populates="paris")

    def __repr__(self) -> str:
        return f"<Pari {self.prediction} @ {self.cote} - {self.statut}>"


# ═══════════════════════════════════════════════════════════════════
# MODÈLES LOTO
# ═══════════════════════════════════════════════════════════════════

class TirageLoto(Base):
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
    jackpot_euros: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    gagnants_rang1: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Méta
    cree_le: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<Tirage {self.date_tirage}: {self.numeros_str}>"
    
    @property
    def numeros(self) -> List[int]:
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
    tirage_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("jeux_tirages_loto.id"), nullable=True)
    
    # Numéros choisis
    numero_1: Mapped[int] = mapped_column(Integer, nullable=False)
    numero_2: Mapped[int] = mapped_column(Integer, nullable=False)
    numero_3: Mapped[int] = mapped_column(Integer, nullable=False)
    numero_4: Mapped[int] = mapped_column(Integer, nullable=False)
    numero_5: Mapped[int] = mapped_column(Integer, nullable=False)
    numero_chance: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # Tracking
    est_virtuelle: Mapped[bool] = mapped_column(Boolean, default=True)
    source_prediction: Mapped[str] = mapped_column(String(50), default="manuel")  # "manuel", "ia", "aleatoire"
    mise: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("2.20"))
    
    # Résultat (après tirage)
    numeros_trouves: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # 0-5
    chance_trouvee: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    gain: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    rang: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # 1-9 ou null
    
    # Méta
    date_creation: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relations
    tirage: Mapped[Optional["TirageLoto"]] = relationship("TirageLoto")

    def __repr__(self) -> str:
        return f"<Grille {self.numeros_str}>"
    
    @property
    def numeros(self) -> List[int]:
        return sorted([self.numero_1, self.numero_2, self.numero_3, self.numero_4, self.numero_5])
    
    @property
    def numeros_str(self) -> str:
        return f"{'-'.join(map(str, self.numeros))} + N°{self.numero_chance}"


class StatistiquesLoto(Base):
    """Statistiques calculées sur les tirages (cache)"""
    __tablename__ = "jeux_stats_loto"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    date_calcul: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Stats par numéro (JSON: {1: {freq: 123, dernier: "2024-01-01", ecart: 5}, ...})
    frequences_numeros: Mapped[dict] = mapped_column(JSON, nullable=True)
    frequences_chance: Mapped[dict] = mapped_column(JSON, nullable=True)
    
    # Numéros chauds/froids (top 5)
    numeros_chauds: Mapped[dict] = mapped_column(JSON, nullable=True)  # Plus fréquents
    numeros_froids: Mapped[dict] = mapped_column(JSON, nullable=True)  # Moins fréquents
    numeros_retard: Mapped[dict] = mapped_column(JSON, nullable=True)  # Plus grand écart
    
    # Patterns
    somme_moyenne: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    paires_frequentes: Mapped[dict] = mapped_column(JSON, nullable=True)
    
    # Méta
    nb_tirages_analyses: Mapped[int] = mapped_column(Integer, default=0)


# ═══════════════════════════════════════════════════════════════════
# SUIVI GLOBAL (Bankroll & Performance)
# ═══════════════════════════════════════════════════════════════════

class HistoriqueJeux(Base):
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
    
    # Méta
    cree_le: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

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
