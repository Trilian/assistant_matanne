"""Plan 2D interactif des pièces — Plotly shapes + scatter."""

from __future__ import annotations

import plotly.graph_objects as go
import streamlit as st

from .constants import COULEURS_ETATS, EMOJIS_PIECES


def afficher_plan_2d(
    pieces: list[dict],
    service,
    key_prefix: str = "plan_2d",
) -> int | None:
    """Affiche le plan 2D des pièces avec Plotly.

    Args:
        pieces: Liste de pièces enrichies depuis le service.
        service: VisualisationService pour sauvegarder les positions.
        key_prefix: Préfixe pour les clés session_state.

    Returns:
        ID de la pièce sélectionnée (clic), ou None.
    """
    if not pieces:
        st.info(
            "🏠 Aucune pièce à afficher. " "Les pièces par défaut seront créées au rechargement."
        )
        return None

    # Mode édition
    mode_edit = st.toggle("✏️ Mode édition", value=False, key=f"{key_prefix}_edit")

    # Construire la figure
    fig = go.Figure()

    shapes = []
    annotations = []

    for p in pieces:
        etat_style = COULEURS_ETATS.get(p["etat"], COULEURS_ETATS["ok"])
        emoji = EMOJIS_PIECES.get(p["type_piece"], "🏠")

        x0 = p["position_x"]
        y0 = p["position_y"]
        x1 = x0 + p["largeur_px"]
        y1 = y0 + p["hauteur_px"]

        shapes.append(
            dict(
                type="rect",
                x0=x0,
                y0=y0,
                x1=x1,
                y1=y1,
                fillcolor=etat_style["fill"],
                line=dict(color=etat_style["border"], width=2),
                layer="below",
            )
        )

        # Label au centre
        cx = (x0 + x1) / 2
        cy = (y0 + y1) / 2
        label_lines = [
            f"{emoji} {p['nom']}",
            f"{p['superficie_m2']}m²" if p["superficie_m2"] else "",
        ]
        if p["nb_travaux"] > 0:
            label_lines.append(f"🔨{p['nb_travaux']}")
        if p["taches_retard"] > 0:
            label_lines.append(f"⚠️{p['taches_retard']}")

        annotations.append(
            dict(
                x=cx,
                y=cy,
                text="<br>".join(line for line in label_lines if line),
                showarrow=False,
                font=dict(size=11, color="#333"),
                align="center",
            )
        )

    # Scatter invisible pour la sélection (un point par pièce)
    min_w = min(p["largeur_px"] for p in pieces) if pieces else 100
    fig.add_trace(
        go.Scatter(
            x=[(p["position_x"] + p["largeur_px"] / 2) for p in pieces],
            y=[(p["position_y"] + p["hauteur_px"] / 2) for p in pieces],
            mode="markers",
            marker=dict(size=max(20, min_w // 3), opacity=0),
            customdata=[p["id"] for p in pieces],
            hovertext=[
                f"<b>{EMOJIS_PIECES.get(p['type_piece'], '🏠')} {p['nom']}</b><br>"
                f"📐 {p['superficie_m2']}m² · 📦 {p['nb_objets']} objets<br>"
                f"🔨 {p['nb_travaux']} travaux · 💰 {p['cout_total_travaux']:.0f}€<br>"
                f"État: {COULEURS_ETATS.get(p['etat'], {}).get('label', p['etat'])}"
                for p in pieces
            ],
            hoverinfo="text",
            name="Pièces",
        )
    )

    max_x = max(p["position_x"] + p["largeur_px"] for p in pieces)
    max_y = max(p["position_y"] + p["hauteur_px"] for p in pieces)

    fig.update_layout(
        shapes=shapes,
        annotations=annotations,
        xaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor="rgba(0,0,0,0.05)",
            zeroline=False,
            showticklabels=False,
            range=[-10, max_x + 30],
        ),
        yaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor="rgba(0,0,0,0.05)",
            zeroline=False,
            showticklabels=False,
            range=[max_y + 30, -10],
            scaleanchor="x",
            scaleratio=1,
        ),
        height=500,
        margin=dict(l=10, r=10, t=10, b=10),
        plot_bgcolor="white",
        showlegend=False,
        dragmode="pan",
    )

    # Légende manuelle
    with st.expander("🎨 Légende", expanded=False):
        legend_cols = st.columns(len(COULEURS_ETATS))
        for i, (_key, style) in enumerate(COULEURS_ETATS.items()):
            with legend_cols[i]:
                st.markdown(
                    f'<div style="background:{style["fill"]};border:2px solid {style["border"]};'
                    f'padding:4px 8px;border-radius:6px;text-align:center;font-size:0.85em">'
                    f'{style["label"]}</div>',
                    unsafe_allow_html=True,
                )

    # Afficher le plan
    event = st.plotly_chart(
        fig,
        use_container_width=True,
        key=f"{key_prefix}_chart",
        on_select="rerun",
        config={"scrollZoom": True, "displayModeBar": True},
    )

    # Gérer la sélection
    piece_sel_id = None
    if event and hasattr(event, "selection") and event.selection:
        points = event.selection.get("points", [])
        if points:
            idx = points[0].get("point_index")
            if idx is not None and idx < len(pieces):
                piece_sel_id = pieces[idx]["id"]
                st.info(
                    f"🏠 Pièce sélectionnée : **{pieces[idx]['nom']}** " "— voir onglet Détails"
                )

    # Mode édition : formulaire de position
    if mode_edit:
        _afficher_editeur_positions(pieces, service, key_prefix)

    return piece_sel_id


def _afficher_editeur_positions(pieces: list[dict], service, key_prefix: str):
    """Formulaire d'édition des positions des pièces."""
    st.markdown("### ✏️ Éditer les positions")

    piece_edit = st.selectbox(
        "Pièce à déplacer",
        options=range(len(pieces)),
        format_func=lambda i: (
            f"{EMOJIS_PIECES.get(pieces[i]['type_piece'], '🏠')} {pieces[i]['nom']}"
        ),
        key=f"{key_prefix}_edit_sel",
    )

    if piece_edit is not None:
        p = pieces[piece_edit]
        col1, col2 = st.columns(2)
        with col1:
            new_x = st.number_input(
                "Position X",
                value=p["position_x"],
                min_value=0,
                max_value=800,
                key=f"{key_prefix}_x",
            )
            new_w = st.number_input(
                "Largeur",
                value=p["largeur_px"],
                min_value=30,
                max_value=400,
                key=f"{key_prefix}_w",
            )
        with col2:
            new_y = st.number_input(
                "Position Y",
                value=p["position_y"],
                min_value=0,
                max_value=600,
                key=f"{key_prefix}_y",
            )
            new_h = st.number_input(
                "Hauteur",
                value=p["hauteur_px"],
                min_value=30,
                max_value=400,
                key=f"{key_prefix}_h",
            )

        if st.button(
            "💾 Sauvegarder la position",
            type="primary",
            key=f"{key_prefix}_save",
        ):
            service.sauvegarder_positions(
                [
                    {
                        "id": p["id"],
                        "position_x": new_x,
                        "position_y": new_y,
                        "largeur_px": new_w,
                        "hauteur_px": new_h,
                    }
                ]
            )
            st.success(f"✅ Position de {p['nom']} mise à jour !")
            st.rerun()
