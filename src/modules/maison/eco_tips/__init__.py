"""
Module Éco-Tips - Conseils écologiques pour la maison.

Conseils éco-gestes, astuces économies d'énergie et alternatives durables
avec suggestions IA personnalisées selon le profil du foyer.
Gestion CRUD des actions écologiques avec suivi des économies.
"""

import logging
from decimal import Decimal

import streamlit as st

from src.core.db import obtenir_contexte_db
from src.core.monitoring.rerun_profiler import profiler_rerun
from src.modules._framework import error_boundary
from src.ui.keys import KeyNamespace
from src.ui.state.url import tabs_with_url

__all__ = ["app"]

_keys = KeyNamespace("eco_tips")
logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════
# CONSTANTES
# ═══════════════════════════════════════════════════════════

TYPE_LABELS = {
    "lavable": "🧽 Lavable/Réutilisable",
    "energie": "⚡ Énergie",
    "eau": "💧 Eau",
    "dechets": "♻️ Déchets",
    "alimentation": "🍽️ Alimentation",
}

IDEES_ACTIONS = [
    {
        "nom": "Éponges lavables",
        "type": "lavable",
        "economie_estimee": 5.0,
        "cout_nouveau_initial": 15.0,
        "description": "Remplacer les éponges jetables par des éponges lavables en tissu.",
    },
    {
        "nom": "Serviettes en tissu",
        "type": "lavable",
        "economie_estimee": 8.0,
        "cout_nouveau_initial": 25.0,
        "description": "Utiliser des serviettes en tissu au lieu de l'essuie-tout.",
    },
    {
        "nom": "LED partout",
        "type": "energie",
        "economie_estimee": 15.0,
        "cout_nouveau_initial": 40.0,
        "description": "Remplacer toutes les ampoules par des LED basse consommation.",
    },
    {
        "nom": "Mousseurs robinets",
        "type": "eau",
        "economie_estimee": 10.0,
        "cout_nouveau_initial": 12.0,
        "description": "Installer des mousseurs sur tous les robinets (40% économie eau).",
    },
    {
        "nom": "Composteur",
        "type": "dechets",
        "economie_estimee": 5.0,
        "cout_nouveau_initial": 50.0,
        "description": "Composter les déchets organiques pour réduire les poubelles.",
    },
    {
        "nom": "Batch cooking",
        "type": "alimentation",
        "economie_estimee": 40.0,
        "cout_nouveau_initial": 0.0,
        "description": "Cuisiner en lots pour la semaine, réduire le gaspillage et les repas à emporter.",
    },
    {
        "nom": "Thermostat programmable",
        "type": "energie",
        "economie_estimee": 25.0,
        "cout_nouveau_initial": 80.0,
        "description": "Programmer le chauffage: 17°C la nuit, 19°C le jour.",
    },
    {
        "nom": "Récupérateur eau pluie",
        "type": "eau",
        "economie_estimee": 12.0,
        "cout_nouveau_initial": 60.0,
        "description": "Récupérer l'eau de pluie pour l'arrosage du jardin.",
    },
]

# ═══════════════════════════════════════════════════════════
# DONNÉES STATIQUES
# ═══════════════════════════════════════════════════════════

ECO_TIPS_DATA = {
    "🔌 Énergie": [
        {
            "tip": "Baisser le chauffage de 1°C = 7% d'économies",
            "impact": "haute",
            "difficulte": "facile",
        },
        {
            "tip": "Éteindre les appareils en veille = 10% d'économies",
            "impact": "moyenne",
            "difficulte": "facile",
        },
        {
            "tip": "Utiliser des multiprises à interrupteur",
            "impact": "moyenne",
            "difficulte": "facile",
        },
        {
            "tip": "Privilégier les LED (80% moins gourmandes)",
            "impact": "haute",
            "difficulte": "facile",
        },
        {
            "tip": "Programmer le chauffage (17°C la nuit, 19°C le jour)",
            "impact": "haute",
            "difficulte": "moyen",
        },
        {"tip": "Installer un thermostat connecté", "impact": "haute", "difficulte": "moyen"},
    ],
    "💧 Eau": [
        {
            "tip": "Douche de 5 min max = 60L vs 150L pour un bain",
            "impact": "haute",
            "difficulte": "facile",
        },
        {
            "tip": "Installer des mousseurs (40% d'économie d'eau)",
            "impact": "haute",
            "difficulte": "facile",
        },
        {
            "tip": "Récupérer l'eau de pluie pour le jardin",
            "impact": "moyenne",
            "difficulte": "moyen",
        },
        {
            "tip": "Lancer le lave-vaisselle uniquement plein",
            "impact": "moyenne",
            "difficulte": "facile",
        },
        {
            "tip": "Réparer les fuites (10L/jour pour un robinet)",
            "impact": "haute",
            "difficulte": "moyen",
        },
    ],
    "🍽️ Cuisine": [
        {
            "tip": "Couvrir les casseroles (4x plus rapide)",
            "impact": "moyenne",
            "difficulte": "facile",
        },
        {
            "tip": "Décongeler au frigo plutôt qu'au micro-ondes",
            "impact": "basse",
            "difficulte": "facile",
        },
        {
            "tip": "Utiliser une bouilloire vs casserole pour l'eau",
            "impact": "moyenne",
            "difficulte": "facile",
        },
        {
            "tip": "Batch cooking = moins de cuissons par semaine",
            "impact": "moyenne",
            "difficulte": "moyen",
        },
        {"tip": "Composter les déchets organiques", "impact": "haute", "difficulte": "moyen"},
    ],
    "♻️ Déchets": [
        {"tip": "Privilégier les produits en vrac", "impact": "haute", "difficulte": "moyen"},
        {"tip": "Utiliser des sacs réutilisables", "impact": "moyenne", "difficulte": "facile"},
        {
            "tip": "Faire ses produits ménagers (vinaigre + bicarbonate)",
            "impact": "moyenne",
            "difficulte": "moyen",
        },
        {
            "tip": "Donner/vendre plutôt que jeter (Leboncoin, Vinted)",
            "impact": "haute",
            "difficulte": "facile",
        },
        {
            "tip": "Trier rigoureusement (verre, plastique, papier, bio)",
            "impact": "haute",
            "difficulte": "facile",
        },
    ],
    "🌿 Jardin": [
        {"tip": "Arroser tôt le matin ou tard le soir", "impact": "haute", "difficulte": "facile"},
        {"tip": "Pailler pour conserver l'humidité", "impact": "haute", "difficulte": "facile"},
        {
            "tip": "Planter des espèces locales résistantes",
            "impact": "moyenne",
            "difficulte": "moyen",
        },
        {
            "tip": "Installer un récupérateur d'eau de pluie",
            "impact": "haute",
            "difficulte": "moyen",
        },
    ],
}

IMPACT_COLORS = {
    "haute": "#2e7d32",
    "moyenne": "#e65100",
    "basse": "#616161",
}


# ═══════════════════════════════════════════════════════════
# CRUD FONCTIONS
# ═══════════════════════════════════════════════════════════


def get_all_actions(actif_only: bool = False) -> list:
    """Récupère toutes les actions écologiques.

    Args:
        actif_only: Ne retourner que les actions actives.

    Returns:
        Liste d'objets ActionEcologique.
    """
    try:
        from src.core.models import ActionEcologique
    except ImportError:
        # Modèle pas encore créé — utiliser un générique
        ActionEcologique = type("ActionEcologique", (), {"__tablename__": "actions_ecologiques"})

    with obtenir_contexte_db() as db:
        query = db.query(ActionEcologique)
        if actif_only:
            query = query.filter(ActionEcologique.actif == True)  # noqa: E712
        return query.order_by(ActionEcologique.id).all()


def get_action_by_id(action_id: int):
    """Récupère une action par son ID.

    Args:
        action_id: ID de l'action.

    Returns:
        Objet ActionEcologique ou None.
    """
    try:
        from src.core.models import ActionEcologique
    except ImportError:
        ActionEcologique = type("ActionEcologique", (), {"__tablename__": "actions_ecologiques"})

    with obtenir_contexte_db() as db:
        return db.query(ActionEcologique).filter(ActionEcologique.id == action_id).first()


def create_action(data: dict) -> None:
    """Crée une nouvelle action écologique.

    Args:
        data: Dict avec les champs de l'action.
    """
    try:
        from src.core.models import ActionEcologique
    except ImportError:
        ActionEcologique = type("ActionEcologique", (), {"__tablename__": "actions_ecologiques"})

    with obtenir_contexte_db() as db:
        action = ActionEcologique(**data)
        db.add(action)
        db.commit()
        db.refresh(action)


def update_action(action_id: int, data: dict):
    """Met à jour une action existante.

    Args:
        action_id: ID de l'action.
        data: Dict des champs à mettre à jour.

    Returns:
        Objet ActionEcologique mis à jour ou None si non trouvé.
    """
    try:
        from src.core.models import ActionEcologique
    except ImportError:
        ActionEcologique = type("ActionEcologique", (), {"__tablename__": "actions_ecologiques"})

    with obtenir_contexte_db() as db:
        action = db.query(ActionEcologique).filter(ActionEcologique.id == action_id).first()
        if action is None:
            return None
        for key, value in data.items():
            setattr(action, key, value)
        db.commit()
        db.refresh(action)
        return action


def delete_action(action_id: int) -> bool:
    """Supprime une action écologique.

    Args:
        action_id: ID de l'action.

    Returns:
        True si supprimée, False si non trouvée.
    """
    try:
        from src.core.models import ActionEcologique
    except ImportError:
        ActionEcologique = type("ActionEcologique", (), {"__tablename__": "actions_ecologiques"})

    with obtenir_contexte_db() as db:
        action = db.query(ActionEcologique).filter(ActionEcologique.id == action_id).first()
        if action is None:
            return False
        db.delete(action)
        db.commit()
        return True


# ═══════════════════════════════════════════════════════════
# STATISTIQUES
# ═══════════════════════════════════════════════════════════


def calculate_stats() -> dict:
    """Calcule les statistiques des actions écologiques.

    Returns:
        Dict avec nb_actions, economie_mensuelle, economie_annuelle,
        cout_nouveau_initial, roi_mois, economies_totales.
    """
    actions = get_all_actions()

    if not actions:
        return {
            "nb_actions": 0,
            "economie_mensuelle": 0,
            "economie_annuelle": 0,
            "cout_nouveau_initial": 0,
            "roi_mois": 0,
            "economies_totales": 0,
        }

    eco_mensuelle = sum(float(a.economie_mensuelle) for a in actions if a.economie_mensuelle)
    cout_initial = sum(float(a.cout_nouveau_initial) for a in actions if a.cout_nouveau_initial)
    eco_annuelle = eco_mensuelle * 12
    roi_mois = (cout_initial / eco_mensuelle) if eco_mensuelle > 0 else 0

    # Calcul des économies totales (depuis la date de début de chaque action)
    from datetime import date

    economies_totales = 0.0
    for a in actions:
        if a.economie_mensuelle and a.date_debut:
            mois_actifs = max(
                0,
                (date.today().year - a.date_debut.year) * 12
                + (date.today().month - a.date_debut.month),
            )
            economies_totales += float(a.economie_mensuelle) * mois_actifs

    return {
        "nb_actions": len(actions),
        "economie_mensuelle": eco_mensuelle,
        "economie_annuelle": eco_annuelle,
        "cout_nouveau_initial": cout_initial,
        "roi_mois": roi_mois,
        "economies_totales": economies_totales,
    }


# ═══════════════════════════════════════════════════════════
# UI COMPONENTS
# ═══════════════════════════════════════════════════════════


def afficher_stats_dashboard() -> None:
    """Affiche le dashboard de statistiques des éco-actions."""
    st.subheader("📊 Vos économies")
    stats = calculate_stats()
    cols = st.columns(4)
    with cols[0]:
        st.metric("Actions actives", stats["nb_actions"])
    with cols[1]:
        st.metric("Économie/mois", f"{stats['economie_mensuelle']:.0f}€")
    with cols[2]:
        st.metric("Économie/an", f"{stats['economie_annuelle']:.0f}€")
    with cols[3]:
        st.metric("ROI", f"{stats['roi_mois']:.1f} mois")


def afficher_action_card(action) -> None:
    """Affiche une carte pour une action écologique.

    Args:
        action: Objet ActionEcologique.
    """
    type_label = TYPE_LABELS.get(getattr(action, "type_action", ""), "")
    with st.container(border=True):
        cols = st.columns(3)
        with cols[0]:
            st.markdown(f"**{action.nom}**")
            st.caption(type_label)
        with cols[1]:
            eco = getattr(action, "economie_mensuelle", None)
            st.metric("Économie/mois", f"{float(eco):.0f}€" if eco else "—")
        with cols[2]:
            actif = getattr(action, "actif", True)
            new_actif = st.checkbox("Actif", value=actif, key=f"actif_{action.id}")
            if new_actif != actif:
                update_action(action.id, {"actif": new_actif})

        cols2 = st.columns(2)
        with cols2[0]:
            if st.button("✏️ Modifier", key=f"edit_{action.id}"):
                st.session_state[_keys("edit_id")] = action.id
                st.rerun()
        with cols2[1]:
            if st.button("🗑️ Supprimer", key=f"del_{action.id}"):
                delete_action(action.id)
                st.rerun()


def afficher_formulaire(action=None) -> None:
    """Affiche le formulaire de création/édition d'une action.

    Args:
        action: Objet ActionEcologique existant pour édition, ou None pour création.
    """
    from datetime import date as date_type

    with st.form(key=_keys("form_action")):
        nom = st.text_input("Nom", value=getattr(action, "nom", ""))
        type_action = st.selectbox(
            "Type",
            list(TYPE_LABELS.keys()),
            format_func=lambda x: TYPE_LABELS[x],
            index=list(TYPE_LABELS.keys()).index(getattr(action, "type_action", "lavable"))
            if action and hasattr(action, "type_action")
            else 0,
        )
        description = st.text_area("Description", value=getattr(action, "description", ""))
        eco = st.number_input(
            "Économie mensuelle (€)",
            min_value=0.0,
            value=float(getattr(action, "economie_mensuelle", 0) or 0),
        )
        cout = st.number_input(
            "Coût initial (€)",
            min_value=0.0,
            value=float(getattr(action, "cout_nouveau_initial", 0) or 0),
        )

        submitted = st.form_submit_button("💾 Enregistrer", use_container_width=True)

    if submitted and nom:
        data = {
            "nom": nom,
            "type_action": type_action,
            "description": description,
            "economie_mensuelle": Decimal(str(eco)),
            "cout_nouveau_initial": Decimal(str(cout)),
            "date_debut": date_type.today(),
            "actif": True,
        }
        if action:
            update_action(action.id, data)
            st.success("✅ Action mise à jour !")
        else:
            create_action(data)
            st.success("✅ Action créée !")
        st.rerun()


def afficher_idees() -> None:
    """Affiche les idées d'actions prédéfinies."""
    st.subheader("💡 Idées d'actions")
    existantes = get_all_actions()
    noms_existants = {a.nom for a in existantes} if existantes else set()

    cols = st.columns(3)
    for i, idee in enumerate(IDEES_ACTIONS):
        with cols[i % 3]:
            with st.container(border=True):
                st.markdown(f"**{idee['nom']}**")
                st.caption(idee["description"])
                st.caption(f"💰 ~{idee['economie_estimee']:.0f}€/mois")
                if idee["nom"] not in noms_existants:
                    if st.button("➕ Adopter", key=f"adopt_{i}"):
                        create_action(
                            {
                                "nom": idee["nom"],
                                "type_action": idee["type"],
                                "description": idee["description"],
                                "economie_mensuelle": Decimal(str(idee["economie_estimee"])),
                                "cout_nouveau_initial": Decimal(str(idee["cout_nouveau_initial"])),
                                "actif": True,
                            }
                        )
                        st.rerun()
                else:
                    st.success("✅ Déjà adoptée")


def afficher_onglet_mes_actions() -> None:
    """Affiche l'onglet 'Mes actions'."""
    actions = get_all_actions()
    if not actions:
        st.info("Aucune action éco-responsable. Ajoutez-en une ou consultez les idées !")
        return

    filtre = st.radio("Filtrer", ["Toutes", "Actives", "Inactives"], horizontal=True)

    for action in actions:
        if filtre == "Actives" and not action.actif:
            continue
        if filtre == "Inactives" and action.actif:
            continue
        afficher_action_card(action)


def afficher_onglet_ajouter() -> None:
    """Affiche l'onglet 'Ajouter une action'."""
    st.subheader("➕ Nouvelle action")
    afficher_formulaire(None)


def app():
    """Point d'entrée du module Éco-Tips."""
    st.title("💡 Éco-Tips")
    st.caption("Adoptez des gestes simples pour réduire votre impact et vos factures.")

    # Mode édition
    edit_id = st.session_state.get(_keys("edit_id"))
    if edit_id:
        action = get_action_by_id(edit_id)
        if action:
            st.subheader(f"✏️ Modifier : {action.nom}")
            afficher_formulaire(action)
            if st.button("← Annuler"):
                del st.session_state[_keys("edit_id")]
                st.rerun()
            return
        else:
            # Action non trouvée — continuer normalement
            del st.session_state[_keys("edit_id")]

    # Dashboard stats
    afficher_stats_dashboard()
    st.divider()

    # Onglets
    TAB_LABELS = [
        "📋 Mes actions",
        "➕ Ajouter",
        "💡 Idées",
    ]
    tab1, tab2, tab3 = st.tabs(TAB_LABELS)

    with tab1:
        afficher_onglet_mes_actions()

    with tab2:
        afficher_onglet_ajouter()

    with tab3:
        afficher_idees()


def _onglet_tips():
    """Affiche tous les éco-tips par catégorie."""
    # Filtre de difficulté
    filtre = st.selectbox(
        "Filtrer par difficulté",
        ["Tous", "facile", "moyen"],
        key=_keys("filtre_difficulte"),
    )

    for categorie, tips in ECO_TIPS_DATA.items():
        with st.expander(f"{categorie} ({len(tips)} tips)", expanded=True):
            for tip in tips:
                if filtre != "Tous" and tip["difficulte"] != filtre:
                    continue

                impact_color = IMPACT_COLORS.get(tip["impact"], "#616161")
                col1, col2, col3 = st.columns([5, 1, 1])
                with col1:
                    st.markdown(f"• {tip['tip']}")
                with col2:
                    st.markdown(
                        f'<span style="color: {impact_color}; font-weight: 600; font-size: 0.8rem;">'
                        f"{tip['impact']}</span>",
                        unsafe_allow_html=True,
                    )
                with col3:
                    st.caption(tip["difficulte"])


def _onglet_eco_score():
    """Calcule un éco-score basé sur les habitudes du foyer."""
    st.subheader("📊 Votre éco-score")
    st.caption("Répondez à ces questions pour évaluer vos pratiques écologiques.")

    with st.form(key=_keys("form_eco_score")):
        score = 0

        st.markdown("**🔌 Énergie**")
        if st.checkbox("J'éteins les appareils en veille", key=_keys("veille")):
            score += 10
        if st.checkbox("J'utilise des LED", key=_keys("led")):
            score += 10
        if st.checkbox("Mon chauffage est programmé", key=_keys("chauffage")):
            score += 15

        st.markdown("**💧 Eau**")
        if st.checkbox("Douches courtes (< 5 min)", key=_keys("douche")):
            score += 10
        if st.checkbox("Mousseurs installés", key=_keys("mousseur")):
            score += 10

        st.markdown("**♻️ Déchets**")
        if st.checkbox("Je trie mes déchets", key=_keys("tri")):
            score += 10
        if st.checkbox("Je composte", key=_keys("compost")):
            score += 15
        if st.checkbox("J'achète en vrac", key=_keys("vrac")):
            score += 10

        st.markdown("**🍽️ Cuisine**")
        if st.checkbox("Je pratique le batch cooking", key=_keys("batch")):
            score += 10

        submitted = st.form_submit_button("📊 Calculer mon score", use_container_width=True)

    if submitted:
        st.divider()
        pct = score

        if pct >= 80:
            emoji, label, color = "🌟", "Excellent !", "#2e7d32"
        elif pct >= 60:
            emoji, label, color = "👍", "Bien !", "#1565c0"
        elif pct >= 40:
            emoji, label, color = "🔧", "Peut mieux faire", "#e65100"
        else:
            emoji, label, color = "⚠️", "À améliorer", "#c62828"

        st.markdown(
            f'<div style="text-align:center; padding:1.5rem; border-radius:10px; '
            f'background: linear-gradient(135deg, {color}22 0%, {color}11 100%);">'
            f'<h1 style="color: {color};">{emoji} {pct}/100</h1>'
            f'<p style="font-size: 1.2rem; color: {color};">{label}</p></div>',
            unsafe_allow_html=True,
        )

        if pct < 80:
            st.info("💡 Consultez l'onglet 'Tous les tips' pour découvrir de nouveaux éco-gestes !")


def _onglet_conseils_ia():
    """Conseils personnalisés par l'IA."""
    st.subheader("🤖 Conseils IA personnalisés")
    st.caption("Décrivez votre situation pour recevoir des conseils adaptés.")

    situation = st.text_area(
        "Décrivez votre logement et vos habitudes",
        placeholder="ex: Appartement 60m², 2 personnes + 1 bébé, chauffage gaz, "
        "pas encore de compost, machine à laver tous les jours...",
        key=_keys("situation"),
    )

    if st.button("🤖 Obtenir des conseils", key=_keys("btn_conseils"), use_container_width=True):
        if not situation:
            st.warning("Veuillez décrire votre situation d'abord.")
            return

        try:
            from src.core.ai import obtenir_client_ia

            client = obtenir_client_ia()

            with st.spinner("🤖 Analyse de votre situation..."):
                import asyncio

                prompt = (
                    f"Analyse cette situation de foyer et donne 5-7 conseils écologiques "
                    f"concrets et personnalisés, classés par impact:\n\n{situation}\n\n"
                    f"Pour chaque conseil, indique l'économie potentielle en €/an."
                )

                response = asyncio.run(
                    client.generer(
                        prompt=prompt,
                        system_prompt="Tu es un expert en transition écologique et économies "
                        "d'énergie domestique en France.",
                        max_tokens=800,
                    )
                )

                st.markdown("---")
                st.markdown(response)

        except Exception as e:
            st.warning(f"Service IA indisponible: {e}")
            st.info("En attendant, consultez nos éco-tips dans l'onglet principal !")
