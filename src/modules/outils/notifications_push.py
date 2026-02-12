"""
Module Notifications Push - Configuration et test des alertes.

FonctionnalitÃes:
- Configuration du topic ntfy.sh
- Test de connexion
- Envoi manuel de notifications
- Visualisation des tâches en retard
- QR Code pour s'abonner
"""

import streamlit as st
from datetime import date

from src.services.notifications import (
    obtenir_service_ntfy,
    ConfigurationNtfy,
    NotificationNtfy,
    ServiceNtfy,
    # Alias rÃetrocompatibilitÃe
    get_notification_push_service,
    NotificationPushConfig,
    NotificationPush,
    NotificationPushService,
)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# CONSTANTES
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

HELP_NTFY = """
**ntfy.sh** est un service gratuit de notifications push.

### Comment ça marche?
1. Installez l'app **ntfy** sur votre tÃelÃephone (Android/iOS)
2. Abonnez-vous au topic de votre famille
3. Recevez les alertes en temps rÃeel!

### Avantages:
- âœ… Gratuit et open-source
- âœ… Pas de compte requis
- âœ… Multi-appareils
- âœ… Fonctionne même hors app Matanne
"""


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# HELPERS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

def charger_config() -> NotificationPushConfig:
    """Charge la configuration depuis session_state."""
    if "notif_config" not in st.session_state:
        st.session_state["notif_config"] = NotificationPushConfig()
    return st.session_state["notif_config"]


def sauvegarder_config(config: NotificationPushConfig):
    """Sauvegarde la configuration en session_state."""
    st.session_state["notif_config"] = config


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# UI COMPONENTS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

def render_configuration():
    """Interface de configuration des notifications."""
    st.subheader("âš™ï¸ Configuration")
    
    config = charger_config()
    
    with st.form("config_notif"):
        col1, col2 = st.columns(2)
        
        with col1:
            topic = st.text_input(
                "Topic ntfy.sh",
                value=config.topic,
                help="Identifiant unique pour votre famille (ex: matanne-famille)"
            )
            
            actif = st.toggle(
                "Notifications actives",
                value=config.actif
            )
        
        with col2:
            rappels_taches = st.toggle(
                "Alertes tâches en retard",
                value=config.rappels_taches
            )
            
            rappels_courses = st.toggle(
                "Rappels courses",
                value=config.rappels_courses
            )
        
        heure_digest = st.slider(
            "Heure du digest quotidien",
            min_value=6,
            max_value=22,
            value=config.heure_digest,
            format="%dh"
        )
        
        submitted = st.form_submit_button("ðŸ’¾ Enregistrer", type="primary", use_container_width=True)
        
        if submitted:
            new_config = NotificationPushConfig(
                topic=topic,
                actif=actif,
                rappels_taches=rappels_taches,
                rappels_courses=rappels_courses,
                heure_digest=heure_digest
            )
            sauvegarder_config(new_config)
            st.success("âœ… Configuration sauvegardÃee!")
            st.rerun()


def render_abonnement():
    """Interface pour s'abonner aux notifications."""
    st.subheader("ðŸ“± S'abonner aux notifications")
    
    config = charger_config()
    service = get_notification_push_service(config)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### Scanner le QR Code")
        st.caption("Avec l'app ntfy sur votre tÃelÃephone")
        
        # Afficher QR Code
        qr_url = service.get_subscribe_qr_url()
        st.image(qr_url, width=200)
    
    with col2:
        st.markdown("### Liens directs")
        
        web_url = service.get_web_url()
        st.markdown(f"ðŸŒ **Web:** [{web_url}]({web_url})")
        
        st.divider()
        
        st.markdown("### Installation app")
        st.markdown("""
        - [Android (Play Store)](https://play.google.com/store/apps/details?id=io.heckel.ntfy)
        - [iOS (App Store)](https://apps.apple.com/app/ntfy/id1625396347)
        - [F-Droid](https://f-droid.org/packages/io.heckel.ntfy/)
        """)
    
    # Topic actuel
    st.divider()
    st.info(f"ðŸ“ **Topic actuel:** `{config.topic}`")


def render_test():
    """Interface de test des notifications."""
    st.subheader("ðŸ§ª Tester les notifications")
    
    config = charger_config()
    service = get_notification_push_service(config)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("ðŸ”” Envoyer test", type="primary", use_container_width=True):
            with st.spinner("Envoi en cours..."):
                resultat = service.test_connexion_sync()
                
                if resultat.succes:
                    st.success(f"âœ… {resultat.message}")
                    st.caption(f"ID: {resultat.notification_id}")
                else:
                    st.error(f"âŒ {resultat.message}")
    
    with col2:
        if st.button("ðŸ“‹ Envoyer digest", use_container_width=True):
            with st.spinner("GÃenÃeration du digest..."):
                import asyncio
                resultat = asyncio.run(service.envoyer_digest_quotidien())
                
                if resultat.succes:
                    st.success(f"âœ… {resultat.message}")
                else:
                    st.error(f"âŒ {resultat.message}")
    
    # Notification personnalisÃee
    st.divider()
    st.markdown("### Notification personnalisÃee")
    
    with st.form("notif_custom"):
        titre = st.text_input("Titre", value="ðŸ“¢ Message Matanne")
        message = st.text_area("Message", value="Ceci est un test.", height=100)
        
        col1, col2 = st.columns(2)
        with col1:
            priorite = st.select_slider(
                "PrioritÃe",
                options=[1, 2, 3, 4, 5],
                value=3,
                format_func=lambda x: {1: "Min", 2: "Basse", 3: "Normale", 4: "Haute", 5: "Urgente"}[x]
            )
        with col2:
            tags = st.multiselect(
                "Tags (emojis)",
                options=["bell", "warning", "calendar", "house", "shopping_cart", "heart", "star"],
                default=["bell"]
            )
        
        if st.form_submit_button("ðŸ“¤ Envoyer", use_container_width=True):
            notification = NotificationPush(
                titre=titre,
                message=message,
                priorite=priorite,
                tags=tags
            )
            
            with st.spinner("Envoi..."):
                resultat = service.envoyer_sync(notification)
                
                if resultat.succes:
                    st.success("âœ… Notification envoyÃee!")
                else:
                    st.error(f"âŒ {resultat.message}")


def render_taches_retard():
    """Affiche les tâches en retard et permet d'envoyer des alertes."""
    st.subheader("â° Tâches en retard")
    
    config = charger_config()
    service = get_notification_push_service(config)
    
    taches_retard = service.obtenir_taches_en_retard()
    taches_jour = service.obtenir_taches_du_jour()
    
    # MÃetriques
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("âš ï¸ En retard", len(taches_retard))
    with col2:
        st.metric("ðŸ“… Aujourd'hui", len(taches_jour))
    with col3:
        total = len(taches_retard) + len(taches_jour)
        st.metric("ðŸ“Š Total Ã  traiter", total)
    
    st.divider()
    
    # Liste des tâches en retard
    if taches_retard:
        st.markdown("### âš ï¸ Tâches en retard")
        
        for tache in taches_retard[:10]:
            jours_retard = (date.today() - tache.date_echeance).days
            urgence = "ðŸ”´" if jours_retard > 7 else "ðŸŸ " if jours_retard > 3 else "ðŸŸ¡"
            
            with st.container(border=True):
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    st.markdown(f"**{urgence} {tache.titre}**")
                    st.caption(f"ðŸ“… PrÃevue: {tache.date_echeance.strftime('%d/%m/%Y')}")
                
                with col2:
                    st.markdown(f"**{jours_retard}j** retard")
                
                with col3:
                    if st.button("ðŸ“¤", key=f"notif_{tache.id}", help="Envoyer alerte"):
                        import asyncio
                        resultat = asyncio.run(service.envoyer_alerte_tache_retard(tache))
                        if resultat.succes:
                            st.toast(f"âœ… Alerte envoyÃee pour {tache.titre}")
                        else:
                            st.toast(f"âŒ Erreur: {resultat.message}")
        
        # Action groupÃee
        st.divider()
        if st.button(
            f"ðŸ“¤ Envoyer alertes pour {min(5, len(taches_retard))} tâches",
            type="primary",
            use_container_width=True
        ):
            from src.services.notifications_push import get_notification_push_scheduler
            scheduler = get_notification_push_scheduler()
            
            with st.spinner("Envoi des alertes..."):
                resultats = scheduler.lancer_verification_sync()
                succes = sum(1 for r in resultats if r.succes)
                st.success(f"âœ… {succes}/{len(resultats)} alertes envoyÃees")
    else:
        st.success("âœ… Aucune tâche en retard! ðŸŽ‰")
    
    # Tâches du jour
    if taches_jour:
        st.divider()
        st.markdown("### ðŸ“… Tâches du jour")
        
        for tache in taches_jour[:5]:
            st.markdown(f"â€¢ {tache.titre}")


def render_aide():
    """Affiche l'aide sur ntfy.sh."""
    st.subheader("â“ Aide")
    st.markdown(HELP_NTFY)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# PAGE PRINCIPALE
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

def app():
    """Point d'entrÃee du module notifications push."""
    st.title("ðŸ”” Notifications Push")
    st.caption("Recevez des alertes sur votre tÃelÃephone")
    
    # Tabs
    tabs = st.tabs([
        "ðŸ“± S'abonner",
        "âš™ï¸ Configuration",
        "â° Tâches",
        "ðŸ§ª Test",
        "â“ Aide"
    ])
    
    with tabs[0]:
        render_abonnement()
    
    with tabs[1]:
        render_configuration()
    
    with tabs[2]:
        render_taches_retard()
    
    with tabs[3]:
        render_test()
    
    with tabs[4]:
        render_aide()


if __name__ == "__main__":
    app()
