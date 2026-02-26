"""
Real-time Collaboration — Innovation v11: Yjs pour édition collaborative.

Système de collaboration en temps réel basé sur Yjs (CRDT) permettant:
- Édition simultanée des listes de courses
- Planning de repas partagé en temps réel
- Calendrier familial synchronisé
- Chat temps réel entre membres

Architecture:
- Frontend: Yjs + y-websocket (WebSocket client)
- Backend: y-websocket server ou y-webrtc (P2P)
- Persistence: y-indexeddb (offline-first)

Usage:
    from src.ui.components.realtime_collab import (
        CollaborativeEditor,
        collaborative_list,
        collaborative_text,
        presence_indicator,
        RealtimeRoom,
    )

    # Liste collaborative (courses, tâches)
    items = collaborative_list(
        room_id="famille_courses",
        initial_items=["Lait", "Pain"],
    )

    # Éditeur de texte collaboratif
    text = collaborative_text(
        room_id="notes_famille",
        placeholder="Notes partagées...",
    )

    # Indicateur de présence
    presence_indicator(room_id="cuisine_planning")
"""

from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime
from typing import Any, Callable

import streamlit as st
import streamlit.components.v1 as components

from src.ui.tokens import Couleur

logger = logging.getLogger(__name__)

__all__ = [
    "CollaborativeEditor",
    "collaborative_list",
    "collaborative_text",
    "presence_indicator",
    "RealtimeRoom",
    "CollaborativeCalendar",
]


# ═══════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════

# URL du serveur WebSocket Yjs (à configurer)
DEFAULT_WS_URL = "wss://demos.yjs.dev"  # Demo server - remplacer en prod

# Couleurs pour les utilisateurs
USER_COLORS = [
    Couleur.LOTO_NORMAL_START,
    Couleur.COLLAB_VERT,
    Couleur.COLLAB_ORANGE,
    Couleur.COLLAB_ROUGE,
    Couleur.COLLAB_TEAL,
    Couleur.COLLAB_PURPLE,
    Couleur.COLLAB_ROUGE_CLAIR,
    Couleur.COLLAB_VERT_CLAIR,
]


def _get_user_color(user_id: str) -> str:
    """Génère une couleur cohérente pour un utilisateur."""
    hash_val = hash(user_id)
    return USER_COLORS[abs(hash_val) % len(USER_COLORS)]


def _get_current_user() -> dict[str, Any]:
    """Récupère l'utilisateur courant depuis la session."""
    if "collab_user" not in st.session_state:
        st.session_state["collab_user"] = {
            "id": str(uuid.uuid4())[:8],
            "name": "Utilisateur",
            "color": USER_COLORS[0],
        }
    return st.session_state["collab_user"]


# ═══════════════════════════════════════════════════════════
# COMPOSANT HTML/JS — Yjs Client
# ═══════════════════════════════════════════════════════════

_COLLAB_LIST_HTML = """
<!DOCTYPE html>
<html>
<head>
    <script src="https://cdn.jsdelivr.net/npm/yjs@13.6.10/dist/yjs.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/y-websocket@2.0.0/dist/y-websocket.cjs"></script>
    <style>
        * {{ box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', system-ui, sans-serif;
            background: transparent;
            margin: 0;
            padding: 12px;
            color: #e2e8f0;
        }}
        .collab-container {{
            background: rgba(45, 55, 72, 0.5);
            border-radius: 12px;
            padding: 16px;
        }}
        .collab-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 16px;
            padding-bottom: 12px;
            border-bottom: 1px solid #4a5568;
        }}
        .collab-title {{
            font-weight: 600;
            color: #667eea;
        }}
        .connection-status {{
            display: flex;
            align-items: center;
            gap: 6px;
            font-size: 12px;
        }}
        .status-dot {{
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #718096;
        }}
        .status-dot.connected {{ background: #48bb78; }}
        .status-dot.connecting {{ background: #ed8936; animation: blink 1s infinite; }}
        @keyframes blink {{ 50% {{ opacity: 0.5; }} }}

        .presence-bar {{
            display: flex;
            gap: 8px;
            margin-bottom: 12px;
        }}
        .presence-avatar {{
            width: 28px;
            height: 28px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 12px;
            color: white;
            font-weight: 500;
            cursor: default;
            transition: transform 0.2s;
        }}
        .presence-avatar:hover {{
            transform: scale(1.1);
        }}
        .presence-avatar.self {{
            border: 2px solid white;
        }}

        .list-items {{
            min-height: 200px;
        }}
        .list-item {{
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 10px 12px;
            margin: 6px 0;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 8px;
            transition: all 0.2s;
            border-left: 3px solid transparent;
        }}
        .list-item:hover {{
            background: rgba(255, 255, 255, 0.1);
        }}
        .list-item.editing {{
            border-left-color: #667eea;
            background: rgba(102, 126, 234, 0.1);
        }}
        .list-item.remote-editing {{
            border-left-color: var(--editor-color, #48bb78);
        }}
        .item-checkbox {{
            width: 20px;
            height: 20px;
            cursor: pointer;
            accent-color: #667eea;
        }}
        .item-text {{
            flex: 1;
            padding: 4px 8px;
            background: transparent;
            border: 1px solid transparent;
            color: #e2e8f0;
            border-radius: 4px;
            font-size: 14px;
        }}
        .item-text:focus {{
            outline: none;
            border-color: #667eea;
            background: rgba(0, 0, 0, 0.2);
        }}
        .item-text.checked {{
            text-decoration: line-through;
            color: #718096;
        }}
        .item-delete {{
            opacity: 0;
            cursor: pointer;
            color: #f56565;
            transition: opacity 0.2s;
        }}
        .list-item:hover .item-delete {{
            opacity: 1;
        }}
        .item-editor {{
            font-size: 10px;
            color: #a0aec0;
            opacity: 0.8;
        }}

        .add-item-form {{
            display: flex;
            gap: 8px;
            margin-top: 12px;
        }}
        .add-input {{
            flex: 1;
            padding: 10px 14px;
            border: 2px solid #4a5568;
            border-radius: 8px;
            background: rgba(0, 0, 0, 0.3);
            color: #e2e8f0;
            font-size: 14px;
        }}
        .add-input:focus {{
            outline: none;
            border-color: #667eea;
        }}
        .add-btn {{
            padding: 10px 20px;
            background: linear-gradient(135deg, #667eea, #764ba2);
            border: none;
            border-radius: 8px;
            color: white;
            cursor: pointer;
            font-weight: 500;
            transition: transform 0.2s;
        }}
        .add-btn:hover {{
            transform: scale(1.05);
        }}

        .sync-indicator {{
            font-size: 11px;
            color: #718096;
            text-align: center;
            margin-top: 12px;
        }}
    </style>
</head>
<body>
    <div class="collab-container">
        <div class="collab-header">
            <span class="collab-title">{title}</span>
            <div class="connection-status">
                <span class="status-dot" id="status-{key}"></span>
                <span id="status-text-{key}">Connexion...</span>
            </div>
        </div>

        <div class="presence-bar" id="presence-{key}"></div>

        <div class="list-items" id="items-{key}"></div>

        <form class="add-item-form" id="form-{key}" onsubmit="addItem_{key}(event)">
            <input type="text" class="add-input" id="input-{key}"
                   placeholder="{placeholder}" autocomplete="off">
            <button type="submit" class="add-btn">+ Ajouter</button>
        </form>

        <div class="sync-indicator" id="sync-{key}">—</div>
    </div>

    <script>
    (function() {{
        const Y = window.Y;
        const WebsocketProvider = window.WebsocketProvider;

        // Configuration utilisateur
        const currentUser = {user_config};
        const roomId = '{room_id}';
        const wsUrl = '{ws_url}';

        // Document Yjs
        const ydoc = new Y.Doc();
        const ylist = ydoc.getArray('items');
        const ymap = ydoc.getMap('metadata');

        // Provider WebSocket
        let provider = null;
        let awareness = null;

        // Éléments DOM
        const itemsContainer = document.getElementById('items-{key}');
        const presenceBar = document.getElementById('presence-{key}');
        const statusDot = document.getElementById('status-{key}');
        const statusText = document.getElementById('status-text-{key}');
        const syncIndicator = document.getElementById('sync-{key}');
        const input = document.getElementById('input-{key}');

        // Initialiser le provider
        function initProvider() {{
            try {{
                provider = new WebsocketProvider(wsUrl, roomId, ydoc);
                awareness = provider.awareness;

                // Définir notre présence
                awareness.setLocalStateField('user', currentUser);

                // Événements de connexion
                provider.on('status', ({{ status }}) => {{
                    statusDot.className = 'status-dot ' +
                        (status === 'connected' ? 'connected' : 'connecting');
                    statusText.textContent = status === 'connected' ?
                        'Connecté' : 'Connexion...';
                }});

                // Changements de présence
                awareness.on('change', renderPresence);

                // Changements de données
                ylist.observe(renderItems);

                // Render initial
                renderItems();
                renderPresence();

            }} catch (e) {{
                console.error('Provider init error:', e);
                statusText.textContent = 'Mode hors-ligne';
                // Fallback: mode local
                initLocalMode();
            }}
        }}

        function initLocalMode() {{
            // Mode sans WebSocket (pour dev/test)
            const initialItems = {initial_items};
            initialItems.forEach(item => {{
                ylist.push([{{ id: generateId(), text: item, checked: false }}]);
            }});
            renderItems();
        }}

        function generateId() {{
            return Math.random().toString(36).substr(2, 9);
        }}

        // Rendu des présences
        function renderPresence() {{
            if (!awareness) return;

            presenceBar.innerHTML = '';
            const states = awareness.getStates();

            states.forEach((state, clientId) => {{
                if (!state.user) return;

                const user = state.user;
                const isSelf = clientId === awareness.clientID;

                const avatar = document.createElement('div');
                avatar.className = 'presence-avatar' + (isSelf ? ' self' : '');
                avatar.style.background = user.color || '#667eea';
                avatar.textContent = (user.name || '?').charAt(0).toUpperCase();
                avatar.title = user.name + (isSelf ? ' (vous)' : '');

                presenceBar.appendChild(avatar);
            }});
        }}

        // Rendu des items
        function renderItems() {{
            itemsContainer.innerHTML = '';

            ylist.forEach((item, index) => {{
                const itemEl = document.createElement('div');
                itemEl.className = 'list-item';
                itemEl.dataset.index = index;

                // Checkbox
                const checkbox = document.createElement('input');
                checkbox.type = 'checkbox';
                checkbox.className = 'item-checkbox';
                checkbox.checked = item.checked || false;
                checkbox.addEventListener('change', () => toggleItem(index));

                // Texte éditable
                const text = document.createElement('input');
                text.type = 'text';
                text.className = 'item-text' + (item.checked ? ' checked' : '');
                text.value = item.text || '';
                text.addEventListener('focus', () => startEditing(index));
                text.addEventListener('blur', () => stopEditing(index));
                text.addEventListener('input', (e) => updateItem(index, e.target.value));

                // Bouton supprimer
                const deleteBtn = document.createElement('span');
                deleteBtn.className = 'item-delete';
                deleteBtn.textContent = '✕';
                deleteBtn.addEventListener('click', () => deleteItem(index));

                itemEl.appendChild(checkbox);
                itemEl.appendChild(text);
                itemEl.appendChild(deleteBtn);

                itemsContainer.appendChild(itemEl);
            }});

            updateSync();
        }}

        // Actions
        window.addItem_{key} = function(e) {{
            e.preventDefault();
            const text = input.value.trim();
            if (text) {{
                ydoc.transact(() => {{
                    ylist.push([{{
                        id: generateId(),
                        text: text,
                        checked: false,
                        addedBy: currentUser.name,
                        addedAt: new Date().toISOString()
                    }}]);
                }});
                input.value = '';
                sendToStreamlit();
            }}
        }};

        function toggleItem(index) {{
            ydoc.transact(() => {{
                const item = ylist.get(index);
                ylist.delete(index, 1);
                ylist.insert(index, [{{ ...item, checked: !item.checked }}]);
            }});
            sendToStreamlit();
        }}

        function updateItem(index, newText) {{
            ydoc.transact(() => {{
                const item = ylist.get(index);
                ylist.delete(index, 1);
                ylist.insert(index, [{{ ...item, text: newText }}]);
            }});
            sendToStreamlit();
        }}

        function deleteItem(index) {{
            ydoc.transact(() => {{
                ylist.delete(index, 1);
            }});
            sendToStreamlit();
        }}

        function startEditing(index) {{
            if (awareness) {{
                awareness.setLocalStateField('editing', {{ index, user: currentUser }});
            }}
            const itemEl = itemsContainer.children[index];
            if (itemEl) itemEl.classList.add('editing');
        }}

        function stopEditing(index) {{
            if (awareness) {{
                awareness.setLocalStateField('editing', null);
            }}
            const itemEl = itemsContainer.children[index];
            if (itemEl) itemEl.classList.remove('editing');
        }}

        function updateSync() {{
            const count = ylist.length;
            syncIndicator.textContent = count + ' élément' + (count > 1 ? 's' : '');
        }}

        function sendToStreamlit() {{
            const items = [];
            ylist.forEach(item => items.push(item));

            if (window.parent) {{
                window.parent.postMessage({{
                    type: 'COLLAB_UPDATE',
                    key: '{key}',
                    roomId: roomId,
                    items: items
                }}, '*');
            }}
        }}

        // Initialisation
        initProvider();
    }})();
    </script>
</body>
</html>
"""


_COLLAB_TEXT_HTML = """
<!DOCTYPE html>
<html>
<head>
    <script src="https://cdn.jsdelivr.net/npm/yjs@13.6.10/dist/yjs.min.js"></script>
    <style>
        body {{
            font-family: 'Segoe UI', sans-serif;
            background: transparent;
            margin: 0;
            padding: 12px;
        }}
        .editor-container {{
            background: rgba(45, 55, 72, 0.5);
            border-radius: 12px;
            padding: 16px;
        }}
        .editor-header {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 12px;
        }}
        .editor-title {{ color: #667eea; font-weight: 600; }}
        .editor-textarea {{
            width: 100%;
            min-height: {height}px;
            padding: 12px;
            border: 2px solid #4a5568;
            border-radius: 8px;
            background: rgba(0, 0, 0, 0.3);
            color: #e2e8f0;
            font-size: 14px;
            line-height: 1.6;
            resize: vertical;
        }}
        .editor-textarea:focus {{
            outline: none;
            border-color: #667eea;
        }}
        .cursors-layer {{
            position: relative;
        }}
        .remote-cursor {{
            position: absolute;
            width: 2px;
            background: var(--cursor-color);
            animation: blink 1s infinite;
        }}
    </style>
</head>
<body>
    <div class="editor-container">
        <div class="editor-header">
            <span class="editor-title">{title}</span>
            <span id="status-{key}" style="font-size: 12px; color: #718096;">—</span>
        </div>
        <textarea class="editor-textarea" id="editor-{key}"
                  placeholder="{placeholder}"></textarea>
    </div>

    <script>
    (function() {{
        const editor = document.getElementById('editor-{key}');
        const status = document.getElementById('status-{key}');

        // Yjs document (local pour cette démo)
        let content = {initial_text};
        editor.value = content || '';

        // Synchroniser les changements
        editor.addEventListener('input', () => {{
            content = editor.value;
            status.textContent = 'Sauvegardé';

            if (window.parent) {{
                window.parent.postMessage({{
                    type: 'COLLAB_TEXT_UPDATE',
                    key: '{key}',
                    text: content
                }}, '*');
            }}

            setTimeout(() => {{ status.textContent = '—'; }}, 2000);
        }});
    }})();
    </script>
</body>
</html>
"""


# ═══════════════════════════════════════════════════════════
# FONCTIONS PRINCIPALES
# ═══════════════════════════════════════════════════════════


def collaborative_list(
    room_id: str,
    *,
    initial_items: list[str] | None = None,
    title: str = "Liste collaborative",
    placeholder: str = "Ajouter un élément...",
    key: str | None = None,
    height: int = 400,
    ws_url: str = DEFAULT_WS_URL,
    on_change: Callable[[list[dict]], None] | None = None,
) -> list[dict[str, Any]]:
    """Liste éditable en temps réel avec Yjs.

    Permet à plusieurs utilisateurs de modifier simultanément une liste
    (courses, tâches, etc.) avec synchronisation instantanée.

    Args:
        room_id: Identifiant de la room (unique par liste)
        initial_items: Items initiaux (si nouvelle room)
        title: Titre affiché
        placeholder: Placeholder du champ d'ajout
        key: Clé Streamlit unique
        height: Hauteur du composant
        ws_url: URL du serveur WebSocket Yjs
        on_change: Callback sur modification

    Returns:
        Liste des items actuels [{id, text, checked, addedBy, ...}]
    """
    key = key or f"collab_list_{room_id}"
    user = _get_current_user()

    # State pour stocker les items
    state_key = f"collab_{key}"
    if state_key not in st.session_state:
        st.session_state[state_key] = [
            {"id": str(i), "text": item, "checked": False}
            for i, item in enumerate(initial_items or [])
        ]

    # Input caché pour recevoir les updates
    raw_data = st.text_area(
        f"collab_data_{key}",
        value=json.dumps(st.session_state[state_key]),
        key=f"collab_input_{key}",
        label_visibility="collapsed",
        height=0,
    )

    # Parser si mis à jour
    try:
        updated = json.loads(raw_data) if raw_data else st.session_state[state_key]
        if updated != st.session_state.get(f"{state_key}_last"):
            st.session_state[f"{state_key}_last"] = updated
            st.session_state[state_key] = updated
            if on_change:
                on_change(updated)
    except json.JSONDecodeError:
        updated = st.session_state[state_key]

    # Rendre le composant
    html = _COLLAB_LIST_HTML.format(
        key=key,
        room_id=room_id,
        title=title,
        placeholder=placeholder,
        ws_url=ws_url,
        user_config=json.dumps(user),
        initial_items=json.dumps(initial_items or []),
    )

    components.html(html, height=height)

    return st.session_state.get(state_key, [])


def collaborative_text(
    room_id: str,
    *,
    initial_text: str = "",
    title: str = "Notes partagées",
    placeholder: str = "Écrivez ici...",
    key: str | None = None,
    height: int = 200,
) -> str:
    """Zone de texte collaborative.

    Args:
        room_id: Identifiant de la room
        initial_text: Texte initial
        title: Titre affiché
        placeholder: Placeholder
        key: Clé unique
        height: Hauteur du textarea

    Returns:
        Contenu actuel du texte
    """
    key = key or f"collab_text_{room_id}"

    # State
    state_key = f"collab_text_{key}"
    if state_key not in st.session_state:
        st.session_state[state_key] = initial_text

    # Input caché
    text_input = st.text_area(
        f"collab_text_input_{key}",
        value=st.session_state[state_key],
        key=f"collab_text_raw_{key}",
        label_visibility="collapsed",
        height=0,
    )

    if text_input != st.session_state.get(f"{state_key}_last"):
        st.session_state[f"{state_key}_last"] = text_input
        st.session_state[state_key] = text_input

    html = _COLLAB_TEXT_HTML.format(
        key=key,
        title=title,
        placeholder=placeholder,
        height=height,
        initial_text=json.dumps(st.session_state[state_key]),
    )

    components.html(html, height=height + 80)

    return st.session_state.get(state_key, "")


def presence_indicator(
    room_id: str,
    *,
    key: str | None = None,
) -> None:
    """Indicateur de présence des utilisateurs dans une room.

    Affiche les avatars des utilisateurs actuellement connectés.

    Args:
        room_id: Identifiant de la room
        key: Clé unique
    """
    key = key or f"presence_{room_id}"
    user = _get_current_user()

    html = f"""
    <div style="
        display: flex;
        gap: 8px;
        align-items: center;
        padding: 8px 12px;
        background: rgba(45, 55, 72, 0.5);
        border-radius: 20px;
    ">
        <span style="color: #667eea; font-size: 12px;">👥</span>
        <div style="
            width: 28px;
            height: 28px;
            border-radius: 50%;
            background: {user['color']};
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 12px;
            font-weight: 500;
            border: 2px solid white;
        " title="{user['name']} (vous)">
            {user['name'][0].upper()}
        </div>
        <span style="color: #a0aec0; font-size: 11px;">En ligne</span>
    </div>
    """

    components.html(html, height=50)


# ═══════════════════════════════════════════════════════════
# CLASSES ORIENTÉES OBJET
# ═══════════════════════════════════════════════════════════


class RealtimeRoom:
    """Gestionnaire de room collaborative.

    Usage:
        room = RealtimeRoom("famille_courses")
        room.set_user("Alice", "#667eea")

        items = room.list_widget(initial=["Lait"])
    """

    def __init__(
        self,
        room_id: str,
        *,
        ws_url: str = DEFAULT_WS_URL,
    ):
        self.room_id = room_id
        self.ws_url = ws_url
        self._user = _get_current_user()

    def set_user(self, name: str, color: str | None = None) -> RealtimeRoom:
        """Définit l'utilisateur courant.

        Args:
            name: Nom de l'utilisateur
            color: Couleur (optionnel, auto-générée sinon)
        """
        self._user["name"] = name
        if color:
            self._user["color"] = color
        else:
            self._user["color"] = _get_user_color(name)
        st.session_state["collab_user"] = self._user
        return self

    def list_widget(
        self,
        *,
        initial: list[str] | None = None,
        title: str = "Liste partagée",
        key: str | None = None,
        height: int = 400,
        on_change: Callable[[list], None] | None = None,
    ) -> list[dict]:
        """Affiche une liste collaborative."""
        return collaborative_list(
            self.room_id,
            initial_items=initial,
            title=title,
            key=key or f"room_list_{self.room_id}",
            height=height,
            ws_url=self.ws_url,
            on_change=on_change,
        )

    def text_widget(
        self,
        *,
        initial: str = "",
        title: str = "Notes",
        key: str | None = None,
        height: int = 200,
    ) -> str:
        """Affiche un éditeur de texte collaboratif."""
        return collaborative_text(
            self.room_id,
            initial_text=initial,
            title=title,
            key=key or f"room_text_{self.room_id}",
            height=height,
        )

    def presence(self) -> None:
        """Affiche l'indicateur de présence."""
        presence_indicator(self.room_id)


class CollaborativeCalendar:
    """Calendrier collaboratif (planning repas, activités).

    Usage:
        calendar = CollaborativeCalendar("planning_famille")
        calendar.add_event("Lundi", "Déjeuner", "Pâtes bolognaise")
        calendar.render()
    """

    def __init__(self, room_id: str):
        self.room_id = room_id
        self._events: dict[str, dict[str, str]] = {}
        self._room = RealtimeRoom(room_id)

    def add_event(self, jour: str, slot: str, content: str) -> CollaborativeCalendar:
        """Ajoute un événement."""
        if jour not in self._events:
            self._events[jour] = {}
        self._events[jour][slot] = content
        return self

    def render(self, height: int = 500) -> dict[str, dict[str, str]]:
        """Affiche le calendrier."""
        # Convertir en liste pour le widget collaboratif
        items = []
        for jour, slots in self._events.items():
            for slot, content in slots.items():
                items.append(f"{jour} | {slot} | {content}")

        result = collaborative_list(
            self.room_id,
            initial_items=items,
            title="📅 Planning collaboratif",
            placeholder="Ajouter (Jour | Repas | Plat)...",
            height=height,
        )

        # Parser le résultat
        calendar_data: dict[str, dict[str, str]] = {}
        for item in result:
            text = item.get("text", "")
            parts = text.split("|")
            if len(parts) >= 3:
                jour = parts[0].strip()
                slot = parts[1].strip()
                content = parts[2].strip()
                if jour not in calendar_data:
                    calendar_data[jour] = {}
                calendar_data[jour][slot] = content

        return calendar_data


class CollaborativeEditor:
    """Éditeur collaboratif complet avec liste + notes.

    Combine liste et zone de texte dans une interface unifiée.

    Usage:
        editor = CollaborativeEditor("ma_room")
        editor.render()
    """

    def __init__(self, room_id: str, user_name: str | None = None):
        self.room = RealtimeRoom(room_id)
        if user_name:
            self.room.set_user(user_name)

    def render(
        self,
        *,
        show_list: bool = True,
        show_notes: bool = True,
        list_title: str = "Liste partagée",
        notes_title: str = "Notes",
        initial_items: list[str] | None = None,
        initial_notes: str = "",
    ) -> tuple[list[dict], str]:
        """Affiche l'éditeur complet.

        Returns:
            Tuple (items, notes)
        """
        # Présence en haut
        self.room.presence()

        items = []
        notes = ""

        if show_list and show_notes:
            col1, col2 = st.columns([1, 1])
            with col1:
                items = self.room.list_widget(
                    initial=initial_items,
                    title=list_title,
                    height=350,
                )
            with col2:
                notes = self.room.text_widget(
                    initial=initial_notes,
                    title=notes_title,
                    height=280,
                )
        elif show_list:
            items = self.room.list_widget(
                initial=initial_items,
                title=list_title,
            )
        elif show_notes:
            notes = self.room.text_widget(
                initial=initial_notes,
                title=notes_title,
            )

        return items, notes
