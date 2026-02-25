"""
Interface UI pour les fonctionnalités PWA (Progressive Web App).

Note: Ce fichier a été extrait depuis src/services/web/pwa.py
pour respecter la séparation UI/Services.
"""

import streamlit.components.v1 as components

from src.ui.tokens_semantic import Sem


def injecter_meta_pwa():
    """
    Injecte les meta tags PWA dans le <head> du document.

    Utilise JavaScript pour ajouter les éléments au vrai <head>
    au lieu de les rendre dans un iframe (U4).
    """
    pwa_script = f"""
    <script>
        (function() {{
            // Éviter les injections multiples
            if (document.querySelector('link[rel="manifest"]')) return;

            var parent = window.parent.document.head || document.head;

            // Manifest
            var manifest = document.createElement('link');
            manifest.rel = 'manifest';
            manifest.href = '/static/manifest.json';
            parent.appendChild(manifest);

            // Theme color
            var themeColor = document.createElement('meta');
            themeColor.name = 'theme-color';
            themeColor.content = '{Sem.INTERACTIVE}';
            parent.appendChild(themeColor);

            // Apple meta tags
            var awac = document.createElement('meta');
            awac.name = 'apple-mobile-web-app-capable';
            awac.content = 'yes';
            parent.appendChild(awac);

            var awabs = document.createElement('meta');
            awabs.name = 'apple-mobile-web-app-status-bar-style';
            awabs.content = 'black-translucent';
            parent.appendChild(awabs);

            var awat = document.createElement('meta');
            awat.name = 'apple-mobile-web-app-title';
            awat.content = 'Matanne';
            parent.appendChild(awat);

            // Apple touch icons
            var icon152 = document.createElement('link');
            icon152.rel = 'apple-touch-icon';
            icon152.href = '/static/icons/icon-152x152.png';
            parent.appendChild(icon152);

            var icon192 = document.createElement('link');
            icon192.rel = 'apple-touch-icon';
            icon192.sizes = '180x180';
            icon192.href = '/static/icons/icon-192x192.png';
            parent.appendChild(icon192);

            // Splash screen
            var splash = document.createElement('link');
            splash.rel = 'apple-touch-startup-image';
            splash.href = '/static/splash/splash.png';
            parent.appendChild(splash);

            // Service Worker
            if ('serviceWorker' in navigator) {{
                window.addEventListener('load', function() {{
                    navigator.serviceWorker.register('/static/sw.js')
                        .then(function(reg) {{ console.log('SW registered:', reg.scope); }})
                        .catch(function(err) {{ console.log('SW registration failed:', err); }});
                }});
            }}

            // Notification permission
            if ('Notification' in window && Notification.permission === 'default') {{
                Notification.requestPermission();
            }}

            // PWA install events
            window.addEventListener('appinstalled', function() {{
                console.log('PWA installed');
            }});

            var deferredPrompt;
            window.addEventListener('beforeinstallprompt', function(e) {{
                e.preventDefault();
                deferredPrompt = e;
            }});
        }})();
    </script>
    """

    components.html(pwa_script, height=0)


def afficher_invite_installation_pwa():
    """Affiche un bouton d'installation PWA si disponible."""
    install_script = f"""
    <div id="pwa-install-container" style="display: none;" role="region" aria-label="Installation application">
        <button id="pwa-install-btn" onclick="installPWA()" style="
            background: linear-gradient(135deg, {Sem.INFO} 0%, {Sem.INTERACTIVE} 100%);
            color: {Sem.ON_INTERACTIVE};
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 8px;
        " aria-label="Installer l'application Matanne">
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
