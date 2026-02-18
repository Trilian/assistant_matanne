"""
Interface UI pour les fonctionnalités PWA (Progressive Web App).

Note: Ce fichier a été extrait depuis src/services/web/pwa.py
pour respecter la séparation UI/Services.
"""

import streamlit.components.v1 as components


def injecter_meta_pwa():
    """
    Injecte les meta tags PWA dans la page Streamlit.

    Doit être appelé au début de l'application.
    """
    pwa_meta = """
    <head>
        <!-- PWA Meta Tags -->
        <link rel="manifest" href="/static/manifest.json">
        <meta name="theme-color" content="#667eea">
        <meta name="apple-mobile-web-app-capable" content="yes">
        <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
        <meta name="apple-mobile-web-app-title" content="Matanne">

        <!-- iOS Icons -->
        <link rel="apple-touch-icon" href="/static/icons/icon-152x152.png">
        <link rel="apple-touch-icon" sizes="180x180" href="/static/icons/icon-192x192.png">

        <!-- Splash Screens iOS -->
        <link rel="apple-touch-startup-image" href="/static/splash/splash.png">
    </head>

    <script>
        // Enregistrer le Service Worker
        if ('serviceWorker' in navigator) {
            window.addEventListener('load', () => {
                navigator.serviceWorker.register('/static/sw.js')
                    .then((registration) => {
                        console.log('SW registered:', registration.scope);
                    })
                    .catch((error) => {
                        console.log('SW registration failed:', error);
                    });
            });
        }

        // Demander la permission pour les notifications
        async function requestNotificationPermission() {
            if ('Notification' in window && Notification.permission === 'default') {
                const permission = await Notification.requestPermission();
                console.log('Notification permission:', permission);
            }
        }

        // Détecter si installé en PWA
        window.addEventListener('appinstalled', () => {
            console.log('PWA installed');
        });

        // Proposer l'installation
        let deferredPrompt;
        window.addEventListener('beforeinstallprompt', (e) => {
            e.preventDefault();
            deferredPrompt = e;
            // Afficher un bouton d'installation custom si besoin
        });
    </script>
    """

    components.html(pwa_meta, height=0)


# Alias rétrocompatibilité
inject_pwa_meta = injecter_meta_pwa


__all__ = [
    "injecter_meta_pwa",
    # Alias rétrocompatibilité
    "inject_pwa_meta",
]
