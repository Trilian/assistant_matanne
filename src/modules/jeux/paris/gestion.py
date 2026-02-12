"""
Interface de gestion des equipes et matchs.
"""

from .utils import (
    st, date, timedelta,
    obtenir_contexte_db, Match,
    CHAMPIONNATS,
)
from .utilitaires import charger_equipes
from .crud import ajouter_equipe, ajouter_match, enregistrer_resultat_match, supprimer_match


def afficher_gestion_donnees():
    """Interface pour gerer les equipes et matchs"""
    
    tab1, tab2, tab3, tab4 = st.tabs(["➕ Ajouter Équipe", "➕ Ajouter Match", "📝 Resultats", "🗑️ Supprimer"])
    
    with tab1:
        st.subheader("Ajouter une equipe")
        
        col1, col2 = st.columns(2)
        with col1:
            nom_equipe = st.text_input("Nom de l'equipe", key="new_team_name")
        with col2:
            championnat = st.selectbox("Championnat", CHAMPIONNATS, key="new_team_champ")
        
        if st.button("Ajouter l'equipe", type="primary"):
            if nom_equipe:
                ajouter_equipe(nom_equipe, championnat)
            else:
                st.warning("Veuillez entrer un nom d'equipe")
    
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
                ext_nom = st.selectbox("Équipe exterieur", ext_options, key="ext_sel")
            
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
            st.warning("Ajoutez au moins 2 equipes pour creer un match")
    
    with tab3:
        st.subheader("Enregistrer un resultat")
        
        try:
            with obtenir_contexte_db() as session:
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
                    st.info("Aucun match en attente de resultat")
        except Exception as e:
            st.error(f"Erreur: {e}")
    
    with tab4:
        st.subheader("🗑️ Supprimer des matchs")
        st.caption("Supprime un match et tous les paris associes")
        
        try:
            with obtenir_contexte_db() as session:
                tous_matchs = session.query(Match).order_by(Match.date_match.desc()).limit(50).all()
                
                if tous_matchs:
                    champ_filter = st.selectbox(
                        "Filtrer par championnat", 
                        ["Tous"] + CHAMPIONNATS,
                        key="del_champ_filter"
                    )
                    
                    matchs_affiches = [
                        m for m in tous_matchs 
                        if champ_filter == "Tous" or m.championnat == champ_filter
                    ]
                    
                    if matchs_affiches:
                        for m in matchs_affiches:
                            dom = m.equipe_domicile.nom if m.equipe_domicile else "?"
                            ext = m.equipe_exterieur.nom if m.equipe_exterieur else "?"
                            statut = "✅ Joue" if m.joue else "⏳ À venir"
                            score = f"({m.score_domicile}-{m.score_exterieur})" if m.joue else ""
                            
                            col1, col2 = st.columns([4, 1])
                            with col1:
                                st.write(f"**{dom}** vs **{ext}** {score}")
                                st.caption(f"{m.date_match} | {m.championnat} | {statut}")
                            with col2:
                                if st.button("🗑️", key=f"del_{m.id}", help="Supprimer ce match"):
                                    if supprimer_match(m.id):
                                        st.success("Match supprime!")
                                        st.rerun()
                                    else:
                                        st.error("Erreur lors de la suppression")
                            st.divider()
                    else:
                        st.info(f"Aucun match pour {champ_filter}")
                else:
                    st.info("Aucun match enregistre")
        except Exception as e:
            st.error(f"Erreur: {e}")


__all__ = ["afficher_gestion_donnees"]

