"""
Interface UI pour les fonctionnalités PWA (Progressive Web App).

Note: Ce fichier a été extrait depuis src/services/web/pwa.py
pour respecter la séparation UI/Services.
"""

import streamlit.components.v1 as components

from src.ui.tokens import Couleur


def injecter_meta_pwa():
    """
    Injecte les meta tags PWA dans la page Streamlit.

    Doit être appelé au début de l'application.
    """
    pwa_meta = f"""
    <head>
        <!-- PWA Meta Tags -->
        <link rel="manifest" href="/static/manifest.json">
        <meta name="theme-color" content="{Couleur.PUSH_GRADIENT_START}">
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
        if ('serviceWorker' in navigator) {{
            window.addEventListener('load', () => {{
                navigator.serviceWorker.register('/static/sw.js')
                    .then((registration) => {{
                        console.log('SW registered:', registration.scope);
                    }})
                    .catch((error) => {{
                        console.log('SW registration failed:', error);
                    }});
            }});
        }}

        // Demander la permission pour les notifications
        async function requestNotificationPermission() {{
            if ('Notification' in window && Notification.permission === 'default') {{
                const permission = await Notification.requestPermission();
                console.log('Notification permission:', permission);
            }}
        }}

        // Détecter si installé en PWA
        window.addEventListener('appinstalled', () => {{
            console.log('PWA installed');
        }});

        // Proposer l'installation
        let deferredPrompt;
        window.addEventListener('beforeinstallprompt', (e) => {{
            e.preventDefault();
            deferredPrompt = e;
            // Afficher un bouton d'installation custom si besoin
        }});
    </script>
    """

    components.html(pwa_meta, height=0)


def afficher_invite_installation_pwa():
    """Affiche un bouton d'installation PWA si disponible."""
    install_script = f"""
    <div id="pwa-install-container" style="display: none;">
        <button id="pwa-install-btn" onclick="installPWA()" style="
            background: linear-gradient(135deg, {Couleur.PUSH_GRADIENT_START} 0%, {Couleur.PUSH_GRADIENT_END} 100%);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 8px;
        ">
            📲 Installer l'application
        </button>
    </div>

    <script>
        let deferredPrompt;

        window.addEventListener('beforeinstallprompt', (e) => {{
            e.preventDefault();
            deferredPrompt = e;
            document.getElementById('pwa-install-container').style.display = 'block';
        }});

        async function installPWA() {{
            if (deferredPrompt) {{
                deferredPrompt.prompt();
                const {{ outcome }} = await deferredPrompt.userChoice;
                console.log('Install outcome:', outcome);
                deferredPrompt = null;
                document.getElementById('pwa-install-container').style.display = 'none';
            }}
        }}
    </script>
    """

    components.html(install_script, height=60)


__all__ = [
    "injecter_meta_pwa",
    "afficher_invite_installation_pwa",
]
