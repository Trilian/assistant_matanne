"""
Module Loto - Analyse statistique et simulation de stratégies

⚠️ DISCLAIMER: Le Loto est un jeu de hasard pur.
Aucune stratégie ne peut prédire les résultats.
Ce module est à but éducatif et de divertissement.

Fonctionnalités:
- Historique des tirages avec statistiques
- Analyse des fréquences (curiosité mathématique)
- Génération de grilles selon différentes stratégies
- Suivi des "paris virtuels" pour tester les stratégies
- Simulation et backtesting
"""

import streamlit as st
from datetime import date, timedelta
from decimal import Decimal
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import random

from src.core.database import get_session
from src.core.models import TirageLoto, GrilleLoto, StatistiquesLoto

from src.domains.jeux.logic.loto_logic import (
    NUMERO_MIN, NUMERO_MAX, CHANCE_MIN, CHANCE_MAX, NB_NUMEROS,
    COUT_GRILLE, GAINS_PAR_RANG, PROBA_JACKPOT,
    calculer_frequences_numeros,
    identifier_numeros_chauds_froids,
    analyser_patterns_tirages,
    generer_grille_aleatoire,
    generer_grille_eviter_populaires,
    generer_grille_equilibree,
    generer_grille_chauds_froids,
    verifier_grille,
    simuler_strategie,
    calculer_esperance_mathematique,
    comparer_strategies
)


# ═══════════════════════════════════════════════════════════════════
# FONCTIONS HELPER (DB)
# ═══════════════════════════════════════════════════════════════════

def charger_tirages(limite: int = 100):
    """Charge l'historique des tirages"""
    try:
        with get_session() as session:
            tirages = session.query(TirageLoto).order_by(
                TirageLoto.date_tirage.desc()
            ).limit(limite).all()
            
            return [
                {
                    "id": t.id,
                    "date_tirage": t.date_tirage,
                    "numero_1": t.numero_1,
                    "numero_2": t.numero_2,
                    "numero_3": t.numero_3,
                    "numero_4": t.numero_4,
                    "numero_5": t.numero_5,
                    "numero_chance": t.numero_chance,
                    "jackpot_euros": t.jackpot_euros,
                    "numeros": t.numeros,
                    "numeros_str": t.numeros_str
                }
                for t in tirages
            ]
    except Exception as e:
        st.error(f"❌ Erreur chargement tirages: {e}")
        return []


def ajouter_tirage(date_t: date, numeros: list, chance: int, jackpot: int = None):
    """Ajoute un nouveau tirage"""
    try:
        if len(numeros) != 5:
            st.error("Il faut exactement 5 numéros")
            return False
        
        numeros = sorted(numeros)
        
        with get_session() as session:
            tirage = TirageLoto(
                date_tirage=date_t,
                numero_1=numeros[0],
                numero_2=numeros[1],
                numero_3=numeros[2],
                numero_4=numeros[3],
                numero_5=numeros[4],
                numero_chance=chance,
                jackpot_euros=jackpot
            )
            session.add(tirage)
            session.commit()
            
            # Mettre à jour les grilles en attente
            grilles = session.query(GrilleLoto).filter(
                GrilleLoto.tirage_id == None
            ).all()
            
            for grille in grilles:
                grille_data = {
                    "numeros": grille.numeros,
                    "numero_chance": grille.numero_chance
                }
                resultat = verifier_grille(grille_data, {
                    "numero_1": numeros[0],
                    "numero_2": numeros[1],
                    "numero_3": numeros[2],
                    "numero_4": numeros[3],
                    "numero_5": numeros[4],
                    "numero_chance": chance,
                    "jackpot_euros": jackpot or 2_000_000
                })
                
                grille.tirage_id = tirage.id
                grille.numeros_trouves = resultat["bons_numeros"]
                grille.chance_trouvee = resultat["chance_ok"]
                grille.rang = resultat["rang"]
                grille.gain = resultat["gain"]
            
            session.commit()
            st.success(f"✅ Tirage du {date_t} enregistré!")
            return True
            
    except Exception as e:
        st.error(f"❌ Erreur ajout tirage: {e}")
        return False


def charger_grilles_utilisateur():
    """Charge les grilles de l'utilisateur"""
    try:
        with get_session() as session:
            grilles = session.query(GrilleLoto).order_by(
                GrilleLoto.date_creation.desc()
            ).limit(50).all()
            
            return [
                {
                    "id": g.id,
                    "numeros": g.numeros,
                    "numeros_str": g.numeros_str,
                    "numero_chance": g.numero_chance,
                    "source": g.source_prediction,
                    "est_virtuelle": g.est_virtuelle,
                    "mise": g.mise,
                    "tirage_id": g.tirage_id,
                    "numeros_trouves": g.numeros_trouves,
                    "chance_trouvee": g.chance_trouvee,
                    "rang": g.rang,
                    "gain": g.gain,
                    "date": g.date_creation
                }
                for g in grilles
            ]
    except Exception as e:
        st.error(f"❌ Erreur chargement grilles: {e}")
        return []


def enregistrer_grille(numeros: list, chance: int, source: str = "manuel", 
                       est_virtuelle: bool = True):
    """Enregistre une nouvelle grille"""
    try:
        if len(numeros) != 5:
            st.error("Il faut exactement 5 numéros")
            return False
        
        numeros = sorted(numeros)
        
        with get_session() as session:
            grille = GrilleLoto(
                numero_1=numeros[0],
                numero_2=numeros[1],
                numero_3=numeros[2],
                numero_4=numeros[3],
                numero_5=numeros[4],
                numero_chance=chance,
                source_prediction=source,
                est_virtuelle=est_virtuelle,
                mise=COUT_GRILLE
            )
            session.add(grille)
            session.commit()
            st.success(f"✅ Grille enregistrée: {'-'.join(map(str, numeros))} + N°{chance}")
            return True
            
    except Exception as e:
        st.error(f"❌ Erreur enregistrement grille: {e}")
        return False


# ═══════════════════════════════════════════════════════════════════
# UI COMPONENTS
# ═══════════════════════════════════════════════════════════════════

def afficher_dernier_tirage(tirages: list):
    """Affiche le dernier tirage avec style"""
    if not tirages:
        st.info("📊 Aucun tirage enregistré")
        return
    
    dernier = tirages[0]
    
    st.markdown("### 🎰 Dernier tirage")
    
    with st.container(border=True):
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown(f"**{dernier['date_tirage']}**")
            
            # Afficher les boules
            cols_boules = st.columns(6)
            for i, num in enumerate(dernier["numeros"]):
                with cols_boules[i]:
                    st.markdown(
                        f"<div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); "
                        f"color: white; border-radius: 50%; width: 50px; height: 50px; "
                        f"display: flex; align-items: center; justify-content: center; "
                        f"font-size: 20px; font-weight: bold; margin: auto;'>{num}</div>",
                        unsafe_allow_html=True
                    )
            
            with cols_boules[5]:
                st.markdown(
                    f"<div style='background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); "
                    f"color: white; border-radius: 50%; width: 50px; height: 50px; "
                    f"display: flex; align-items: center; justify-content: center; "
                    f"font-size: 20px; font-weight: bold; margin: auto;'>{dernier['numero_chance']}</div>",
                    unsafe_allow_html=True
                )
        
        with col2:
            if dernier.get("jackpot_euros"):
                st.metric("💰 Jackpot", f"{dernier['jackpot_euros']:,}€")


def afficher_statistiques_frequences(tirages: list):
    """Affiche les statistiques de fréquence"""
    if not tirages:
        st.warning("Pas assez de données pour les statistiques")
        return
    
    freq_data = calculer_frequences_numeros(tirages)
    frequences = freq_data.get("frequences", {})
    
    if not frequences:
        return
    
    chauds_froids = identifier_numeros_chauds_froids(frequences, nb_top=10)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 🔥 Numéros Chauds")
        st.caption("Les plus fréquents")
        for num in chauds_froids.get("chauds", [])[:5]:
            freq = frequences[num]["frequence"]
            pct = frequences[num]["pourcentage"]
            st.write(f"**{num}** - {freq} fois ({pct}%)")
    
    with col2:
        st.markdown("### ❄️ Numéros Froids")
        st.caption("Les moins fréquents")
        for num in chauds_froids.get("froids", [])[:5]:
            freq = frequences[num]["frequence"]
            pct = frequences[num]["pourcentage"]
            st.write(f"**{num}** - {freq} fois ({pct}%)")
    
    with col3:
        st.markdown("### ⏰ En Retard")
        st.caption("Pas sortis depuis longtemps")
        for num in chauds_froids.get("retard", [])[:5]:
            ecart = frequences[num]["ecart"]
            st.write(f"**{num}** - {ecart} tirages")
    
    st.divider()
    
    # Graphique de fréquence
    st.markdown("### 📊 Distribution des fréquences")
    
    nums = list(range(NUMERO_MIN, NUMERO_MAX + 1))
    freqs = [frequences.get(n, {}).get("frequence", 0) for n in nums]
    
    fig = go.Figure(data=[
        go.Bar(
            x=nums,
            y=freqs,
            marker_color=["#f5576c" if n in chauds_froids.get("chauds", [])[:10] 
                          else "#667eea" if n in chauds_froids.get("froids", [])[:10]
                          else "#95a5a6" for n in nums],
            hovertemplate="Numéro %{x}<br>Fréquence: %{y}<extra></extra>"
        )
    ])
    
    fig.update_layout(
        xaxis_title="Numéro",
        yaxis_title="Fréquence",
        height=300,
        margin=dict(l=20, r=20, t=20, b=40)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Avertissement
    st.warning(
        "⚠️ **Rappel**: Ces statistiques sont purement informatives. "
        "Chaque tirage est indépendant et aléatoire. "
        "Un numéro 'en retard' n'a pas plus de chances de sortir!"
    )


def afficher_generateur_grilles(tirages: list):
    """Interface de génération de grilles"""
    
    st.markdown("### 🎲 Générer une grille")
    
    # Préparer les données si disponibles
    freq_data = calculer_frequences_numeros(tirages) if tirages else {}
    patterns = analyser_patterns_tirages(tirages) if tirages else {}
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        strategie = st.selectbox(
            "Stratégie de génération",
            [
                ("🎲 Aléatoire", "aleatoire"),
                ("🧠 Éviter populaires (32-49)", "eviter_populaires"),
                ("⚖️ Équilibrée (somme moyenne)", "equilibree"),
                ("🔥 Numéros chauds", "chauds"),
                ("❄️ Numéros froids", "froids"),
                ("🔄 Mixte (chauds + froids)", "mixte"),
                ("✏️ Manuelle", "manuel")
            ],
            format_func=lambda x: x[0]
        )
    
    grille_generee = None
    
    if strategie[1] == "manuel":
        with col2:
            st.markdown("**Choisissez vos numéros:**")
        
        # Sélection manuelle
        numeros_selectionnes = st.multiselect(
            "5 numéros (1-49)",
            list(range(NUMERO_MIN, NUMERO_MAX + 1)),
            max_selections=5
        )
        
        chance = st.selectbox("Numéro Chance (1-10)", list(range(CHANCE_MIN, CHANCE_MAX + 1)))
        
        if len(numeros_selectionnes) == 5:
            grille_generee = {
                "numeros": sorted(numeros_selectionnes),
                "numero_chance": chance,
                "source": "manuel"
            }
    else:
        with col2:
            if st.button("🎲 Générer!", type="primary", use_container_width=True):
                if strategie[1] == "aleatoire":
                    grille_generee = generer_grille_aleatoire()
                elif strategie[1] == "eviter_populaires":
                    grille_generee = generer_grille_eviter_populaires()
                elif strategie[1] == "equilibree":
                    grille_generee = generer_grille_equilibree(patterns)
                elif strategie[1] in ["chauds", "froids", "mixte"]:
                    grille_generee = generer_grille_chauds_froids(
                        freq_data.get("frequences", {}), 
                        strategie[1]
                    )
    
    # Afficher la grille générée
    if grille_generee:
        st.divider()
        st.markdown("### ✨ Votre grille")
        
        with st.container(border=True):
            cols = st.columns(6)
            for i, num in enumerate(grille_generee["numeros"]):
                with cols[i]:
                    st.markdown(
                        f"<div style='background: #667eea; color: white; "
                        f"border-radius: 50%; width: 60px; height: 60px; "
                        f"display: flex; align-items: center; justify-content: center; "
                        f"font-size: 24px; font-weight: bold; margin: auto;'>{num}</div>",
                        unsafe_allow_html=True
                    )
            
            with cols[5]:
                st.markdown(
                    f"<div style='background: #f5576c; color: white; "
                    f"border-radius: 50%; width: 60px; height: 60px; "
                    f"display: flex; align-items: center; justify-content: center; "
                    f"font-size: 24px; font-weight: bold; margin: auto;'>{grille_generee['numero_chance']}</div>",
                    unsafe_allow_html=True
                )
            
            if grille_generee.get("note"):
                st.caption(grille_generee["note"])
            
            # Bouton enregistrer
            col_save, col_empty = st.columns([1, 2])
            with col_save:
                if st.button("💾 Enregistrer (virtuel)", use_container_width=True):
                    enregistrer_grille(
                        grille_generee["numeros"],
                        grille_generee["numero_chance"],
                        source=grille_generee.get("source", "ia"),
                        est_virtuelle=True
                    )
                    st.rerun()


def afficher_mes_grilles():
    """Affiche les grilles de l'utilisateur"""
    grilles = charger_grilles_utilisateur()
    
    if not grilles:
        st.info("📝 Aucune grille enregistrée. Générez-en une!")
        return
    
    # Stats globales
    total_mise = sum(float(g.get("mise", 0)) for g in grilles)
    total_gain = sum(float(g.get("gain", 0) or 0) for g in grilles if g.get("gain"))
    nb_gagnantes = sum(1 for g in grilles if g.get("rang"))
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🎫 Grilles jouées", len(grilles))
    with col2:
        st.metric("💸 Total misé", f"{total_mise:.2f}€")
    with col3:
        st.metric("💰 Total gagné", f"{total_gain:.2f}€")
    with col4:
        profit = total_gain - total_mise
        st.metric("📈 Bilan", f"{profit:+.2f}€", 
                  delta_color="normal" if profit >= 0 else "inverse")
    
    st.divider()
    
    # Liste des grilles
    for grille in grilles[:20]:
        with st.container(border=True):
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                st.write(f"🎫 {grille['numeros_str']}")
                st.caption(f"Source: {grille['source']} | {grille['date'].strftime('%d/%m/%Y')}")
            
            with col2:
                if grille.get("rang"):
                    st.success(f"🏆 Rang {grille['rang']}")
                    st.write(f"+{grille['gain']:.2f}€")
                elif grille.get("tirage_id"):
                    st.error("❌ Perdu")
                else:
                    st.warning("⏳ En attente")
            
            with col3:
                if grille.get("numeros_trouves") is not None:
                    st.write(f"✅ {grille['numeros_trouves']}/5")
                    if grille.get("chance_trouvee"):
                        st.write("+ Chance ✓")


def afficher_simulation():
    """Interface de simulation de stratégies"""
    
    st.markdown("### 🔬 Simulation de stratégies")
    st.caption("Testez différentes stratégies sur l'historique des tirages")
    
    tirages = charger_tirages(limite=500)
    
    if len(tirages) < 10:
        st.warning("⚠️ Pas assez de tirages pour une simulation fiable (minimum 10)")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        nb_tirages = st.slider("Nombre de tirages à simuler", 10, len(tirages), min(100, len(tirages)))
    
    with col2:
        grilles_par_tirage = st.slider("Grilles par tirage", 1, 10, 1)
    
    if st.button("🚀 Lancer la simulation", type="primary"):
        with st.spinner("Simulation en cours..."):
            freq_data = calculer_frequences_numeros(tirages[:nb_tirages])
            patterns = analyser_patterns_tirages(tirages[:nb_tirages])
            
            resultats = {}
            strategies = ["aleatoire", "eviter_populaires", "equilibree", "chauds", "froids"]
            
            progress = st.progress(0)
            
            for i, strat in enumerate(strategies):
                res = simuler_strategie(
                    tirages[:nb_tirages],
                    strategie=strat,
                    nb_grilles_par_tirage=grilles_par_tirage,
                    frequences=freq_data.get("frequences"),
                    patterns=patterns
                )
                resultats[strat] = res
                progress.progress((i + 1) / len(strategies))
            
            progress.empty()
        
        # Afficher résultats
        st.divider()
        st.markdown("### 📊 Résultats de la simulation")
        
        df_res = pd.DataFrame([
            {
                "Stratégie": strat,
                "Grilles": res["nb_grilles"],
                "Mise totale": f"{res['mises_totales']:.2f}€",
                "Gains": f"{res['gains_totaux']:.2f}€",
                "Profit": f"{res['profit']:+.2f}€",
                "ROI": f"{res['roi']:+.1f}%",
                "Gagnants": res["nb_gagnants"],
                "Taux": f"{res['taux_gain']:.1f}%"
            }
            for strat, res in resultats.items()
        ])
        
        st.dataframe(df_res, hide_index=True, use_container_width=True)
        
        # Graphique comparatif
        fig = go.Figure(data=[
            go.Bar(
                x=list(resultats.keys()),
                y=[r["roi"] for r in resultats.values()],
                marker_color=["#4CAF50" if r["roi"] > 0 else "#f44336" for r in resultats.values()],
                text=[f"{r['roi']:+.1f}%" for r in resultats.values()],
                textposition="auto"
            )
        ])
        
        fig.update_layout(
            title="Comparaison des ROI par stratégie",
            xaxis_title="Stratégie",
            yaxis_title="ROI (%)",
            height=300
        )
        fig.add_hline(y=0, line_dash="dash", line_color="gray")
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Conclusion
        st.info(
            "💡 **Conclusion**: Les résultats varient aléatoirement d'une simulation à l'autre. "
            "Sur le long terme, aucune stratégie ne bat la probabilité mathématique. "
            "Le Loto reste un jeu de hasard avec une espérance négative."
        )


def afficher_gestion_tirages():
    """Interface pour gérer les tirages"""
    
    st.markdown("### ➕ Ajouter un tirage")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        date_tirage = st.date_input("Date du tirage", value=date.today())
        
        st.write("**Numéros (1-49):**")
        cols_num = st.columns(5)
        numeros = []
        for i in range(5):
            with cols_num[i]:
                num = st.number_input(f"N°{i+1}", NUMERO_MIN, NUMERO_MAX, 
                                     value=random.randint(NUMERO_MIN, NUMERO_MAX),
                                     key=f"tirage_num_{i}")
                numeros.append(num)
    
    with col2:
        chance = st.number_input("N° Chance (1-10)", CHANCE_MIN, CHANCE_MAX, value=1)
        jackpot = st.number_input("Jackpot (€)", 0, 100_000_000, value=2_000_000, step=1_000_000)
    
    # Validation
    if len(set(numeros)) != 5:
        st.warning("⚠️ Les 5 numéros doivent être différents")
    else:
        if st.button("💾 Enregistrer le tirage", type="primary"):
            ajouter_tirage(date_tirage, numeros, chance, jackpot)
            st.rerun()
    
    st.divider()
    
    # Historique
    st.markdown("### 📜 Historique des tirages")
    tirages = charger_tirages(limite=20)
    
    if tirages:
        df = pd.DataFrame([
            {
                "Date": t["date_tirage"],
                "Numéros": t["numeros_str"],
                "Jackpot": f"{t['jackpot_euros']:,}€" if t.get("jackpot_euros") else "-"
            }
            for t in tirages
        ])
        st.dataframe(df, hide_index=True, use_container_width=True)
    else:
        st.info("Aucun tirage enregistré")


def afficher_esperance():
    """Affiche l'espérance mathématique du Loto"""
    
    esp = calculer_esperance_mathematique()
    
    st.markdown("### 📐 Mathématiques du Loto")
    
    with st.container(border=True):
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("💸 Coût grille", f"{esp['cout_grille']:.2f}€")
            st.metric("📉 Espérance", f"{esp['esperance']:+.4f}€")
        
        with col2:
            st.metric("🎯 Gains espérés", f"{esp['gains_esperes']:.4f}€")
            st.metric("📊 Perte moyenne", f"{esp['perte_moyenne_pct']:.1f}%")
        
        st.info(esp["conclusion"])
    
    st.divider()
    
    st.markdown("### 🎲 Probabilités de gain")
    
    df_probas = pd.DataFrame([
        {"Rang": rang, "Gains": f"{GAINS_PAR_RANG.get(rang, 'Jackpot'):,}€" if GAINS_PAR_RANG.get(rang) else "Jackpot", "Probabilité": proba}
        for rang, proba in esp["probabilites"].items()
    ])
    
    st.dataframe(df_probas, hide_index=True, use_container_width=True)
    
    st.warning(
        "⚠️ **Rappel**: Vous avez plus de chances de mourir d'une chute de météorite (1/700 000) "
        "que de gagner le jackpot du Loto (1/19 068 840)!"
    )


# ═══════════════════════════════════════════════════════════════════
# POINT D'ENTRÉE
# ═══════════════════════════════════════════════════════════════════

def app():
    """Point d'entrée du module Loto"""
    
    st.title("🎰 Loto - Analyse & Simulation")
    st.caption("Analysez les statistiques et testez vos stratégies (virtuellement)")
    
    # Avertissement
    with st.expander("⚠️ Avertissement important", expanded=False):
        st.markdown("""
        **Le Loto est un jeu de hasard pur.**
        
        - Chaque tirage est **totalement indépendant** des précédents
        - Un numéro "en retard" n'a **pas plus de chances** de sortir
        - Aucune stratégie ne peut **prédire** les résultats
        - L'espérance mathématique est **négative** (vous perdez en moyenne)
        
        Ce module est à but **éducatif et de divertissement**. 
        Ne jouez que ce que vous pouvez vous permettre de perdre.
        """)
    
    # Charger données
    tirages = charger_tirages(limite=200)
    
    # Tabs principaux
    tabs = st.tabs([
        "📊 Statistiques", 
        "🎲 Générer Grille",
        "🎫 Mes Grilles",
        "🔬 Simulation",
        "📐 Maths",
        "⚙️ Tirages"
    ])
    
    # ═══════════════════════════════════════════════════════════════
    # TAB 1: STATISTIQUES
    # ═══════════════════════════════════════════════════════════════
    with tabs[0]:
        afficher_dernier_tirage(tirages)
        st.divider()
        afficher_statistiques_frequences(tirages)
    
    # ═══════════════════════════════════════════════════════════════
    # TAB 2: GÉNÉRATION
    # ═══════════════════════════════════════════════════════════════
    with tabs[1]:
        afficher_generateur_grilles(tirages)
    
    # ═══════════════════════════════════════════════════════════════
    # TAB 3: MES GRILLES
    # ═══════════════════════════════════════════════════════════════
    with tabs[2]:
        afficher_mes_grilles()
    
    # ═══════════════════════════════════════════════════════════════
    # TAB 4: SIMULATION
    # ═══════════════════════════════════════════════════════════════
    with tabs[3]:
        afficher_simulation()
    
    # ═══════════════════════════════════════════════════════════════
    # TAB 5: MATHÉMATIQUES
    # ═══════════════════════════════════════════════════════════════
    with tabs[4]:
        afficher_esperance()
    
    # ═══════════════════════════════════════════════════════════════
    # TAB 6: GESTION TIRAGES
    # ═══════════════════════════════════════════════════════════════
    with tabs[5]:
        afficher_gestion_tirages()


# Alias
def main():
    app()


if __name__ == "__main__":
    app()
