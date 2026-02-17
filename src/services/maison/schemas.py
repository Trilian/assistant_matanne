"""
Schemas Pydantic pour les services Maison.

Modèles de validation pour:
- Briefings et alertes
- Jardin (conseils, arrosage, plantes)
- Entretien (routines, tâches)
- Projets (estimation, matériaux)
- Énergie (éco-score, badges)
- Inventaire (pièces, objets, recherche)
"""

from datetime import date as date_type
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

# ═══════════════════════════════════════════════════════════
# ENUMS
# ═══════════════════════════════════════════════════════════


class NiveauUrgence(str, Enum):
    """Niveau d'urgence pour alertes."""

    HAUTE = "haute"
    MOYENNE = "moyenne"
    BASSE = "basse"
    INFO = "info"


class TypeAlerteMaison(str, Enum):
    """Types d'alertes maison."""

    METEO = "meteo"
    ENTRETIEN = "entretien"
    PROJET = "projet"
    STOCK = "stock"
    ENERGIE = "energie"
    JARDIN = "jardin"


class CategorieObjet(str, Enum):
    """Catégories d'objets maison."""

    ELECTROMENAGER = "electromenager"
    VAISSELLE = "vaisselle"
    OUTIL = "outil"
    DECORATION = "decoration"
    VETEMENT = "vetement"
    ELECTRONIQUE = "electronique"
    MEUBLE = "meuble"
    LINGE = "linge"
    JOUET = "jouet"
    LIVRE = "livre"
    AUTRE = "autre"


class TypeZoneJardin(str, Enum):
    """Types de zones jardin."""

    POTAGER = "potager"
    PELOUSE = "pelouse"
    MASSIF = "massif"
    VERGER = "verger"
    HAIE = "haie"
    TERRASSE = "terrasse"
    COMPOST = "compost"
    SERRE = "serre"
    CABANE = "cabane"
    ALLEE = "allee"
    AUTRE = "autre"


class EtatPlante(str, Enum):
    """État de santé d'une plante."""

    EXCELLENT = "excellent"
    BON = "bon"
    ATTENTION = "attention"
    PROBLEME = "probleme"


class StatutObjet(str, Enum):
    """Statut d'un objet dans l'inventaire."""

    FONCTIONNE = "fonctionne"  # En bon état
    A_REPARER = "a_reparer"  # Nécessite réparation
    A_CHANGER = "a_changer"  # À remplacer
    A_ACHETER = "a_acheter"  # Nouvel achat prévu
    EN_COMMANDE = "en_commande"  # Déjà commandé
    HORS_SERVICE = "hors_service"  # Ne fonctionne plus
    A_DONNER = "a_donner"  # À donner/vendre
    ARCHIVE = "archive"  # Historique seulement


class TypeModificationPiece(str, Enum):
    """Types de modifications de pièce."""

    AJOUT_MEUBLE = "ajout_meuble"
    RETRAIT_MEUBLE = "retrait_meuble"
    DEPLACEMENT = "deplacement"
    RENOVATION = "renovation"
    PEINTURE = "peinture"
    AMENAGEMENT = "amenagement"
    REPARATION = "reparation"


class PrioriteRemplacement(str, Enum):
    """Priorité pour remplacement d'objet."""

    URGENTE = "urgente"  # Dans la semaine
    HAUTE = "haute"  # Dans le mois
    NORMALE = "normale"  # Quand budget permet
    BASSE = "basse"  # Optionnel
    FUTURE = "future"  # Un jour...


# ═══════════════════════════════════════════════════════════
# BRIEFING & ALERTES
# ═══════════════════════════════════════════════════════════


class AlerteMaison(BaseModel):
    """Alerte maison avec niveau d'urgence."""

    model_config = ConfigDict(from_attributes=True)

    type: TypeAlerteMaison
    niveau: NiveauUrgence
    titre: str
    message: str
    action_suggeree: str | None = None
    date_limite: date_type | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class ActionPrioritaire(BaseModel):
    """Action prioritaire pour le briefing quotidien."""

    titre: str
    description: str | None = None
    duree_estimee_min: int | None = None
    module: str  # jardin, entretien, projet
    lien: str | None = None  # Lien vers le module


class BriefingMaison(BaseModel):
    """Briefing quotidien maison généré par l'IA."""

    date: date_type = Field(default_factory=date_type.today)
    resume: str = ""
    taches_jour: list[str] = Field(default_factory=list)
    alertes: list[AlerteMaison] = Field(default_factory=list)
    meteo_impact: str | None = None
    projets_actifs: list[str] = Field(default_factory=list)
    priorites: list[str] = Field(default_factory=list)
    eco_score_jour: int | None = None


# ═══════════════════════════════════════════════════════════
# JARDIN
# ═══════════════════════════════════════════════════════════


class ConseilJardin(BaseModel):
    """Conseil jardin contextuel."""

    titre: str
    contenu: str
    priorite: NiveauUrgence = NiveauUrgence.MOYENNE
    type_conseil: str  # saison, meteo, plante, general
    plantes_concernees: list[str] = Field(default_factory=list)


class PlanArrosage(BaseModel):
    """Plan d'arrosage pour une zone/plante."""

    zone_ou_plante: str
    frequence: str  # quotidien, tous_2_jours, hebdo
    quantite_litres: float | None = None
    meilleur_moment: str  # matin, soir
    ajuste_meteo: bool = True
    prochaine_date: date_type | None = None
    notes: str | None = None


class DiagnosticPlante(BaseModel):
    """Diagnostic d'une plante (via photo IA)."""

    plante_identifiee: str | None = None
    etat: EtatPlante
    problemes_detectes: list[str] = Field(default_factory=list)
    traitements_suggeres: list[str] = Field(default_factory=list)
    confiance: float = 0.0  # 0-1


class ZoneJardinCreate(BaseModel):
    """Création d'une zone jardin."""

    nom: str
    type_zone: TypeZoneJardin
    superficie_m2: float | None = None
    exposition: str | None = None  # N, S, E, O, NE...
    type_sol: str | None = None
    coordonnees: list[list[float]] | None = None  # Polygone [[x,y], ...]
    arrosage_auto: bool = False
    notes: str | None = None


class PlanJardinCreate(BaseModel):
    """Création d'un plan de jardin."""

    nom: str
    largeur: float  # mètres
    hauteur: float  # mètres
    description: str | None = None


class PlanteJardinCreate(BaseModel):
    """Ajout d'une plante sur le plan jardin (avec position)."""

    nom: str
    variete: str | None = None
    zone_id: int
    position_x: float
    position_y: float
    date_plantation: date_type | None = None
    etat: EtatPlante = EtatPlante.BON
    notes: str | None = None


class ActionPlanteCreate(BaseModel):
    """Action effectuée sur une plante."""

    plante_id: int
    type_action: str  # arrosage, taille, recolte, traitement, etc.
    date_action: date_type | None = None
    notes: str | None = None
    quantite: float | None = None  # Pour récoltes


class PlanteCreate(BaseModel):
    """Création d'une plante dans le jardin."""

    nom: str
    variete: str | None = None
    zone_id: int
    position_x: float | None = None
    position_y: float | None = None
    date_plantation: date_type | None = None
    arrosage_frequence: str | None = None
    exposition_ideale: str | None = None
    notes: str | None = None


# ═══════════════════════════════════════════════════════════
# ENTRETIEN
# ═══════════════════════════════════════════════════════════


class TacheRoutineCreate(BaseModel):
    """Tâche d'une routine."""

    nom: str
    description: str | None = None
    ordre: int = 0
    heure_prevue: str | None = None  # HH:MM
    duree_estimee_min: int | None = None


class RoutineCreate(BaseModel):
    """Création d'une routine d'entretien."""

    nom: str
    description: str | None = None
    categorie: str  # menage, cuisine, jardin, enfant
    frequence: str  # quotidien, hebdo, mensuel, saisonnier
    jour_semaine: int | None = None  # 0=lundi, 6=dimanche
    taches: list[TacheRoutineCreate] = Field(default_factory=list)


class RoutineSuggestionIA(BaseModel):
    """Suggestion de routine par l'IA."""

    nom: str
    description: str
    taches_suggerees: list[str]
    frequence_recommandee: str
    duree_totale_estimee_min: int


# ═══════════════════════════════════════════════════════════
# PROJETS
# ═══════════════════════════════════════════════════════════


class MaterielProjet(BaseModel):
    """Matériel nécessaire pour un projet."""

    nom: str
    quantite: float = 1.0
    unite: str = "unité"
    prix_estime: Decimal | None = None
    magasin_suggere: str | None = None
    url: str | None = None
    alternatif_eco: str | None = None
    alternatif_prix: Decimal | None = None


class TacheProjetCreate(BaseModel):
    """Tâche d'un projet."""

    nom: str
    description: str | None = None
    ordre: int = 0
    duree_estimee_min: int | None = None
    date_echeance: date_type | None = None
    materiels_requis: list[str] = Field(default_factory=list)


class ProjetCreate(BaseModel):
    """Création d'un projet maison."""

    nom: str
    description: str | None = None
    categorie: str  # travaux, renovation, amenagement, reparation
    priorite: str = "moyenne"
    date_fin_prevue: date_type | None = None
    budget_estime: Decimal | None = None


class ProjetEstimation(BaseModel):
    """Estimation complète d'un projet par l'IA."""

    nom_projet: str
    description_analysee: str
    budget_estime_min: Decimal
    budget_estime_max: Decimal
    duree_estimee_jours: int
    taches_suggerees: list[TacheProjetCreate]
    materiels_necessaires: list[MaterielProjet]
    risques_identifies: list[str] = Field(default_factory=list)
    conseils_ia: list[str] = Field(default_factory=list)


# ═══════════════════════════════════════════════════════════
# ÉNERGIE & ÉCO-SCORE
# ═══════════════════════════════════════════════════════════


class ConsommationMois(BaseModel):
    """Consommation mensuelle d'une énergie."""

    mois: date_type
    energie: str  # electricite, gaz, eau
    consommation: float
    unite: str
    montant: Decimal | None = None
    variation_pct: float | None = None  # vs mois précédent


class BadgeEco(BaseModel):
    """Badge éco-score gagné."""

    nom: str
    description: str
    icone: str
    date_obtention: date_type
    categorie: str  # energie, eau, dechets


class EcoScoreResult(BaseModel):
    """Résultat éco-score mensuel."""

    mois: date_type
    score: int = Field(ge=0, le=100)
    score_precedent: int | None = None
    variation: int | None = None
    streak_jours: int = 0
    economies_euros: Decimal = Decimal("0.00")
    badges_obtenus: list[BadgeEco] = Field(default_factory=list)
    conseils_amelioration: list[str] = Field(default_factory=list)
    comparaison_moyenne: str | None = None  # "10% sous la moyenne"


class AnalyseEnergie(BaseModel):
    """Analyse détaillée consommation énergie."""

    periode: str
    energie: str
    consommation_totale: float
    cout_total: Decimal
    tendance: str  # hausse, stable, baisse
    anomalies_detectees: list[str] = Field(default_factory=list)
    correlation_meteo: str | None = None
    suggestions_economies: list[str] = Field(default_factory=list)


# ═══════════════════════════════════════════════════════════
# INVENTAIRE MAISON
# ═══════════════════════════════════════════════════════════


class ConteneurCreate(BaseModel):
    """Conteneur/rangement dans une pièce."""

    nom: str
    type: str  # placard, tiroir, etagere, boite, autre
    position: str | None = None  # gauche, droite, sous_evier


class PieceCreate(BaseModel):
    """Création d'une pièce."""

    nom: str
    etage: str = "RDC"  # RDC, 1er, Sous-sol, Grenier
    superficie_m2: float | None = None
    conteneurs: list[ConteneurCreate] = Field(default_factory=list)


# ═══════════════════════════════════════════════════════════
# VERSIONING PIÈCES & COÛTS TRAVAUX
# ═══════════════════════════════════════════════════════════


class ModificationPieceCreate(BaseModel):
    """Modification apportée à une pièce (pour versioning)."""

    type_modification: TypeModificationPiece
    description: str
    objet_concerne: str | None = None  # Ex: "Bibliothèque BILLY"
    cout_estime: Decimal = Decimal("0")
    cout_reel: Decimal | None = None
    date_modification: date_type = Field(default_factory=date_type.today)
    notes: str | None = None


class PieceVersion(BaseModel):
    """Version d'une pièce avec son état à un moment donné."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    piece_id: int
    numero_version: int
    date_creation: datetime
    nom_version: str | None = None  # Ex: "Avant réaménagement", "Config été 2024"
    modifications: list[ModificationPieceCreate] = Field(default_factory=list)
    cout_total_version: Decimal = Decimal("0")
    image_url: str | None = None  # Photo avant/après
    commentaire: str | None = None


class PlanReorganisationPiece(BaseModel):
    """Plan de réorganisation d'une pièce avec coûts."""

    piece_id: int
    nom_version: str  # Ex: "Nouveau bureau gaming"
    modifications_prevues: list[ModificationPieceCreate] = Field(default_factory=list)
    budget_total_estime: Decimal = Decimal("0")
    objets_a_acheter: list["ObjetCreate"] = Field(default_factory=list)
    objets_a_retirer: list[int] = Field(default_factory=list)  # IDs des objets
    date_fin_prevue: date_type | None = None
    ajouter_au_budget_global: bool = True


class CoutTravauxPiece(BaseModel):
    """Suivi des coûts de travaux pour une pièce."""

    model_config = ConfigDict(from_attributes=True)

    piece_id: int
    piece_nom: str
    type_travaux: TypeModificationPiece
    description: str
    budget_prevu: Decimal
    budget_reel: Decimal = Decimal("0")
    date_debut: date_type | None = None
    date_fin: date_type | None = None
    statut: str = "planifie"  # planifie, en_cours, termine, annule
    fournisseur: str | None = None
    factures: list[str] = Field(default_factory=list)  # URLs/refs factures
    notes: str | None = None


class ResumeTravauxMaison(BaseModel):
    """Résumé de tous les travaux maison."""

    budget_total_prevu: Decimal = Decimal("0")
    budget_total_depense: Decimal = Decimal("0")
    budget_restant: Decimal = Decimal("0")
    travaux_en_cours: int = 0
    travaux_planifies: int = 0
    travaux_termines: int = 0
    prochaine_echeance: date_type | None = None
    cout_par_piece: dict[str, Decimal] = Field(default_factory=dict)


class ObjetCreate(BaseModel):
    """Création d'un objet dans l'inventaire."""

    nom: str
    categorie: CategorieObjet = CategorieObjet.AUTRE
    conteneur_id: int | None = None
    quantite: int = 1
    marque: str | None = None
    modele: str | None = None
    date_achat: date_type | None = None
    prix_achat: Decimal | None = None
    date_garantie: date_type | None = None
    code_barre: str | None = None
    notes: str | None = None
    # Nouveaux champs statut/remplacement
    statut: StatutObjet = StatutObjet.FONCTIONNE
    priorite_remplacement: PrioriteRemplacement | None = None
    cout_remplacement_estime: Decimal | None = None
    url_produit_remplacement: str | None = None


class ObjetUpdate(BaseModel):
    """Mise à jour d'un objet (changement statut, etc.)."""

    nom: str | None = None
    statut: StatutObjet | None = None
    priorite_remplacement: PrioriteRemplacement | None = None
    cout_remplacement_estime: Decimal | None = None
    url_produit_remplacement: str | None = None
    notes: str | None = None


class DemandeChangementObjet(BaseModel):
    """Demande de changement/achat d'un objet.

    Créé quand on clique "À changer" ou "À acheter" sur un objet.
    Peut être lié au budget et à la liste de courses.
    """

    objet_id: int
    ancien_statut: StatutObjet
    nouveau_statut: StatutObjet
    raison: str | None = None
    priorite: PrioriteRemplacement = PrioriteRemplacement.NORMALE
    cout_estime: Decimal | None = None
    date_souhaitee: date_type | None = None
    ajouter_liste_courses: bool = False
    ajouter_budget: bool = False


class ObjetAvecStatut(BaseModel):
    """Objet avec son statut et liens vers modules."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    nom: str
    categorie: CategorieObjet
    piece: str
    conteneur: str | None = None
    statut: StatutObjet
    priorite_remplacement: PrioriteRemplacement | None = None
    cout_remplacement_estime: Decimal | None = None
    url_produit_remplacement: str | None = None
    date_statut_change: datetime | None = None
    # Liens inter-modules
    lien_course_id: int | None = None  # Article liste courses
    lien_budget_id: int | None = None  # Dépense budget prévue


class ResultatRecherche(BaseModel):
    """Résultat de recherche 'où est...'"""

    objet_trouve: str
    emplacement: str  # "Cuisine > Placard haut > Étagère 2"
    piece: str
    conteneur: str | None = None
    quantite: int = 1
    confiance: float = 1.0  # 1.0 = exact, <1.0 = suggestion IA
    suggestions_similaires: list[str] = Field(default_factory=list)


# ═══════════════════════════════════════════════════════════
# INTEGRATION INTER-MODULES
# ═══════════════════════════════════════════════════════════


class ArticleCoursesGenere(BaseModel):
    """Article de courses généré automatiquement."""

    nom: str
    quantite: float = 1.0
    unite: str = "unité"
    categorie: str  # menage, bricolage, jardin
    prix_estime: Decimal | None = None
    source: str  # projet, jardin, stock_bas, objet_a_acheter, objet_a_changer
    source_id: int | None = None
    priorite: str = "normale"


class PipelineResult(BaseModel):
    """Résultat d'un pipeline automatique."""

    succes: bool
    pipeline: str  # nom du pipeline exécuté
    etapes_completees: list[str] = Field(default_factory=list)
    erreurs: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


# Alias pour compatibilité
PipelineResultat = PipelineResult


# ═══════════════════════════════════════════════════════════
# INTÉGRATION OBJETS → BUDGET/COURSES
# ═══════════════════════════════════════════════════════════


class LienObjetBudget(BaseModel):
    """Lien entre un objet à acheter/changer et le budget."""

    model_config = ConfigDict(from_attributes=True)

    objet_id: int
    objet_nom: str
    depense_budget_id: int | None = None
    montant_prevu: Decimal
    categorie_budget: str = "maison"  # maison, travaux, equipement
    date_prevue: date_type | None = None
    statut: str = "prevu"  # prevu, achete, annule


class LienObjetCourses(BaseModel):
    """Lien entre un objet à acheter et la liste de courses."""

    model_config = ConfigDict(from_attributes=True)

    objet_id: int
    objet_nom: str
    article_courses_id: int | None = None
    magasin_suggere: str | None = None
    prix_estime: Decimal | None = None
    url_produit: str | None = None
    date_ajout: datetime = Field(default_factory=datetime.now)


class ActionObjetResult(BaseModel):
    """Résultat d'une action sur un objet (changer/acheter)."""

    succes: bool
    objet_id: int
    nouveau_statut: StatutObjet
    message: str
    lien_budget: LienObjetBudget | None = None
    lien_courses: LienObjetCourses | None = None
    erreurs: list[str] = Field(default_factory=list)


# ═══════════════════════════════════════════════════════════
# TÂCHES RÉCURRENTES & PLANNING
# ═══════════════════════════════════════════════════════════


class FrequenceTache(str, Enum):
    """Fréquence de récurrence d'une tâche."""

    QUOTIDIEN = "quotidien"
    HEBDOMADAIRE = "hebdomadaire"
    BIHEBDOMADAIRE = "bihebdomadaire"
    MENSUEL = "mensuel"
    TRIMESTRIEL = "trimestriel"
    SEMESTRIEL = "semestriel"
    ANNUEL = "annuel"


class TacheMaisonRecurrente(BaseModel):
    """Tâche maison récurrente à synchroniser avec le planning."""

    model_config = ConfigDict(from_attributes=True)

    id: int | None = None
    nom: str
    description: str | None = None
    categorie: str  # entretien, jardin, menage, administratif
    frequence: FrequenceTache
    jour_semaine: int | None = None  # 0=lundi, 6=dimanche (pour hebdo)
    jour_mois: int | None = None  # 1-31 (pour mensuel)
    mois: int | None = None  # 1-12 (pour annuel)
    duree_estimee_min: int | None = None
    priorite: NiveauUrgence = NiveauUrgence.MOYENNE
    actif: bool = True
    derniere_execution: date_type | None = None
    prochaine_execution: date_type | None = None


class SyncPlanningRequest(BaseModel):
    """Demande de synchronisation avec le planning familial."""

    taches_a_synchroniser: list[int] = Field(default_factory=list)  # IDs tâches
    projets_a_synchroniser: list[int] = Field(default_factory=list)  # IDs projets
    periode_debut: date_type = Field(default_factory=date_type.today)
    periode_fin: date_type | None = None
    inclure_recurrentes: bool = True
    notifier_membres: bool = True


class SyncPlanningResult(BaseModel):
    """Résultat de la synchronisation avec le planning."""

    succes: bool
    evenements_crees: int = 0
    evenements_mis_a_jour: int = 0
    evenements_supprimes: int = 0
    conflits_detectes: list[str] = Field(default_factory=list)
    prochains_evenements: list[dict[str, Any]] = Field(default_factory=list)
    message: str = ""


# ═══════════════════════════════════════════════════════════
# SUIVI DU TEMPS - ENTRETIEN & JARDINAGE
# ═══════════════════════════════════════════════════════════


class TypeActiviteEntretien(str, Enum):
    """Types d'activités d'entretien/jardinage."""

    # Jardin
    ARROSAGE = "arrosage"
    TONTE = "tonte"
    TAILLE = "taille"
    DESHERBAGE = "desherbage"
    PLANTATION = "plantation"
    RECOLTE = "recolte"
    COMPOST = "compost"
    TRAITEMENT = "traitement"

    # Ménage intérieur
    MENAGE_GENERAL = "menage_general"
    ASPIRATEUR = "aspirateur"
    LAVAGE_SOL = "lavage_sol"
    POUSSIERE = "poussiere"
    VITRES = "vitres"
    LESSIVE = "lessive"
    REPASSAGE = "repassage"

    # Entretien maison
    BRICOLAGE = "bricolage"
    PEINTURE = "peinture"
    PLOMBERIE = "plomberie"
    ELECTRICITE = "electricite"
    NETTOYAGE_EXTERIEUR = "nettoyage_exterieur"

    # Autres
    RANGEMENT = "rangement"
    ADMINISTRATIF = "administratif"
    AUTRE = "autre"


class SessionTravailCreate(BaseModel):
    """Création d'une session de travail."""

    type_activite: TypeActiviteEntretien
    zone_id: int | None = None  # Zone jardin si applicable
    piece_id: int | None = None  # Pièce si applicable
    description: str | None = None
    debut: datetime = Field(default_factory=datetime.now)


class SessionTravailUpdate(BaseModel):
    """Mise à jour d'une session (arrêt)."""

    fin: datetime = Field(default_factory=datetime.now)
    notes: str | None = None
    difficulte: int | None = Field(None, ge=1, le=5)  # 1-5
    satisfaction: int | None = Field(None, ge=1, le=5)  # 1-5


class SessionTravail(BaseModel):
    """Session de travail complète."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    type_activite: TypeActiviteEntretien
    zone_id: int | None = None
    piece_id: int | None = None
    description: str | None = None
    debut: datetime
    fin: datetime | None = None
    duree_minutes: int | None = None
    notes: str | None = None
    difficulte: int | None = None
    satisfaction: int | None = None
    date_creation: datetime


class StatistiqueTempsActivite(BaseModel):
    """Statistiques de temps par type d'activité."""

    type_activite: TypeActiviteEntretien
    icone: str = "⏱️"
    temps_total_minutes: int = 0
    nb_sessions: int = 0
    temps_moyen_minutes: float = 0.0
    derniere_session: datetime | None = None
    tendance: str = "stable"  # hausse, baisse, stable


class StatistiqueTempsZone(BaseModel):
    """Statistiques de temps par zone/pièce."""

    zone_nom: str
    zone_type: str  # jardin, piece
    temps_total_minutes: int = 0
    nb_sessions: int = 0
    activites_principales: list[str] = Field(default_factory=list)


class ResumeTempsHebdo(BaseModel):
    """Résumé hebdomadaire du temps passé."""

    semaine_debut: date_type
    semaine_fin: date_type
    temps_total_minutes: int = 0
    temps_jardin_minutes: int = 0
    temps_menage_minutes: int = 0
    temps_bricolage_minutes: int = 0
    nb_sessions: int = 0
    jour_plus_actif: str | None = None
    activite_plus_frequente: TypeActiviteEntretien | None = None
    comparaison_semaine_precedente: float = 0.0  # % difference


class SuggestionOptimisation(BaseModel):
    """Suggestion IA pour optimiser le temps."""

    titre: str
    description: str
    type_suggestion: str  # regroupement, planification, materiel, delegation
    temps_economise_estime_min: int | None = None
    activites_concernees: list[TypeActiviteEntretien] = Field(default_factory=list)
    priorite: NiveauUrgence = NiveauUrgence.MOYENNE
    action_directe: str | None = None  # Lien ou action à effectuer


class RecommandationMateriel(BaseModel):
    """Recommandation IA d'achat de matériel pour gagner du temps."""

    nom_materiel: str
    description: str
    categorie: str  # jardin, menage, bricolage
    prix_estime_min: Decimal | None = None
    prix_estime_max: Decimal | None = None
    temps_economise_par_session_min: int | None = None
    retour_investissement_semaines: int | None = None
    activites_ameliorees: list[TypeActiviteEntretien] = Field(default_factory=list)
    priorite_achat: PrioriteRemplacement = PrioriteRemplacement.NORMALE
    lien_produit: str | None = None
    notes: str | None = None


class AnalyseTempsIA(BaseModel):
    """Analyse complète du temps par l'IA."""

    periode_analysee: str  # "semaine", "mois", "trimestre"
    resume_textuel: str
    temps_total_minutes: int = 0
    repartition_par_categorie: dict[str, int] = Field(default_factory=dict)
    suggestions_optimisation: list[SuggestionOptimisation] = Field(default_factory=list)
    recommandations_materiel: list[RecommandationMateriel] = Field(default_factory=list)
    objectif_temps_suggere_min: int | None = None  # Temps hebdo optimal suggéré
    score_efficacite: int | None = Field(None, ge=0, le=100)  # 0-100


class AnalyseTempsRequest(BaseModel):
    """Demande d'analyse IA du temps."""

    periode: str = "mois"  # semaine, mois, trimestre, annee
    inclure_suggestions: bool = True
    inclure_materiel: bool = True
    budget_materiel_max: Decimal | None = None
    objectif_temps_hebdo_min: int | None = None  # Objectif utilisateur
