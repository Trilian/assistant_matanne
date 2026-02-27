"""Jardin — Onglet Plan 2D/3D interactif.

Remplace l'ancien onglet_plan() statique par une vue Plotly interactive
des zones du jardin avec plan 2D et vue 3D.
"""

from __future__ import annotations

import logging

import plotly.graph_objects as go
import streamlit as st

from src.ui.fragments import ui_fragment

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# CONSTANTES JARDIN
# ═══════════════════════════════════════════════════════════

COULEURS_ZONES = {
    "potager": {"fill": "rgba(76,175,80,0.4)", "border": "#4CAF50", "hex": "#4CAF50"},
    "pelouse": {"fill": "rgba(139,195,74,0.3)", "border": "#8BC34A", "hex": "#8BC34A"},
    "arbres": {"fill": "rgba(46,125,50,0.4)", "border": "#2E7D32", "hex": "#2E7D32"},
    "fleurs": {"fill": "rgba(233,30,99,0.3)", "border": "#E91E63", "hex": "#E91E63"},
    "aromatiques": {"fill": "rgba(156,39,176,0.3)", "border": "#9C27B0", "hex": "#9C27B0"},
    "verger": {"fill": "rgba(255,152,0,0.3)", "border": "#FF9800", "hex": "#FF9800"},
    "compost": {"fill": "rgba(121,85,72,0.4)", "border": "#795548", "hex": "#795548"},
    "serre": {"fill": "rgba(0,188,212,0.3)", "border": "#00BCD4", "hex": "#00BCD4"},
    "autre": {"fill": "rgba(158,158,158,0.3)", "border": "#9E9E9E", "hex": "#9E9E9E"},
}

EMOJI_ZONES = {
    "potager": "🥬",
    "pelouse": "🌿",
    "arbres": "🌳",
    "fleurs": "🌸",
    "aromatiques": "🌿",
    "verger": "🍎",
    "compost": "♻️",
    "serre": "🏠",
    "autre": "📍",
}

HAUTEUR_3D_ZONE = {
    "potager": 0.5,
    "pelouse": 0.15,
    "arbres": 3.0,
    "fleurs": 0.4,
    "aromatiques": 0.3,
    "verger": 2.5,
    "compost": 0.8,
    "serre": 2.0,
    "autre": 0.5,
}


def _get_service():
    """Retourne le service jardin."""
    from src.services.maison import get_jardin_service

    return get_jardin_service()


@ui_fragment
def onglet_plan_interactif():
    """Onglet plan du jardin — Vue 2D Plotly + Vue 3D."""
    st.subheader("🗺️ Plan du Jardin")

    service = _get_service()
    zones = service.charger_zones()

    if not zones:
        st.info(
            "🌱 Aucune zone de jardin enregistrée.\n\n"
            "Allez dans **Zones Jardin** pour créer vos premières zones, "
            "puis revenez ici pour les visualiser sur le plan."
        )
        return

    # Sélection vue
    vue_sel = st.radio(
        "Vue",
        ["🗺️ Plan 2D", "🏔️ Vue 3D"],
        horizontal=True,
        key="jardin_plan_vue",
        label_visibility="collapsed",
    )

    if vue_sel == "🗺️ Plan 2D":
        _afficher_plan_2d_jardin(zones)
    else:
        _afficher_vue_3d_jardin(zones)


# ═══════════════════════════════════════════════════════════
# PLAN 2D
# ═══════════════════════════════════════════════════════════


def _afficher_plan_2d_jardin(zones: list[dict]):
    """Plan 2D du jardin avec Plotly shapes."""
    fig = go.Figure()

    shapes = []
    annotations = []

    # S'assurer que toutes les zones ont des positions
    zones_pos = _assurer_positions(zones)

    for z in zones_pos:
        type_z = z.get("type_zone", "autre")
        style = COULEURS_ZONES.get(type_z, COULEURS_ZONES["autre"])
        emoji = EMOJI_ZONES.get(type_z, "📍")

        x0 = z["position_x"]
        y0 = z["position_y"]
        x1 = x0 + z["largeur_px"]
        y1 = y0 + z["hauteur_px"]

        note = z.get("etat_note", 3)
        border_width = 2 if note >= 3 else 3

        shapes.append(
            dict(
                type="rect",
                x0=x0,
                y0=y0,
                x1=x1,
                y1=y1,
                fillcolor=style["fill"],
                line=dict(color=style["border"], width=border_width),
                layer="below",
            )
        )

        # Étoiles d'état colorées
        etat_colors = {1: "#F44336", 2: "#FF9800", 3: "#FFC107", 4: "#8BC34A", 5: "#4CAF50"}
        etat_color = etat_colors.get(note, "#FFC107")

        cx = (x0 + x1) / 2
        cy = (y0 + y1) / 2

        stars = "⭐" * note
        sub_label = f"{z.get('surface_m2', 0):.0f}m²"

        annotations.append(
            dict(
                x=cx,
                y=cy,
                text=(
                    f"<b>{emoji} {z['nom']}</b><br>"
                    f"<span style='color:{etat_color}'>{stars}</span><br>"
                    f"{sub_label}"
                ),
                showarrow=False,
                font=dict(size=11),
                align="center",
            )
        )

    # Scatter pour hover + sélection
    fig.add_trace(
        go.Scatter(
            x=[(z["position_x"] + z["largeur_px"] / 2) for z in zones_pos],
            y=[(z["position_y"] + z["hauteur_px"] / 2) for z in zones_pos],
            mode="markers",
            marker=dict(size=20, opacity=0),
            hovertext=[
                f"<b>{EMOJI_ZONES.get(z.get('type_zone', 'autre'), '📍')} {z['nom']}</b><br>"
                f"Type: {z.get('type_zone', '?')} · {z.get('surface_m2', 0):.0f}m²<br>"
                f"État: {'⭐' * z.get('etat_note', 3)} ({z.get('etat_note', 3)}/5)<br>"
                f"{z.get('etat_description', '') or 'Pas de description'}"
                for z in zones_pos
            ],
            hoverinfo="text",
            name="Zones",
        )
    )

    x_max = max((z["position_x"] + z["largeur_px"]) for z in zones_pos) + 30
    y_max = max((z["position_y"] + z["hauteur_px"]) for z in zones_pos) + 30

    fig.update_layout(
        shapes=shapes,
        annotations=annotations,
        xaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor="rgba(0,0,0,0.05)",
            zeroline=False,
            showticklabels=False,
            range=[-10, x_max],
        ),
        yaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor="rgba(0,0,0,0.05)",
            zeroline=False,
            showticklabels=False,
            range=[y_max, -10],
            scaleanchor="x",
            scaleratio=1,
        ),
        height=450,
        margin=dict(l=10, r=10, t=10, b=10),
        plot_bgcolor="#f0f4e8",  # Vert clair
        showlegend=False,
        dragmode="pan",
    )

    st.plotly_chart(fig, use_container_width=True, key="jardin_plan_2d")

    # Légende
    with st.expander("🎨 Légende types de zones", expanded=False):
        cols = st.columns(4)
        for i, (type_z, style) in enumerate(COULEURS_ZONES.items()):
            if type_z == "autre":
                continue
            with cols[i % 4]:
                emoji = EMOJI_ZONES.get(type_z, "📍")
                st.markdown(
                    f'<div style="background:{style["fill"]};border:2px solid {style["border"]};'
                    f'padding:3px 6px;border-radius:4px;text-align:center;font-size:0.8em;margin:2px 0">'
                    f"{emoji} {type_z.capitalize()}</div>",
                    unsafe_allow_html=True,
                )


# ═══════════════════════════════════════════════════════════
# VUE 3D
# ═══════════════════════════════════════════════════════════


def _afficher_vue_3d_jardin(zones: list[dict]):
    """Vue 3D extrudée du jardin."""
    zones_pos = _assurer_positions(zones)

    fig = go.Figure()
    scale = 0.01

    for z in zones_pos:
        type_z = z.get("type_zone", "autre")
        style = COULEURS_ZONES.get(type_z, COULEURS_ZONES["autre"])
        emoji = EMOJI_ZONES.get(type_z, "📍")
        hauteur = HAUTEUR_3D_ZONE.get(type_z, 0.5)

        x0 = z["position_x"] * scale
        y0 = z["position_y"] * scale
        dx = z["largeur_px"] * scale
        dy = z["hauteur_px"] * scale

        hover = (
            f"<b>{emoji} {z['nom']}</b><br>"
            f"Type: {type_z} · {z.get('surface_m2', 0):.0f}m²<br>"
            f"État: {'⭐' * z.get('etat_note', 3)}"
        )

        # 8 vertices de la boîte
        x = [x0, x0 + dx, x0 + dx, x0, x0, x0 + dx, x0 + dx, x0]
        y = [y0, y0, y0 + dy, y0 + dy, y0, y0, y0 + dy, y0 + dy]
        zz = [0, 0, 0, 0, hauteur, hauteur, hauteur, hauteur]
        i = [0, 0, 4, 4, 0, 0, 1, 1, 0, 0, 3, 3]
        j = [1, 2, 5, 6, 1, 4, 2, 5, 3, 4, 2, 6]
        k = [2, 3, 6, 7, 4, 5, 5, 6, 4, 7, 6, 7]

        fig.add_trace(
            go.Mesh3d(
                x=x,
                y=y,
                z=zz,
                i=i,
                j=j,
                k=k,
                color=style["hex"],
                opacity=0.7,
                name=z["nom"],
                hovertext=hover,
                hoverinfo="text",
                flatshading=True,
            )
        )

    # Sol
    x_max = max((z["position_x"] + z["largeur_px"]) for z in zones_pos) * scale + 0.5
    y_max = max((z["position_y"] + z["hauteur_px"]) for z in zones_pos) * scale + 0.5

    fig.add_trace(
        go.Mesh3d(
            x=[0, x_max, x_max, 0],
            y=[0, 0, y_max, y_max],
            z=[-0.02, -0.02, -0.02, -0.02],
            i=[0, 0],
            j=[1, 2],
            k=[2, 3],
            color="#8D6E63",
            opacity=0.3,
            name="Sol",
            hoverinfo="name",
            flatshading=True,
        )
    )

    fig.update_layout(
        scene=dict(
            xaxis=dict(title="", showticklabels=False, showgrid=False, zeroline=False),
            yaxis=dict(title="", showticklabels=False, showgrid=False, zeroline=False),
            zaxis=dict(title="Hauteur (m)", showgrid=True),
            camera=dict(eye=dict(x=1.2, y=-1.5, z=1.0)),
            aspectmode="data",
        ),
        height=500,
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

    st.plotly_chart(fig, use_container_width=True, key="jardin_plan_3d")
    st.caption("🖱️ Clic + glisser pour tourner · Molette pour zoomer")


# ═══════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════


def _assurer_positions(zones: list[dict]) -> list[dict]:
    """Ajoute des positions automatiques si les zones n'en ont pas."""
    result = []
    col = 0
    row = 0
    max_cols = 4  # 4 zones par ligne

    for z in zones:
        pos_x = z.get("position_x", 0) or 0
        pos_y = z.get("position_y", 0) or 0
        larg = z.get("largeur_px", 0) or 0
        haut = z.get("hauteur_px", 0) or 0

        # Si pas de position assignée, disposition en grille auto
        if pos_x == 0 and pos_y == 0 and larg == 0:
            surface = z.get("surface_m2", 0) or 10
            # Taille proportionnelle à la surface
            side = max(60, min(200, int(surface**0.5 * 40)))
            pos_x = 20 + col * 210
            pos_y = 20 + row * 180
            larg = side
            haut = side

            col += 1
            if col >= max_cols:
                col = 0
                row += 1

        result.append(
            {
                **z,
                "position_x": pos_x,
                "position_y": pos_y,
                "largeur_px": larg if larg > 0 else 100,
                "hauteur_px": haut if haut > 0 else 100,
            }
        )

    return result
