"""
Composants UI réutilisables pour le module Maison.

Widgets et composants spécialisés:
- carte_objet_statut: Carte d'objet avec statut et actions
- badge_priorite: Badge de priorité coloré
- modal_changement_statut: Modal pour changer le statut d'un objet
- widget_cout_travaux: Widget d'affichage des coûts
- timeline_versions: Timeline des versions/modifications
"""

from datetime import date
from decimal import Decimal
from typing import Any, Callable

import streamlit as st

# ═══════════════════════════════════════════════════════════
# STYLES CSS
# ═══════════════════════════════════════════════════════════

COMPOSANTS_CSS = """
<style>
/* Carte objet avec statut */
.carte-objet {
    background: white;
    border-radius: 12px;
    padding: 16px;
    margin: 8px 0;
    border: 2px solid #e5e7eb;
    transition: all 0.2s ease;
}

.carte-objet:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
}

.carte-objet.a-changer {
    border-color: #f59e0b;
    background: linear-gradient(to right, #fffbeb, white);
}

.carte-objet.a-acheter {
    border-color: #3b82f6;
    background: linear-gradient(to right, #eff6ff, white);
}

.carte-objet.urgent {
    border-color: #ef4444;
    background: linear-gradient(to right, #fef2f2, white);
}

.carte-objet.en-commande {
    border-color: #8b5cf6;
    background: linear-gradient(to right, #f5f3ff, white);
}

/* Header carte */
.carte-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 10px;
}

.carte-nom {
    font-size: 1.1rem;
    font-weight: 600;
    color: #1f2937;
}

.carte-categorie {
    font-size: 0.8rem;
    color: #6b7280;
}

/* Badge priorité */
.badge-priorite {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 4px 10px;
    border-radius: 12px;
    font-size: 0.8rem;
    font-weight: 600;
}

.badge-priorite.critique {
    background: #fef2f2;
    color: #991b1b;
    border: 1px solid #fecaca;
}

.badge-priorite.haute {
    background: #fff7ed;
    color: #c2410c;
    border: 1px solid #fed7aa;
}

.badge-priorite.moyenne {
    background: #fefce8;
    color: #a16207;
    border: 1px solid #fef08a;
}

.badge-priorite.basse {
    background: #f0fdf4;
    color: #166534;
    border: 1px solid #bbf7d0;
}

/* Badge statut */
.badge-statut {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 4px 10px;
    border-radius: 12px;
    font-size: 0.75rem;
    font-weight: 500;
}

.badge-statut.fonctionnel {
    background: #dcfce7;
    color: #166534;
}

.badge-statut.a-reparer {
    background: #fef3c7;
    color: #92400e;
}

.badge-statut.a-changer {
    background: #ffedd5;
    color: #c2410c;
}

.badge-statut.a-acheter {
    background: #dbeafe;
    color: #1e40af;
}

.badge-statut.commande {
    background: #ede9fe;
    color: #6b21a8;
}

.badge-statut.obsolete {
    background: #f3f4f6;
    color: #6b7280;
}

/* Widget coût */
.widget-cout {
    background: linear-gradient(135deg, #f0fdf4, #dcfce7);
    border: 1px solid #86efac;
    border-radius: 12px;
    padding: 16px;
}

.cout-montant {
    font-size: 1.8rem;
    font-weight: 700;
    color: #166534;
}

.cout-label {
    font-size: 0.85rem;
    color: #15803d;
}

/* Timeline versions */
.timeline-container {
    position: relative;
    padding-left: 24px;
}

.timeline-line {
    position: absolute;
    left: 8px;
    top: 0;
    bottom: 0;
    width: 2px;
    background: #e5e7eb;
}

.timeline-item {
    position: relative;
    padding: 12px 0;
    margin-left: 16px;
}

.timeline-dot {
    position: absolute;
    left: -24px;
    top: 14px;
    width: 12px;
    height: 12px;
    border-radius: 50%;
    background: white;
    border: 2px solid #3b82f6;
}

.timeline-dot.active {
    background: #3b82f6;
}

.timeline-date {
    font-size: 0.75rem;
    color: #6b7280;
    margin-bottom: 4px;
}

.timeline-title {
    font-weight: 600;
    color: #1f2937;
}

.timeline-desc {
    font-size: 0.85rem;
    color: #4b5563;
}

/* Actions rapides */
.actions-rapides {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
    margin-top: 10px;
}

.action-btn {
    padding: 6px 12px;
    border-radius: 8px;
    font-size: 0.8rem;
    cursor: pointer;
    transition: all 0.2s;
    border: none;
}

.action-btn.primaire {
    background: #3b82f6;
    color: white;
}

.action-btn.secondaire {
    background: #f3f4f6;
    color: #374151;
}

.action-btn:hover {
    transform: translateY(-1px);
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}
</style>
"""


# ═══════════════════════════════════════════════════════════
# CONSTANTES
# ═══════════════════════════════════════════════════════════

STATUT_CONFIG = {
    "fonctionnel": {"icone": "✅", "couleur": "#22c55e", "label": "Fonctionnel"},
    "a_reparer": {"icone": "🔧", "couleur": "#f59e0b", "label": "À réparer"},
    "a_changer": {"icone": "🔄", "couleur": "#f97316", "label": "À changer"},
    "a_acheter": {"icone": "🛒", "couleur": "#3b82f6", "label": "À acheter"},
    "en_commande": {"icone": "📦", "couleur": "#8b5cf6", "label": "En commande"},
    "obsolete": {"icone": "⚠️", "couleur": "#6b7280", "label": "Obsolète"},
    "a_donner": {"icone": "🎁", "couleur": "#14b8a6", "label": "À donner"},
    "a_jeter": {"icone": "🗑️", "couleur": "#ef4444", "label": "À jeter"},
}

PRIORITE_CONFIG = {
    "critique": {"icone": "🔴", "couleur": "#ef4444", "label": "Critique"},
    "haute": {"icone": "🟠", "couleur": "#f97316", "label": "Haute"},
    "moyenne": {"icone": "🟡", "couleur": "#eab308", "label": "Moyenne"},
    "basse": {"icone": "🟢", "couleur": "#22c55e", "label": "Basse"},
}


# ═══════════════════════════════════════════════════════════
# COMPOSANTS
# ═══════════════════════════════════════════════════════════


def carte_objet_statut(
    nom: str,
    categorie: str,
    statut: str = "fonctionnel",
    priorite: str | None = None,
    date_achat: date | None = None,
    prix_estime: Decimal | None = None,
    notes: str | None = None,
    on_changer_statut: Callable[[str], None] | None = None,
    on_ajouter_courses: Callable[[], None] | None = None,
    on_ajouter_budget: Callable[[], None] | None = None,
    key: str = "objet",
):
    """
    Affiche une carte d'objet avec statut et actions.

    Args:
        nom: Nom de l'objet
        categorie: Catégorie de l'objet
        statut: Statut actuel (fonctionnel, a_changer, a_acheter, etc.)
        priorite: Priorité de remplacement (critique, haute, moyenne, basse)
        date_achat: Date d'achat si connue
        prix_estime: Prix estimé de remplacement
        notes: Notes additionnelles
        on_changer_statut: Callback pour changer le statut
        on_ajouter_courses: Callback pour ajouter aux courses
        on_ajouter_budget: Callback pour ajouter au budget
        key: Clé unique
    """
    st.markdown(COMPOSANTS_CSS, unsafe_allow_html=True)

    with st.container(border=True):
        # Header
        col_nom, col_badge = st.columns([3, 1])

        with col_nom:
            st.markdown(f"### {nom}")
            st.caption(f"📁 {categorie}")

        with col_badge:
            badge_statut_widget(statut)

        # Priorité si définie
        if priorite:
            badge_priorite(priorite)

        # Détails
        if date_achat or prix_estime:
            col1, col2 = st.columns(2)
            with col1:
                if date_achat:
                    st.markdown(f"📅 Acheté le {date_achat.strftime('%d/%m/%Y')}")
            with col2:
                if prix_estime:
                    st.markdown(f"💰 ~{prix_estime:.2f} €")

        # Notes
        if notes:
            st.caption(f"📝 {notes}")

        # Actions
        st.divider()

        col_actions = st.columns(4)

        with col_actions[0]:
            if st.button("🔄 Statut", key=f"{key}_statut", use_container_width=True):
                if on_changer_statut:
                    # Ouvre modal
                    st.session_state[f"{key}_modal_statut"] = True

        with col_actions[1]:
            if statut in ("a_acheter", "a_changer"):
                if st.button("🛒 Courses", key=f"{key}_courses", use_container_width=True):
                    if on_ajouter_courses:
                        on_ajouter_courses()

        with col_actions[2]:
            if statut in ("a_acheter", "a_changer") and prix_estime:
                if st.button("💰 Budget", key=f"{key}_budget", use_container_width=True):
                    if on_ajouter_budget:
                        on_ajouter_budget()

        with col_actions[3]:
            if st.button("ℹ️ Détails", key=f"{key}_details", use_container_width=True):
                st.session_state[f"{key}_show_details"] = True


def badge_priorite(priorite: str, size: str = "normal"):
    """
    Affiche un badge de priorité coloré.

    Args:
        priorite: Niveau de priorité (critique, haute, moyenne, basse)
        size: Taille du badge (small, normal, large)
    """
    config = PRIORITE_CONFIG.get(priorite.lower(), PRIORITE_CONFIG["moyenne"])

    size_styles = {
        "small": "font-size: 0.7rem; padding: 2px 6px;",
        "normal": "font-size: 0.8rem; padding: 4px 10px;",
        "large": "font-size: 0.9rem; padding: 6px 14px;",
    }

    style = size_styles.get(size, size_styles["normal"])

    st.markdown(
        f"""
        <span class="badge-priorite {priorite.lower()}" style="{style}">
            {config["icone"]} {config["label"]}
        </span>
        """,
        unsafe_allow_html=True,
    )


def badge_statut_widget(statut: str):
    """
    Affiche un badge de statut.

    Args:
        statut: Statut de l'objet
    """
    config = STATUT_CONFIG.get(statut, STATUT_CONFIG["fonctionnel"])
    classe = statut.replace("_", "-")

    st.markdown(
        f"""
        <span class="badge-statut {classe}">
            {config["icone"]} {config["label"]}
        </span>
        """,
        unsafe_allow_html=True,
    )


def modal_changement_statut(
    statuts_disponibles: list[str] | None = None,
    statut_actuel: str = "fonctionnel",
    on_confirm: Callable[[str, str | None], None] | None = None,
    key: str = "modal_statut",
):
    """
    Modal pour changer le statut d'un objet.

    Args:
        statuts_disponibles: Liste des statuts possibles
        statut_actuel: Statut actuel de l'objet
        on_confirm: Callback(nouveau_statut, raison) quand confirmé
        key: Clé unique
    """
    if statuts_disponibles is None:
        statuts_disponibles = list(STATUT_CONFIG.keys())

    st.markdown("### 🔄 Changer le statut")

    # Sélection du nouveau statut
    options = []
    for s in statuts_disponibles:
        if s != statut_actuel:
            config = STATUT_CONFIG.get(s, {"icone": "•", "label": s})
            options.append(f"{config['icone']} {config['label']}")

    nouveau = st.selectbox(
        "Nouveau statut",
        options,
        key=f"{key}_select",
    )

    # Raison optionnelle
    raison = st.text_area(
        "Raison (optionnel)",
        placeholder="Pourquoi ce changement ?",
        key=f"{key}_raison",
        max_chars=200,
    )

    # Boutons
    col1, col2 = st.columns(2)

    with col1:
        if st.button(
            "✅ Confirmer", key=f"{key}_confirm", type="primary", use_container_width=True
        ):
            # Extraire le statut depuis le label
            for s, config in STATUT_CONFIG.items():
                if f"{config['icone']} {config['label']}" == nouveau:
                    if on_confirm:
                        on_confirm(s, raison if raison else None)
                    return s, raison

    with col2:
        if st.button("❌ Annuler", key=f"{key}_cancel", use_container_width=True):
            return None, None

    return None, None


def widget_cout_travaux(
    cout_total: Decimal,
    cout_main_oeuvre: Decimal | None = None,
    cout_materiaux: Decimal | None = None,
    nb_pieces: int = 0,
    titre: str = "Coûts des travaux",
    key: str = "cout",
):
    """
    Widget d'affichage des coûts de travaux.

    Args:
        cout_total: Coût total
        cout_main_oeuvre: Coût de main d'œuvre
        cout_materiaux: Coût des matériaux
        nb_pieces: Nombre de pièces concernées
        titre: Titre du widget
        key: Clé unique
    """
    st.markdown(COMPOSANTS_CSS, unsafe_allow_html=True)

    st.markdown(
        f"""
        <div class="widget-cout">
            <div class="cout-label">{titre}</div>
            <div class="cout-montant">{cout_total:,.2f} €</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Détail des coûts
    if cout_main_oeuvre or cout_materiaux:
        cols = st.columns(3 if nb_pieces > 0 else 2)

        if cout_materiaux:
            with cols[0]:
                st.metric("🧱 Matériaux", f"{cout_materiaux:,.2f} €")

        if cout_main_oeuvre:
            with cols[1]:
                st.metric("👷 Main d'œuvre", f"{cout_main_oeuvre:,.2f} €")

        if nb_pieces > 0:
            with cols[2]:
                st.metric("🏠 Pièces", nb_pieces)


def timeline_versions(
    versions: list[dict[str, Any]],
    max_items: int = 5,
    key: str = "timeline",
):
    """
    Affiche une timeline des versions/modifications.

    Args:
        versions: Liste de dicts avec: date, titre, description, active
        max_items: Nombre max d'items à afficher
        key: Clé unique

    Example:
        versions = [
            {"date": date(2024, 1, 15), "titre": "Rénovation", "description": "Peinture", "active": True},
            {"date": date(2023, 6, 1), "titre": "Création", "description": "Ajout pièce", "active": False},
        ]
    """
    st.markdown(COMPOSANTS_CSS, unsafe_allow_html=True)

    if not versions:
        st.info("Aucune version enregistrée")
        return

    # Trier par date décroissante
    versions_triees = sorted(versions, key=lambda v: v.get("date", date.min), reverse=True)

    st.markdown('<div class="timeline-container">', unsafe_allow_html=True)
    st.markdown('<div class="timeline-line"></div>', unsafe_allow_html=True)

    for idx, version in enumerate(versions_triees[:max_items]):
        date_v = version.get("date", "")
        titre = version.get("titre", "Version")
        description = version.get("description", "")

        date_str = date_v.strftime("%d/%m/%Y") if isinstance(date_v, date) else str(date_v)

        with st.container(border=True):
            col1, col2 = st.columns([1, 3])
            with col1:
                st.caption(f"📅 {date_str}")
            with col2:
                st.markdown(f"**{titre}**")
                if description:
                    st.caption(description)

    st.markdown("</div>", unsafe_allow_html=True)

    # Voir plus
    if len(versions) > max_items:
        if st.button(
            f"Voir les {len(versions) - max_items} versions précédentes", key=f"{key}_more"
        ):
            st.session_state[f"{key}_show_all"] = True


def selecteur_statut(
    statut_actuel: str = "fonctionnel",
    statuts_exclus: list[str] | None = None,
    key: str = "sel_statut",
) -> str | None:
    """
    Sélecteur de statut avec icônes.

    Args:
        statut_actuel: Statut actuel (présélectionné)
        statuts_exclus: Statuts à exclure des options
        key: Clé unique

    Returns:
        Statut sélectionné ou None
    """
    statuts_exclus = statuts_exclus or []

    options = [
        f"{config['icone']} {config['label']}"
        for s, config in STATUT_CONFIG.items()
        if s not in statuts_exclus
    ]

    # Trouver l'index actuel
    index_actuel = 0
    for i, (s, config) in enumerate(STATUT_CONFIG.items()):
        if s not in statuts_exclus and s == statut_actuel:
            index_actuel = i
            break

    selection = st.selectbox(
        "Statut",
        options,
        index=index_actuel,
        key=key,
    )

    # Convertir label -> clé statut
    if selection:
        for s, config in STATUT_CONFIG.items():
            if f"{config['icone']} {config['label']}" == selection:
                return s

    return None


def indicateur_urgence(
    nb_critique: int = 0,
    nb_haute: int = 0,
    nb_moyenne: int = 0,
    nb_basse: int = 0,
    key: str = "urgence",
):
    """
    Affiche un indicateur visuel des urgences.

    Args:
        nb_critique: Nombre d'items critiques
        nb_haute: Nombre d'items haute priorité
        nb_moyenne: Nombre d'items moyenne priorité
        nb_basse: Nombre d'items basse priorité
        key: Clé unique
    """
    total = nb_critique + nb_haute + nb_moyenne + nb_basse

    if total == 0:
        st.success("✅ Aucune urgence")
        return

    cols = st.columns(4)

    with cols[0]:
        if nb_critique > 0:
            st.markdown(
                f"""
                <div style="text-align: center; padding: 8px; background: #fef2f2; border-radius: 8px;">
                    <div style="font-size: 1.5rem; font-weight: bold; color: #ef4444;">{nb_critique}</div>
                    <div style="font-size: 0.75rem; color: #991b1b;">Critique</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.caption("🔴 0 critique")

    with cols[1]:
        if nb_haute > 0:
            st.markdown(
                f"""
                <div style="text-align: center; padding: 8px; background: #fff7ed; border-radius: 8px;">
                    <div style="font-size: 1.5rem; font-weight: bold; color: #f97316;">{nb_haute}</div>
                    <div style="font-size: 0.75rem; color: #c2410c;">Haute</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.caption("🟠 0 haute")

    with cols[2]:
        if nb_moyenne > 0:
            st.markdown(
                f"""
                <div style="text-align: center; padding: 8px; background: #fefce8; border-radius: 8px;">
                    <div style="font-size: 1.5rem; font-weight: bold; color: #eab308;">{nb_moyenne}</div>
                    <div style="font-size: 0.75rem; color: #a16207;">Moyenne</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.caption("🟡 0 moyenne")

    with cols[3]:
        if nb_basse > 0:
            st.markdown(
                f"""
                <div style="text-align: center; padding: 8px; background: #f0fdf4; border-radius: 8px;">
                    <div style="font-size: 1.5rem; font-weight: bold; color: #22c55e;">{nb_basse}</div>
                    <div style="font-size: 0.75rem; color: #166534;">Basse</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.caption("🟢 0 basse")
