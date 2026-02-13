"""
Module Meubles - Wishlist d'achats par pièce avec budget.

Gestion des achats progressifs de meubles/equipements pour la maison.
Classement par pièce, priorite et budget prevu.
"""

from decimal import Decimal

import streamlit as st

from src.core.database import obtenir_contexte_db
from src.core.models import Furniture

# ═══════════════════════════════════════════════════════════
# CONSTANTES
# ═══════════════════════════════════════════════════════════

PIECES_LABELS = {
    "salon": "🛋️ Salon",
    "cuisine": "🍳 Cuisine",
    "chambre_parentale": "🛏️ Chambre parentale",
    "chambre_jules": "🧸 Chambre Jules",
    "bureau": "💻 Bureau",
    "salle_de_bain": "🚿 Salle de bain",
    "garage": "🚗 Garage",
    "entree": "🚪 Entree",
    "exterieur": "🌳 Exterieur",
    "buanderie": "🧺 Buanderie",
    "autre": "📦 Autre",
}

STATUTS_LABELS = {
    "souhaite": "💭 Souhaite",
    "recherche": "🔍 En recherche",
    "trouve": "✨ Trouve",
    "commande": "📦 Commande",
    "achete": "✅ Achete",
    "annule": "❌ Annule",
}

PRIORITES_LABELS = {
    "urgent": "🔴 Urgent",
    "haute": "🟠 Haute",
    "normale": "🟡 Normale",
    "basse": "🟢 Basse",
    "plus_tard": "⚪ Plus tard",
}


# ═══════════════════════════════════════════════════════════
# CRUD FUNCTIONS
# ═══════════════════════════════════════════════════════════


def get_all_meubles(
    filtre_statut: str | None = None, filtre_piece: str | None = None
) -> list[Furniture]:
    """Recupère tous les meubles avec filtres optionnels"""
    with obtenir_contexte_db() as db:
        query = db.query(Furniture)

        if filtre_statut:
            query = query.filter(Furniture.statut == filtre_statut)
        if filtre_piece:
            query = query.filter(Furniture.piece == filtre_piece)

        return query.order_by(Furniture.priorite, Furniture.created_at.desc()).all()


def get_meuble_by_id(meuble_id: int) -> Furniture | None:
    """Recupère un meuble par son ID"""
    with obtenir_contexte_db() as db:
        return db.query(Furniture).filter(Furniture.id == meuble_id).first()


def create_meuble(data: dict) -> Furniture:
    """Cree un nouveau meuble"""
    with obtenir_contexte_db() as db:
        meuble = Furniture(**data)
        db.add(meuble)
        db.commit()
        db.refresh(meuble)
        return meuble


def update_meuble(meuble_id: int, data: dict) -> Furniture | None:
    """Met à jour un meuble"""
    with obtenir_contexte_db() as db:
        meuble = db.query(Furniture).filter(Furniture.id == meuble_id).first()
        if meuble:
            for key, value in data.items():
                setattr(meuble, key, value)
            db.commit()
            db.refresh(meuble)
        return meuble


def delete_meuble(meuble_id: int) -> bool:
    """Supprime un meuble"""
    with obtenir_contexte_db() as db:
        meuble = db.query(Furniture).filter(Furniture.id == meuble_id).first()
        if meuble:
            db.delete(meuble)
            db.commit()
            return True
        return False


def get_budget_resume() -> dict:
    """Calcule le resume du budget"""
    with obtenir_contexte_db() as db:
        meubles = db.query(Furniture).filter(Furniture.statut != "achete").all()

        budget_par_piece = {}
        for meuble in meubles:
            piece = meuble.piece or "autre"
            if piece not in budget_par_piece:
                budget_par_piece[piece] = {"count": 0, "total_estime": 0, "total_max": 0}

            budget_par_piece[piece]["count"] += 1
            budget_par_piece[piece]["total_estime"] += float(meuble.prix_estime or 0)
            budget_par_piece[piece]["total_max"] += float(
                meuble.prix_max or meuble.prix_estime or 0
            )

        total_estime = sum(p["total_estime"] for p in budget_par_piece.values())
        total_max = sum(p["total_max"] for p in budget_par_piece.values())

        return {
            "par_piece": budget_par_piece,
            "total_estime": total_estime,
            "total_max": total_max,
            "nb_articles": len(meubles),
        }


# ═══════════════════════════════════════════════════════════
# FORMULAIRE
# ═══════════════════════════════════════════════════════════


def render_formulaire(meuble: Furniture | None = None):
    """Formulaire d'ajout/edition de meuble"""
    is_edit = meuble is not None
    prefix = "edit" if is_edit else "new"

    with st.form(f"form_meuble_{prefix}"):
        col1, col2 = st.columns(2)

        with col1:
            nom = st.text_input(
                "Nom *",
                value=meuble.nom if is_edit else "",
                placeholder="Ex: Table basse, Étagère...",
            )

            pieces = list(PIECES_LABELS.keys())
            piece_index = pieces.index(meuble.piece) if is_edit and meuble.piece in pieces else 0
            piece = st.selectbox(
                "Pièce",
                options=pieces,
                format_func=lambda x: PIECES_LABELS.get(x, x),
                index=piece_index,
            )

            description = st.text_area(
                "Description",
                value=meuble.description if is_edit else "",
                placeholder="Details, caracteristiques...",
            )

        with col2:
            priorites = list(PRIORITES_LABELS.keys())
            prio_index = (
                priorites.index(meuble.priorite) if is_edit and meuble.priorite in priorites else 2
            )
            priorite = st.selectbox(
                "Priorite",
                options=priorites,
                format_func=lambda x: PRIORITES_LABELS.get(x, x),
                index=prio_index,
            )

            statuts = list(STATUTS_LABELS.keys())
            stat_index = statuts.index(meuble.statut) if is_edit and meuble.statut in statuts else 0
            statut = st.selectbox(
                "Statut",
                options=statuts,
                format_func=lambda x: STATUTS_LABELS.get(x, x),
                index=stat_index,
            )

            col_prix1, col_prix2 = st.columns(2)
            with col_prix1:
                prix_estime = st.number_input(
                    "Prix estime (€)",
                    min_value=0.0,
                    value=float(meuble.prix_estime) if is_edit and meuble.prix_estime else 0.0,
                    step=10.0,
                )
            with col_prix2:
                prix_max = st.number_input(
                    "Prix max (€)",
                    min_value=0.0,
                    value=float(meuble.prix_max) if is_edit and meuble.prix_max else 0.0,
                    step=10.0,
                )

        # Ligne supplementaire
        col3, col4 = st.columns(2)
        with col3:
            magasin = st.text_input(
                "Magasin envisage",
                value=meuble.magasin if is_edit else "",
                placeholder="IKEA, Maisons du Monde, Brocante...",
            )
        with col4:
            url = st.text_input(
                "Lien URL", value=meuble.url if is_edit else "", placeholder="https://..."
            )

        dimensions = st.text_input(
            "Dimensions",
            value=meuble.dimensions if is_edit else "",
            placeholder="L x l x H (ex: 120x60x45 cm)",
        )

        submitted = st.form_submit_button(
            "💾 Enregistrer" if is_edit else "➕ Ajouter", use_container_width=True, type="primary"
        )

        if submitted:
            if not nom:
                st.error("Le nom est obligatoire!")
                return None

            data = {
                "nom": nom,
                "piece": piece,
                "description": description or None,
                "priorite": priorite,
                "statut": statut,
                "prix_estime": Decimal(str(prix_estime)) if prix_estime > 0 else None,
                "prix_max": Decimal(str(prix_max)) if prix_max > 0 else None,
                "magasin": magasin or None,
                "url": url or None,
                "dimensions": dimensions or None,
            }

            if is_edit:
                update_meuble(meuble.id, data)
                st.success("✅ Meuble mis à jour!")
            else:
                create_meuble(data)
                st.success("✅ Meuble ajoute à la wishlist!")

            st.rerun()


# ═══════════════════════════════════════════════════════════
# AFFICHAGE LISTE
# ═══════════════════════════════════════════════════════════


def render_meuble_card(meuble: Furniture):
    """Affiche une card de meuble"""
    with st.container(border=True):
        col1, col2, col3 = st.columns([3, 1, 1])

        with col1:
            # Nom et pièce
            piece_label = PIECES_LABELS.get(meuble.piece, "📦")
            st.markdown(f"**{meuble.nom}**  {piece_label}")

            # Description
            if meuble.description:
                st.caption(
                    meuble.description[:100] + "..."
                    if len(meuble.description) > 100
                    else meuble.description
                )

            # Infos
            infos = []
            if meuble.magasin:
                infos.append(f"🏪 {meuble.magasin}")
            if meuble.dimensions:
                infos.append(f"📐 {meuble.dimensions}")
            if meuble.url:
                infos.append(f"[🔗 Voir]({meuble.url})")

            if infos:
                st.caption(" | ".join(infos))

        with col2:
            # Statut et priorite
            st.markdown(STATUTS_LABELS.get(meuble.statut, meuble.statut))
            st.caption(PRIORITES_LABELS.get(meuble.priorite, meuble.priorite))

        with col3:
            # Prix
            if meuble.prix_estime:
                st.metric("Prix", f"{meuble.prix_estime:.0f}€")

            # Actions
            col_edit, col_del = st.columns(2)
            with col_edit:
                if st.button("✏️", key=f"edit_{meuble.id}", help="Modifier"):
                    st.session_state["edit_meuble_id"] = meuble.id
                    st.rerun()
            with col_del:
                if st.button("🗑️", key=f"del_{meuble.id}", help="Supprimer"):
                    delete_meuble(meuble.id)
                    st.rerun()


def render_budget_summary():
    """Affiche le resume budget"""
    resume = get_budget_resume()

    st.subheader("💰 Resume Budget")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Articles en wishlist", resume["nb_articles"])
    with col2:
        st.metric("Budget estime", f"{resume['total_estime']:.0f}€")
    with col3:
        st.metric("Budget max", f"{resume['total_max']:.0f}€")

    if resume["par_piece"]:
        st.divider()
        st.caption("Par pièce:")

        cols = st.columns(min(3, len(resume["par_piece"])))
        for idx, (piece, data) in enumerate(resume["par_piece"].items()):
            with cols[idx % 3]:
                label = PIECES_LABELS.get(piece, piece)
                st.markdown(f"**{label}**")
                st.caption(f"{data['count']} articles | ~{data['total_estime']:.0f}€")


# ═══════════════════════════════════════════════════════════
# VUE PAR PIÈCE
# ═══════════════════════════════════════════════════════════


def render_vue_par_piece():
    """Affiche les meubles groupes par pièce"""
    meubles = get_all_meubles(filtre_statut=None)

    if not meubles:
        st.info("📋 Aucun meuble dans la wishlist. Ajoutez-en un!")
        return

    # Grouper par pièce
    par_piece = {}
    for meuble in meubles:
        piece = meuble.piece or "autre"
        if piece not in par_piece:
            par_piece[piece] = []
        par_piece[piece].append(meuble)

    # Afficher par pièce
    for piece in PIECES_LABELS.keys():
        if piece in par_piece:
            with st.expander(
                f"{PIECES_LABELS[piece]} ({len(par_piece[piece])} articles)", expanded=True
            ):
                for meuble in par_piece[piece]:
                    render_meuble_card(meuble)


# ═══════════════════════════════════════════════════════════
# ONGLETS
# ═══════════════════════════════════════════════════════════


def render_onglet_wishlist():
    """Onglet liste wishlist avec filtres"""
    # Filtres
    col1, col2 = st.columns(2)
    with col1:
        filtre_statut = st.selectbox(
            "Filtrer par statut",
            options=[""] + list(STATUTS_LABELS.keys()),
            format_func=lambda x: "Tous les statuts" if x == "" else STATUTS_LABELS.get(x, x),
        )
    with col2:
        filtre_piece = st.selectbox(
            "Filtrer par pièce",
            options=[""] + list(PIECES_LABELS.keys()),
            format_func=lambda x: "Toutes les pièces" if x == "" else PIECES_LABELS.get(x, x),
        )

    meubles = get_all_meubles(
        filtre_statut=filtre_statut or None, filtre_piece=filtre_piece or None
    )

    if not meubles:
        st.info("Aucun meuble trouve avec ces filtres.")
        return

    st.caption(f"📋 {len(meubles)} article(s)")

    for meuble in meubles:
        render_meuble_card(meuble)


def render_onglet_ajouter():
    """Onglet ajout nouveau meuble"""
    st.subheader("➕ Ajouter un meuble")
    render_formulaire(None)


def render_onglet_budget():
    """Onglet vue budget"""
    render_budget_summary()
    st.divider()
    render_vue_par_piece()


# ═══════════════════════════════════════════════════════════
# POINT D'ENTRÉE
# ═══════════════════════════════════════════════════════════


def app():
    """Point d'entree module Meubles"""
    st.title("🛋️ Wishlist Meubles")
    st.caption("Gerez vos achats de meubles par pièce et budget")

    # Mode edition
    if "edit_meuble_id" in st.session_state:
        meuble = get_meuble_by_id(st.session_state["edit_meuble_id"])
        if meuble:
            st.subheader(f"✏️ Modifier: {meuble.nom}")
            if st.button("❌ Annuler"):
                del st.session_state["edit_meuble_id"]
                st.rerun()
            render_formulaire(meuble)
            del st.session_state["edit_meuble_id"]
            return

    # Onglets
    tab1, tab2, tab3 = st.tabs(["📋 Wishlist", "➕ Ajouter", "💰 Budget"])

    with tab1:
        render_onglet_wishlist()

    with tab2:
        render_onglet_ajouter()

    with tab3:
        render_onglet_budget()
