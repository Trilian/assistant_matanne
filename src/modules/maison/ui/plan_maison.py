"""
Plan Maison Interactif - Visualisation 2D de la maison.

Features:
- Plan des étages avec pièces cliquables
- Visualisation des objets par pièce
- Statut des objets (OK, à changer, à acheter)
- Timeline des versions et travaux
- Mode édition pour réorganiser
"""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Any, Callable

import streamlit as st

# ═══════════════════════════════════════════════════════════
# STYLES CSS
# ═══════════════════════════════════════════════════════════

PLAN_MAISON_CSS = """
<style>
/* Container principal du plan */
.plan-maison-container {
    background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
    border-radius: 16px;
    padding: 20px;
    margin: 10px 0;
    box-shadow: 0 4px 20px rgba(0,0,0,0.08);
}

/* Grille d'étage */
.etage-grid {
    display: grid;
    gap: 12px;
    padding: 15px;
    background: white;
    border-radius: 12px;
    box-shadow: inset 0 2px 8px rgba(0,0,0,0.04);
}

/* Pièce dans le plan */
.piece-card {
    background: linear-gradient(145deg, #ffffff 0%, #f0f4f8 100%);
    border: 2px solid #e2e8f0;
    border-radius: 12px;
    padding: 16px;
    cursor: pointer;
    transition: all 0.3s ease;
    position: relative;
    min-height: 120px;
}

.piece-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 25px rgba(0,0,0,0.12);
    border-color: #667eea;
}

.piece-card.selected {
    border-color: #667eea;
    background: linear-gradient(145deg, #f0f4ff 0%, #e8ecff 100%);
    box-shadow: 0 0 0 3px rgba(102,126,234,0.2);
}

/* Nom de la pièce */
.piece-nom {
    font-size: 1.1rem;
    font-weight: 700;
    color: #2d3748;
    margin-bottom: 8px;
    display: flex;
    align-items: center;
    gap: 8px;
}

/* Stats de la pièce */
.piece-stats {
    display: flex;
    gap: 12px;
    font-size: 0.85rem;
    color: #718096;
}

.piece-stat {
    display: flex;
    align-items: center;
    gap: 4px;
}

/* Badge compteur */
.badge-count {
    background: #667eea;
    color: white;
    font-size: 0.75rem;
    padding: 2px 8px;
    border-radius: 10px;
    font-weight: 600;
}

.badge-warning {
    background: #f59e0b;
}

.badge-danger {
    background: #ef4444;
}

/* Carte objet */
.objet-card {
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 12px;
    margin: 8px 0;
    display: flex;
    justify-content: space-between;
    align-items: center;
    transition: all 0.2s ease;
}

.objet-card:hover {
    background: #f8fafc;
    border-color: #cbd5e0;
}

.objet-card.a-changer {
    border-left: 4px solid #f59e0b;
    background: #fffbeb;
}

.objet-card.a-acheter {
    border-left: 4px solid #3b82f6;
    background: #eff6ff;
}

.objet-card.hors-service {
    border-left: 4px solid #ef4444;
    background: #fef2f2;
}

/* Info objet */
.objet-info {
    display: flex;
    flex-direction: column;
    gap: 4px;
}

.objet-nom {
    font-weight: 600;
    color: #2d3748;
}

.objet-detail {
    font-size: 0.85rem;
    color: #718096;
}

/* Prix */
.objet-prix {
    font-weight: 700;
    color: #059669;
}

/* Timeline travaux */
.timeline-container {
    position: relative;
    padding-left: 30px;
}

.timeline-item {
    position: relative;
    padding: 15px 0;
    border-left: 2px solid #e2e8f0;
    padding-left: 25px;
    margin-left: -1px;
}

.timeline-item::before {
    content: '';
    position: absolute;
    left: -8px;
    top: 20px;
    width: 14px;
    height: 14px;
    border-radius: 50%;
    background: #667eea;
    border: 3px solid white;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.timeline-item.completed::before {
    background: #10b981;
}

.timeline-item.pending::before {
    background: #f59e0b;
}

/* Légende */
.legende {
    display: flex;
    gap: 20px;
    padding: 12px 16px;
    background: white;
    border-radius: 10px;
    margin-top: 15px;
    flex-wrap: wrap;
}

.legende-item {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 0.85rem;
    color: #4a5568;
}

.legende-dot {
    width: 12px;
    height: 12px;
    border-radius: 50%;
}
</style>
"""


# ═══════════════════════════════════════════════════════════
# DATA CLASSES
# ═══════════════════════════════════════════════════════════


@dataclass
class PieceData:
    """Données d'une pièce."""

    id: int
    nom: str
    etage: str
    icone: str
    superficie_m2: float | None = None
    nb_objets: int = 0
    nb_a_changer: int = 0
    nb_a_acheter: int = 0
    valeur_totale: Decimal = Decimal("0")
    position_grid: tuple[int, int] = (0, 0)  # row, col
    largeur_grid: int = 1
    hauteur_grid: int = 1


@dataclass
class ObjetData:
    """Données d'un objet."""

    id: int
    nom: str
    categorie: str
    statut: str  # fonctionne, a_changer, a_acheter, hors_service
    marque: str | None = None
    prix_achat: Decimal | None = None
    cout_remplacement: Decimal | None = None
    date_achat: date | None = None
    priorite: str | None = None  # urgente, haute, normale, basse


# ═══════════════════════════════════════════════════════════
# CONSTANTES ICÔNES
# ═══════════════════════════════════════════════════════════

ICONES_PIECES = {
    "cuisine": "🍳",
    "salon": "🛋️",
    "chambre": "🛏️",
    "sdb": "🚿",
    "wc": "🚽",
    "bureau": "💻",
    "garage": "🚗",
    "buanderie": "🧺",
    "entree": "🚪",
    "cave": "🍷",
    "grenier": "📦",
    "terrasse": "☀️",
    "default": "🏠",
}

ICONES_CATEGORIES = {
    "electromenager": "🔌",
    "meuble": "🪑",
    "electronique": "📱",
    "decoration": "🖼️",
    "outil": "🔧",
    "linge": "🛏️",
    "vaisselle": "🍽️",
    "default": "📦",
}

COULEURS_STATUT = {
    "fonctionne": "#10b981",
    "a_changer": "#f59e0b",
    "a_acheter": "#3b82f6",
    "hors_service": "#ef4444",
    "en_commande": "#8b5cf6",
}


# ═══════════════════════════════════════════════════════════
# CLASSE PRINCIPALE
# ═══════════════════════════════════════════════════════════


class PlanMaisonInteractif:
    """Plan interactif de la maison avec pièces et objets."""

    def __init__(
        self,
        pieces: list[PieceData],
        objets_par_piece: dict[int, list[ObjetData]] | None = None,
        on_piece_click: Callable[[PieceData], None] | None = None,
        on_objet_click: Callable[[ObjetData], None] | None = None,
    ):
        """
        Initialise le plan interactif.

        Args:
            pieces: Liste des pièces de la maison
            objets_par_piece: Dictionnaire piece_id -> liste d'objets
            on_piece_click: Callback quand une pièce est cliquée
            on_objet_click: Callback quand un objet est cliqué
        """
        self.pieces = pieces
        self.objets_par_piece = objets_par_piece or {}
        self.on_piece_click = on_piece_click
        self.on_objet_click = on_objet_click

        # Grouper les pièces par étage
        self.etages = self._grouper_par_etage()

    def _grouper_par_etage(self) -> dict[str, list[PieceData]]:
        """Groupe les pièces par étage."""
        etages: dict[str, list[PieceData]] = {}
        for piece in self.pieces:
            if piece.etage not in etages:
                etages[piece.etage] = []
            etages[piece.etage].append(piece)
        return etages

    def render(self, key: str = "plan_maison"):
        """Affiche le plan interactif complet."""
        # Injecter CSS
        st.markdown(PLAN_MAISON_CSS, unsafe_allow_html=True)

        # Container principal
        st.markdown('<div class="plan-maison-container">', unsafe_allow_html=True)

        # Header avec stats globales
        self._render_header()

        # Sélecteur d'étage si plusieurs
        etage_actif = self._render_etage_selector(key)

        # Plan de l'étage sélectionné
        if etage_actif and etage_activ in self.etages:
            self._render_etage(etage_actif, key)

        # Légende
        self._render_legende()

        st.markdown("</div>", unsafe_allow_html=True)

    def _render_header(self):
        """Affiche le header avec statistiques globales."""
        total_pieces = len(self.pieces)
        total_objets = sum(p.nb_objets for p in self.pieces)
        total_a_changer = sum(p.nb_a_changer for p in self.pieces)
        total_a_acheter = sum(p.nb_a_acheter for p in self.pieces)
        valeur_totale = sum(p.valeur_totale for p in self.pieces)

        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            st.metric("🏠 Pièces", total_pieces)
        with col2:
            st.metric("📦 Objets", total_objets)
        with col3:
            st.metric("🔄 À changer", total_a_changer)
        with col4:
            st.metric("🛒 À acheter", total_a_acheter)
        with col5:
            st.metric("💰 Valeur", f"{valeur_totale:,.0f}€")

    def _render_etage_selector(self, key: str) -> str:
        """Affiche le sélecteur d'étage."""
        if len(self.etages) <= 1:
            return list(self.etages.keys())[0] if self.etages else "RDC"

        etages_options = list(self.etages.keys())
        ordre_etages = ["Sous-sol", "RDC", "1er", "2e", "Grenier"]
        etages_tries = sorted(
            etages_options,
            key=lambda e: ordre_etages.index(e) if e in ordre_etages else 99,
        )

        return st.selectbox(
            "🏢 Étage",
            etages_tries,
            key=f"{key}_etage",
            index=etages_tries.index("RDC") if "RDC" in etages_tries else 0,
        )

    def _render_etage(self, etage: str, key: str):
        """Affiche le plan d'un étage."""
        pieces_etage = self.etages.get(etage, [])

        if not pieces_etage:
            st.info(f"Aucune pièce définie pour l'étage {etage}")
            return

        # Calculer la grille optimale
        nb_pieces = len(pieces_etage)
        nb_cols = min(4, nb_pieces)

        st.markdown('<div class="etage-grid">', unsafe_allow_html=True)

        # Afficher les pièces en grille
        cols = st.columns(nb_cols)
        for idx, piece in enumerate(pieces_etage):
            with cols[idx % nb_cols]:
                self._render_piece_card(piece, key)

        st.markdown("</div>", unsafe_allow_html=True)

    def _render_piece_card(self, piece: PieceData, key: str):
        """Affiche la carte d'une pièce."""
        # Déterminer l'icône
        icone = piece.icone or ICONES_PIECES.get(
            piece.nom.lower().split()[0], ICONES_PIECES["default"]
        )

        # Classes CSS conditionnelles
        css_class = "piece-card"
        if st.session_state.get(f"{key}_selected") == piece.id:
            css_class += " selected"

        # Construct badges
        badges_html = ""
        if piece.nb_objets > 0:
            badges_html += f'<span class="badge-count">{piece.nb_objets}</span>'
        if piece.nb_a_changer > 0:
            badges_html += f'<span class="badge-count badge-warning">{piece.nb_a_changer} 🔄</span>'
        if piece.nb_a_acheter > 0:
            badges_html += f'<span class="badge-count badge-danger">{piece.nb_a_acheter} 🛒</span>'

        # Carte HTML
        card_html = f"""
        <div class="{css_class}" onclick="this.classList.toggle('selected')">
            <div class="piece-nom">
                <span style="font-size: 1.5rem;">{icone}</span>
                {piece.nom}
            </div>
            <div class="piece-stats">
                {f'<span class="piece-stat">📐 {piece.superficie_m2} m²</span>' if piece.superficie_m2 else ''}
                <span class="piece-stat">💰 {piece.valeur_totale:,.0f}€</span>
            </div>
            <div style="margin-top: 10px; display: flex; gap: 6px; flex-wrap: wrap;">
                {badges_html}
            </div>
        </div>
        """

        st.markdown(card_html, unsafe_allow_html=True)

        # Bouton Streamlit pour interaction
        if st.button(
            f"Voir {piece.nom}",
            key=f"{key}_btn_{piece.id}",
            use_container_width=True,
        ):
            st.session_state[f"{key}_selected"] = piece.id
            if self.on_piece_click:
                self.on_piece_click(piece)

    def _render_legende(self):
        """Affiche la légende des statuts."""
        st.markdown(
            """
            <div class="legende">
                <div class="legende-item">
                    <div class="legende-dot" style="background: #10b981;"></div>
                    Fonctionne
                </div>
                <div class="legende-item">
                    <div class="legende-dot" style="background: #f59e0b;"></div>
                    À changer
                </div>
                <div class="legende-item">
                    <div class="legende-dot" style="background: #3b82f6;"></div>
                    À acheter
                </div>
                <div class="legende-item">
                    <div class="legende-dot" style="background: #ef4444;"></div>
                    Hors service
                </div>
                <div class="legende-item">
                    <div class="legende-dot" style="background: #8b5cf6;"></div>
                    En commande
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ═══════════════════════════════════════════════════════════
# COMPOSANTS HELPER
# ═══════════════════════════════════════════════════════════


def carte_piece(
    piece: PieceData,
    show_objets: bool = False,
    objets: list[ObjetData] | None = None,
    on_click: Callable | None = None,
    key: str = "piece",
):
    """
    Affiche une carte de pièce individuelle.

    Args:
        piece: Données de la pièce
        show_objets: Afficher la liste des objets
        objets: Liste optionnelle des objets
        on_click: Callback au clic
        key: Clé unique
    """
    icone = piece.icone or ICONES_PIECES.get(piece.nom.lower().split()[0], ICONES_PIECES["default"])

    with st.container():
        col_info, col_stats = st.columns([2, 1])

        with col_info:
            st.markdown(f"### {icone} {piece.nom}")
            if piece.superficie_m2:
                st.caption(f"📐 {piece.superficie_m2} m² • 📍 {piece.etage}")

        with col_stats:
            st.metric("Objets", piece.nb_objets)

        # Alerts badges
        if piece.nb_a_changer > 0 or piece.nb_a_acheter > 0:
            cols = st.columns(2)
            if piece.nb_a_changer > 0:
                with cols[0]:
                    st.warning(f"🔄 {piece.nb_a_changer} à changer")
            if piece.nb_a_acheter > 0:
                with cols[1]:
                    st.info(f"🛒 {piece.nb_a_acheter} à acheter")

        # Liste des objets si demandé
        if show_objets and objets:
            st.divider()
            for objet in objets:
                _render_objet_card(objet, key)


def _render_objet_card(objet: ObjetData, key: str):
    """Affiche une carte d'objet."""
    icone = ICONES_CATEGORIES.get(objet.categorie, ICONES_CATEGORIES["default"])
    couleur = COULEURS_STATUT.get(objet.statut, "#6b7280")

    statut_labels = {
        "fonctionne": "✅ OK",
        "a_changer": "🔄 À changer",
        "a_acheter": "🛒 À acheter",
        "hors_service": "❌ HS",
        "en_commande": "📦 Commandé",
    }

    col1, col2, col3 = st.columns([3, 1, 1])

    with col1:
        st.markdown(f"**{icone} {objet.nom}**")
        if objet.marque:
            st.caption(objet.marque)

    with col2:
        st.markdown(
            f'<span style="background: {couleur}; color: white; '
            f'padding: 2px 8px; border-radius: 8px; font-size: 0.8rem;">'
            f"{statut_labels.get(objet.statut, objet.statut)}</span>",
            unsafe_allow_html=True,
        )

    with col3:
        if objet.cout_remplacement:
            st.markdown(f"**{objet.cout_remplacement:,.0f}€**")
        elif objet.prix_achat:
            st.caption(f"{objet.prix_achat:,.0f}€")


def grille_objets(
    objets: list[ObjetData],
    nb_cols: int = 3,
    on_click: Callable[[ObjetData], None] | None = None,
    key: str = "objets",
):
    """
    Affiche une grille d'objets.

    Args:
        objets: Liste des objets
        nb_cols: Nombre de colonnes
        on_click: Callback au clic sur un objet
        key: Clé unique
    """
    if not objets:
        st.info("Aucun objet dans cette pièce")
        return

    cols = st.columns(nb_cols)

    for idx, objet in enumerate(objets):
        with cols[idx % nb_cols]:
            icone = ICONES_CATEGORIES.get(objet.categorie, "📦")

            with st.container(border=True):
                st.markdown(f"### {icone} {objet.nom}")

                if objet.marque:
                    st.caption(objet.marque)

                # Badge statut
                statut_emoji = {
                    "fonctionne": "✅",
                    "a_changer": "🔄",
                    "a_acheter": "🛒",
                    "hors_service": "❌",
                }
                st.markdown(
                    f"{statut_emoji.get(objet.statut, '•')} "
                    f"**{objet.statut.replace('_', ' ').title()}**"
                )

                if objet.cout_remplacement:
                    st.metric("Coût estimé", f"{objet.cout_remplacement:,.0f}€")

                if on_click:
                    if st.button("Modifier", key=f"{key}_edit_{objet.id}"):
                        on_click(objet)


def timeline_travaux(
    travaux: list[dict[str, Any]],
    key: str = "timeline",
):
    """
    Affiche une timeline des travaux.

    Args:
        travaux: Liste des travaux avec date, titre, statut
        key: Clé unique

    Example:
        travaux = [
            {"date": date(2024, 1, 15), "titre": "Peinture salon", "statut": "completed"},
            {"date": date(2024, 2, 1), "titre": "Nouvelle cuisine", "statut": "pending"},
        ]
    """
    if not travaux:
        st.info("Aucun travaux planifié")
        return

    st.markdown('<div class="timeline-container">', unsafe_allow_html=True)

    for travail in sorted(travaux, key=lambda t: t.get("date", date.today())):
        statut = travail.get("statut", "pending")
        titre = travail.get("titre", "Sans titre")
        date_travail = travail.get("date", date.today())
        cout = travail.get("cout")

        statut_class = "completed" if statut == "completed" else "pending"
        statut_icon = "✅" if statut == "completed" else "⏳"

        st.markdown(
            f"""
            <div class="timeline-item {statut_class}">
                <div style="font-weight: 600; color: #2d3748;">
                    {statut_icon} {titre}
                </div>
                <div style="font-size: 0.85rem; color: #718096; margin-top: 4px;">
                    📅 {date_travail.strftime('%d/%m/%Y')}
                    {f' • 💰 {cout:,.0f}€' if cout else ''}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("</div>", unsafe_allow_html=True)
