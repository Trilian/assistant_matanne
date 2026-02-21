"""
UI Components - Layouts
Grilles et cartes
"""

from collections.abc import Callable

import streamlit as st

from src.ui.engine import StyleSheet
from src.ui.registry import composant_ui
from src.ui.tokens import Couleur, Espacement, Rayon
from src.ui.utils import echapper_html


@composant_ui("layouts", exemple="disposition_grille(items, 3)", tags=["grid", "layout"])
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


@composant_ui("layouts", exemple='carte_item("Titre", ["meta1", "meta2"])', tags=["card", "item"])
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
    border_color = couleur_statut or Couleur.BORDER

    with st.container(border=True):
        if url_image:
            col_img, col_content = st.columns([1, 4])
            with col_img:
                st.image(url_image, width="stretch")
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
                        f'<div style="text-align: right; color: {couleur_statut or Couleur.TEXT_SECONDARY}; '
                        f'font-weight: 600;">{echapper_html(statut)}</div>',
                        unsafe_allow_html=True,
                    )
            else:
                st.markdown(f"### {titre}")

            if metadonnees:
                st.caption(" • ".join(metadonnees))

            if tags:
                tag_cls = StyleSheet.create_class(
                    {
                        "background": Couleur.BG_INFO,
                        "padding": f"{Espacement.XS} {Espacement.SM}",
                        "border-radius": Rayon.PILL,
                        "font-size": "0.875rem",
                    }
                )
                tag_html = " ".join(
                    f'<span class="{tag_cls}">{echapper_html(tag)}</span>' for tag in tags
                )
                StyleSheet.inject()
                st.markdown(tag_html, unsafe_allow_html=True)

        if actions:
            cols = st.columns(len(actions))
            for idx, (label, callback) in enumerate(actions):
                with cols[idx]:
                    if st.button(label, key=f"{cle}_action_{idx}", use_container_width=True):
                        callback()
