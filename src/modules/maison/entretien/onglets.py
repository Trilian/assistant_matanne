"""Entretien - Onglets principaux."""

import logging
from datetime import date, datetime, timedelta

import streamlit as st

from .data import charger_catalogue_entretien
from .logic import (
    calculer_score_proprete,
    calculer_stats_globales,
    calculer_streak,
    generer_alertes_predictives,
    generer_planning_previsionnel,
    generer_taches_entretien,
    obtenir_badges_obtenus,
)
from .ui import afficher_alertes_predictives as ui_alertes_predictives
from .ui import (
    afficher_badges_entretien,
    afficher_piece_card,
    afficher_score_gamifie,
    afficher_stats_rapides,
    afficher_tache_entretien,
    afficher_timeline_item,
)

# Import optionnel Plotly
try:
    import plotly.express as px
    import plotly.graph_objects as go

    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False

# Import pandas pour export
try:
    import pandas as pd

    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False

logger = logging.getLogger(__name__)


def onglet_taches(mes_objets: list[dict], historique: list[dict]):
    """Onglet des tâches automatiques."""
    st.subheader("🎯 Tâches d'entretien")

    taches = generer_taches_entretien(mes_objets, historique)

    if not taches:
        st.success("✨ **Maison impeccable !** Tout est à jour.")
        st.info(
            "Les tâches apparaissent automatiquement selon vos équipements et leur calendrier d'entretien."
        )
        return

    # Stats rapides
    afficher_stats_rapides(taches)

    # Filtres
    col1, col2 = st.columns(2)
    with col1:
        filtre_piece = st.selectbox(
            "Filtrer par pièce",
            ["Toutes"] + list(set(t.get("piece", "") for t in taches if t.get("piece"))),
        )
    with col2:
        filtre_priorite = st.selectbox(
            "Filtrer par priorité", ["Toutes", "Urgente", "Haute", "Moyenne"]
        )

    # Appliquer filtres
    taches_filtrees = taches
    if filtre_piece != "Toutes":
        taches_filtrees = [t for t in taches_filtrees if t.get("piece") == filtre_piece]
    if filtre_priorite != "Toutes":
        taches_filtrees = [
            t for t in taches_filtrees if t.get("priorite") == filtre_priorite.lower()
        ]

    st.divider()

    # Afficher les tâches groupées par catégorie
    categories = {}
    for t in taches_filtrees:
        cat = t.get("categorie_id", "divers")
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(t)

    catalogue = charger_catalogue_entretien()

    for cat_id, cat_taches in categories.items():
        cat_data = catalogue.get("categories", {}).get(cat_id, {})

        st.markdown(
            f"""
        <div class="categorie-header">
            <span class="icon">{cat_data.get('icon', '📦')}</span>
            <span class="title">{cat_id.replace('_', ' ').capitalize()} ({len(cat_taches)})</span>
        </div>
        """,
            unsafe_allow_html=True,
        )

        for i, tache in enumerate(cat_taches):
            done = afficher_tache_entretien(tache, f"{cat_id}_{i}")
            if done:
                # Enregistrer dans l'historique
                nouvelle_entree = {
                    "objet_id": tache.get("objet_id"),
                    "tache_nom": tache.get("tache_nom"),
                    "date": date.today().isoformat(),
                }
                historique.append(nouvelle_entree)
                st.session_state.historique_entretien = historique
                st.toast(f"✅ {tache['tache_nom']} accompli !")
                st.rerun()


def onglet_inventaire(mes_objets: list[dict]):
    """Onglet de gestion de l'inventaire."""
    st.subheader("📦 Mon Inventaire")

    catalogue = charger_catalogue_entretien()

    # Bouton ajouter
    if st.button("➕ Ajouter un équipement", type="primary", use_container_width=True):
        st.session_state.entretien_mode_ajout = True

    # Mode ajout
    if st.session_state.get("entretien_mode_ajout"):
        st.markdown("### Ajouter un nouvel équipement")

        with st.form("form_ajout_objet"):
            # Sélection catégorie
            categories = catalogue.get("categories", {})
            cat_options = {
                k: f"{v.get('icon', '📦')} {k.replace('_', ' ').capitalize()}"
                for k, v in categories.items()
            }
            categorie_sel = st.selectbox(
                "Catégorie", options=list(cat_options.keys()), format_func=lambda x: cat_options[x]
            )

            # Sélection objet
            objets_cat = categories.get(categorie_sel, {}).get("objets", {})
            obj_options = {k: v.get("nom", k) for k, v in objets_cat.items()}
            objet_sel = st.selectbox(
                "Type d'équipement",
                options=list(obj_options.keys()),
                format_func=lambda x: obj_options[x],
            )

            # Sélection pièce
            pieces = catalogue.get("pieces_type", {})
            piece_options = {
                k: f"{v.get('icon', '🏠')} {v.get('nom', k)}" for k, v in pieces.items()
            }
            piece_sel = st.selectbox(
                "Pièce", options=list(piece_options.keys()), format_func=lambda x: piece_options[x]
            )

            # Détails optionnels
            col1, col2 = st.columns(2)
            with col1:
                nom_perso = st.text_input(
                    "Nom personnalisé (optionnel)", placeholder="Ex: Frigo cuisine principale"
                )
            with col2:
                date_achat = st.date_input("Date d'achat (optionnel)", value=None)

            marque = st.text_input("Marque/Modèle (optionnel)")

            if st.form_submit_button("✅ Ajouter", type="primary"):
                nouvel_objet = {
                    "objet_id": objet_sel,
                    "categorie_id": categorie_sel,
                    "piece": piece_options[piece_sel].split(" ", 1)[-1] if piece_sel else "",
                    "piece_id": piece_sel,
                    "nom_perso": nom_perso or None,
                    "date_achat": date_achat.isoformat() if date_achat else None,
                    "marque": marque or None,
                    "date_ajout": date.today().isoformat(),
                }
                mes_objets.append(nouvel_objet)
                st.session_state.mes_objets_entretien = mes_objets
                st.session_state.entretien_mode_ajout = False
                st.success(f"✅ {obj_options[objet_sel]} ajouté !")
                st.rerun()

        if st.button("❌ Annuler"):
            st.session_state.entretien_mode_ajout = False
            st.rerun()

    else:
        # Afficher l'inventaire existant
        if not mes_objets:
            st.info(
                "📦 Votre inventaire est vide. Ajoutez vos équipements pour générer automatiquement les tâches d'entretien."
            )

            # Suggestion rapide
            st.markdown("### 💡 Ajout rapide par pièce")

            pieces = catalogue.get("pieces_type", {})
            cols = st.columns(3)

            for i, (piece_id, piece_data) in enumerate(pieces.items()):
                with cols[i % 3]:
                    if st.button(
                        f"{piece_data.get('icon', '🏠')} {piece_data.get('nom', piece_id)}",
                        key=f"quick_{piece_id}",
                        use_container_width=True,
                    ):
                        # Ajouter les objets courants de cette pièce
                        objets_courants = piece_data.get("objets_courants", [])
                        for obj_id in objets_courants:
                            # Trouver la catégorie de l'objet
                            for cat_id, cat_data in catalogue.get("categories", {}).items():
                                if obj_id in cat_data.get("objets", {}):
                                    mes_objets.append(
                                        {
                                            "objet_id": obj_id,
                                            "categorie_id": cat_id,
                                            "piece": piece_data.get("nom", piece_id),
                                            "piece_id": piece_id,
                                            "date_ajout": date.today().isoformat(),
                                        }
                                    )
                                    break

                        st.session_state.mes_objets_entretien = mes_objets
                        st.success(
                            f"✅ {len(objets_courants)} équipements ajoutés pour {piece_data.get('nom')} !"
                        )
                        st.rerun()
            return

        # Grouper par pièce
        par_piece = {}
        for obj in mes_objets:
            piece = obj.get("piece", "Non assigné")
            if piece not in par_piece:
                par_piece[piece] = []
            par_piece[piece].append(obj)

        for piece, objets in par_piece.items():
            with st.expander(f"🏠 **{piece}** ({len(objets)} équipements)", expanded=True):
                for i, obj in enumerate(objets):
                    objet_data = None
                    for cat_data in catalogue.get("categories", {}).values():
                        if obj["objet_id"] in cat_data.get("objets", {}):
                            objet_data = cat_data["objets"][obj["objet_id"]]
                            break

                    nom = obj.get("nom_perso") or (
                        objet_data.get("nom") if objet_data else obj["objet_id"]
                    )
                    nb_taches = len(objet_data.get("taches", [])) if objet_data else 0

                    col1, col2 = st.columns([5, 1])
                    with col1:
                        st.markdown(
                            f"""
                        <div class="objet-inventaire">
                            <div class="icon">{catalogue.get("categories", {}).get(obj.get("categorie_id"), {}).get("icon", "📦")}</div>
                            <div class="info">
                                <div class="nom">{nom}</div>
                                <div class="piece">{obj.get("marque", "") or "Marque non renseignée"}</div>
                            </div>
                            <div class="stats">
                                <div class="taches-count">{nb_taches} tâches auto</div>
                            </div>
                        </div>
                        """,
                            unsafe_allow_html=True,
                        )

                    with col2:
                        if st.button("🗑️", key=f"del_obj_{piece}_{i}", help="Supprimer"):
                            # Trouver et supprimer l'objet
                            idx = mes_objets.index(obj)
                            mes_objets.pop(idx)
                            st.session_state.mes_objets_entretien = mes_objets
                            st.rerun()


def onglet_pieces(mes_objets: list[dict], historique: list[dict]):
    """Onglet vue par pièces."""
    st.subheader("🏠 Vue par pièces")

    catalogue = charger_catalogue_entretien()
    taches = generer_taches_entretien(mes_objets, historique)

    # Compter les tâches par pièce
    taches_par_piece = {}
    for t in taches:
        piece = t.get("piece", "Non assigné")
        if piece not in taches_par_piece:
            taches_par_piece[piece] = 0
        taches_par_piece[piece] += 1

    # Grille des pièces
    pieces = catalogue.get("pieces_type", {})

    cols = st.columns(4)
    for i, (piece_id, piece_data) in enumerate(pieces.items()):
        piece_nom = piece_data.get("nom", piece_id)
        nb_taches = taches_par_piece.get(piece_nom, 0)

        with cols[i % 4]:
            # Card cliquable
            afficher_piece_card(piece_id, piece_data, nb_taches)

            if st.button("Voir", key=f"voir_{piece_id}", use_container_width=True):
                st.session_state.piece_selectionnee = piece_nom

    # Détail d'une pièce sélectionnée
    if st.session_state.get("piece_selectionnee"):
        piece = st.session_state.piece_selectionnee

        st.divider()
        st.markdown(f"### 📍 {piece}")

        # Tâches de cette pièce
        taches_piece = [t for t in taches if t.get("piece") == piece]

        if taches_piece:
            for i, tache in enumerate(taches_piece):
                done = afficher_tache_entretien(tache, f"piece_{i}")
                if done:
                    historique.append(
                        {
                            "objet_id": tache.get("objet_id"),
                            "tache_nom": tache.get("tache_nom"),
                            "date": date.today().isoformat(),
                        }
                    )
                    st.session_state.historique_entretien = historique
                    st.toast(f"✅ {tache['tache_nom']} accompli !")
                    st.rerun()
        else:
            st.success(f"✨ Tout est à jour dans {piece} !")

        if st.button("← Retour"):
            del st.session_state.piece_selectionnee
            st.rerun()


def onglet_historique(historique: list[dict]):
    """Onglet historique des entretiens."""
    st.subheader("📜 Historique")

    if not historique:
        st.info(
            "L'historique apparaîtra ici une fois que vous aurez effectué des tâches d'entretien."
        )
        return

    catalogue = charger_catalogue_entretien()

    # Trier par date décroissante
    historique_trie = sorted(historique, key=lambda h: h.get("date", ""), reverse=True)

    # Stats rapides
    total_taches = len(historique_trie)
    derniere_semaine = len(
        [
            h
            for h in historique_trie
            if h.get("date", "") >= (date.today() - timedelta(days=7)).isoformat()
        ]
    )

    col1, col2 = st.columns(2)
    col1.metric("Total accompli", total_taches)
    col2.metric("Cette semaine", derniere_semaine)

    st.divider()

    # Timeline
    st.markdown("### Timeline")

    date_courante = None
    for h in historique_trie[:50]:  # Limiter à 50 entrées
        h_date = h.get("date", "")

        # Séparer par jour
        if h_date != date_courante:
            date_courante = h_date
            try:
                d = datetime.fromisoformat(h_date).date()
                if d == date.today():
                    label_date = "Aujourd'hui"
                elif d == date.today() - timedelta(days=1):
                    label_date = "Hier"
                else:
                    label_date = d.strftime("%d/%m/%Y")
            except Exception:
                label_date = h_date

            st.markdown(f"**{label_date}**")

        afficher_timeline_item(h, catalogue)


def onglet_stats(mes_objets: list[dict], historique: list[dict]):
    """Onglet statistiques détaillées avec gamification."""
    st.subheader("📊 Statistiques & Badges")

    score = calculer_score_proprete(mes_objets, historique)
    streak = calculer_streak(historique)
    stats = calculer_stats_globales(mes_objets, historique)
    badges_obtenus = obtenir_badges_obtenus(stats)

    col1, col2 = st.columns([1, 2])

    with col1:
        afficher_score_gamifie(score, streak)

    with col2:
        # Stats rapides
        st.markdown("### 📈 Vos performances")
        m1, m2, m3 = st.columns(3)
        m1.metric(
            "Tâches accomplies", stats["taches_accomplies"], help="Total des entretiens effectués"
        )
        m2.metric("Équipements", stats["nb_objets"], help="Nombre d'appareils enregistrés")
        m3.metric(
            "Streak actuel",
            f"{streak}j 🔥" if streak > 0 else "0j",
            help="Jours consécutifs d'entretien",
        )

        # Alertes
        alertes = generer_alertes_predictives(mes_objets, historique)
        if alertes:
            ui_alertes_predictives(alertes)

    st.divider()

    # Badges collection
    afficher_badges_entretien(badges_obtenus, stats)

    st.divider()

    # Stats par catégorie
    st.markdown("### 📦 Par catégorie d'équipement")

    catalogue = charger_catalogue_entretien()
    taches = generer_taches_entretien(mes_objets, historique)

    # Compter par catégorie
    par_cat = {}
    for obj in mes_objets:
        cat = obj.get("categorie_id", "divers")
        if cat not in par_cat:
            par_cat[cat] = {"objets": 0, "taches": 0}
        par_cat[cat]["objets"] += 1

    for t in taches:
        cat = t.get("categorie_id", "divers")
        if cat in par_cat:
            par_cat[cat]["taches"] += 1

    cols = st.columns(3)
    for i, (cat_id, data) in enumerate(par_cat.items()):
        cat_data = catalogue.get("categories", {}).get(cat_id, {})
        with cols[i % 3]:
            st.markdown(
                f"""
            <div class="entretien-card">
                <div style="font-size: 2rem; margin-bottom: 0.5rem">{cat_data.get('icon', '📦')}</div>
                <div style="font-weight: 600">{cat_id.replace('_', ' ').capitalize()}</div>
                <div style="font-size: 0.85rem; color: #718096">
                    {data['objets']} équipements • {data['taches']} tâches en attente
                </div>
            </div>
            """,
                unsafe_allow_html=True,
            )


def onglet_graphiques(mes_objets: list[dict], historique: list[dict]):
    """Onglet graphiques Plotly avec visualisations interactives."""
    st.subheader("📈 Graphiques & Analyses")

    if not HAS_PLOTLY:
        st.warning("📦 Plotly non installé. `pip install plotly` pour les graphiques interactifs.")
        return

    if not historique:
        st.info("📊 Les graphiques apparaîtront avec vos premières tâches accomplies.")
        return

    # Tab internes pour différents graphiques
    g1, g2, g3 = st.tabs(["📅 Évolution", "🗂️ Répartition", "📊 Planning"])

    with g1:
        # Graphique évolution des tâches dans le temps
        st.markdown("### Évolution des entretiens")

        # Préparer les données par mois
        par_mois = {}
        for h in historique:
            date_str = h.get("date", "")
            if date_str:
                try:
                    d = datetime.fromisoformat(date_str).date()
                    mois_key = d.strftime("%Y-%m")
                    par_mois[mois_key] = par_mois.get(mois_key, 0) + 1
                except Exception:
                    pass

        if par_mois:
            mois_sorted = sorted(par_mois.keys())
            counts = [par_mois[m] for m in mois_sorted]
            mois_labels = [datetime.strptime(m, "%Y-%m").strftime("%b %Y") for m in mois_sorted]

            fig = go.Figure()
            fig.add_trace(
                go.Scatter(
                    x=mois_labels,
                    y=counts,
                    mode="lines+markers",
                    name="Tâches accomplies",
                    line={"color": "#3498db", "width": 3},
                    marker={"size": 10, "color": "#3498db"},
                    fill="tozeroy",
                    fillcolor="rgba(52, 152, 219, 0.2)",
                )
            )
            fig.update_layout(
                title="Tâches d'entretien par mois",
                xaxis_title="Mois",
                yaxis_title="Nombre de tâches",
                template="plotly_dark",
                height=350,
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Pas assez de données pour le graphique d'évolution.")

    with g2:
        # Répartition par catégorie
        st.markdown("### Répartition par catégorie")

        catalogue = charger_catalogue_entretien()
        par_cat = {}
        for h in historique:
            obj_id = h.get("objet_id", "inconnu")
            # Trouver la catégorie
            cat_found = "Autre"
            for cat_id, cat_data in catalogue.get("categories", {}).items():
                if obj_id in cat_data.get("objets", {}):
                    cat_found = cat_id.replace("_", " ").capitalize()
                    break
            par_cat[cat_found] = par_cat.get(cat_found, 0) + 1

        if par_cat:
            fig = px.pie(
                values=list(par_cat.values()),
                names=list(par_cat.keys()),
                title="Entretiens par catégorie",
                color_discrete_sequence=px.colors.qualitative.Set3,
                hole=0.4,
            )
            fig.update_layout(template="plotly_dark", height=350)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Pas de données pour la répartition.")

    with g3:
        # Planning prévisionnel visuel
        st.markdown("### Planning prévisionnel")

        planning = generer_planning_previsionnel(mes_objets, historique, horizon_jours=60)

        if planning:
            # Créer un timeline
            df_planning = []
            for t in planning[:20]:
                df_planning.append(
                    {
                        "Tâche": t["tache_nom"][:20],
                        "Jours": t["jours_restants"],
                        "Objet": t["objet_nom"],
                        "Pièce": t["piece"],
                    }
                )

            fig = px.bar(
                df_planning,
                y="Tâche",
                x="Jours",
                orientation="h",
                color="Jours",
                color_continuous_scale=["#e74c3c", "#f39c12", "#27ae60"],
                title="Prochaines tâches (jours restants)",
            )
            fig.update_layout(
                template="plotly_dark", height=400, yaxis={"categoryorder": "total ascending"}
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.success("✨ Aucune tâche prévue dans les 60 prochains jours !")


def onglet_export(mes_objets: list[dict], historique: list[dict]):
    """Onglet export CSV de l'historique et de l'inventaire."""
    st.subheader("📥 Export des données")

    if not HAS_PANDAS:
        st.warning("📦 Pandas non installé. `pip install pandas` pour l'export.")
        return

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📜 Historique des entretiens")

        if not historique:
            st.info("Aucun historique à exporter.")
        else:
            # Préparer le DataFrame
            df_hist = pd.DataFrame(
                [
                    {
                        "Date": h.get("date", ""),
                        "Objet": h.get("objet_id", "").replace("_", " "),
                        "Tâche": h.get("tache_nom", ""),
                        "Pro": "Oui" if h.get("est_pro") else "Non",
                    }
                    for h in historique
                ]
            )
            df_hist = df_hist.sort_values("Date", ascending=False)

            st.dataframe(df_hist, use_container_width=True, height=300)

            # Bouton download CSV
            csv = df_hist.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥 Télécharger CSV",
                data=csv,
                file_name=f"entretien_historique_{date.today().isoformat()}.csv",
                mime="text/csv",
                type="primary",
            )

            st.metric("Total tâches", len(historique))

    with col2:
        st.markdown("### 📦 Inventaire équipements")

        if not mes_objets:
            st.info("Aucun équipement à exporter.")
        else:
            df_inv = pd.DataFrame(
                [
                    {
                        "Objet": obj.get("objet_id", "").replace("_", " "),
                        "Catégorie": obj.get("categorie_id", "").replace("_", " "),
                        "Pièce": obj.get("piece", ""),
                        "Marque": obj.get("marque", ""),
                        "Date ajout": obj.get("date_ajout", ""),
                        "Date achat": obj.get("date_achat", ""),
                    }
                    for obj in mes_objets
                ]
            )

            st.dataframe(df_inv, use_container_width=True, height=300)

            csv_inv = df_inv.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥 Télécharger CSV",
                data=csv_inv,
                file_name=f"entretien_inventaire_{date.today().isoformat()}.csv",
                mime="text/csv",
                key="download_inv",
            )

            st.metric("Total équipements", len(mes_objets))

    st.divider()

    # Planning prévisionnel export
    st.markdown("### 📅 Planning prévisionnel")

    planning = generer_planning_previsionnel(mes_objets, historique, horizon_jours=90)

    if planning:
        df_plan = pd.DataFrame(
            [
                {
                    "Date prévue": t.get("date_prevue", ""),
                    "Jours restants": t.get("jours_restants", 0),
                    "Tâche": t.get("tache_nom", ""),
                    "Objet": t.get("objet_nom", ""),
                    "Pièce": t.get("piece", ""),
                    "Durée (min)": t.get("duree_min", 15),
                }
                for t in planning
            ]
        )

        st.dataframe(df_plan, use_container_width=True, height=200)

        csv_plan = df_plan.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Télécharger Planning CSV",
            data=csv_plan,
            file_name=f"entretien_planning_{date.today().isoformat()}.csv",
            mime="text/csv",
            key="download_plan",
        )
    else:
        st.success("✨ Aucune tâche prévue dans les 90 prochains jours !")
