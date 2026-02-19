"""
Composants UI pour les notifications push.

Widgets Streamlit pour demander les permissions et configurer les préférences.

Note: Ce fichier a été déplacé depuis src/services/notifications/ui.py
pour respecter la séparation UI/Services.
"""

import streamlit as st
import streamlit.components.v1 as components

from src.services.core.notifications.types import (
    VAPID_PUBLIC_KEY,
    PreferencesNotification,
)


def afficher_demande_permission_push():
    """
    Affiche une demande de permission pour les notifications push.
    """
    html = f"""
    <div id="push-permission-container" style="
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 16px 20px;
        border-radius: 12px;
        color: white;
        display: none;
    ">
        <div style="display: flex; align-items: center; gap: 12px;">
            <span style="font-size: 24px;">🔔</span>
            <div style="flex: 1;">
                <div style="font-weight: 600;">Activer les notifications</div>
                <div style="font-size: 13px; opacity: 0.9;">
                    Recevez des alertes pour les péremptions et rappels
                </div>
            </div>
            <button onclick="requestPushPermission()" style="
                background: white;
                color: #667eea;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: 600;
                cursor: pointer;
            ">Activer</button>
            <button onclick="dismissPushPrompt()" style="
                background: transparent;
                color: white;
                border: 1px solid rgba(255,255,255,0.3);
                padding: 8px 12px;
                border-radius: 6px;
                cursor: pointer;
            ">Plus tard</button>
        </div>
    </div>

    <script>
        const VAPID_PUBLIC_KEY = '{VAPID_PUBLIC_KEY}';

        // Afficher si permission non accordée
        if ('Notification' in window && Notification.permission === 'default') {{
            document.getElementById('push-permission-container').style.display = 'block';
        }}

        async function requestPushPermission() {{
            try {{
                const permission = await Notification.requestPermission();

                if (permission === 'granted') {{
                    await subscribeToPush();
                    document.getElementById('push-permission-container').style.display = 'none';
                }}
            }} catch (error) {{
                console.error('Push permission error:', error);
            }}
        }}

        async function subscribeToPush() {{
            if ('serviceWorker' in navigator) {{
                const registration = await navigator.serviceWorker.ready;

                const subscription = await registration.pushManager.subscribe({{
                    userVisibleOnly: true,
                    applicationServerKey: urlBase64ToUint8Array(VAPID_PUBLIC_KEY)
                }});

                // Envoyer l'abonnement au serveur
                console.log('Push subscription:', JSON.stringify(subscription));
                // TODO: Créer un endpoint FastAPI POST /api/push/subscribe
                // qui appelle notif_web.sauvegarder_abonnement_supabase()
                // puis envoyer via fetch() depuis ce JS
            }}
        }}

        function dismissPushPrompt() {{
            document.getElementById('push-permission-container').style.display = 'none';
            localStorage.setItem('push_prompt_dismissed', Date.now());
        }}

        function urlBase64ToUint8Array(base64String) {{
            const padding = '='.repeat((4 - base64String.length % 4) % 4);
            const base64 = (base64String + padding)
                .replace(/-/g, '+')
                .replace(/_/g, '/');

            const rawData = window.atob(base64);
            const outputArray = new Uint8Array(rawData.length);

            for (let i = 0; i < rawData.length; ++i) {{
                outputArray[i] = rawData.charCodeAt(i);
            }}
            return outputArray;
        }}
    </script>
    """

    components.html(html, height=100)


def afficher_preferences_notification():
    """Affiche les paramètres de notifications."""
    from src.services.core.notifications.notif_web import obtenir_service_webpush

    push_service = obtenir_service_webpush()

    # Récupérer l'utilisateur courant
    try:
        from src.services.core.utilisateur import get_auth_service

        auth = get_auth_service()
        user = auth.get_current_user()
        user_id = user.id if user else "anonymous"
    except Exception:
        user_id = "anonymous"

    prefs = push_service.obtenir_preferences(user_id)

    st.markdown("### 🔔 Préférences de notifications")

    with st.form("notification_prefs"):
        st.markdown("**Catégories de notifications:**")

        col1, col2 = st.columns(2)

        with col1:
            alertes_stock = st.checkbox("Stock bas", value=prefs.alertes_stock)
            alertes_peremption = st.checkbox("Péremptions", value=prefs.alertes_peremption)
            rappels_repas = st.checkbox("Rappels de repas", value=prefs.rappels_repas)

        with col2:
            rappels_activites = st.checkbox("Rappels d'activités", value=prefs.rappels_activites)
            mises_a_jour_courses = st.checkbox(
                "Mises à jour courses", value=prefs.mises_a_jour_courses
            )
            rappels_famille = st.checkbox("Rappels famille", value=prefs.rappels_famille)

        mises_a_jour_systeme = st.checkbox("Mises à jour système", value=prefs.mises_a_jour_systeme)

        st.markdown("---")
        st.markdown("**Heures de silence:**")

        col1, col2 = st.columns(2)
        with col1:
            heures_debut = st.number_input(
                "Début (heure)",
                min_value=0,
                max_value=23,
                value=prefs.heures_silencieuses_debut or 22,
            )
        with col2:
            heures_fin = st.number_input(
                "Fin (heure)",
                min_value=0,
                max_value=23,
                value=prefs.heures_silencieuses_fin or 7,
            )

        st.markdown("---")
        max_par_heure = st.slider(
            "Maximum de notifications par heure",
            min_value=1,
            max_value=20,
            value=prefs.max_par_heure,
        )

        if st.form_submit_button("Enregistrer", use_container_width=True):
            new_prefs = PreferencesNotification(
                user_id=user_id,
                alertes_stock=alertes_stock,
                alertes_peremption=alertes_peremption,
                rappels_repas=rappels_repas,
                rappels_activites=rappels_activites,
                mises_a_jour_courses=mises_a_jour_courses,
                rappels_famille=rappels_famille,
                mises_a_jour_systeme=mises_a_jour_systeme,
                heures_silencieuses_debut=heures_debut,
                heures_silencieuses_fin=heures_fin,
                max_par_heure=max_par_heure,
            )
            push_service.mettre_a_jour_preferences(user_id, new_prefs)
            st.success("✅ Préférences enregistrées!")


__all__ = [
    "afficher_demande_permission_push",
    "afficher_preferences_notification",
]
