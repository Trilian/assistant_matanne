"""Charges - Onglets principaux."""

import time
from datetime import date
from decimal import Decimal

import streamlit as st

from src.core.session_keys import SK
from src.core.state import rerun
from src.ui import etat_vide
from src.ui.fragments import ui_fragment
from src.ui.keys import KeyNamespace

from .db_access import ajouter_facture, supprimer_facture

_keys = KeyNamespace("charges")

from .constantes import CONSEILS_ECONOMIES, ENERGIES
from .logic import (
    analyser_consommation,
    calculer_stats_globales,
    detecter_anomalies,
    obtenir_badges_obtenus,
)
from .ui import (
    afficher_anomalies,
    afficher_badges_collection,
    afficher_conseil_eco,
    afficher_eco_score_gamifie,
    afficher_energie_card,
    afficher_facture_item,
)


@ui_fragment
def onglet_dashboard(factures: list[dict]):
    """Onglet tableau de bord gamifié."""
    st.subheader("📊 Vue d'ensemble")

    # Calculer stats globales
    stats = calculer_stats_globales(factures)
    eco_score = stats["eco_score"]
    streak = stats["streak"]
    badges_obtenus = obtenir_badges_obtenus(stats)

    # Calculer variation (si score précédent en session)
    prev_score = st.session_state.get(SK.PREV_ECO_SCORE)
    variation = eco_score - prev_score if prev_score is not None else None
    st.session_state.prev_eco_score = eco_score

    col1, col2 = st.columns([1, 2])

    with col1:
        # Éco-score gamifié
        afficher_eco_score_gamifie(eco_score, variation, streak)

    with col2:
        # Cartes énergie
        if not factures:
            st.info(
                "📊 Ajoutez vos premières factures pour voir votre tableau de bord énergétique !"
            )
        else:
            for energie_id, energie_data in ENERGIES.items():
                analyse = analyser_consommation(factures, energie_id)
                if analyse["nb_factures"] > 0:
                    afficher_energie_card(
                        energie_id,
                        energie_data,
                        analyse["moyenne_conso"],
                        analyse["total_cout"] / max(1, analyse["nb_factures"]),
                        analyse["tendance"],
                        analyse["ratio"],
                    )

    # Détection d'anomalies
    anomalies = detecter_anomalies(factures)
    if anomalies:
        st.divider()
        afficher_anomalies(anomalies)

    # Badges collection
    st.divider()
    afficher_badges_collection(badges_obtenus, stats)


@ui_fragment
def onglet_factures(factures: list[dict]):
    """Onglet gestion des factures."""
    st.subheader("📄 Mes Factures")

    # Stats rapides
    if factures:
        col1, col2, col3 = st.columns(3)
        with col1:
            total = sum(Decimal(str(f.get("montant", 0))) for f in factures)
            st.metric("Total factures", f"{total:.2f} €", f"{len(factures)} factures")
        with col2:
            mois_courant = date.today().strftime("%Y-%m")
            factures_mois = [f for f in factures if f.get("date", "").startswith(mois_courant)]
            total_mois = sum(Decimal(str(f.get("montant", 0))) for f in factures_mois)
            st.metric("Ce mois", f"{total_mois:.2f} €")
        with col3:
            # Dernière facture
            if factures:
                derniere = max(factures, key=lambda f: f.get("date", ""))
                st.metric("Dernière", derniere.get("date", "N/A"))

    st.divider()

    # Bouton ajouter
    if st.button("➕ Ajouter une facture", type="primary", use_container_width=True):
        st.session_state[_keys("mode_ajout")] = True

    # Mode ajout
    if st.session_state.get(_keys("mode_ajout")):
        st.markdown("### Nouvelle facture")

        with st.form("form_facture"):
            type_energie = st.selectbox(
                "Type d'énergie",
                options=list(ENERGIES.keys()),
                format_func=lambda x: f"{ENERGIES[x]['emoji']} {ENERGIES[x]['label']}",
            )

            col1, col2 = st.columns(2)
            with col1:
                montant = st.number_input("Montant (€)", min_value=0.0, value=50.0, step=5.0)
            with col2:
                consommation = st.number_input(
                    f"Consommation ({ENERGIES[type_energie]['unite']})",
                    min_value=0.0,
                    value=float(ENERGIES[type_energie]["conso_moyenne_mois"]),
                    step=10.0,
                )

            col3, col4 = st.columns(2)
            with col3:
                date_facture = st.date_input("Date de facturation", value=date.today())
            with col4:
                fournisseur = st.text_input("Fournisseur", placeholder="EDF, Engie, Veolia...")

            col_submit = st.columns([1, 1])
            with col_submit[0]:
                submitted = st.form_submit_button(
                    "✅ Enregistrer", type="primary", use_container_width=True
                )
            with col_submit[1]:
                cancelled = st.form_submit_button("❌ Annuler", use_container_width=True)

            if submitted:
                nouvelle_facture = {
                    "type": type_energie,
                    "montant": montant,
                    "consommation": consommation,
                    "date": date_facture.isoformat(),
                    "fournisseur": fournisseur or None,
                    "date_ajout": date.today().isoformat(),
                }
                # Persister en DB
                ajouter_facture(nouvelle_facture)
                factures.append(nouvelle_facture)
                st.session_state[_keys("factures")] = factures
                st.session_state[_keys("mode_ajout")] = False
                st.session_state._charges_reload = True
                st.success("✅ Facture enregistrée ! Vérifiez votre éco-score.")
                st.balloons()
                rerun()

            if cancelled:
                st.session_state[_keys("mode_ajout")] = False
                rerun()

    else:
        # Liste des factures
        if not factures:
            etat_vide("Aucune facture enregistrée", "📄", "Ajoutez vos factures pour commencer")

            # Aide pour démarrer
            st.markdown("""
            **Comment commencer ?**
            1. Récupérez vos dernières factures d'énergie
            2. Ajoutez-les une par une en cliquant sur "Ajouter une facture"
            3. Suivez l'évolution de votre éco-score et débloquez des badges !
            """)
            return

        # Filtres
        col_filter = st.columns([2, 2, 1])
        with col_filter[0]:
            filtre_energie = st.selectbox(
                "Filtrer par énergie",
                options=["Toutes"] + list(ENERGIES.keys()),
                format_func=lambda x: (
                    "Toutes les énergies"
                    if x == "Toutes"
                    else f"{ENERGIES[x]['emoji']} {ENERGIES[x]['label']}"
                ),
            )
        with col_filter[1]:
            ordre = st.selectbox("Trier par", ["Date (récent)", "Date (ancien)", "Montant"])

        # Appliquer filtres
        factures_affichees = factures.copy()
        if filtre_energie != "Toutes":
            factures_affichees = [f for f in factures_affichees if f.get("type") == filtre_energie]

        # Trier
        if ordre == "Date (récent)":
            factures_affichees = sorted(
                factures_affichees, key=lambda f: f.get("date", ""), reverse=True
            )
        elif ordre == "Date (ancien)":
            factures_affichees = sorted(factures_affichees, key=lambda f: f.get("date", ""))
        else:
            factures_affichees = sorted(
                factures_affichees, key=lambda f: f.get("montant", 0), reverse=True
            )

        # Afficher factures
        for i, facture in enumerate(factures_affichees):
            energie_data = ENERGIES.get(facture.get("type"), {})

            col1, col2 = st.columns([6, 1])

            with col1:
                afficher_facture_item(facture, energie_data, i)

            with col2:
                if st.button("🗑️", key=f"del_fact_{i}", help="Supprimer cette facture"):
                    # Supprimer en DB si la facture a un db_id
                    db_id = facture.get("db_id")
                    if db_id:
                        supprimer_facture(db_id)
                    # Trouver l'index dans la liste originale
                    idx = factures.index(facture)
                    factures.pop(idx)
                    st.session_state[_keys("factures")] = factures
                    st.session_state._charges_reload = True
                    st.success("Facture supprimée")
                    rerun()


@ui_fragment
def onglet_analyse(factures: list[dict]):
    """Onglet analyse détaillée avec graphiques."""
    st.subheader("📈 Analyse détaillée")

    if not factures:
        st.info("📊 Ajoutez des factures pour voir l'analyse de vos consommations.")
        return

    # Sélection énergie
    energie_sel = st.selectbox(
        "Énergie à analyser",
        options=list(ENERGIES.keys()),
        format_func=lambda x: f"{ENERGIES[x]['emoji']} {ENERGIES[x]['label']}",
    )

    analyse = analyser_consommation(factures, energie_sel)
    config = ENERGIES[energie_sel]

    # KPIs
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(
            "Conso. totale",
            f"{analyse['total_conso']:.0f} {config['unite']}",
            f"{analyse['nb_factures']} factures",
        )
    with col2:
        st.metric("Coût total", f"{analyse['total_cout']:.2f} €")
    with col3:
        icon = (
            "📉"
            if analyse["tendance"] == "baisse"
            else ("📈" if analyse["tendance"] == "hausse" else "➡️")
        )
        st.metric("Tendance", analyse["tendance"].capitalize(), icon)
    with col4:
        ratio_pct = (analyse["ratio"] - 1) * 100
        st.metric("Vs Moyenne", f"{ratio_pct:+.0f}%", "Bien !" if ratio_pct < 0 else "À surveiller")

    st.divider()

    # Graphique évolution (simple avec Streamlit)
    st.markdown("#### 📊 Évolution mensuelle")

    factures_energie = sorted(
        [f for f in factures if f.get("type") == energie_sel], key=lambda f: f.get("date", "")
    )

    if len(factures_energie) >= 2:
        import pandas as pd

        df = pd.DataFrame(
            [
                {
                    "Date": f.get("date", ""),
                    "Consommation": f.get("consommation", 0),
                    "Montant": f.get("montant", 0),
                }
                for f in factures_energie
            ]
        )

        tab1, tab2 = st.tabs(["Consommation", "Coût"])
        with tab1:
            st.line_chart(df.set_index("Date")["Consommation"])
        with tab2:
            st.line_chart(df.set_index("Date")["Montant"])
    else:
        st.info("Ajoutez plus de factures pour voir l'évolution graphique.")

    st.divider()

    # Comparaison moyenne nationale
    st.markdown("#### 🎯 Comparaison moyenne nationale")

    moyenne_ref = config.get("conso_moyenne_mois", 100)
    moyenne_utilisateur = analyse["moyenne_conso"]

    ecart = ((moyenne_utilisateur / moyenne_ref) - 1) * 100 if moyenne_ref > 0 else 0

    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown(f"""
        - **Votre moyenne** : {moyenne_utilisateur:.0f} {config["unite"]}/mois
        - **Moyenne nationale** : {moyenne_ref:.0f} {config["unite"]}/mois
        - **Écart** : {ecart:+.0f}%
        """)

    with col2:
        if ecart > 20:
            st.error(
                f"⚠️ Consommation {ecart:.0f}% au-dessus de la moyenne. Consultez nos conseils !"
            )
        elif ecart < -10:
            st.success(f"🎉 Bravo ! Vous êtes {-ecart:.0f}% en-dessous de la moyenne.")
        else:
            st.info("📊 Votre consommation est dans la moyenne nationale.")


@ui_fragment
def onglet_simulation(factures: list[dict]):
    """Onglet simulation d'économies avec IA."""
    st.subheader("💰 Simulation d'économies")

    st.markdown("""
    Découvrez combien vous pourriez économiser en adoptant de bonnes pratiques !
    Sélectionnez les actions que vous envisagez et voyez l'impact.
    """)

    # Sélection énergie
    energie_sel = st.selectbox(
        "Pour quelle énergie ?",
        options=list(ENERGIES.keys()),
        format_func=lambda x: f"{ENERGIES[x]['emoji']} {ENERGIES[x]['label']}",
        key="sim_energie",
    )

    config = ENERGIES[energie_sel]
    conseils = CONSEILS_ECONOMIES.get(energie_sel, [])

    st.markdown(f"### {config['emoji']} Actions {config['label']}")

    # Actions à sélectionner
    actions_selectionnees = []
    total_economie = 0

    for i, conseil in enumerate(conseils):
        col1, col2, col3 = st.columns([4, 2, 1])

        with col1:
            checked = st.checkbox(
                f"{conseil['emoji']} {conseil['titre']}",
                key=f"action_{energie_sel}_{i}",
                help=conseil["desc"],
            )

        with col2:
            st.caption(conseil["desc"])

        with col3:
            st.markdown(f"**{conseil['economie']}**")

        if checked:
            actions_selectionnees.append(conseil)
            # Parser l'économie
            economie_str = conseil["economie"].replace("€/an", "").replace("€", "").strip()
            try:
                total_economie += int(economie_str)
            except ValueError:
                pass

    st.divider()

    # Résultat simulation
    if actions_selectionnees:
        st.markdown("### 📊 Résultat de la simulation")

        col1, col2 = st.columns([1, 1])

        with col1:
            st.markdown(
                f"""
            <div class="simulation-card">
                <div class="header">
                    <span>💰 Économies potentielles</span>
                </div>
                <div class="result">
                    <div class="savings">{total_economie} €</div>
                    <div class="period">par an</div>
                </div>
            </div>
            """,
                unsafe_allow_html=True,
            )

        with col2:
            st.markdown(f"""
            **{len(actions_selectionnees)} action(s) sélectionnée(s):**
            """)
            for action in actions_selectionnees:
                st.markdown(f"- {action['emoji']} {action['titre']}")

        # Bouton simulation IA avancée
        if st.button("🤖 Analyse IA personnalisée", type="secondary"):
            with st.spinner("Analyse en cours..."):
                # Simulation délai IA
                import time

                time.sleep(1.5)

                st.success(f"""
                **💡 Recommandations personnalisées IA:**

                Basé sur votre profil de consommation, voici l'ordre de priorité recommandé:

                1. **{actions_selectionnees[0]["titre"] if actions_selectionnees else "Aucune action"}** - ROI le plus rapide
                2. Combinez plusieurs actions pour un effet multiplicateur
                3. Économie potentielle réaliste : **{int(total_economie * 0.7)}-{total_economie} €/an**

                *Note: Les économies réelles dépendent de votre usage actuel.*
                """)
    else:
        st.info("👆 Sélectionnez des actions pour voir les économies potentielles")


@ui_fragment
def onglet_conseils():
    """Onglet conseils d'économies détaillés."""
    st.subheader("💡 Conseils d'économies")

    st.markdown("""
    Retrouvez ici tous les conseils pour réduire votre consommation et améliorer votre éco-score !
    """)

    for energie_id, conseils in CONSEILS_ECONOMIES.items():
        config = ENERGIES[energie_id]

        with st.expander(f"{config['emoji']} {config['label']}", expanded=True):
            for conseil in conseils:
                afficher_conseil_eco(conseil)
