"""
Plan Jardin Interactif - Visualisation 2D du jardin.

Features:
- Plan des zones avec formes personnalisables
- Visualisation des plantes avec icônes
- Calendrier saisonnier des activités
- Compagnonnage et rotation des cultures
- Météo et alertes jardin
"""

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Callable

import streamlit as st

# ═══════════════════════════════════════════════════════════
# STYLES CSS
# ═══════════════════════════════════════════════════════════

PLAN_JARDIN_CSS = """
<style>
/* Container principal du jardin */
.plan-jardin-container {
    background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%);
    border-radius: 16px;
    padding: 20px;
    margin: 10px 0;
    box-shadow: 0 4px 20px rgba(0,0,0,0.08);
}

/* Zone du jardin */
.zone-jardin {
    background: white;
    border-radius: 12px;
    padding: 16px;
    margin: 10px 0;
    border: 2px solid #10b981;
    position: relative;
    transition: all 0.3s ease;
}

.zone-jardin:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(16,185,129,0.2);
}

.zone-jardin.potager {
    border-color: #84cc16;
    background: linear-gradient(to bottom, #f7fee7, white);
}

.zone-jardin.pelouse {
    border-color: #22c55e;
    background: linear-gradient(to bottom, #dcfce7, white);
}

.zone-jardin.massif {
    border-color: #f472b6;
    background: linear-gradient(to bottom, #fce7f3, white);
}

.zone-jardin.verger {
    border-color: #fb923c;
    background: linear-gradient(to bottom, #ffedd5, white);
}

.zone-jardin.terrasse {
    border-color: #94a3b8;
    background: linear-gradient(to bottom, #f1f5f9, white);
}

/* Header zone */
.zone-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 12px;
}

.zone-nom {
    font-size: 1.2rem;
    font-weight: 700;
    color: #1f2937;
    display: flex;
    align-items: center;
    gap: 8px;
}

.zone-superficie {
    background: #f3f4f6;
    padding: 4px 10px;
    border-radius: 8px;
    font-size: 0.85rem;
    color: #6b7280;
}

/* Grille plantes */
.plantes-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(80px, 1fr));
    gap: 10px;
    margin-top: 12px;
}

/* Plante individuelle */
.plante-item {
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 10px;
    padding: 10px;
    text-align: center;
    cursor: pointer;
    transition: all 0.2s ease;
}

.plante-item:hover {
    transform: scale(1.05);
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.plante-item.excellent {
    border-color: #22c55e;
    background: #f0fdf4;
}

.plante-item.bon {
    border-color: #84cc16;
    background: #fefce8;
}

.plante-item.attention {
    border-color: #f59e0b;
    background: #fffbeb;
}

.plante-item.probleme {
    border-color: #ef4444;
    background: #fef2f2;
}

.plante-icone {
    font-size: 2rem;
    line-height: 1;
}

.plante-nom {
    font-size: 0.75rem;
    color: #374151;
    margin-top: 6px;
    font-weight: 500;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

/* Calendrier jardin */
.calendrier-jardin {
    background: white;
    border-radius: 12px;
    padding: 16px;
    margin-top: 15px;
}

.calendrier-mois {
    display: grid;
    grid-template-columns: repeat(12, 1fr);
    gap: 4px;
    margin-top: 10px;
}

.mois-cell {
    padding: 8px 4px;
    text-align: center;
    border-radius: 6px;
    font-size: 0.75rem;
    font-weight: 600;
}

.mois-cell.actif {
    background: #dcfce7;
    color: #166534;
}

.mois-cell.recolte {
    background: #fef3c7;
    color: #92400e;
}

.mois-cell.semis {
    background: #dbeafe;
    color: #1e40af;
}

.mois-cell.inactif {
    background: #f3f4f6;
    color: #9ca3af;
}

/* Compagnonnage */
.compagnonnage-grid {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-top: 10px;
}

.compagnon-badge {
    display: flex;
    align-items: center;
    gap: 4px;
    padding: 4px 10px;
    border-radius: 20px;
    font-size: 0.8rem;
}

.compagnon-badge.ami {
    background: #dcfce7;
    color: #166534;
}

.compagnon-badge.ennemi {
    background: #fef2f2;
    color: #991b1b;
}

/* Météo widget */
.meteo-jardin {
    background: linear-gradient(135deg, #60a5fa, #3b82f6);
    color: white;
    padding: 16px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    gap: 16px;
}

.meteo-icone {
    font-size: 3rem;
}

.meteo-info {
    flex: 1;
}

.meteo-temp {
    font-size: 2rem;
    font-weight: 700;
}

.meteo-detail {
    font-size: 0.9rem;
    opacity: 0.9;
}

/* Alertes jardin */
.alerte-jardin {
    padding: 12px 16px;
    border-radius: 10px;
    margin: 8px 0;
    display: flex;
    align-items: center;
    gap: 10px;
}

.alerte-jardin.gel {
    background: #eff6ff;
    border: 1px solid #3b82f6;
    color: #1e40af;
}

.alerte-jardin.secheresse {
    background: #fffbeb;
    border: 1px solid #f59e0b;
    color: #92400e;
}

.alerte-jardin.pluie {
    background: #f0fdf4;
    border: 1px solid #22c55e;
    color: #166534;
}

/* Légende zones */
.legende-zones {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
    padding: 12px;
    background: white;
    border-radius: 10px;
    margin-top: 15px;
}

.legende-zone-item {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 0.85rem;
}
</style>
"""


# ═══════════════════════════════════════════════════════════
# DATA CLASSES
# ═══════════════════════════════════════════════════════════


@dataclass
class ZoneJardinData:
    """Données d'une zone de jardin."""

    id: int
    nom: str
    type_zone: str  # potager, pelouse, massif, verger, terrasse, etc.
    superficie_m2: float | None = None
    exposition: str | None = None  # N, S, E, O, etc.
    type_sol: str | None = None
    arrosage_auto: bool = False
    nb_plantes: int = 0
    couleur: str = "#22c55e"


@dataclass
class PlanteData:
    """Données d'une plante."""

    id: int
    nom: str
    variete: str | None = None
    icone: str = "🌱"
    etat: str = "bon"  # excellent, bon, attention, probleme
    date_plantation: date | None = None
    mois_semis: list[int] = field(default_factory=list)
    mois_recolte: list[int] = field(default_factory=list)
    arrosage: str | None = None  # quotidien, hebdo, etc.
    compagnons_amis: list[str] = field(default_factory=list)
    compagnons_ennemis: list[str] = field(default_factory=list)


@dataclass
class MeteoJardinData:
    """Données météo pour le jardin."""

    temperature: float
    icone: str
    description: str
    precipitation_mm: float = 0
    vent_kmh: float = 0
    gel_prevu: bool = False
    alertes: list[str] = field(default_factory=list)


# ═══════════════════════════════════════════════════════════
# CONSTANTES ICÔNES
# ═══════════════════════════════════════════════════════════

ICONES_ZONES = {
    "potager": "🥬",
    "pelouse": "🌿",
    "massif": "🌸",
    "verger": "🍎",
    "haie": "🌳",
    "terrasse": "🪴",
    "serre": "🏡",
    "compost": "♻️",
    "bassin": "💧",
    "allee": "🚶",
    "default": "🌱",
}

ICONES_PLANTES = {
    "tomate": "🍅",
    "carotte": "🥕",
    "salade": "🥬",
    "courgette": "🥒",
    "aubergine": "🍆",
    "poivron": "🫑",
    "fraise": "🍓",
    "pomme": "🍎",
    "poire": "🍐",
    "cerise": "🍒",
    "rose": "🌹",
    "tournesol": "🌻",
    "tulipe": "🌷",
    "lavande": "💜",
    "basilic": "🌿",
    "menthe": "🍃",
    "persil": "🥬",
    "default": "🌱",
}

ICONES_METEO = {
    "soleil": "☀️",
    "nuageux": "⛅",
    "pluie": "🌧️",
    "orage": "⛈️",
    "neige": "❄️",
    "brouillard": "🌫️",
}

COULEURS_ZONES = {
    "potager": "#84cc16",
    "pelouse": "#22c55e",
    "massif": "#f472b6",
    "verger": "#fb923c",
    "terrasse": "#94a3b8",
    "serre": "#14b8a6",
    "haie": "#166534",
}


# ═══════════════════════════════════════════════════════════
# CLASSE PRINCIPALE
# ═══════════════════════════════════════════════════════════


class PlanJardinInteractif:
    """Plan interactif du jardin avec zones et plantes."""

    def __init__(
        self,
        zones: list[ZoneJardinData],
        plantes_par_zone: dict[int, list[PlanteData]] | None = None,
        meteo: MeteoJardinData | None = None,
        on_zone_click: Callable[[ZoneJardinData], None] | None = None,
        on_plante_click: Callable[[PlanteData], None] | None = None,
    ):
        """
        Initialise le plan jardin interactif.

        Args:
            zones: Liste des zones du jardin
            plantes_par_zone: Dictionnaire zone_id -> liste de plantes
            meteo: Données météo actuelles
            on_zone_click: Callback quand une zone est cliquée
            on_plante_click: Callback quand une plante est cliquée
        """
        self.zones = zones
        self.plantes_par_zone = plantes_par_zone or {}
        self.meteo = meteo
        self.on_zone_click = on_zone_click
        self.on_plante_click = on_plante_click

    def render(self, key: str = "plan_jardin"):
        """Affiche le plan jardin interactif complet."""
        # Injecter CSS
        st.markdown(PLAN_JARDIN_CSS, unsafe_allow_html=True)

        # Container principal
        st.markdown('<div class="plan-jardin-container">', unsafe_allow_html=True)

        # Header avec météo
        self._render_header()

        # Alertes météo
        if self.meteo and self.meteo.alertes:
            self._render_alertes()

        # Vue principale (plan ou liste)
        vue = st.radio(
            "Vue",
            ["🗺️ Plan", "📋 Liste", "📅 Calendrier"],
            horizontal=True,
            key=f"{key}_vue",
        )

        if vue == "🗺️ Plan":
            self._render_plan_zones(key)
        elif vue == "📋 Liste":
            self._render_liste_zones(key)
        else:
            self._render_calendrier_global(key)

        # Légende
        self._render_legende()

        st.markdown("</div>", unsafe_allow_html=True)

    def _render_header(self):
        """Affiche le header avec statistiques et météo."""
        col_stats, col_meteo = st.columns([2, 1])

        with col_stats:
            total_zones = len(self.zones)
            total_plantes = sum(len(self.plantes_par_zone.get(z.id, [])) for z in self.zones)
            superficie_totale = sum(z.superficie_m2 or 0 for z in self.zones)

            c1, c2, c3 = st.columns(3)
            with c1:
                st.metric("🌳 Zones", total_zones)
            with c2:
                st.metric("🌱 Plantes", total_plantes)
            with c3:
                st.metric("📐 Surface", f"{superficie_totale:.0f} m²")

        with col_meteo:
            if self.meteo:
                self._render_meteo_widget()

    def _render_meteo_widget(self):
        """Affiche le widget météo."""
        if not self.meteo:
            return

        st.markdown(
            f"""
            <div class="meteo-jardin">
                <div class="meteo-icone">{self.meteo.icone}</div>
                <div class="meteo-info">
                    <div class="meteo-temp">{self.meteo.temperature:.0f}°C</div>
                    <div class="meteo-detail">
                        {self.meteo.description}
                        {" • 🌧️ " + str(self.meteo.precipitation_mm) + "mm" if self.meteo.precipitation_mm > 0 else ""}
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    def _render_alertes(self):
        """Affiche les alertes météo pour le jardin."""
        for alerte in self.meteo.alertes:
            alerte_type = "gel" if "gel" in alerte.lower() else "pluie"
            icone = "🥶" if "gel" in alerte.lower() else "⚠️"

            st.markdown(
                f"""
                <div class="alerte-jardin {alerte_type}">
                    <span style="font-size: 1.5rem;">{icone}</span>
                    <span>{alerte}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

    def _render_plan_zones(self, key: str):
        """Affiche le plan visuel des zones."""
        if not self.zones:
            st.info("Aucune zone définie dans le jardin")
            return

        # Afficher les zones en grille adaptative
        nb_zones = len(self.zones)
        nb_cols = min(3, nb_zones)

        cols = st.columns(nb_cols)

        for idx, zone in enumerate(self.zones):
            with cols[idx % nb_cols]:
                self._render_zone_card(zone, key)

    def _render_zone_card(self, zone: ZoneJardinData, key: str):
        """Affiche une carte de zone."""
        icone = ICONES_ZONES.get(zone.type_zone, ICONES_ZONES["default"])
        plantes = self.plantes_par_zone.get(zone.id, [])

        # Card de zone
        with st.container(border=True):
            # Header
            col_nom, col_sup = st.columns([3, 1])
            with col_nom:
                st.markdown(f"### {icone} {zone.nom}")
            with col_sup:
                if zone.superficie_m2:
                    st.caption(f"📐 {zone.superficie_m2} m²")

            # Info zone
            info_parts = []
            if zone.exposition:
                info_parts.append(f"🧭 {zone.exposition}")
            if zone.type_sol:
                info_parts.append(f"🪨 {zone.type_sol}")
            if zone.arrosage_auto:
                info_parts.append("💧 Auto")

            if info_parts:
                st.caption(" • ".join(info_parts))

            # Plantes dans cette zone
            if plantes:
                st.markdown("**Plantes:**")
                plantes_html = '<div class="plantes-grid">'
                for plante in plantes[:6]:  # Max 6 affichées
                    icone_plante = ICONES_PLANTES.get(plante.nom.lower(), plante.icone)
                    plantes_html += f"""
                    <div class="plante-item {plante.etat}">
                        <div class="plante-icone">{icone_plante}</div>
                        <div class="plante-nom">{plante.nom}</div>
                    </div>
                    """
                plantes_html += "</div>"
                st.markdown(plantes_html, unsafe_allow_html=True)

                if len(plantes) > 6:
                    st.caption(f"+{len(plantes) - 6} autres plantes...")
            else:
                st.caption("🌱 Aucune plante")

            # Bouton voir détails
            if st.button(
                f"Voir {zone.nom}",
                key=f"{key}_zone_{zone.id}",
                use_container_width=True,
            ):
                st.session_state[f"{key}_selected_zone"] = zone.id
                if self.on_zone_click:
                    self.on_zone_click(zone)

    def _render_liste_zones(self, key: str):
        """Affiche la liste détaillée des zones avec plantes."""
        for zone in self.zones:
            icone = ICONES_ZONES.get(zone.type_zone, "🌱")
            plantes = self.plantes_par_zone.get(zone.id, [])

            with st.expander(f"{icone} {zone.nom} ({len(plantes)} plantes)", expanded=False):
                # Info zone
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Surface", f"{zone.superficie_m2 or 0} m²")
                with col2:
                    st.metric("Exposition", zone.exposition or "N/D")
                with col3:
                    st.metric("Sol", zone.type_sol or "N/D")

                # Liste des plantes
                if plantes:
                    st.divider()
                    for plante in plantes:
                        self._render_plante_detail(plante, key)

    def _render_plante_detail(self, plante: PlanteData, key: str):
        """Affiche le détail d'une plante."""
        icone = ICONES_PLANTES.get(plante.nom.lower(), plante.icone)
        etat_emoji = {
            "excellent": "🌟",
            "bon": "✅",
            "attention": "⚠️",
            "probleme": "❌",
        }

        col1, col2, col3 = st.columns([2, 1, 1])

        with col1:
            st.markdown(f"**{icone} {plante.nom}**")
            if plante.variete:
                st.caption(f"Variété: {plante.variete}")

        with col2:
            st.markdown(f"{etat_emoji.get(plante.etat, '•')} {plante.etat.title()}")

        with col3:
            if plante.date_plantation:
                st.caption(f"🌱 {plante.date_plantation.strftime('%d/%m/%Y')}")

        # Compagnonnage
        if plante.compagnons_amis or plante.compagnons_ennemis:
            compagnonnage_html = '<div class="compagnonnage-grid">'
            for ami in plante.compagnons_amis[:3]:
                compagnonnage_html += f'<span class="compagnon-badge ami">✓ {ami}</span>'
            for ennemi in plante.compagnons_ennemis[:3]:
                compagnonnage_html += f'<span class="compagnon-badge ennemi">✗ {ennemi}</span>'
            compagnonnage_html += "</div>"
            st.markdown(compagnonnage_html, unsafe_allow_html=True)

    def _render_calendrier_global(self, key: str):
        """Affiche le calendrier global du jardin."""
        st.markdown("### 📅 Calendrier du Jardin")

        # Collecter toutes les plantes
        toutes_plantes = []
        for zone_id, plantes in self.plantes_par_zone.items():
            toutes_plantes.extend(plantes)

        if not toutes_plantes:
            st.info("Ajoutez des plantes pour voir le calendrier")
            return

        # Afficher calendrier par plante
        calendrier_jardin(toutes_plantes, key=key)

    def _render_legende(self):
        """Affiche la légende des types de zones."""
        st.markdown(
            """
            <div class="legende-zones">
                <div class="legende-zone-item">
                    <span style="color: #84cc16; font-size: 1.2rem;">●</span> Potager
                </div>
                <div class="legende-zone-item">
                    <span style="color: #22c55e; font-size: 1.2rem;">●</span> Pelouse
                </div>
                <div class="legende-zone-item">
                    <span style="color: #f472b6; font-size: 1.2rem;">●</span> Massif
                </div>
                <div class="legende-zone-item">
                    <span style="color: #fb923c; font-size: 1.2rem;">●</span> Verger
                </div>
                <div class="legende-zone-item">
                    <span style="color: #94a3b8; font-size: 1.2rem;">●</span> Terrasse
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ═══════════════════════════════════════════════════════════
# COMPOSANTS HELPER
# ═══════════════════════════════════════════════════════════


def carte_zone(
    zone: ZoneJardinData,
    plantes: list[PlanteData] | None = None,
    show_details: bool = True,
    key: str = "zone",
):
    """
    Affiche une carte de zone jardin.

    Args:
        zone: Données de la zone
        plantes: Plantes dans cette zone
        show_details: Afficher les détails
        key: Clé unique
    """
    icone = ICONES_ZONES.get(zone.type_zone, "🌱")

    with st.container(border=True):
        st.markdown(f"### {icone} {zone.nom}")

        col1, col2 = st.columns(2)
        with col1:
            if zone.superficie_m2:
                st.metric("Surface", f"{zone.superficie_m2} m²")
        with col2:
            st.metric("Plantes", zone.nb_plantes)

        if show_details and plantes:
            st.divider()
            for plante in plantes[:5]:
                p_icone = ICONES_PLANTES.get(plante.nom.lower(), "🌱")
                st.markdown(f"- {p_icone} {plante.nom}")


def calendrier_jardin(
    plantes: list[PlanteData],
    key: str = "calendrier",
):
    """
    Affiche un calendrier des semis et récoltes.

    Args:
        plantes: Liste des plantes
        key: Clé unique
    """
    mois_noms = ["J", "F", "M", "A", "M", "J", "J", "A", "S", "O", "N", "D"]
    mois_actuel = datetime.now().month

    st.markdown('<div class="calendrier-jardin">', unsafe_allow_html=True)

    # Header mois
    cols = st.columns(13)
    with cols[0]:
        st.markdown("**Plante**")
    for i, mois in enumerate(mois_noms):
        with cols[i + 1]:
            style = "font-weight: bold;" if i + 1 == mois_actuel else ""
            st.markdown(f'<div style="{style}">{mois}</div>', unsafe_allow_html=True)

    # Lignes par plante
    for plante in plantes:
        icone = ICONES_PLANTES.get(plante.nom.lower(), "🌱")
        cols = st.columns(13)

        with cols[0]:
            st.markdown(f"{icone} {plante.nom[:10]}")

        for mois_idx in range(12):
            mois = mois_idx + 1
            with cols[mois_idx + 1]:
                if mois in plante.mois_semis:
                    st.markdown("🌱", help=f"Semis: {mois_noms[mois_idx]}")
                elif mois in plante.mois_recolte:
                    st.markdown("🥕", help=f"Récolte: {mois_noms[mois_idx]}")
                else:
                    st.markdown("·")

    st.markdown("</div>", unsafe_allow_html=True)

    # Légende
    st.caption("🌱 = Semis • 🥕 = Récolte")


def grille_plantes(
    plantes: list[PlanteData],
    nb_cols: int = 4,
    on_click: Callable[[PlanteData], None] | None = None,
    key: str = "plantes",
):
    """
    Affiche une grille de plantes.

    Args:
        plantes: Liste des plantes
        nb_cols: Nombre de colonnes
        on_click: Callback au clic
        key: Clé unique
    """
    if not plantes:
        st.info("Aucune plante dans cette zone")
        return

    cols = st.columns(nb_cols)

    for idx, plante in enumerate(plantes):
        with cols[idx % nb_cols]:
            icone = ICONES_PLANTES.get(plante.nom.lower(), plante.icone)

            etat_couleurs = {
                "excellent": "#22c55e",
                "bon": "#84cc16",
                "attention": "#f59e0b",
                "probleme": "#ef4444",
            }
            couleur = etat_couleurs.get(plante.etat, "#6b7280")

            with st.container(border=True):
                st.markdown(
                    f'<div style="text-align: center; font-size: 2.5rem;">{icone}</div>',
                    unsafe_allow_html=True,
                )
                st.markdown(f"**{plante.nom}**")

                if plante.variete:
                    st.caption(plante.variete)

                # Badge état
                st.markdown(
                    f'<span style="background: {couleur}; color: white; '
                    f'padding: 2px 8px; border-radius: 8px; font-size: 0.75rem;">'
                    f"{plante.etat.title()}</span>",
                    unsafe_allow_html=True,
                )

                if on_click:
                    if st.button("Détails", key=f"{key}_{plante.id}", use_container_width=True):
                        on_click(plante)
