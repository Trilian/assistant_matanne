"""Vue 3D des pièces — Plotly Mesh3d extrusion."""

from __future__ import annotations

import plotly.graph_objects as go
import streamlit as st

from .constants import COULEURS_TYPE_PIECE, EMOJIS_PIECES, ETAGE_LABELS, HAUTEUR_3D_PIECE


def _creer_boite_3d(
    x0: float,
    y0: float,
    z0: float,
    dx: float,
    dy: float,
    dz: float,
    color: str,
    nom: str,
    hover_text: str,
) -> go.Mesh3d:
    """Crée un Mesh3d en forme de boîte (8 vertices, 12 triangles).

    Args:
        x0, y0, z0: Coin inférieur.
        dx, dy, dz: Dimensions.
        color: Couleur hex.
        nom: Nom affiché en légende.
        hover_text: Texte au survol.
    """
    x = [x0, x0 + dx, x0 + dx, x0, x0, x0 + dx, x0 + dx, x0]
    y = [y0, y0, y0 + dy, y0 + dy, y0, y0, y0 + dy, y0 + dy]
    z = [z0, z0, z0, z0, z0 + dz, z0 + dz, z0 + dz, z0 + dz]

    # 12 triangles (2 par face, 6 faces)
    i = [0, 0, 4, 4, 0, 0, 1, 1, 0, 0, 3, 3]
    j = [1, 2, 5, 6, 1, 4, 2, 5, 3, 4, 2, 6]
    k = [2, 3, 6, 7, 4, 5, 5, 6, 4, 7, 6, 7]

    return go.Mesh3d(
        x=x,
        y=y,
        z=z,
        i=i,
        j=j,
        k=k,
        color=color,
        opacity=0.7,
        name=nom,
        hovertext=hover_text,
        hoverinfo="text",
        flatshading=True,
    )


def afficher_vue_3d(pieces: list[dict]):
    """Affiche la vue 3D extrudée de toutes les pièces.

    Les pièces sont empilées par étage (z_offset = étage * 3.5).
    """
    if not pieces:
        st.info("🏠 Aucune pièce à afficher en 3D.")
        return

    fig = go.Figure()

    # Facteur d'échelle pixel → unités 3D (100px ≈ 1 unité)
    scale = 0.01

    for p in pieces:
        type_p = p.get("type_piece", "autre")
        color = COULEURS_TYPE_PIECE.get(type_p, "#BDBDBD")
        emoji = EMOJIS_PIECES.get(type_p, "🏠")
        hauteur = HAUTEUR_3D_PIECE.get(type_p, 2.5)

        # Position
        x0 = p["position_x"] * scale
        y0 = p["position_y"] * scale
        z0 = p["etage"] * 3.5  # Espacement entre étages
        dx = p["largeur_px"] * scale
        dy = p["hauteur_px"] * scale

        etage_str = ETAGE_LABELS.get(p["etage"], f"Ét.{p['etage']}")
        hover = (
            f"<b>{emoji} {p['nom']}</b><br>"
            f"Étage: {etage_str}<br>"
            f"Surface: {p['superficie_m2']}m²<br>"
            f"Objets: {p['nb_objets']} · Travaux: {p['nb_travaux']}<br>"
            f"Budget travaux: {p['cout_total_travaux']:.0f}€"
        )

        boite = _creer_boite_3d(x0, y0, z0, dx, dy, hauteur, color, p["nom"], hover)
        fig.add_trace(boite)

    # Ajouter un sol par étage
    etages_presents = sorted(set(p["etage"] for p in pieces))
    for etage in etages_presents:
        pieces_etage = [p for p in pieces if p["etage"] == etage]
        max_x = max(p["position_x"] + p["largeur_px"] for p in pieces_etage) * scale + 0.5
        max_y = max(p["position_y"] + p["hauteur_px"] for p in pieces_etage) * scale + 0.5
        z_sol = etage * 3.5 - 0.05

        fig.add_trace(
            go.Mesh3d(
                x=[0, max_x, max_x, 0],
                y=[0, 0, max_y, max_y],
                z=[z_sol, z_sol, z_sol, z_sol],
                i=[0, 0],
                j=[1, 2],
                k=[2, 3],
                color="#E0E0E0",
                opacity=0.4,
                name=f"Sol {ETAGE_LABELS.get(etage, f'Ét.{etage}')}",
                hoverinfo="name",
                flatshading=True,
            )
        )

    fig.update_layout(
        scene=dict(
            xaxis=dict(
                title="",
                showticklabels=False,
                showgrid=False,
                zeroline=False,
            ),
            yaxis=dict(
                title="",
                showticklabels=False,
                showgrid=False,
                zeroline=False,
            ),
            zaxis=dict(title="Étage", showticklabels=True, showgrid=True),
            camera=dict(
                eye=dict(x=1.5, y=-1.8, z=1.2),
                center=dict(x=0, y=0, z=0.2),
            ),
            aspectmode="data",
        ),
        height=600,
        margin=dict(l=0, r=0, t=30, b=0),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
            font=dict(size=10),
        ),
    )

    st.plotly_chart(fig, use_container_width=True, key="plan_3d_chart")

    # Aide
    st.caption(
        "🖱️ Clic + glisser pour tourner · " "Molette pour zoomer · " "Shift+clic pour déplacer"
    )
