"""
UI Components - Layouts
Grilles, cartes, containers
"""

from collections.abc import Callable

import streamlit as st


def disposition_grille(
    items: list[dict],
    colonnes_par_ligne: int = 3,
    rendu_carte: Callable[[dict, str], None] | None = None,
    cle: str = "grid",
):
    """
    Layout en grille

    Args:
        items: Liste d'items
        colonnes_par_ligne: Colonnes par ligne
        rendu_carte: Fonction render carte (item, key)
        cle: Clé unique

    Example:
        disposition_grille(
            recipes,
            colonnes_par_ligne=3,
            rendu_carte=lambda item, k: st.write(item["nom"]),
            cle="recipes_grid"
        )
    """
    if not items:
        st.info("Aucun élément")
        return

    for row_idx in range(0, len(items), colonnes_par_ligne):
        cols = st.columns(colonnes_par_ligne)

        for col_idx in range(colonnes_par_ligne):
            item_idx = row_idx + col_idx

            if item_idx < len(items):
                with cols[col_idx]:
                    if rendu_carte:
                        rendu_carte(items[item_idx], f"{cle}_{item_idx}")
                    else:
                        st.write(items[item_idx])


def carte_item(
    titre: str,
    metadonnees: list[str],
    statut: str | None = None,
    couleur_statut: str | None = None,
    tags: list[str] | None = None,
    url_image: str | None = None,
    actions: list[tuple] | None = None,
    cle: str = "item",
):
    """
    Carte item universelle

    Args:
        titre: Titre
        metadonnees: Liste de métadonnées
        statut: Statut (optionnel)
        couleur_statut: Couleur statut
        tags: Tags (optionnel)
        url_image: URL image
        actions: Liste (label, callback)
        cle: Clé unique

    Example:
        carte_item(
            titre="Tarte aux pommes",
            metadonnees=["45min", "6 portions"],
            statut="facile",
            couleur_statut="#4CAF50",
            tags=["Dessert", "Automne"],
            actions=[("Voir", lambda: view()), ("Éditer", lambda: edit())]
        )
    """
    border_color = couleur_statut or "#e2e8e5"

    with st.container():
        st.markdown(
            f'<div style="border-left: 4px solid {border_color}; padding: 1rem; '
            f'background: #f8f9fa; border-radius: 8px; margin-bottom: 0.5rem;"></div>',
            unsafe_allow_html=True,
        )

        if url_image:
            col_img, col_content = st.columns([1, 4])
            with col_img:
                st.image(url_image, use_container_width=True)
            content_col = col_content
        else:
            content_col = st.container()

        with content_col:
            if statut:
                col_title, col_status = st.columns([3, 1])
                with col_title:
                    st.markdown(f"### {titre}")
                with col_status:
                    st.markdown(
                        f'<div style="text-align: right; color: {couleur_statut or "#6c757d"}; '
                        f'font-weight: 600;">{statut}</div>',
                        unsafe_allow_html=True,
                    )
            else:
                st.markdown(f"### {titre}")

            if metadonnees:
                st.caption(" • ".join(metadonnees))

            if tags:
                tag_html = " ".join(
                    [
                        f'<span style="background: #e7f3ff; padding: 0.25rem 0.5rem; '
                        f'border-radius: 12px; font-size: 0.875rem;">{tag}</span>'
                        for tag in tags
                    ]
                )
                st.markdown(tag_html, unsafe_allow_html=True)

        if actions:
            cols = st.columns(len(actions))
            for idx, (label, callback) in enumerate(actions):
                with cols[idx]:
                    if st.button(label, key=f"{cle}_action_{idx}", use_container_width=True):
                        callback()


def section_pliable(
    titre: str, fonction_contenu: Callable, etendu: bool = False, cle: str = "section"
):
    """
    Section pliable

    Args:
        titre: Titre
        fonction_contenu: Fonction qui render le contenu
        etendu: Ouvert par défaut
        cle: Clé unique

    Example:
        section_pliable(
            "Détails avancés",
            lambda: st.write("Contenu détaillé"),
            etendu=False,
            cle="advanced"
        )
    """
    with st.expander(titre, expanded=etendu):
        fonction_contenu()


def disposition_onglets(onglets: dict[str, Callable], cle: str = "tabs"):
    """
    Layout tabs

    Args:
        onglets: Dict {label: content_fn}
        cle: Clé unique

    Example:
        disposition_onglets({
            "Vue 1": lambda: st.write("Contenu 1"),
            "Vue 2": lambda: st.write("Contenu 2")
        }, "views")
    """
    tab_objects = st.tabs(list(onglets.keys()))

    for idx, (label, content_fn) in enumerate(onglets.items()):
        with tab_objects[idx]:
            content_fn()


def conteneur_carte(fonction_contenu: Callable, couleur: str = "#ffffff"):
    """
    Container carte stylé

    Args:
        fonction_contenu: Fonction render contenu
        couleur: Couleur fond

    Example:
        conteneur_carte(
            lambda: st.write("Contenu"),
            couleur="#f0f0f0"
        )
    """
    st.markdown(
        f'<div style="background: {couleur}; padding: 1.5rem; '
        f'border-radius: 12px; box-shadow: 0 2px 4px rgba(0,0,0,0.04);">',
        unsafe_allow_html=True,
    )
    fonction_contenu()
    st.markdown("</div>", unsafe_allow_html=True)

