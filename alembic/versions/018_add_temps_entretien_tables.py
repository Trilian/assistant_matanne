"""Add temps entretien tables

Revision ID: 018
Revises: 017
Create Date: 2026-03-15 10:00:00.000000

Tables créées:
- sessions_travail: Sessions de travail avec chronomètre
- versions_pieces: Historique des modifications de pièces
- couts_travaux: Détails des coûts de travaux
- logs_statut_objets: Historique des changements de statut
- pieces_maison: Pièces de la maison
- objets_maison: Objets/équipements par pièce
- zones_jardin: Zones du jardin
- plantes_jardin: Plantes dans les zones

"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision = "018"
down_revision = "017"
branch_labels = None
depends_on = None


def upgrade():
    # ═══════════════════════════════════════════════════════════
    # TABLE: pieces_maison
    # Pièces de la maison avec leurs caractéristiques
    # ═══════════════════════════════════════════════════════════
    op.create_table(
        "pieces_maison",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("nom", sa.String(100), nullable=False),
        sa.Column("etage", sa.Integer(), default=0),
        sa.Column("superficie_m2", sa.Numeric(6, 2), nullable=True),
        sa.Column("type_piece", sa.String(50), nullable=True, index=True),
        sa.Column("description", sa.Text(), nullable=True),
        # Timestamps
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()
        ),
    )

    # ═══════════════════════════════════════════════════════════
    # TABLE: objets_maison
    # Objets/équipements dans les pièces
    # ═══════════════════════════════════════════════════════════
    op.create_table(
        "objets_maison",
        sa.Column("id", sa.Integer(), primary_key=True),
        # Localisation
        sa.Column(
            "piece_id",
            sa.Integer(),
            sa.ForeignKey("pieces_maison.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        # Identification
        sa.Column("nom", sa.String(200), nullable=False),
        sa.Column("categorie", sa.String(50), nullable=True, index=True),
        # Statut
        sa.Column("statut", sa.String(50), default="fonctionne", index=True),
        sa.Column("priorite_remplacement", sa.String(20), nullable=True),
        # Infos achat
        sa.Column("date_achat", sa.Date(), nullable=True),
        sa.Column("prix_achat", sa.Numeric(10, 2), nullable=True),
        sa.Column("prix_remplacement_estime", sa.Numeric(10, 2), nullable=True),
        # Détails produit
        sa.Column("marque", sa.String(100), nullable=True),
        sa.Column("modele", sa.String(100), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        # Timestamps
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()
        ),
    )

    # ═══════════════════════════════════════════════════════════
    # TABLE: zones_jardin
    # Zones du jardin (potager, pelouse, massif, etc.)
    # ═══════════════════════════════════════════════════════════
    op.create_table(
        "zones_jardin",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("nom", sa.String(100), nullable=False),
        sa.Column("type_zone", sa.String(50), nullable=False, index=True),
        sa.Column("superficie_m2", sa.Numeric(8, 2), nullable=True),
        sa.Column("exposition", sa.String(10), nullable=True),
        sa.Column("type_sol", sa.String(50), nullable=True),
        sa.Column("arrosage_auto", sa.Boolean(), default=False),
        sa.Column("description", sa.Text(), nullable=True),
        # Timestamps
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()
        ),
    )

    # ═══════════════════════════════════════════════════════════
    # TABLE: plantes_jardin
    # Plantes dans les zones du jardin
    # ═══════════════════════════════════════════════════════════
    op.create_table(
        "plantes_jardin",
        sa.Column("id", sa.Integer(), primary_key=True),
        # Localisation
        sa.Column(
            "zone_id",
            sa.Integer(),
            sa.ForeignKey("zones_jardin.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        # Identification
        sa.Column("nom", sa.String(100), nullable=False),
        sa.Column("variete", sa.String(100), nullable=True),
        # État
        sa.Column("etat", sa.String(20), default="bon"),
        # Dates
        sa.Column("date_plantation", sa.Date(), nullable=True),
        sa.Column("mois_semis", sa.String(100), nullable=True),  # JSON array
        sa.Column("mois_recolte", sa.String(100), nullable=True),  # JSON array
        # Entretien
        sa.Column("arrosage", sa.String(50), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        # Timestamps
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()
        ),
    )

    # ═══════════════════════════════════════════════════════════
    # TABLE: sessions_travail
    # Sessions de travail avec chronomètre
    # ═══════════════════════════════════════════════════════════
    op.create_table(
        "sessions_travail",
        sa.Column("id", sa.Integer(), primary_key=True),
        # Type et contexte
        sa.Column("type_activite", sa.String(50), nullable=False, index=True),
        sa.Column("zone_jardin_id", sa.Integer(), nullable=True, index=True),
        sa.Column("piece_id", sa.Integer(), nullable=True, index=True),
        sa.Column("description", sa.Text(), nullable=True),
        # Temps
        sa.Column("debut", sa.DateTime(), nullable=False),
        sa.Column("fin", sa.DateTime(), nullable=True),
        sa.Column("duree_minutes", sa.Integer(), nullable=True),
        # Feedback
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("difficulte", sa.Integer(), nullable=True),
        sa.Column("satisfaction", sa.Integer(), nullable=True),
        # Timestamps
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        # Contraintes
        sa.CheckConstraint(
            "difficulte IS NULL OR (difficulte >= 1 AND difficulte <= 5)",
            name="ck_sessions_travail_difficulte_1_5",
        ),
        sa.CheckConstraint(
            "satisfaction IS NULL OR (satisfaction >= 1 AND satisfaction <= 5)",
            name="ck_sessions_travail_satisfaction_1_5",
        ),
        sa.CheckConstraint(
            "duree_minutes IS NULL OR duree_minutes >= 0",
            name="ck_sessions_travail_duree_positive",
        ),
    )

    # ═══════════════════════════════════════════════════════════
    # TABLE: versions_pieces
    # Historique des versions/modifications de pièces
    # ═══════════════════════════════════════════════════════════
    op.create_table(
        "versions_pieces",
        sa.Column("id", sa.Integer(), primary_key=True),
        # Pièce et version
        sa.Column("piece_id", sa.Integer(), nullable=False, index=True),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("type_modification", sa.String(50), nullable=False),
        # Détails
        sa.Column("titre", sa.String(200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("date_modification", sa.Date(), nullable=False),
        # Coûts
        sa.Column("cout_total", sa.Numeric(10, 2), nullable=True),
        # Photos
        sa.Column("photo_avant_url", sa.String(500), nullable=True),
        sa.Column("photo_apres_url", sa.String(500), nullable=True),
        # Métadonnées
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("cree_par", sa.String(100), nullable=True),
    )

    # ═══════════════════════════════════════════════════════════
    # TABLE: couts_travaux
    # Détails des coûts de travaux par version de pièce
    # ═══════════════════════════════════════════════════════════
    op.create_table(
        "couts_travaux",
        sa.Column("id", sa.Integer(), primary_key=True),
        # Lien version
        sa.Column(
            "version_id",
            sa.Integer(),
            sa.ForeignKey("versions_pieces.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        # Détails coût
        sa.Column("categorie", sa.String(50), nullable=False),
        sa.Column("libelle", sa.String(200), nullable=False),
        sa.Column("montant", sa.Numeric(10, 2), nullable=False),
        # Infos complémentaires
        sa.Column("fournisseur", sa.String(200), nullable=True),
        sa.Column("facture_ref", sa.String(100), nullable=True),
        sa.Column("date_paiement", sa.Date(), nullable=True),
        # Timestamps
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        # Contraintes
        sa.CheckConstraint("montant >= 0", name="ck_couts_travaux_montant_positif"),
    )

    # ═══════════════════════════════════════════════════════════
    # TABLE: logs_statut_objets
    # Historique des changements de statut d'objets
    # ═══════════════════════════════════════════════════════════
    op.create_table(
        "logs_statut_objets",
        sa.Column("id", sa.Integer(), primary_key=True),
        # Objet concerné
        sa.Column("objet_id", sa.Integer(), nullable=False, index=True),
        # Changement de statut
        sa.Column("ancien_statut", sa.String(50), nullable=True),
        sa.Column("nouveau_statut", sa.String(50), nullable=False),
        sa.Column("raison", sa.Text(), nullable=True),
        # Infos remplacement
        sa.Column("prix_estime", sa.Numeric(10, 2), nullable=True),
        sa.Column("priorite", sa.String(20), nullable=True),
        # Actions déclenchées
        sa.Column("ajoute_courses", sa.Boolean(), default=False),
        sa.Column("ajoute_budget", sa.Boolean(), default=False),
        # Métadonnées
        sa.Column("date_changement", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("change_par", sa.String(100), nullable=True),
    )

    # ═══════════════════════════════════════════════════════════
    # INDEX COMPOSITES
    # ═══════════════════════════════════════════════════════════
    op.create_index(
        "ix_sessions_travail_type_debut",
        "sessions_travail",
        ["type_activite", "debut"],
    )
    op.create_index(
        "ix_versions_pieces_piece_version",
        "versions_pieces",
        ["piece_id", "version"],
    )


def downgrade():
    # Index composites
    op.drop_index("ix_versions_pieces_piece_version", table_name="versions_pieces")
    op.drop_index("ix_sessions_travail_type_debut", table_name="sessions_travail")

    # Tables (ordre inverse des dépendances)
    op.drop_table("logs_statut_objets")
    op.drop_table("couts_travaux")
    op.drop_table("versions_pieces")
    op.drop_table("sessions_travail")
    op.drop_table("plantes_jardin")
    op.drop_table("zones_jardin")
    op.drop_table("objets_maison")
    op.drop_table("pieces_maison")
