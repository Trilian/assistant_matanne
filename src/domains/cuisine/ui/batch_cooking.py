"""
Module Batch Cooking - Interface utilisateur complète
 
Fonctionnalités:
- 🗓️ Configuration et planification des sessions
- 🍳 Mode cuisine interactif avec étapes et timers
- 📦 Gestion des préparations stockées
- 🤖 Génération IA de plans optimisés
- 👶 Mode Jules (adaptation pour cuisiner avec bébé)
"""

import streamlit as st
from datetime import date, datetime, time, timedelta
import logging

from src.services.batch_cooking import get_batch_cooking_service, ROBOTS_DISPONIBLES, JOURS_SEMAINE
from src.services.recettes import get_recette_service
from src.core.database import obtenir_contexte_db
from src.core.models import (
    Recette,
    SessionBatchCooking,
    EtapeBatchCooking,
    PreparationBatch,
    StatutSessionEnum,
    StatutEtapeEnum,
)
from src.domains.cuisine.logic.batch_cooking_logic import (
    formater_duree,
    calculer_duree_totale_optimisee,
    calculer_statistiques_session,
    identifier_moments_jules,
    generer_planning_jules,
    ROBOTS_INFO,
    LOCALISATIONS,
)

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════════
# POINT D'ENTRÉE
# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════════


def app():
    """Point d'entrée module batch cooking"""
    st.title("🍳 Batch Cooking")
    st.caption("Préparez vos repas de la semaine en une session organisée")
    
    # Vérifier si session en cours
    service = get_batch_cooking_service()
    session_active = service.get_session_active()
    
    if session_active:
        # Mode cuisine actif
        render_mode_cuisine(session_active)
    else:
        # Tabs normaux
        tabs = st.tabs([
            "📋 Planifier", 
            "📅 Sessions", 
            "📦 Préparations", 
            "⚙️ Configuration"
        ])
        
        with tabs[0]:
            render_planifier()
        
        with tabs[1]:
            render_sessions()
        
        with tabs[2]:
            render_preparations()
        
        with tabs[3]:
            render_configuration()


# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════════
# SECTION 1: PLANIFIER UNE SESSION
# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════════


def render_planifier():
    """Interface de planification d'une nouvelle session"""
    service = get_batch_cooking_service()
    config = service.get_config()
    
    st.subheader("📋 Nouvelle Session Batch Cooking")
    
    # Step 1: Date et configuration
    col1, col2 = st.columns(2)
    
    with col1:
        # Suggérer les prochains jours de batch
        jours_suggeres = config.jours_batch if config else [6]
        today = date.today()
        prochaine_date = today
        
        for i in range(7):
            check_date = today + timedelta(days=i)
            if check_date.weekday() in jours_suggeres:
                prochaine_date = check_date
                break
        
        date_session = st.date_input(
            "📅 Date de la session",
            value=prochaine_date,
            min_value=today,
            format="DD/MM/YYYY",
        )
        
        jour_nom = JOURS_SEMAINE[date_session.weekday()]
        if date_session.weekday() in jours_suggeres:
            st.success(f"✅ {jour_nom} - Jour de batch habituel")
        else:
            st.info(f"ℹ️ {jour_nom} - Jour inhabituel pour le batch")
    
    with col2:
        heure_debut = st.time_input(
            "⏰ Heure de début",
            value=config.heure_debut_preferee if config else time(10, 0),
        )
        
        avec_jules = st.toggle(
            "👶 Jules sera présent",
            value=config.avec_jules_par_defaut if config else True,
            help="Active les conseils de sécurité et identifie les moments où Jules peut participer"
        )
    
    st.divider()
    
    # Step 2: Sélection des robots
    st.subheader("🤖 Équipements disponibles")
    
    robots_defaut = config.robots_disponibles if config else ["four", "plaques"]
    
    cols = st.columns(3)
    robots_selectionnes = []
    
    for i, (robot_id, robot_info) in enumerate(ROBOTS_INFO.items()):
        with cols[i % 3]:
            checked = st.checkbox(
                f"{robot_info['emoji']} {robot_info['nom']}",
                value=robot_id in robots_defaut,
                key=f"robot_{robot_id}",
                help=robot_info['description']
            )
            if checked:
                robots_selectionnes.append(robot_id)
    
    st.divider()
    
    # Step 3: Sélection des recettes
    st.subheader("🍽️ Recettes à préparer")
    
    # Récupérer les recettes compatibles batch
    with obtenir_contexte_db() as db:
        recettes_batch = db.query(Recette).filter(
            Recette.compatible_batch == True
        ).order_by(Recette.nom).all()
        
        # Filtrer pour bébé si Jules présent
        if avec_jules:
            recettes_bebe = db.query(Recette).filter(
                Recette.compatible_bebe == True,
                Recette.compatible_batch == True
            ).order_by(Recette.nom).all()
            
            if recettes_bebe:
                st.info(f"👶 {len(recettes_bebe)} recettes compatibles bébé disponibles")
        
        all_recettes = db.query(Recette).order_by(Recette.nom).all()
    
    # Option: suggestions IA ou sélection manuelle
    mode_selection = st.radio(
        "Mode de sélection",
        ["🤖 Suggestions IA", "✏️ Sélection manuelle"],
        horizontal=True,
    )
    
    recettes_selectionnees = []
    
    if mode_selection == "🤖 Suggestions IA":
        col1, col2 = st.columns([3, 1])
        with col1:
            nb_recettes = st.slider("Nombre de recettes", 2, 6, 4)
        with col2:
            if st.button("🔮 Suggérer", type="primary"):
                with st.spinner("Recherche des meilleures recettes..."):
                    suggestions = service.suggerer_recettes_batch(
                        nb_recettes=nb_recettes,
                        robots_disponibles=robots_selectionnes,
                        avec_jules=avec_jules,
                    )
                    if suggestions:
                        st.session_state.recettes_suggerees = [r.id for r in suggestions]
                        st.success(f"✅ {len(suggestions)} recettes suggérées!")
        
        if "recettes_suggerees" in st.session_state:
            recettes_ids = st.session_state.recettes_suggerees
            for recette in [r for r in all_recettes if r.id in recettes_ids]:
                _afficher_carte_recette(recette, avec_jules)
                recettes_selectionnees.append(recette.id)
    
    else:
        # Sélection manuelle avec filtres
        col1, col2 = st.columns(2)
        with col1:
            filtre_batch = st.checkbox("Compatible batch uniquement", value=True)
        with col2:
            filtre_bebe = st.checkbox("Compatible bébé", value=avec_jules)
        
        recettes_filtrees = all_recettes
        if filtre_batch:
            recettes_filtrees = [r for r in recettes_filtrees if r.compatible_batch]
        if filtre_bebe:
            recettes_filtrees = [r for r in recettes_filtrees if r.compatible_bebe]
        
        recettes_options = {r.nom: r.id for r in recettes_filtrees}
        
        selection = st.multiselect(
            "Sélectionner les recettes",
            options=list(recettes_options.keys()),
            max_selections=8,
            help="Choisissez entre 2 et 8 recettes"
        )
        
        recettes_selectionnees = [recettes_options[nom] for nom in selection]
        
        # Afficher les recettes sélectionnées
        for nom in selection:
            recette = next((r for r in recettes_filtrees if r.nom == nom), None)
            if recette:
                _afficher_carte_recette(recette, avec_jules)
    
    st.divider()
    
    # Step 4: Génération du plan
    if recettes_selectionnees:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("📊 Recettes", len(recettes_selectionnees))
        with col2:
            st.metric("🤖 Robots", len(robots_selectionnes))
        with col3:
            st.metric("👶 Mode Jules", "Oui" if avec_jules else "Non")
        
        st.divider()
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🤖 Générer plan IA optimisé", use_container_width=True, type="primary"):
                with st.spinner("🧠 L'IA optimise votre session..."):
                    plan_ia = service.generer_plan_ia(
                        recettes_ids=recettes_selectionnees,
                        robots_disponibles=robots_selectionnes,
                        avec_jules=avec_jules,
                    )
                    
                    if plan_ia:
                        st.session_state.plan_ia = plan_ia
                        st.success(f"✅ Plan généré! Durée estimée: {formater_duree(plan_ia.duree_totale_estimee)}")
                    else:
                        st.error("❌ Erreur lors de la génération du plan")
        
        with col2:
            if st.button("📋 Créer session simple", use_container_width=True):
                session = service.creer_session(
                    date_session=date_session,
                    recettes_ids=recettes_selectionnees,
                    avec_jules=avec_jules,
                    robots=robots_selectionnes,
                    heure_debut=heure_debut,
                )
                if session:
                    st.success(f"✅ Session créée: {session.nom}")
                    st.rerun()
        
        # Afficher le plan IA s'il existe
        if "plan_ia" in st.session_state:
            _afficher_plan_ia(st.session_state.plan_ia, avec_jules)
            
            if st.button("✅ Créer cette session", use_container_width=True, type="primary"):
                plan = st.session_state.plan_ia
                
                # Créer la session
                session = service.creer_session(
                    date_session=date_session,
                    recettes_ids=recettes_selectionnees,
                    avec_jules=avec_jules,
                    robots=robots_selectionnes,
                    heure_debut=heure_debut,
                )
                
                if session:
                    # Ajouter les étapes
                    etapes_data = []
                    for etape in plan.etapes:
                        etapes_data.append({
                            "ordre": etape.ordre,
                            "titre": etape.titre,
                            "description": etape.description,
                            "duree_minutes": etape.duree_minutes,
                            "robots": etape.robots,
                            "groupe_parallele": etape.groupe_parallele,
                            "est_supervision": etape.est_supervision,
                            "alerte_bruit": etape.alerte_bruit,
                            "temperature": etape.temperature,
                        })
                    
                    service.ajouter_etapes(session.id, etapes_data)
                    
                    # Nettoyer session state
                    del st.session_state.plan_ia
                    if "recettes_suggerees" in st.session_state:
                        del st.session_state.recettes_suggerees
                    
                    st.success(f"✅ Session créée avec {len(etapes_data)} étapes!")
                    st.rerun()
    
    else:
        st.info("👆 Sélectionnez au moins 2 recettes pour créer une session")


def _afficher_carte_recette(recette: Recette, avec_jules: bool):
    """Affiche une carte de recette"""
    with st.container():
        col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
        
        with col1:
            badges = []
            if recette.compatible_batch:
                badges.append("📦 Batch")
            if recette.congelable:
                badges.append("❄️ Congel.")
            if avec_jules and recette.compatible_bebe:
                badges.append("👶 Bébé")
            
            st.write(f"**{recette.nom}** {' '.join(badges)}")
        
        with col2:
            st.caption(f"⏱️ {recette.temps_total} min")
        
        with col3:
            st.caption(f"🍽️ {recette.portions} pers.")
        
        with col4:
            if recette.robots_compatibles:
                robots_emojis = " ".join([
                    ROBOTS_INFO.get(r.lower().replace(" ", "_"), {}).get("emoji", "🔧") 
                    for r in recette.robots_compatibles
                ])
                st.caption(robots_emojis)


def _afficher_plan_ia(plan, avec_jules: bool):
    """Affiche le plan généré par l'IA"""
    st.subheader("📋 Plan optimisé par l'IA")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("⏱️ Durée estimée", formater_duree(plan.duree_totale_estimee))
    with col2:
        st.metric("📊 Étapes", len(plan.etapes))
    
    # Conseils Jules
    if avec_jules and plan.conseils_jules:
        st.info("👶 **Conseils pour cuisiner avec Jules:**\n" + "\n".join([f"• {c}" for c in plan.conseils_jules]))
    
    # Ordre optimal
    if plan.ordre_optimal:
        st.success(f"💡 **Stratégie:** {plan.ordre_optimal}")
    
    # Aperçu des étapes
    with st.expander("👀 Voir les étapes", expanded=False):
        groupe_actuel = -1
        
        for etape in plan.etapes:
            if etape.groupe_parallele != groupe_actuel:
                if groupe_actuel >= 0:
                    st.divider()
                groupe_actuel = etape.groupe_parallele
                st.caption(f"**Groupe {groupe_actuel + 1}** (étapes parallèles)")
            
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                icons = []
                if etape.est_supervision:
                    icons.append("👁️")
                if etape.alerte_bruit:
                    icons.append("🔊")
                if etape.temperature:
                    icons.append(f"🌡️{etape.temperature}°C")
                
                st.write(f"{etape.ordre}. **{etape.titre}** {' '.join(icons)}")
                st.caption(etape.description[:100] + "..." if len(etape.description) > 100 else etape.description)
            
            with col2:
                st.caption(f"⏱️ {etape.duree_minutes} min")
            
            with col3:
                if etape.robots:
                    robots_emojis = " ".join([
                        ROBOTS_INFO.get(r, {}).get("emoji", "🔧") 
                        for r in etape.robots
                    ])
                    st.caption(robots_emojis)


# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════════
# SECTION 2: MODE CUISINE (SESSION EN COURS)
# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════════


def render_mode_cuisine(session: SessionBatchCooking):
    """Interface de cuisine interactive avec étapes et timers"""
    service = get_batch_cooking_service()
    
    # Header avec progression
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        st.subheader(f"🍳 {session.nom}")
        progression = session.progression
        st.progress(progression / 100, text=f"Progression: {progression:.0f}%")
    
    with col2:
        if session.avec_jules:
            st.info("👶 **Mode Jules activé** - Conseils de sécurité affichés")
    
    with col3:
        if st.button("⏹️ Terminer", type="secondary"):
            st.session_state.confirmer_fin = True
    
    # Confirmation de fin
    if st.session_state.get("confirmer_fin"):
        st.warning("⚠️ Voulez-vous vraiment terminer cette session?")
        col1, col2 = st.columns(2)
        with col1:
            notes = st.text_area("Notes de fin de session (optionnel)")
        with col2:
            if st.button("✅ Confirmer", type="primary"):
                service.terminer_session(session.id, notes_apres=notes)
                del st.session_state.confirmer_fin
                st.success("✅ Session terminée!")
                st.rerun()
            if st.button("❌ Annuler"):
                del st.session_state.confirmer_fin
                st.rerun()
        return
    
    st.divider()
    
    # Vue des étapes
    etapes = sorted(session.etapes, key=lambda e: e.ordre)
    
    # Identifier l'étape courante
    etape_courante = None
    for etape in etapes:
        if etape.statut == StatutEtapeEnum.EN_COURS.value:
            etape_courante = etape
            break
    
    if not etape_courante:
        # Trouver la prochaine étape à faire
        for etape in etapes:
            if etape.statut == StatutEtapeEnum.A_FAIRE.value:
                etape_courante = etape
                break
    
    # Afficher les robots actifs
    robots_actifs = set()
    for etape in etapes:
        if etape.statut == StatutEtapeEnum.EN_COURS.value and etape.robots_requis:
            robots_actifs.update(etape.robots_requis)
    
    if robots_actifs:
        st.subheader("🤖 Équipements en cours d'utilisation")
        cols = st.columns(len(robots_actifs))
        for i, robot_id in enumerate(robots_actifs):
            robot_info = ROBOTS_INFO.get(robot_id, {"nom": robot_id, "emoji": "🔧"})
            with cols[i]:
                st.metric(
                    f"{robot_info['emoji']} {robot_info['nom']}", 
                    "🔴 Actif",
                )
    
    st.divider()
    
    # Afficher l'étape courante en grand
    if etape_courante:
        _afficher_etape_principale(etape_courante, session.avec_jules, service)
    else:
        st.success("🎉 Toutes les étapes sont terminées!")
        if st.button("📦 Enregistrer les préparations", type="primary", use_container_width=True):
            st.session_state.show_preparations = True
    
    st.divider()
    
    # Liste des étapes (vue d'ensemble)
    st.subheader("📋 Toutes les étapes")
    
    # Grouper par groupe parallèle
    groupes = {}
    for etape in etapes:
        groupe = etape.groupe_parallele
        if groupe not in groupes:
            groupes[groupe] = []
        groupes[groupe].append(etape)
    
    for groupe_id in sorted(groupes.keys()):
        etapes_groupe = groupes[groupe_id]
        
        with st.expander(
            f"**Groupe {groupe_id + 1}** - {len(etapes_groupe)} étape(s)", 
            expanded=(etape_courante and etape_courante.groupe_parallele == groupe_id)
        ):
            for etape in etapes_groupe:
                _afficher_etape_liste(etape, service)


def _afficher_etape_principale(etape: EtapeBatchCooking, avec_jules: bool, service):
    """Affiche l'étape courante en grand avec timer"""
    
    # Statut et indicateurs
    col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
    
    with col1:
        statut_emoji = {
            StatutEtapeEnum.A_FAIRE.value: "⏳",
            StatutEtapeEnum.EN_COURS.value: "🔥",
            StatutEtapeEnum.TERMINEE.value: "✅",
            StatutEtapeEnum.PASSEE.value: "⏭️",
        }
        st.subheader(f"{statut_emoji.get(etape.statut, '❓')} Étape {etape.ordre}: {etape.titre}")
    
    with col2:
        st.metric("⏱️ Durée", f"{etape.duree_minutes} min")
    
    with col3:
        if etape.temperature:
            st.metric("🌡️ Temp.", f"{etape.temperature}°C")
    
    with col4:
        if etape.robots_requis:
            robots_text = " ".join([
                ROBOTS_INFO.get(r, {}).get("emoji", "🔧") 
                for r in etape.robots_requis
            ])
            st.write(robots_text)
    
    # Alertes
    if etape.alerte_bruit:
        st.warning("🔊 **Étape bruyante** - Attention si Jules fait la sieste!")
    
    if etape.est_supervision:
        st.info("👁️ **Étape de supervision** - Vous pouvez faire autre chose pendant ce temps")
    
    # Description
    st.markdown(f"**Instructions:**\n\n{etape.description}")
    
    # Conseils Jules
    if avec_jules:
        conseils = _generer_conseils_jules_etape(etape)
        if conseils:
            st.success(f"👶 **Conseil Jules:** {conseils}")
    
    st.divider()
    
    # Boutons d'action
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if etape.statut == StatutEtapeEnum.A_FAIRE.value:
            if st.button("▶️ Démarrer", type="primary", use_container_width=True):
                service.demarrer_etape(etape.id)
                st.rerun()
    
    with col2:
        if etape.statut == StatutEtapeEnum.EN_COURS.value:
            if st.button("✅ Terminé", type="primary", use_container_width=True):
                service.terminer_etape(etape.id)
                st.rerun()
    
    with col3:
        if etape.statut in [StatutEtapeEnum.A_FAIRE.value, StatutEtapeEnum.EN_COURS.value]:
            if st.button("⏭️ Passer", use_container_width=True):
                service.passer_etape(etape.id)
                st.rerun()
    
    # Timer visuel
    if etape.statut == StatutEtapeEnum.EN_COURS.value and etape.heure_debut:
        temps_ecoule = (datetime.now() - etape.heure_debut).total_seconds() / 60
        temps_restant = max(0, etape.duree_minutes - temps_ecoule)
        
        if temps_restant > 0:
            st.progress(
                min(temps_ecoule / etape.duree_minutes, 1.0),
                text=f"⏱️ Temps restant: {formater_duree(int(temps_restant))}"
            )
        else:
            st.warning(f"⏰ Temps dépassé de {formater_duree(int(-temps_restant))}!")


def _afficher_etape_liste(etape: EtapeBatchCooking, service):
    """Affiche une étape dans la liste compacte"""
    statut_emoji = {
        StatutEtapeEnum.A_FAIRE.value: "⏳",
        StatutEtapeEnum.EN_COURS.value: "🔥",
        StatutEtapeEnum.TERMINEE.value: "✅",
        StatutEtapeEnum.PASSEE.value: "⏭️",
    }
    
    col1, col2, col3, col4 = st.columns([0.5, 3, 1, 1])
    
    with col1:
        st.write(statut_emoji.get(etape.statut, "❓"))
    
    with col2:
        titre = etape.titre
        if etape.alerte_bruit:
            titre += " 🔊"
        if etape.est_supervision:
            titre += " 👁️"
        st.write(f"**{etape.ordre}.** {titre}")
    
    with col3:
        st.caption(f"⏱️ {etape.duree_minutes} min")
    
    with col4:
        if etape.robots_requis:
            robots_text = " ".join([
                ROBOTS_INFO.get(r, {}).get("emoji", "🔧") 
                for r in etape.robots_requis
            ])
            st.caption(robots_text)


def _generer_conseils_jules_etape(etape: EtapeBatchCooking) -> str | None:
    """Génère un conseil pour Jules basé sur l'étape"""
    titre_lower = etape.titre.lower() if etape.titre else ""
    description_lower = etape.description.lower() if etape.description else ""
    
    # Activités où Jules peut participer
    if any(mot in titre_lower or mot in description_lower for mot in ["mélanger", "remuer", "touiller"]):
        return "Jules peut aider à mélanger avec une cuillère en bois!"
    
    if any(mot in titre_lower or mot in description_lower for mot in ["verser", "ajouter"]):
        return "Jules peut verser les ingrédients dans le bol avec votre aide"
    
    if any(mot in titre_lower or mot in description_lower for mot in ["décorer", "garnir"]):
        return "Super moment pour que Jules décore avec vous!"
    
    # Activités dangereuses
    if etape.temperature and etape.temperature > 100:
        return "⚠️ Température élevée - Garder Jules à distance"
    
    if any(mot in titre_lower or mot in description_lower for mot in ["couper", "trancher", "hacher"]):
        return "⚠️ Couteaux utilisés - Installer Jules en sécurité"
    
    if etape.alerte_bruit:
        return "🔊 Bruit - Prévenir Jules ou attendre qu'il soit occupé"
    
    if etape.est_supervision:
        return "👀 Moment idéal pour jouer avec Jules pendant la cuisson!"
    
    return None


# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════════
# SECTION 3: GESTION DES SESSIONS
# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════════


def render_sessions():
    """Liste et gestion des sessions batch cooking"""
    service = get_batch_cooking_service()
    
    st.subheader("📅 Sessions Batch Cooking")
    
    # Filtres
    col1, col2 = st.columns(2)
    with col1:
        date_debut = st.date_input(
            "Du",
            value=date.today() - timedelta(days=30),
        )
    with col2:
        date_fin = st.date_input(
            "Au",
            value=date.today() + timedelta(days=30),
        )
    
    # Sessions planifiées
    st.subheader("📋 Sessions planifiées")
    sessions_planifiees = service.get_sessions_planifiees(date_debut, date_fin)
    
    if sessions_planifiees:
        for session in sessions_planifiees:
            _afficher_carte_session(session, service)
    else:
        st.info("Aucune session planifiée")
        if st.button("➕ Planifier une session", use_container_width=True):
            st.session_state.go_to_planifier = True
    
    st.divider()
    
    # Historique
    st.subheader("📚 Historique")
    
    with obtenir_contexte_db() as db:
        sessions_terminees = (
            db.query(SessionBatchCooking)
            .filter(
                SessionBatchCooking.statut == StatutSessionEnum.TERMINEE.value,
                SessionBatchCooking.date_session >= date_debut,
                SessionBatchCooking.date_session <= date_fin,
            )
            .order_by(SessionBatchCooking.date_session.desc())
            .all()
        )
    
    if sessions_terminees:
        for session in sessions_terminees:
            with st.expander(f"✅ {session.nom} - {session.date_session.strftime('%d/%m/%Y')}"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    duree = session.duree_reelle or session.duree_estimee
                    st.metric("⏱️ Durée", formater_duree(duree))
                with col2:
                    st.metric("🍽️ Recettes", session.nb_recettes_completees)
                with col3:
                    st.metric("📦 Portions", session.nb_portions_preparees)
                
                if session.notes_apres:
                    st.info(f"📝 Notes: {session.notes_apres}")
    else:
        st.info("Aucune session terminée dans cette période")


def _afficher_carte_session(session: SessionBatchCooking, service):
    """Affiche une carte de session"""
    with st.container():
        col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
        
        with col1:
            jour_nom = JOURS_SEMAINE[session.date_session.weekday()]
            st.write(f"**{session.nom}**")
            st.caption(f"📅 {jour_nom} {session.date_session.strftime('%d/%m/%Y')} à {session.heure_debut.strftime('%H:%M') if session.heure_debut else '?'}")
        
        with col2:
            nb_recettes = len(session.recettes_selectionnees) if session.recettes_selectionnees else 0
            st.metric("🍽️", nb_recettes)
        
        with col3:
            if session.avec_jules:
                st.write("👶")
        
        with col4:
            if st.button("▶️ Démarrer", key=f"start_{session.id}", type="primary"):
                service.demarrer_session(session.id)
                st.rerun()
        
        st.divider()


# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════════
# SECTION 4: PRÉPARATIONS STOCKÉES
# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════════


def render_preparations():
    """Gestion des préparations stockées"""
    service = get_batch_cooking_service()
    
    st.subheader("📦 Préparations stockées")
    
    # Alertes péremption
    alertes = service.get_preparations_alertes()
    if alertes:
        st.error(f"⚠️ **{len(alertes)} préparation(s) proche(s) de la péremption!**")
        for prep in alertes:
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                loc_info = LOCALISATIONS.get(prep.localisation, {})
                st.write(f"{loc_info.get('emoji', '📦')} **{prep.nom}** - {prep.portions_restantes} portions")
            with col2:
                jours = prep.jours_avant_peremption
                if jours < 0:
                    st.error(f"⚠️ Périmé!")
                elif jours == 0:
                    st.warning(f"Aujourd'hui!")
                else:
                    st.warning(f"J-{jours}")
            with col3:
                if st.button("✅ Consommé", key=f"consume_alert_{prep.id}"):
                    service.consommer_preparation(prep.id, prep.portions_restantes)
                    st.rerun()
        
        st.divider()
    
    # Filtres
    col1, col2 = st.columns(2)
    with col1:
        localisation_filtre = st.selectbox(
            "Localisation",
            ["Tous"] + [loc["nom"] for loc in LOCALISATIONS.values()],
        )
    with col2:
        show_consommees = st.checkbox("Afficher consommées")
    
    # Mapper le filtre
    loc_key = None
    if localisation_filtre != "Tous":
        for key, val in LOCALISATIONS.items():
            if val["nom"] == localisation_filtre:
                loc_key = key
                break
    
    preparations = service.get_preparations(consommees=show_consommees, localisation=loc_key)
    
    if preparations:
        # Grouper par localisation
        par_localisation = {}
        for prep in preparations:
            loc = prep.localisation
            if loc not in par_localisation:
                par_localisation[loc] = []
            par_localisation[loc].append(prep)
        
        for loc, preps in par_localisation.items():
            loc_info = LOCALISATIONS.get(loc, {"nom": loc, "emoji": "📦"})
            
            with st.expander(f"{loc_info['emoji']} **{loc_info['nom']}** ({len(preps)} préparations)", expanded=True):
                for prep in preps:
                    _afficher_carte_preparation(prep, service)
    else:
        st.info("Aucune préparation stockée")
    
    st.divider()
    
    # Ajouter une préparation manuellement
    st.subheader("➕ Ajouter une préparation")
    
    with st.form("nouvelle_preparation"):
        col1, col2 = st.columns(2)
        
        with col1:
            nom = st.text_input("Nom de la préparation", placeholder="Ex: Bolognaise")
            portions = st.number_input("Portions", min_value=1, max_value=20, value=4)
            localisation = st.selectbox(
                "Localisation",
                options=list(LOCALISATIONS.keys()),
                format_func=lambda x: f"{LOCALISATIONS[x]['emoji']} {LOCALISATIONS[x]['nom']}"
            )
        
        with col2:
            date_prep = st.date_input("Date de préparation", value=date.today())
            conservation = st.number_input(
                "Conservation (jours)", 
                min_value=1, 
                max_value=LOCALISATIONS[localisation]["conservation_max_jours"],
                value=min(5, LOCALISATIONS[localisation]["conservation_max_jours"])
            )
            container = st.text_input("Container", placeholder="Ex: Boîte bleue")
        
        notes = st.text_area("Notes (optionnel)", height=60)
        
        if st.form_submit_button("➕ Ajouter", type="primary", use_container_width=True):
            if nom:
                prep = service.creer_preparation(
                    nom=nom,
                    portions=portions,
                    date_preparation=date_prep,
                    conservation_jours=conservation,
                    localisation=localisation,
                    container=container if container else None,
                    notes=notes if notes else None,
                )
                if prep:
                    st.success(f"✅ Préparation '{nom}' ajoutée!")
                    st.rerun()
            else:
                st.error("Le nom est requis")


def _afficher_carte_preparation(prep: PreparationBatch, service):
    """Affiche une carte de préparation"""
    col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
    
    with col1:
        st.write(f"**{prep.nom}**")
        if prep.container:
            st.caption(f"📦 {prep.container}")
    
    with col2:
        st.metric("🍽️", f"{prep.portions_restantes}/{prep.portions_initiales}")
    
    with col3:
        jours = prep.jours_avant_peremption
        if jours < 0:
            st.error(f"⚠️ Périmé")
        elif jours <= 2:
            st.warning(f"J-{jours}")
        else:
            st.caption(f"J-{jours}")
    
    with col4:
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("➖", key=f"minus_{prep.id}", help="Consommer 1 portion"):
                service.consommer_preparation(prep.id, 1)
                st.rerun()
        with col_b:
            if st.button("✅", key=f"done_{prep.id}", help="Tout consommé"):
                service.consommer_preparation(prep.id, prep.portions_restantes)
                st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════════
# SECTION 5: CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════════


def render_configuration():
    """Configuration du batch cooking"""
    service = get_batch_cooking_service()
    config = service.get_config()
    
    st.subheader("⚙️ Configuration Batch Cooking")
    
    with st.form("config_batch"):
        # Jours de batch
        st.write("**📅 Jours de batch cooking habituels**")
        cols = st.columns(7)
        jours_selectionnes = []
        
        for i, jour in enumerate(JOURS_SEMAINE):
            with cols[i]:
                checked = st.checkbox(
                    jour[:3],
                    value=i in (config.jours_batch if config else [6]),
                    key=f"jour_{i}"
                )
                if checked:
                    jours_selectionnes.append(i)
        
        st.divider()
        
        col1, col2 = st.columns(2)
        
        with col1:
            heure = st.time_input(
                "⏰ Heure de début préférée",
                value=config.heure_debut_preferee if config else time(10, 0),
            )
            
            duree_max = st.slider(
                "⏱️ Durée max souhaitée (minutes)",
                60, 300, 
                config.duree_max_session if config else 180,
                step=15
            )
        
        with col2:
            avec_jules = st.toggle(
                "👶 Jules présent par défaut",
                value=config.avec_jules_par_defaut if config else True,
            )
            
            objectif = st.number_input(
                "🎯 Objectif portions/semaine",
                min_value=5,
                max_value=50,
                value=config.objectif_portions_semaine if config else 20,
            )
        
        st.divider()
        
        # Robots par défaut
        st.write("**🤖 Équipements disponibles par défaut**")
        robots_defaut = config.robots_disponibles if config else ["four", "plaques"]
        
        cols = st.columns(3)
        robots_selectionnes = []
        
        for i, (robot_id, robot_info) in enumerate(ROBOTS_INFO.items()):
            with cols[i % 3]:
                checked = st.checkbox(
                    f"{robot_info['emoji']} {robot_info['nom']}",
                    value=robot_id in robots_defaut,
                    key=f"config_robot_{robot_id}"
                )
                if checked:
                    robots_selectionnes.append(robot_id)
        
        st.divider()
        
        if st.form_submit_button("💾 Sauvegarder", type="primary", use_container_width=True):
            service.update_config(
                jours_batch=jours_selectionnes,
                heure_debut=heure,
                duree_max=duree_max,
                avec_jules=avec_jules,
                robots=robots_selectionnes,
                objectif_portions=objectif,
            )
            st.success("✅ Configuration sauvegardée!")
            st.rerun()
    
    # Stats
    st.divider()
    st.subheader("📊 Statistiques")
    
    with obtenir_contexte_db() as db:
        nb_sessions = db.query(SessionBatchCooking).filter(
            SessionBatchCooking.statut == StatutSessionEnum.TERMINEE.value
        ).count()
        
        nb_preparations = db.query(PreparationBatch).filter(
            PreparationBatch.consomme == False
        ).count()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("📅 Sessions terminées", nb_sessions)
    
    with col2:
        st.metric("📦 Préparations actives", nb_preparations)
    
    with col3:
        st.metric("🎯 Objectif portions", config.objectif_portions_semaine if config else 20)
