"""
Module Notifications Push - Configuration et test des alertes.

Fonctionnalités:
- Configuration du topic ntfy.sh
- Test de connexion
- Envoi manuel de notifications
- Visualisation des tâches en retard
- QR Code pour s'abonner
"""

from datetime import date

import streamlit as st

from src.services.core.notifications import (
    NotificationPush,
    NotificationPushConfig,
    get_notification_push_service,
)

# ═══════════════════════════════════════════════════════════
# CONSTANTES
# ═══════════════════════════════════════════════════════════

HELP_NTFY = """
**ntfy.sh** est un service gratuit de notifications push.

### Comment ça marche?
1. Installez l'app **ntfy** sur votre téléphone (Android/iOS)
2. Abonnez-vous au topic de votre famille
3. Recevez les alertes en temps réel!

### Avantages:
- ✅ Gratuit et open-source
- ✅ Pas de compte requis
- ✅ Multi-appareils
- ✅ Fonctionne même hors app Matanne
"""


# ═══════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════


def charger_config() -> NotificationPushConfig:
    """Charge la configuration depuis session_state."""
    if "notif_config" not in st.session_state:
        st.session_state["notif_config"] = NotificationPushConfig()
    return st.session_state["notif_config"]


def sauvegarder_config(config: NotificationPushConfig):
    """Sauvegarde la configuration en session_state."""
    st.session_state["notif_config"] = config


# ═══════════════════════════════════════════════════════════
# UI COMPONENTS
# ═══════════════════════════════════════════════════════════


def render_configuration():
    """Interface de configuration des notifications."""
    st.subheader("⚙️ Configuration")

    config = charger_config()

    with st.form("config_notif"):
        col1, col2 = st.columns(2)

        with col1:
            topic = st.text_input(
                "Topic ntfy.sh",
                value=config.topic,
                help="Identifiant unique pour votre famille (ex: matanne-famille)",
            )

            actif = st.toggle("Notifications actives", value=config.actif)

        with col2:
            rappels_taches = st.toggle("Alertes tâches en retard", value=config.rappels_taches)

            rappels_courses = st.toggle("Rappels courses", value=config.rappels_courses)

        heure_digest = st.slider(
            "Heure d'envoi du résumé quotidien",
            min_value=6,
            max_value=22,
            value=config.heure_digest,
            format="%dh",
            help="Heure à laquelle vous recevrez le récapitulatif de vos tâches et rappels",
        )

        submitted = st.form_submit_button(
            "💾 Enregistrer", type="primary", use_container_width=True
        )

        if submitted:
            new_config = NotificationPushConfig(
                topic=topic,
                actif=actif,
                rappels_taches=rappels_taches,
                rappels_courses=rappels_courses,
                heure_digest=heure_digest,
            )
            sauvegarder_config(new_config)
            st.success("✅ Configuration sauvegardée!")


def render_abonnement():
    """Interface pour s'abonner aux notifications."""
    st.subheader("📷 S'abonner aux notifications")

    config = charger_config()
    service = get_notification_push_service(config)

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("### Scanner le QR Code")
        st.caption("Avec l'app ntfy sur votre téléphone")

        # Afficher QR Code
        qr_url = service.get_subscribe_qr_url()
        st.image(qr_url, width=200)

    with col2:
        st.markdown("### Liens directs")

        web_url = service.get_web_url()
        st.markdown(f"🌐 **Web:** [{web_url}]({web_url})")

        st.divider()

        st.markdown("### Installation app")
        st.markdown("""
        - [Android (Play Store)](https://play.google.com/store/apps/details?id=io.heckel.ntfy)
        - [iOS (App Store)](https://apps.apple.com/app/ntfy/id1625396347)
        - [F-Droid](https://f-droid.org/packages/io.heckel.ntfy/)
        """)

    # Topic actuel
    st.divider()
    st.info(f"📝 **Topic actuel:** `{config.topic}`")


def _simuler_notification(titre: str, message: str, priorite: int = 3, tags: list = None):
    """Simule l'affichage d'une notification en mode démo."""
    import uuid
    from datetime import datetime

    # Stocker dans session_state
    if "notif_demo_history" not in st.session_state:
        st.session_state["notif_demo_history"] = []

    notif_id = str(uuid.uuid4())[:8]
    st.session_state["notif_demo_history"].append(
        {
            "id": notif_id,
            "titre": titre,
            "message": message,
            "priorite": priorite,
            "tags": tags or [],
            "timestamp": datetime.now().isoformat(),
        }
    )

    # Aperçu visuel de la notification
    priorite_emoji = {1: "⬜", 2: "🟦", 3: "🟩", 4: "🟧", 5: "🟥"}[priorite]

    st.toast(f"{priorite_emoji} {titre}")

    with st.container(border=True):
        st.markdown(f"**{priorite_emoji} {titre}**")
        st.caption(message[:100] + ("..." if len(message) > 100 else ""))
        st.caption(f"ID: {notif_id} | Tags: {', '.join(tags or ['aucun'])}")

    return notif_id


def render_test():
    """Interface de test des notifications."""
    st.subheader("🧪 Tester les notifications")

    config = charger_config()
    service = get_notification_push_service(config)

    # Mode démo toggle
    mode_demo = st.toggle(
        "🎭 Mode démo (simulation locale)",
        value=st.session_state.get("notif_mode_demo", False),
        help="Affiche les notifications localement sans les envoyer à ntfy.sh",
        key="notif_mode_demo",
    )

    if mode_demo:
        st.info("💡 **Mode démo actif** - Les notifications s'affichent ici sans être envoyées.")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🔔 Envoyer test", type="primary", use_container_width=True):
            if mode_demo:
                _simuler_notification(
                    "🔔 Test Matanne",
                    "Les notifications sont correctement configurées!",
                    priorite=3,
                    tags=["white_check_mark"],
                )
                st.success("✅ Notification simulée!")
            else:
                with st.spinner("Envoi en cours..."):
                    resultat = service.test_connexion_sync()
                    if resultat.succes:
                        st.success(f"✅ {resultat.message}")
                        st.caption(f"ID: {resultat.notification_id}")
                    else:
                        st.error(f"❌ {resultat.message}")

    with col2:
        if st.button("📋 Envoyer digest", use_container_width=True):
            if mode_demo:
                taches_retard = service.obtenir_taches_en_retard()
                taches_jour = service.obtenir_taches_du_jour()
                lines = ["📋 Résumé du jour"]
                if taches_retard:
                    lines.append(f"⚠️ {len(taches_retard)} tâche(s) en retard")
                if taches_jour:
                    lines.append(f"📅 {len(taches_jour)} tâche(s) aujourd'hui")
                if not taches_retard and not taches_jour:
                    lines.append("✨ Rien à signaler!")
                _simuler_notification(
                    "📋 Digest Matanne",
                    "\n".join(lines),
                    priorite=4 if taches_retard else 3,
                    tags=["house", "clipboard"],
                )
                st.success("✅ Digest simulé!")
            else:
                with st.spinner("Génération du digest..."):
                    resultat = service.envoyer_digest_quotidien_sync()
                    if resultat.succes:
                        st.success(f"✅ {resultat.message}")
                    else:
                        st.error(f"❌ {resultat.message}")

    # Notification personnalisée
    st.divider()
    st.markdown("### Notification personnalisée")

    with st.form("notif_custom"):
        titre = st.text_input("Titre", value="📝 Message Matanne")
        message = st.text_area("Message", value="Ceci est un test.", height=100)

        col1, col2 = st.columns(2)
        with col1:
            priorite = st.select_slider(
                "Priorité",
                options=[1, 2, 3, 4, 5],
                value=3,
                format_func=lambda x: {
                    1: "Min",
                    2: "Basse",
                    3: "Normale",
                    4: "Haute",
                    5: "Urgente",
                }[x],
            )
        with col2:
            tags = st.multiselect(
                "Tags (emojis)",
                options=["bell", "warning", "calendar", "house", "shopping_cart", "heart", "star"],
                default=["bell"],
            )

        if st.form_submit_button("📤 Envoyer", use_container_width=True):
            notification = NotificationPush(
                title=titre, body=message, tag=tags[0] if tags else None
            )

            if mode_demo:
                _simuler_notification(titre, message, priorite, tags)
                st.success("✅ Notification simulée!")
            else:
                with st.spinner("Envoi..."):
                    resultat = service.envoyer_sync(notification)
                    if resultat.succes:
                        st.success("✅ Notification envoyée!")
                    else:
                        st.error(f"❌ {resultat.message}")

    # Historique des notifications démo
    if mode_demo and st.session_state.get("notif_demo_history"):
        st.divider()
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown("### 📜 Historique démo")
        with col2:
            if st.button("🗑️ Effacer", key="clear_demo_history"):
                st.session_state["notif_demo_history"] = []
                st.rerun()

        for notif in reversed(st.session_state["notif_demo_history"][-5:]):
            priorite_emoji = {1: "⬜", 2: "🟦", 3: "🟩", 4: "🟧", 5: "🟥"}[notif["priorite"]]
            with st.container(border=True):
                st.markdown(f"**{priorite_emoji} {notif['titre']}**")
                st.caption(notif["message"][:80])
                st.caption(f"🕐 {notif['timestamp'][:19]} | ID: {notif['id']}")


def render_taches_retard():
    """Affiche les tâches en retard et permet d'envoyer des alertes."""
    st.subheader("⏰ Tâches en retard")

    config = charger_config()
    service = get_notification_push_service(config)

    taches_retard = service.obtenir_taches_en_retard()
    taches_jour = service.obtenir_taches_du_jour()

    # Métriques
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("⚠️ En retard", len(taches_retard))
    with col2:
        st.metric("📅 Aujourd'hui", len(taches_jour))
    with col3:
        total = len(taches_retard) + len(taches_jour)
        st.metric("📊 Total à traiter", total)

    st.divider()

    # Liste des tâches en retard
    if taches_retard:
        st.markdown("### ⚠️ Tâches en retard")

        for tache in taches_retard[:10]:
            jours_retard = (date.today() - tache.date_echeance).days
            urgence = "🔴" if jours_retard > 7 else "🟠" if jours_retard > 3 else "🟡"

            with st.container(border=True):
                col1, col2, col3 = st.columns([3, 1, 1])

                with col1:
                    st.markdown(f"**{urgence} {tache.titre}**")
                    st.caption(f"📅 Prévue: {tache.date_echeance.strftime('%d/%m/%Y')}")

                with col2:
                    st.markdown(f"**{jours_retard}j** retard")

                with col3:
                    if st.button("📤", key=f"notif_{tache.id}", help="Envoyer alerte"):
                        import asyncio

                        resultat = asyncio.run(service.envoyer_alerte_tache_retard(tache))
                        if resultat.succes:
                            st.toast(f"✅ Alerte envoyée pour {tache.titre}")
                        else:
                            st.toast(f"❌ Erreur: {resultat.message}")

        # Action groupée
        st.divider()
        if st.button(
            f"📤 Envoyer alertes pour {min(5, len(taches_retard))} tâches",
            type="primary",
            use_container_width=True,
        ):
            from src.services.core.notifications_push import get_notification_push_scheduler

            scheduler = get_notification_push_scheduler()

            with st.spinner("Envoi des alertes..."):
                resultats = scheduler.lancer_verification_sync()
                succes = sum(1 for r in resultats if r.succes)
                st.success(f"✅ {succes}/{len(resultats)} alertes envoyées")
    else:
        st.success("✅ Aucune tâche en retard! 🎉")

    # Tâches du jour
    if taches_jour:
        st.divider()
        st.markdown("### 📅 Tâches du jour")

        for tache in taches_jour[:5]:
            st.markdown(f"• {tache.titre}")


def render_aide():
    """Affiche l'aide sur ntfy.sh."""
    st.subheader("❓ Aide")
    st.markdown(HELP_NTFY)


# ═══════════════════════════════════════════════════════════
# PAGE PRINCIPALE
# ═══════════════════════════════════════════════════════════


def app():
    """Point d'entrée du module notifications push."""
    st.title("🔔 Notifications Push")
    st.caption("Recevez des alertes sur votre téléphone")

    # Tabs
    tabs = st.tabs(["📷 S'abonner", "⚙️ Configuration", "⏰ Tâches", "🧪 Test", "❓ Aide"])

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
