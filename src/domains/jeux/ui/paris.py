"""
Module Paris Sportifs - Suivi des championnats européens et prédictions IA

Fonctionnalités:
- Suivi des 5 grands championnats + coupes européennes
- Prédictions basées sur la forme, H2H, avantage domicile
- Suivi des paris virtuels et réels
- Dashboard de performance
"""

import streamlit as st
from datetime import date, timedelta
from decimal import Decimal
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

from src.core.database import get_session
from src.core.models import Equipe, Match, PariSportif, HistoriqueJeux

from src.domains.jeux.logic.paris_logic import (
    CHAMPIONNATS,
    calculer_forme_equipe,
    calculer_historique_face_a_face,
    predire_resultat_match,
    predire_over_under,
    calculer_performance_paris,
    analyser_tendances_championnat
)


# ═══════════════════════════════════════════════════════════════════
# FONCTIONS HELPER (DB)
# ═══════════════════════════════════════════════════════════════════

def charger_championnats_disponibles():
    """Retourne la liste des championnats disponibles"""
    return CHAMPIONNATS


def charger_equipes(championnat: str = None):
    """Charge les équipes, optionnellement filtrées par championnat"""
    try:
        with get_session() as session:
            query = session.query(Equipe)
            if championnat:
                query = query.filter(Equipe.championnat == championnat)
            equipes = query.order_by(Equipe.nom).all()
            return [
                {
                    "id": e.id,
                    "nom": e.nom,
                    "championnat": e.championnat,
                    "matchs_joues": e.matchs_joues,
                    "victoires": e.victoires,
                    "nuls": e.nuls,
                    "defaites": e.defaites,
                    "buts_marques": e.buts_marques,
                    "buts_encaisses": e.buts_encaisses,
                    "points": e.points
                }
                for e in equipes
            ]
    except Exception as e:
        st.error(f"❌ Erreur chargement équipes: {e}")
        return []


def charger_matchs_a_venir(jours: int = 7, championnat: str = None):
    """Charge les matchs des N prochains jours"""
    try:
        with get_session() as session:
            debut = date.today()
            fin = debut + timedelta(days=jours)
            
            query = session.query(Match).filter(
                Match.date_match >= debut,
                Match.date_match <= fin,
                Match.joue == False
            )
            
            if championnat:
                query = query.filter(Match.championnat == championnat)
            
            matchs = query.order_by(Match.date_match, Match.heure).all()
            
            return [
                {
                    "id": m.id,
                    "date": m.date_match,
                    "heure": m.heure,
                    "championnat": m.championnat,
                    "equipe_domicile_id": m.equipe_domicile_id,
                    "equipe_exterieur_id": m.equipe_exterieur_id,
                    "dom_nom": m.equipe_domicile.nom if m.equipe_domicile else "?",
                    "ext_nom": m.equipe_exterieur.nom if m.equipe_exterieur else "?",
                    "cote_dom": m.cote_domicile,
                    "cote_nul": m.cote_nul,
                    "cote_ext": m.cote_exterieur,
                    "prediction": m.prediction_resultat,
                    "confiance": m.prediction_confiance
                }
                for m in matchs
            ]
    except Exception as e:
        st.error(f"❌ Erreur chargement matchs: {e}")
        return []


def charger_matchs_recents(equipe_id: int, nb_matchs: int = 10):
    """Charge les derniers matchs d'une équipe"""
    try:
        with get_session() as session:
            matchs = session.query(Match).filter(
                Match.joue == True,
                (Match.equipe_domicile_id == equipe_id) | 
                (Match.equipe_exterieur_id == equipe_id)
            ).order_by(Match.date_match.desc()).limit(nb_matchs).all()
            
            return [
                {
                    "id": m.id,
                    "date": m.date_match,
                    "equipe_domicile_id": m.equipe_domicile_id,
                    "equipe_exterieur_id": m.equipe_exterieur_id,
                    "score_domicile": m.score_domicile,
                    "score_exterieur": m.score_exterieur
                }
                for m in reversed(matchs)  # Du plus ancien au plus récent
            ]
    except Exception as e:
        st.error(f"❌ Erreur chargement matchs récents: {e}")
        return []


def charger_paris_utilisateur(statut: str = None):
    """Charge les paris de l'utilisateur"""
    try:
        with get_session() as session:
            query = session.query(PariSportif)
            if statut:
                query = query.filter(PariSportif.statut == statut)
            
            paris = query.order_by(PariSportif.cree_le.desc()).limit(100).all()
            
            return [
                {
                    "id": p.id,
                    "match_id": p.match_id,
                    "type_pari": p.type_pari,
                    "prediction": p.prediction,
                    "cote": p.cote,
                    "mise": p.mise,
                    "statut": p.statut,
                    "gain": p.gain,
                    "est_virtuel": p.est_virtuel,
                    "date": p.cree_le
                }
                for p in paris
            ]
    except Exception as e:
        st.error(f"❌ Erreur chargement paris: {e}")
        return []


def enregistrer_pari(match_id: int, prediction: str, cote: float, 
                     mise: float = 0, est_virtuel: bool = True):
    """Enregistre un nouveau pari"""
    try:
        with get_session() as session:
            pari = PariSportif(
                match_id=match_id,
                type_pari="1N2",
                prediction=prediction,
                cote=cote,
                mise=Decimal(str(mise)),
                est_virtuel=est_virtuel,
                statut="en_attente"
            )
            session.add(pari)
            session.commit()
            return True
    except Exception as e:
        st.error(f"❌ Erreur enregistrement pari: {e}")
        return False


def ajouter_equipe(nom: str, championnat: str):
    """Ajoute une nouvelle équipe"""
    try:
        with get_session() as session:
            equipe = Equipe(
                nom=nom,
                championnat=championnat
            )
            session.add(equipe)
            session.commit()
            st.success(f"✅ Équipe '{nom}' ajoutée!")
            return True
    except Exception as e:
        st.error(f"❌ Erreur ajout équipe: {e}")
        return False


def ajouter_match(equipe_dom_id: int, equipe_ext_id: int, 
                  championnat: str, date_match: date, heure: str = None):
    """Ajoute un nouveau match"""
    try:
        with get_session() as session:
            match = Match(
                equipe_domicile_id=equipe_dom_id,
                equipe_exterieur_id=equipe_ext_id,
                championnat=championnat,
                date_match=date_match,
                heure=heure,
                joue=False
            )
            session.add(match)
            session.commit()
            st.success("✅ Match ajouté!")
            return True
    except Exception as e:
        st.error(f"❌ Erreur ajout match: {e}")
        return False


def enregistrer_resultat_match(match_id: int, score_dom: int, score_ext: int):
    """Enregistre le résultat d'un match"""
    try:
        with get_session() as session:
            match = session.query(Match).get(match_id)
            if match:
                match.score_domicile = score_dom
                match.score_exterieur = score_ext
                match.joue = True
                
                # Déterminer le résultat
                if score_dom > score_ext:
                    match.resultat = "1"
                elif score_ext > score_dom:
                    match.resultat = "2"
                else:
                    match.resultat = "N"
                
                # Mettre à jour les paris liés
                for pari in match.paris:
                    if pari.statut == "en_attente":
                        if pari.prediction == match.resultat:
                            pari.statut = "gagne"
                            pari.gain = pari.mise * Decimal(str(pari.cote))
                        else:
                            pari.statut = "perdu"
                            pari.gain = Decimal("0")
                
                session.commit()
                st.success(f"✅ Résultat enregistré: {score_dom}-{score_ext}")
                return True
    except Exception as e:
        st.error(f"❌ Erreur enregistrement résultat: {e}")
        return False


# ═══════════════════════════════════════════════════════════════════
# UI COMPONENTS
# ═══════════════════════════════════════════════════════════════════

def afficher_prediction_match(match: dict):
    """Affiche la carte de prédiction pour un match"""
    
    # Charger données pour prédiction
    matchs_dom = charger_matchs_recents(match["equipe_domicile_id"])
    matchs_ext = charger_matchs_recents(match["equipe_exterieur_id"])
    
    forme_dom = calculer_forme_equipe(matchs_dom, match["equipe_domicile_id"])
    forme_ext = calculer_forme_equipe(matchs_ext, match["equipe_exterieur_id"])
    
    # H2H (matchs entre les deux équipes)
    h2h = {"nb_matchs": 0}  # Simplifié
    
    # Cotes si disponibles
    cotes = None
    if match.get("cote_dom"):
        cotes = {
            "domicile": match["cote_dom"],
            "nul": match["cote_nul"],
            "exterieur": match["cote_ext"]
        }
    
    # Prédiction
    prediction = predire_resultat_match(forme_dom, forme_ext, h2h, cotes)
    over_under = predire_over_under(forme_dom, forme_ext)
    
    # Affichage
    with st.container(border=True):
        col1, col2, col3 = st.columns([2, 1, 2])
        
        with col1:
            st.markdown(f"### 🏠 {match['dom_nom']}")
            st.caption(f"Forme: {forme_dom.get('forme_str', '?')}")
            st.metric("Score forme", f"{forme_dom.get('score', 50):.0f}/100")
        
        with col2:
            st.markdown(f"**{match['date']}**")
            if match.get("heure"):
                st.markdown(f"⏰ {match['heure']}")
            st.markdown(f"🏆 {match['championnat']}")
        
        with col3:
            st.markdown(f"### ✈️ {match['ext_nom']}")
            st.caption(f"Forme: {forme_ext.get('forme_str', '?')}")
            st.metric("Score forme", f"{forme_ext.get('score', 50):.0f}/100")
        
        st.divider()
        
        # Prédiction
        col_pred, col_probas = st.columns([1, 2])
        
        with col_pred:
            niveau = prediction.get("niveau_confiance", "faible")
            couleur = {"haute": "🟢", "moyenne": "🟡", "faible": "🔴"}[niveau]
            
            pred_label = {"1": match['dom_nom'], "N": "Match Nul", "2": match['ext_nom']}
            st.markdown(f"### {couleur} Prédiction: **{pred_label[prediction['prediction']]}**")
            st.caption(f"Confiance: {prediction['confiance']:.0f}%")
            st.info(prediction.get("conseil", ""))
        
        with col_probas:
            probas = prediction.get("probabilites", {})
            
            fig = go.Figure(data=[
                go.Bar(
                    x=["Domicile", "Nul", "Extérieur"],
                    y=[probas.get("domicile", 0), probas.get("nul", 0), probas.get("exterieur", 0)],
                    marker_color=["#4CAF50", "#FFC107", "#2196F3"],
                    text=[f"{v:.1f}%" for v in [probas.get("domicile", 0), probas.get("nul", 0), probas.get("exterieur", 0)]],
                    textposition="auto"
                )
            ])
            fig.update_layout(
                title="Probabilités",
                height=200,
                margin=dict(l=20, r=20, t=40, b=20),
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Over/Under
        st.caption(f"⚽ Buts attendus: {over_under['buts_attendus']:.1f} | "
                   f"Over 2.5: {over_under['probabilite_over']:.0f}%")
        
        # Raisons
        with st.expander("📊 Analyse détaillée"):
            for raison in prediction.get("raisons", []):
                st.write(f"• {raison}")
        
        # Actions
        col_btn1, col_btn2, col_btn3 = st.columns(3)
        with col_btn1:
            if st.button(f"🎯 Parier {match['dom_nom']}", key=f"bet_dom_{match['id']}"):
                enregistrer_pari(
                    match["id"], "1", 
                    match.get("cote_dom") or 2.0,
                    est_virtuel=True
                )
                st.success("✅ Pari virtuel enregistré!")
                st.rerun()
        
        with col_btn2:
            if st.button("🎯 Parier Nul", key=f"bet_nul_{match['id']}"):
                enregistrer_pari(
                    match["id"], "N",
                    match.get("cote_nul") or 3.5,
                    est_virtuel=True
                )
                st.success("✅ Pari virtuel enregistré!")
                st.rerun()
        
        with col_btn3:
            if st.button(f"🎯 Parier {match['ext_nom']}", key=f"bet_ext_{match['id']}"):
                enregistrer_pari(
                    match["id"], "2",
                    match.get("cote_ext") or 3.0,
                    est_virtuel=True
                )
                st.success("✅ Pari virtuel enregistré!")
                st.rerun()


def afficher_dashboard_performance():
    """Affiche le tableau de bord de performance des paris"""
    paris = charger_paris_utilisateur()
    
    if not paris:
        st.info("📊 Aucun pari enregistré. Commencez par faire des prédictions!")
        return
    
    # Calculs
    perf = calculer_performance_paris(paris)
    
    # Métriques principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🎯 Total Paris", perf["nb_paris"])
    
    with col2:
        taux = perf.get("taux_reussite", 0)
        st.metric("✅ Taux Réussite", f"{taux:.1f}%")
    
    with col3:
        profit = perf.get("profit", 0)
        st.metric("💰 Profit/Perte", f"{profit:+.2f}€", 
                  delta_color="normal" if profit >= 0 else "inverse")
    
    with col4:
        roi = perf.get("roi", 0)
        st.metric("📈 ROI", f"{roi:+.1f}%",
                  delta_color="normal" if roi >= 0 else "inverse")
    
    st.divider()
    
    # Graphique évolution
    if len(paris) > 1:
        # Créer historique cumulé
        df = pd.DataFrame(paris)
        df = df[df["statut"] != "en_attente"]
        
        if not df.empty:
            df["date"] = pd.to_datetime(df["date"])
            df = df.sort_values("date")
            df["profit_cumul"] = (df["gain"].fillna(0).astype(float) - df["mise"].astype(float)).cumsum()
            
            fig = px.line(df, x="date", y="profit_cumul", 
                         title="📈 Évolution du profit cumulé")
            fig.update_layout(height=300)
            fig.add_hline(y=0, line_dash="dash", line_color="gray")
            st.plotly_chart(fig, use_container_width=True)
    
    # Liste des derniers paris
    st.subheader("📋 Derniers paris")
    
    for pari in paris[:10]:
        statut_emoji = {
            "en_attente": "⏳",
            "gagne": "✅",
            "perdu": "❌",
            "annule": "🚫"
        }.get(pari["statut"], "?")
        
        pred_label = {"1": "Dom", "N": "Nul", "2": "Ext"}.get(pari["prediction"], "?")
        
        col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
        with col1:
            st.write(f"{statut_emoji} Match #{pari['match_id']}")
        with col2:
            st.write(f"Préd: {pred_label}")
        with col3:
            st.write(f"Cote: {pari['cote']:.2f}")
        with col4:
            if pari["statut"] == "gagne":
                st.write(f"💰 +{pari['gain']:.2f}€")
            elif pari["statut"] == "perdu":
                st.write(f"📉 -{pari['mise']:.2f}€")


def afficher_gestion_donnees():
    """Interface pour gérer les équipes et matchs"""
    
    tab1, tab2, tab3 = st.tabs(["➕ Ajouter Équipe", "➕ Ajouter Match", "📝 Résultats"])
    
    with tab1:
        st.subheader("Ajouter une équipe")
        
        col1, col2 = st.columns(2)
        with col1:
            nom_equipe = st.text_input("Nom de l'équipe", key="new_team_name")
        with col2:
            championnat = st.selectbox("Championnat", CHAMPIONNATS, key="new_team_champ")
        
        if st.button("Ajouter l'équipe", type="primary"):
            if nom_equipe:
                ajouter_equipe(nom_equipe, championnat)
            else:
                st.warning("Veuillez entrer un nom d'équipe")
    
    with tab2:
        st.subheader("Ajouter un match")
        
        championnat_filtre = st.selectbox("Championnat", CHAMPIONNATS, key="match_champ")
        equipes = charger_equipes(championnat_filtre)
        
        if len(equipes) >= 2:
            options = {e["nom"]: e["id"] for e in equipes}
            
            col1, col2 = st.columns(2)
            with col1:
                dom_nom = st.selectbox("Équipe domicile", list(options.keys()), key="dom_sel")
            with col2:
                ext_options = [n for n in options.keys() if n != dom_nom]
                ext_nom = st.selectbox("Équipe extérieur", ext_options, key="ext_sel")
            
            col3, col4 = st.columns(2)
            with col3:
                date_m = st.date_input("Date du match", value=date.today() + timedelta(days=3))
            with col4:
                heure_m = st.text_input("Heure (ex: 21:00)", value="21:00")
            
            if st.button("Ajouter le match", type="primary"):
                ajouter_match(
                    options[dom_nom],
                    options[ext_nom],
                    championnat_filtre,
                    date_m,
                    heure_m
                )
        else:
            st.warning("Ajoutez au moins 2 équipes pour créer un match")
    
    with tab3:
        st.subheader("Enregistrer un résultat")
        
        matchs = charger_matchs_a_venir(jours=0)  # Matchs passés non joués
        
        # Charger matchs non joués dans le passé
        try:
            with get_session() as session:
                matchs_passes = session.query(Match).filter(
                    Match.date_match <= date.today(),
                    Match.joue == False
                ).all()
                
                if matchs_passes:
                    for m in matchs_passes:
                        with st.container(border=True):
                            st.write(f"**{m.equipe_domicile.nom if m.equipe_domicile else '?'} vs "
                                    f"{m.equipe_exterieur.nom if m.equipe_exterieur else '?'}** "
                                    f"({m.date_match})")
                            
                            col1, col2, col3 = st.columns([1, 1, 1])
                            with col1:
                                score_d = st.number_input("Score dom", 0, 20, 0, key=f"sd_{m.id}")
                            with col2:
                                score_e = st.number_input("Score ext", 0, 20, 0, key=f"se_{m.id}")
                            with col3:
                                if st.button("Valider", key=f"val_{m.id}"):
                                    enregistrer_resultat_match(m.id, score_d, score_e)
                                    st.rerun()
                else:
                    st.info("Aucun match en attente de résultat")
        except Exception as e:
            st.error(f"Erreur: {e}")


# ═══════════════════════════════════════════════════════════════════
# POINT D'ENTRÉE
# ═══════════════════════════════════════════════════════════════════

def app():
    """Point d'entrée du module Paris Sportifs"""
    
    st.title("⚽ Paris Sportifs - Prédictions IA")
    st.caption("Suivi des championnats européens avec prédictions intelligentes")
    
    # Tabs principaux
    tabs = st.tabs([
        "🎯 Prédictions", 
        "📊 Performance", 
        "🏆 Classements",
        "⚙️ Gestion"
    ])
    
    # ═══════════════════════════════════════════════════════════════
    # TAB 1: PRÉDICTIONS
    # ═══════════════════════════════════════════════════════════════
    with tabs[0]:
        st.header("Matchs à venir")
        
        col_filtre, col_jours = st.columns([2, 1])
        with col_filtre:
            championnats = ["Tous"] + CHAMPIONNATS
            filtre_champ = st.selectbox("Championnat", championnats)
        with col_jours:
            jours = st.slider("Prochains jours", 1, 14, 7)
        
        champ_filtre = None if filtre_champ == "Tous" else filtre_champ
        matchs = charger_matchs_a_venir(jours=jours, championnat=champ_filtre)
        
        if matchs:
            for match in matchs:
                afficher_prediction_match(match)
        else:
            st.info("📅 Aucun match prévu dans cette période. "
                   "Ajoutez des matchs dans l'onglet Gestion.")
            
            # Données de démo
            with st.expander("🎮 Voir une démo"):
                st.markdown("""
                ### Comment ça marche?
                
                1. **Ajoutez des équipes** dans l'onglet Gestion
                2. **Créez des matchs** entre ces équipes
                3. **L'IA prédit** les résultats basés sur:
                   - Forme récente (5 derniers matchs)
                   - Avantage domicile (+12% statistique)
                   - Historique des confrontations
                   - Régression vers la moyenne
                
                4. **Enregistrez vos paris** (virtuels ou réels)
                5. **Suivez votre performance** dans l'onglet dédié
                """)
    
    # ═══════════════════════════════════════════════════════════════
    # TAB 2: PERFORMANCE
    # ═══════════════════════════════════════════════════════════════
    with tabs[1]:
        st.header("📊 Performance de mes paris")
        afficher_dashboard_performance()
    
    # ═══════════════════════════════════════════════════════════════
    # TAB 3: CLASSEMENTS
    # ═══════════════════════════════════════════════════════════════
    with tabs[2]:
        st.header("🏆 Classements")
        
        champ_classe = st.selectbox("Sélectionner un championnat", CHAMPIONNATS, key="class_champ")
        equipes = charger_equipes(champ_classe)
        
        if equipes:
            # Trier par points
            equipes_triees = sorted(equipes, key=lambda x: (x["points"], x["buts_marques"] - x["buts_encaisses"]), reverse=True)
            
            df = pd.DataFrame(equipes_triees)
            df["Diff"] = df["buts_marques"] - df["buts_encaisses"]
            df = df.rename(columns={
                "nom": "Équipe",
                "matchs_joues": "J",
                "victoires": "V",
                "nuls": "N",
                "defaites": "D",
                "buts_marques": "BP",
                "buts_encaisses": "BC",
                "points": "Pts"
            })
            
            df.insert(0, "#", range(1, len(df) + 1))
            
            st.dataframe(
                df[["#", "Équipe", "J", "V", "N", "D", "BP", "BC", "Diff", "Pts"]],
                hide_index=True,
                use_container_width=True
            )
        else:
            st.info(f"Aucune équipe enregistrée pour {champ_classe}")
    
    # ═══════════════════════════════════════════════════════════════
    # TAB 4: GESTION
    # ═══════════════════════════════════════════════════════════════
    with tabs[3]:
        st.header("⚙️ Gestion des données")
        afficher_gestion_donnees()


# Alias pour compatibilité
def main():
    app()


if __name__ == "__main__":
    app()
