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
from typing import Dict
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import logging

from src.core.database import get_session
from src.core.models import Equipe, Match, PariSportif, HistoriqueJeux

logger = logging.getLogger(__name__)

from src.domains.jeux.logic.paris_logic import (
    CHAMPIONNATS,
    calculer_forme_equipe,
    calculer_historique_face_a_face,
    predire_resultat_match,
    predire_over_under,
    calculer_performance_paris,
    analyser_tendances_championnat,
    generer_conseils_avances,
    generer_analyse_complete,
    generer_resume_parieur,
    SEUIL_SERIE_SANS_NUL
)

from src.domains.jeux.logic.api_football import (
    charger_classement as api_charger_classement,
    charger_matchs_a_venir,
    charger_historique_equipe,
    vider_cache as api_vider_cache
)


# ═══════════════════════════════════════════════════════════════════
# FONCTIONS HELPER (DB)
# ═══════════════════════════════════════════════════════════════════

def sync_equipes_depuis_api(championnat: str) -> int:
    """
    Synchronise TOUTES les équipes d'un championnat depuis l'API.
    Ajoute les nouvelles, met à jour les existantes.
    
    ⚠️ Nécessite une clé API Football-Data.org dans .env
    (FOOTBALL_DATA_API_KEY)
    
    Returns:
        Nombre d'équipes ajoutées/mises à jour
    """
    try:
        logger.info(f"🔄 Synchronisation des équipes: {championnat}")
        
        classement = api_charger_classement(championnat)
        if not classement:
            msg = f"⚠️ Impossible de charger {championnat} via API.\n💡 Conseil: Configurer FOOTBALL_DATA_API_KEY dans .env pour synchroniser depuis l'API Football-Data.org"
            logger.warning(msg)
            return 0
        
        count = 0
        with get_session() as session:
            for equipe_api in classement:
                try:
                    # Chercher si équipe existe déjà
                    equipe = session.query(Equipe).filter(
                        Equipe.nom == equipe_api["nom"],
                        Equipe.championnat == championnat
                    ).first()
                    
                    if equipe:
                        # Mettre à jour les stats
                        equipe.matchs_joues = equipe_api.get("matchs_joues", equipe.matchs_joues)
                        equipe.victoires = equipe_api.get("victoires", equipe.victoires)
                        equipe.nuls = equipe_api.get("nuls", equipe.nuls)
                        equipe.defaites = equipe_api.get("defaites", equipe.defaites)
                        equipe.buts_marques = equipe_api.get("buts_marques", equipe.buts_marques)
                        equipe.buts_encaisses = equipe_api.get("buts_encaisses", equipe.buts_encaisses)
                    else:
                        # Créer nouvelle équipe
                        equipe = Equipe(
                            nom=equipe_api["nom"],
                            championnat=championnat,
                            matchs_joues=equipe_api.get("matchs_joues", 0),
                            victoires=equipe_api.get("victoires", 0),
                            nuls=equipe_api.get("nuls", 0),
                            defaites=equipe_api.get("defaites", 0),
                            buts_marques=equipe_api.get("buts_marques", 0),
                            buts_encaisses=equipe_api.get("buts_encaisses", 0)
                        )
                        session.add(equipe)
                    count += 1
                except Exception as e:
                    logger.debug(f"Erreur équipe {equipe_api.get('nom')}: {e}")
                    continue
            
            try:
                session.commit()
            except Exception as e:
                logger.error(f"Erreur commit équipes: {e}")
                session.rollback()
        
        return count
    except Exception as e:
        logger.error(f"❌ Erreur sync équipes: {e}")
        return 0


def sync_tous_championnats() -> Dict[str, int]:
    """Synchronise TOUS les championnats d'un coup."""
    resultats = {}
    for champ in CHAMPIONNATS:
        count = sync_equipes_depuis_api(champ)
        resultats[champ] = count
    return resultats


def refresh_scores_matchs() -> int:
    """
    Met à jour les scores des matchs terminés depuis la BD.
    (L'API Football-Data sera intégrée plus tard)
    
    Returns:
        Nombre de matchs mis à jour
    """
    try:
        count = 0
        with get_session() as session:
            # Matchs non joués dans le passé (à vérifier manuellement)
            matchs_a_maj = session.query(Match).filter(
                Match.joue == False,
                Match.date_match < date.today()
            ).all()
            
            if not matchs_a_maj:
                logger.info("✅ Tous les matchs sont à jour")
                return 0
            
            logger.info(f"ℹ️ {len(matchs_a_maj)} matchs non terminés à vérifier")
            # Pour l'instant, on affiche juste que c'est détecté
            # La mise à jour se fera via l'interface "Gestion" -> "Enregistrer résultats"
            return len(matchs_a_maj)
            
    except Exception as e:
        logger.error(f"❌ Erreur refresh scores: {e}")
        return 0

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
    """Affiche la carte de prédiction intelligente pour un match"""
    
    # Charger données pour prédiction
    matchs_dom = charger_matchs_recents(match["equipe_domicile_id"])
    matchs_ext = charger_matchs_recents(match["equipe_exterieur_id"])
    
    forme_dom = calculer_forme_equipe(matchs_dom, match["equipe_domicile_id"])
    forme_ext = calculer_forme_equipe(matchs_ext, match["equipe_exterieur_id"])
    
    # H2H (matchs entre les deux équipes)
    h2h = {"nb_matchs": 0}
    
    # Cotes si disponibles
    cotes = None
    if match.get("cote_dom"):
        cotes = {
            "domicile": match["cote_dom"],
            "nul": match["cote_nul"],
            "exterieur": match["cote_ext"]
        }
    
    # 🧠 ANALYSE INTELLIGENTE COMPLÈTE
    analyse = generer_analyse_complete(forme_dom, forme_ext, h2h, cotes, match.get("championnat"))
    prediction = predire_resultat_match(forme_dom, forme_ext, h2h, cotes)
    over_under = predire_over_under(forme_dom, forme_ext)
    
    # ═══════════════════════════════════════════════════════════
    # AFFICHAGE
    # ═══════════════════════════════════════════════════════════
    with st.container(border=True):
        # Header avec les équipes
        col1, col2, col3 = st.columns([2, 1, 2])
        
        with col1:
            st.markdown(f"### 🏠 {match['dom_nom']}")
            forme_str = forme_dom.get('forme_str', '?????')
            # Colorier la forme
            forme_coloree = forme_str.replace("V", "🟢").replace("N", "🟡").replace("D", "🔴").replace("?", "⚪")
            st.markdown(f"Forme: {forme_coloree}")
            
            # Jauge de forme
            score_dom = forme_dom.get('score', 50)
            if score_dom >= 70:
                st.success(f"💪 Excellente forme ({score_dom:.0f}/100)")
            elif score_dom >= 50:
                st.info(f"👍 Bonne forme ({score_dom:.0f}/100)")
            else:
                st.warning(f"😟 Forme moyenne ({score_dom:.0f}/100)")
        
        with col2:
            st.markdown(f"### ⚽")
            st.markdown(f"**{match['date']}**")
            if match.get("heure"):
                st.markdown(f"⏰ {match['heure']}")
            st.markdown(f"🏆 {match['championnat']}")
        
        with col3:
            st.markdown(f"### ✈️ {match['ext_nom']}")
            forme_str = forme_ext.get('forme_str', '?????')
            forme_coloree = forme_str.replace("V", "🟢").replace("N", "🟡").replace("D", "🔴").replace("?", "⚪")
            st.markdown(f"Forme: {forme_coloree}")
            
            score_ext = forme_ext.get('score', 50)
            if score_ext >= 70:
                st.success(f"💪 Excellente forme ({score_ext:.0f}/100)")
            elif score_ext >= 50:
                st.info(f"👍 Bonne forme ({score_ext:.0f}/100)")
            else:
                st.warning(f"😟 Forme moyenne ({score_ext:.0f}/100)")
        
        st.divider()
        
        # ═══════════════════════════════════════════════════════
        # 🎯 RECOMMANDATION PRINCIPALE (MISE EN AVANT)
        # ═══════════════════════════════════════════════════════
        reco = analyse.get("recommandation", {})
        conseils = analyse.get("conseils", [])
        alertes = analyse.get("alertes", [])
        
        confiance = reco.get("confiance", 50)
        pari_reco = reco.get("pari", "?")
        
        # Box de recommandation principale
        if confiance >= 65:
            st.success(f"""
            ### ✅ PARI RECOMMANDÉ: **{pari_reco}**
            
            **Confiance:** {confiance:.0f}% | **Mise suggérée:** {reco.get('mise', '?')}
            
            📊 *{reco.get('raison', '')}*
            """)
        elif confiance >= 50:
            st.warning(f"""
            ### ⚠️ PARI POSSIBLE: **{pari_reco}**
            
            **Confiance:** {confiance:.0f}% | **Mise suggérée:** {reco.get('mise', '?')}
            
            📊 *{reco.get('raison', '')}*
            """)
        else:
            st.error("""
            ### ❌ MATCH À ÉVITER
            
            Pas assez de signaux clairs pour ce match. 
            **Conseil:** Garde tes sous pour un meilleur match!
            """)
        
        # ═══════════════════════════════════════════════════════
        # 📊 PROBABILITÉS & COTES
        # ═══════════════════════════════════════════════════════
        col_prob, col_over = st.columns(2)
        
        with col_prob:
            probas = prediction.get("probabilites", {})
            
            fig = go.Figure(data=[
                go.Bar(
                    x=["🏠 Dom", "⚖️ Nul", "✈️ Ext"],
                    y=[probas.get("domicile", 33), probas.get("nul", 33), probas.get("exterieur", 33)],
                    marker_color=["#4CAF50", "#FFC107", "#2196F3"],
                    text=[f"{v:.0f}%" for v in [probas.get("domicile", 33), probas.get("nul", 33), probas.get("exterieur", 33)]],
                    textposition="outside"
                )
            ])
            fig.update_layout(
                title="📊 Probabilités estimées",
                height=220,
                margin=dict(l=20, r=20, t=40, b=20),
                showlegend=False,
                yaxis=dict(range=[0, 100])
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col_over:
            # Over/Under et BTTS
            stats = analyse.get("stats", {})
            moy_buts = stats.get("moy_buts_match", 2.5)
            
            st.markdown("### ⚽ Paris Buts")
            
            if moy_buts > 2.8:
                st.success(f"**Over 2.5** recommandé ({over_under['probabilite_over']:.0f}%)")
            elif moy_buts < 2.2:
                st.info(f"**Under 2.5** intéressant ({over_under['probabilite_under']:.0f}%)")
            else:
                st.warning(f"50/50 - Prudence")
            
            st.caption(f"Buts attendus: **{over_under['buts_attendus']:.1f}**")
            
            # BTTS
            buts_dom = stats.get("buts_dom", {})
            buts_ext = stats.get("buts_ext", {})
            if buts_dom.get("moy_marques", 0) > 1.0 and buts_ext.get("moy_marques", 0) > 1.0:
                st.success("**BTTS Oui** probable (les 2 marquent)")
        
        # ═══════════════════════════════════════════════════════
        # 💡 CONSEILS INTELLIGENTS
        # ═══════════════════════════════════════════════════════
        if conseils:
            st.markdown("### 💡 Conseils IA")
            
            for conseil in conseils[:4]:
                emoji = conseil.get("emoji", "💡")
                titre = conseil.get("titre", "")
                message = conseil.get("message", "")
                conf = conseil.get("confiance", 50)
                mise = conseil.get("mise", "?")
                pari = conseil.get("pari_suggere", "")
                
                # Couleur selon confiance
                if conf >= 65:
                    container_type = "success"
                elif conf >= 50:
                    container_type = "info"
                else:
                    container_type = "warning"
                
                with st.expander(f"{emoji} {titre} - **{pari}** ({conf:.0f}%)", expanded=(conf >= 60)):
                    st.markdown(message)
                    st.caption(f"💰 Mise suggérée: {mise}")
        
        # ═══════════════════════════════════════════════════════
        # ⚠️ ALERTES
        # ═══════════════════════════════════════════════════════
        if alertes:
            st.markdown("### ⚠️ Points d'attention")
            for alerte in alertes:
                st.warning(f"{alerte['emoji']} **{alerte['titre']}**: {alerte['message']}")
        
        # ═══════════════════════════════════════════════════════
        # 💎 VALUE BETS
        # ═══════════════════════════════════════════════════════
        value_bets = analyse.get("value_bets", [])
        if value_bets:
            st.markdown("### 💎 Value Bets détectées")
            for vb in value_bets:
                if vb["qualite"] in ["excellente", "bonne"]:
                    st.success(
                        f"{vb['emoji']} **Pari {vb['pari']}** @ {vb['cote']:.2f} | "
                        f"Notre proba: {vb['proba_estimee']:.0f}% | "
                        f"EV: **+{vb['ev']:.1f}%** ({vb['qualite']})"
                    )
        
        # ═══════════════════════════════════════════════════════
        # 🎯 BOUTONS DE PARIS
        # ═══════════════════════════════════════════════════════
        st.divider()
        st.markdown("### 🎯 Enregistrer un pari")
        
        col_btn1, col_btn2, col_btn3, col_btn4 = st.columns(4)
        
        with col_btn1:
            cote_d = match.get("cote_dom") or 2.0
            if st.button(f"🏠 {match['dom_nom'][:10]}... ({cote_d:.2f})", key=f"bet_dom_{match['id']}"):
                enregistrer_pari(match["id"], "1", cote_d, est_virtuel=True)
                st.success("✅ Pari enregistré!")
                st.rerun()
        
        with col_btn2:
            cote_n = match.get("cote_nul") or 3.5
            if st.button(f"⚖️ Match Nul ({cote_n:.2f})", key=f"bet_nul_{match['id']}"):
                enregistrer_pari(match["id"], "N", cote_n, est_virtuel=True)
                st.success("✅ Pari enregistré!")
                st.rerun()
        
        with col_btn3:
            cote_e = match.get("cote_ext") or 3.0
            if st.button(f"✈️ {match['ext_nom'][:10]}... ({cote_e:.2f})", key=f"bet_ext_{match['id']}"):
                enregistrer_pari(match["id"], "2", cote_e, est_virtuel=True)
                st.success("✅ Pari enregistré!")
                st.rerun()
        
        with col_btn4:
            if st.button("📊 Analyse complète", key=f"analyse_{match['id']}"):
                st.session_state[f"show_details_{match['id']}"] = True
        
        # Détails complets si demandé
        if st.session_state.get(f"show_details_{match['id']}", False):
            with st.expander("📊 Analyse détaillée complète", expanded=True):
                col_d1, col_d2 = st.columns(2)
                
                with col_d1:
                    st.markdown("**Équipe Domicile:**")
                    st.json(forme_dom)
                
                with col_d2:
                    st.markdown("**Équipe Extérieur:**")
                    st.json(forme_ext)
                
                st.markdown("**Toutes les raisons:**")
                for raison in prediction.get("raisons", []):
                    st.write(f"• {raison}")


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
        
        # Boutons Refresh
        col_refresh1, col_refresh2, col_filtre, col_jours = st.columns([1, 1, 2, 1])
        with col_refresh1:
            if st.button("🔄 Refresh Scores", help="Met à jour les scores depuis l'API"):
                st.info("🔄 Actualisation en cours...")
                try:
                    with st.spinner("Mise à jour des scores..."):
                        logger.info("🔘 Bouton REFRESH cliqué!")
                        count = refresh_scores_matchs()
                        logger.info(f"📊 Résultat refresh: {count} matchs")
                        if count > 0:
                            st.success(f"✅ {count} matchs mis à jour!")
                        else:
                            st.info("✅ Tous les matchs sont à jour")
                        st.rerun()
                except Exception as e:
                    logger.error(f"❌ Erreur refresh: {e}", exc_info=True)
                    st.error(f"❌ Erreur: {e}")
        
        with col_refresh2:
            if st.button("📥 Sync Équipes", help="Charge toutes les équipes depuis l'API"):
                st.info("🔄 Synchronisation en cours...")
                try:
                    with st.spinner("Synchronisation..."):
                        logger.info("🔘 Bouton SYNC cliqué!")
                        resultats = sync_tous_championnats()
                        logger.info(f"📊 Résultats sync: {resultats}")
                        total = sum(resultats.values())
                        if total == 0:
                            st.warning("⚠️ 0 équipes synchronisées - Vérifier la clé API Football-Data")
                            st.info("💡 Voir le diagnostic: python test_final.py")
                        else:
                            st.success(f"✅ {total} équipes synchronisées!")
                        st.rerun()
                except Exception as e:
                    logger.error(f"❌ Erreur sync: {e}", exc_info=True)
                    st.error(f"❌ Erreur: {e}")
        
        with col_filtre:
            championnats = ["Tous"] + CHAMPIONNATS
            filtre_champ = st.selectbox("Championnat", championnats)
        with col_jours:
            jours = st.slider("Jours", 1, 14, 7)
        
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
