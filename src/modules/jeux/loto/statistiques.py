"""
Module Loto - Composants UI de statistiques
"""

from ._common import (
    st, pd, go,
    NUMERO_MIN, NUMERO_MAX, GAINS_PAR_RANG,
    calculer_frequences_numeros, identifier_numeros_chauds_froids,
    calculer_esperance_mathematique
)


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
    
    st.plotly_chart(fig, width="stretch", key="loto_freq_chart")
    
    # Avertissement
    st.warning(
        "⚠️ **Rappel**: Ces statistiques sont purement informatives. "
        "Chaque tirage est indépendant et aléatoire. "
        "Un numéro 'en retard' n'a pas plus de chances de sortir!"
    )


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
    
    st.dataframe(df_probas, hide_index=True, width="stretch")
    
    st.warning(
        "⚠️ **Rappel**: Vous avez plus de chances de mourir d'une chute de météorite (1/700 000) "
        "que de gagner le jackpot du Loto (1/19 068 840)!"
    )
