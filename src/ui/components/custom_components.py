"""
Custom Components — Innovation v11: Streamlit Components Custom.

Composants personnalisés pour:
- Drag & Drop Planning (planning repas, tâches)
- Gantt Chart interactif (timeline projets, batch cooking)
- Kanban Board (gestion tâches familiales)

Ces composants utilisent HTML/JS avec communication bidirectionnelle Streamlit.
Pour des composants plus complexes, voir le template React dans /components/react/.

Usage:
    from src.ui.components.custom_components import (
        drag_drop_planning,
        gantt_chart,
        kanban_board,
    )

    # Planning drag & drop
    planning = drag_drop_planning(
        jours=["Lundi", "Mardi", ...],
        items={"Lundi": ["Salade", "Poulet rôti"], ...},
    )

    # Gantt chart
    gantt_data = [
        {"task": "Préparation", "start": "09:00", "end": "10:00"},
        {"task": "Cuisson", "start": "10:00", "end": "11:30"},
    ]
    gantt_chart(gantt_data, title="Batch Cooking")

    # Kanban
    kanban_board(
        columns=["À faire", "En cours", "Fait"],
        cards=kanban_data,
    )
"""

from __future__ import annotations

import json
import logging
from datetime import date, datetime, time, timedelta
from typing import Any, Callable

import streamlit as st
import streamlit.components.v1 as components

logger = logging.getLogger(__name__)

__all__ = [
    "drag_drop_planning",
    "gantt_chart",
    "kanban_board",
    "timeline_view",
    "DragDropPlanner",
    "GanttChart",
    "KanbanBoard",
]


# ═══════════════════════════════════════════════════════════
# DRAG & DROP PLANNING
# ═══════════════════════════════════════════════════════════

_DRAG_DROP_HTML = """
<!DOCTYPE html>
<html>
<head>
    <style>
        * {{ box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', system-ui, sans-serif;
            background: transparent;
            margin: 0;
            padding: 8px;
        }}
        .planner-container {{
            display: grid;
            grid-template-columns: repeat({num_cols}, 1fr);
            gap: 12px;
            min-height: 400px;
        }}
        .day-column {{
            background: rgba(45, 55, 72, 0.5);
            border-radius: 12px;
            padding: 12px;
            min-height: 350px;
        }}
        .day-header {{
            font-weight: 600;
            color: #667eea;
            padding: 8px;
            text-align: center;
            border-bottom: 2px solid #4a5568;
            margin-bottom: 12px;
        }}
        .drop-zone {{
            min-height: 250px;
            padding: 8px;
            border: 2px dashed transparent;
            border-radius: 8px;
            transition: all 0.2s;
        }}
        .drop-zone.drag-over {{
            border-color: #667eea;
            background: rgba(102, 126, 234, 0.1);
        }}
        .draggable-item {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 10px 14px;
            border-radius: 8px;
            margin-bottom: 8px;
            cursor: grab;
            transition: all 0.2s;
            box-shadow: 0 2px 8px rgba(0,0,0,0.2);
        }}
        .draggable-item:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        }}
        .draggable-item.dragging {{
            opacity: 0.5;
            cursor: grabbing;
        }}
        .item-delete {{
            float: right;
            cursor: pointer;
            opacity: 0.7;
            margin-left: 8px;
        }}
        .item-delete:hover {{ opacity: 1; }}
        .add-item {{
            border: 2px dashed #4a5568;
            padding: 10px;
            border-radius: 8px;
            text-align: center;
            color: #a0aec0;
            cursor: pointer;
            transition: all 0.2s;
        }}
        .add-item:hover {{
            border-color: #667eea;
            color: #667eea;
        }}
        .item-input {{
            width: 100%;
            padding: 8px;
            border: none;
            border-radius: 6px;
            background: rgba(255,255,255,0.1);
            color: white;
            margin-bottom: 8px;
        }}
        .item-input:focus {{
            outline: 2px solid #667eea;
        }}
    </style>
</head>
<body>
    <div class="planner-container" id="planner-{key}">
        {columns_html}
    </div>

    <script>
    (function() {{
        const plannerData_{key} = {initial_data};
        let draggedItem = null;
        let sourceColumn = null;

        // Rendre les items draggables
        document.querySelectorAll('.draggable-item').forEach(item => {{
            item.draggable = true;

            item.addEventListener('dragstart', (e) => {{
                draggedItem = item;
                sourceColumn = item.closest('.day-column').dataset.day;
                item.classList.add('dragging');
                e.dataTransfer.effectAllowed = 'move';
            }});

            item.addEventListener('dragend', () => {{
                item.classList.remove('dragging');
                draggedItem = null;
            }});
        }});

        // Drop zones
        document.querySelectorAll('.drop-zone').forEach(zone => {{
            zone.addEventListener('dragover', (e) => {{
                e.preventDefault();
                zone.classList.add('drag-over');
            }});

            zone.addEventListener('dragleave', () => {{
                zone.classList.remove('drag-over');
            }});

            zone.addEventListener('drop', (e) => {{
                e.preventDefault();
                zone.classList.remove('drag-over');

                if (draggedItem) {{
                    const targetDay = zone.closest('.day-column').dataset.day;
                    zone.insertBefore(draggedItem, zone.querySelector('.add-item'));

                    // Mettre à jour les données
                    updateData_{key}(sourceColumn, targetDay, draggedItem.dataset.item);
                }}
            }});
        }});

        // Supprimer un item
        document.querySelectorAll('.item-delete').forEach(btn => {{
            btn.addEventListener('click', (e) => {{
                const item = e.target.closest('.draggable-item');
                const day = item.closest('.day-column').dataset.day;
                const itemName = item.dataset.item;

                item.remove();
                removeItem_{key}(day, itemName);
            }});
        }});

        // Ajouter un item
        document.querySelectorAll('.add-item').forEach(btn => {{
            btn.addEventListener('click', () => {{
                const day = btn.closest('.day-column').dataset.day;
                const input = document.createElement('input');
                input.className = 'item-input';
                input.placeholder = 'Nouveau repas...';

                btn.replaceWith(input);
                input.focus();

                input.addEventListener('blur', () => finishAdd_{key}(input, day));
                input.addEventListener('keypress', (e) => {{
                    if (e.key === 'Enter') finishAdd_{key}(input, day);
                }});
            }});
        }});

        function finishAdd_{key}(input, day) {{
            const value = input.value.trim();
            if (value) {{
                addItem_{key}(day, value);
            }}
            // Recréer le bouton add
            const addBtn = document.createElement('div');
            addBtn.className = 'add-item';
            addBtn.textContent = '+ Ajouter';
            addBtn.addEventListener('click', () => {{
                const newInput = document.createElement('input');
                newInput.className = 'item-input';
                newInput.placeholder = 'Nouveau repas...';
                addBtn.replaceWith(newInput);
                newInput.focus();
                newInput.addEventListener('blur', () => finishAdd_{key}(newInput, day));
                newInput.addEventListener('keypress', (e) => {{
                    if (e.key === 'Enter') finishAdd_{key}(newInput, day);
                }});
            }});
            input.replaceWith(addBtn);
        }}

        function updateData_{key}(fromDay, toDay, item) {{
            // Retirer de l'ancien jour
            if (plannerData_{key}[fromDay]) {{
                const idx = plannerData_{key}[fromDay].indexOf(item);
                if (idx > -1) plannerData_{key}[fromDay].splice(idx, 1);
            }}
            // Ajouter au nouveau jour
            if (!plannerData_{key}[toDay]) plannerData_{key}[toDay] = [];
            plannerData_{key}[toDay].push(item);

            sendUpdate_{key}();
        }}

        function addItem_{key}(day, item) {{
            if (!plannerData_{key}[day]) plannerData_{key}[day] = [];
            plannerData_{key}[day].push(item);

            // Créer l'élément visuel
            const zone = document.querySelector(`.day-column[data-day="${{day}}"] .drop-zone`);
            const itemEl = document.createElement('div');
            itemEl.className = 'draggable-item';
            itemEl.draggable = true;
            itemEl.dataset.item = item;
            itemEl.innerHTML = item + '<span class="item-delete">✕</span>';

            // Ajouter les événements
            itemEl.addEventListener('dragstart', (e) => {{
                draggedItem = itemEl;
                sourceColumn = day;
                itemEl.classList.add('dragging');
            }});
            itemEl.addEventListener('dragend', () => {{
                itemEl.classList.remove('dragging');
                draggedItem = null;
            }});
            itemEl.querySelector('.item-delete').addEventListener('click', () => {{
                itemEl.remove();
                removeItem_{key}(day, item);
            }});

            zone.insertBefore(itemEl, zone.querySelector('.add-item'));
            sendUpdate_{key}();
        }}

        function removeItem_{key}(day, item) {{
            if (plannerData_{key}[day]) {{
                const idx = plannerData_{key}[day].indexOf(item);
                if (idx > -1) plannerData_{key}[day].splice(idx, 1);
            }}
            sendUpdate_{key}();
        }}

        function sendUpdate_{key}() {{
            if (window.parent) {{
                window.parent.postMessage({{
                    type: 'PLANNER_UPDATE',
                    key: '{key}',
                    data: plannerData_{key}
                }}, '*');
            }}
        }}
    }})();
    </script>
</body>
</html>
"""


def drag_drop_planning(
    jours: list[str],
    items: dict[str, list[str]],
    *,
    key: str = "planner",
    height: int = 450,
    on_change: Callable[[dict[str, list[str]]], None] | None = None,
) -> dict[str, list[str]]:
    """Planning drag & drop pour repas ou tâches.

    Args:
        jours: Liste des jours/colonnes
        items: Dict jour -> liste d'items
        key: Clé unique
        height: Hauteur du composant
        on_change: Callback sur modification

    Returns:
        Dict mis à jour avec les items réorganisés
    """
    # Générer le HTML des colonnes
    columns_html = ""
    for jour in jours:
        jour_items = items.get(jour, [])
        items_html = ""
        for item in jour_items:
            items_html += f"""
                <div class="draggable-item" draggable="true" data-item="{item}">
                    {item}
                    <span class="item-delete">✕</span>
                </div>
            """
        items_html += '<div class="add-item">+ Ajouter</div>'

        columns_html += f"""
            <div class="day-column" data-day="{jour}">
                <div class="day-header">{jour}</div>
                <div class="drop-zone">{items_html}</div>
            </div>
        """

    # State pour stocker le résultat
    state_key = f"planner_{key}"
    if state_key not in st.session_state:
        st.session_state[state_key] = items.copy()

    # Input caché pour recevoir les updates
    raw_data = st.text_area(
        f"planner_data_{key}",
        value=json.dumps(items),
        key=f"planner_input_{key}",
        label_visibility="collapsed",
        height=0,
    )

    # Rendre le composant
    html = _DRAG_DROP_HTML.format(
        key=key,
        num_cols=len(jours),
        columns_html=columns_html,
        initial_data=json.dumps(items),
    )
    components.html(html, height=height)

    # Parser les données mises à jour
    try:
        updated = json.loads(raw_data) if raw_data else items
        if updated != st.session_state.get(f"{state_key}_last"):
            st.session_state[f"{state_key}_last"] = updated
            st.session_state[state_key] = updated
            if on_change:
                on_change(updated)
    except json.JSONDecodeError:
        updated = items

    return st.session_state.get(state_key, items)


# ═══════════════════════════════════════════════════════════
# GANTT CHART
# ═══════════════════════════════════════════════════════════

_GANTT_HTML = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{
            font-family: 'Segoe UI', system-ui, sans-serif;
            background: transparent;
            margin: 0;
            padding: 8px;
            color: #e2e8f0;
        }}
        .gantt-title {{
            font-size: 18px;
            font-weight: 600;
            color: #667eea;
            margin-bottom: 16px;
        }}
        .gantt-container {{
            display: flex;
            flex-direction: column;
            gap: 8px;
        }}
        .gantt-header {{
            display: flex;
            border-bottom: 1px solid #4a5568;
            padding-bottom: 8px;
            margin-bottom: 8px;
        }}
        .gantt-task-label {{
            width: 150px;
            flex-shrink: 0;
            font-weight: 500;
        }}
        .gantt-timeline {{
            flex-grow: 1;
            display: flex;
            position: relative;
        }}
        .gantt-hour {{
            flex: 1;
            text-align: center;
            font-size: 12px;
            color: #a0aec0;
            border-left: 1px solid #4a5568;
        }}
        .gantt-row {{
            display: flex;
            align-items: center;
            height: 40px;
            margin: 4px 0;
        }}
        .gantt-task-name {{
            width: 150px;
            flex-shrink: 0;
            font-size: 14px;
            padding-right: 12px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}
        .gantt-bar-container {{
            flex-grow: 1;
            position: relative;
            height: 100%;
            background: rgba(74, 85, 104, 0.3);
            border-radius: 4px;
        }}
        .gantt-bar {{
            position: absolute;
            height: 28px;
            top: 6px;
            border-radius: 6px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 12px;
            font-weight: 500;
            color: white;
            box-shadow: 0 2px 8px rgba(0,0,0,0.3);
            cursor: pointer;
            transition: transform 0.2s;
        }}
        .gantt-bar:hover {{
            transform: scaleY(1.1);
        }}
        .gantt-bar.type-prep {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }}
        .gantt-bar.type-cook {{
            background: linear-gradient(135deg, #ed8936 0%, #dd6b20 100%);
        }}
        .gantt-bar.type-rest {{
            background: linear-gradient(135deg, #48bb78 0%, #38a169 100%);
        }}
        .gantt-bar.type-default {{
            background: linear-gradient(135deg, #4299e1 0%, #3182ce 100%);
        }}
        .gantt-legend {{
            display: flex;
            gap: 16px;
            margin-top: 16px;
            font-size: 12px;
        }}
        .legend-item {{
            display: flex;
            align-items: center;
            gap: 6px;
        }}
        .legend-color {{
            width: 16px;
            height: 16px;
            border-radius: 4px;
        }}
    </style>
</head>
<body>
    <div class="gantt-title">{title}</div>
    <div class="gantt-container">
        <div class="gantt-header">
            <div class="gantt-task-label">Tâche</div>
            <div class="gantt-timeline">
                {hours_html}
            </div>
        </div>
        {rows_html}
    </div>
    {legend_html}
</body>
</html>
"""


def gantt_chart(
    tasks: list[dict[str, Any]],
    *,
    title: str = "Timeline",
    start_hour: int = 8,
    end_hour: int = 20,
    key: str = "gantt",
    height: int = 400,
    show_legend: bool = True,
) -> None:
    """Affiche un Gantt chart interactif.

    Format des tâches:
    {
        "task": "Nom de la tâche",
        "start": "09:00" ou datetime/time,
        "end": "10:30" ou datetime/time,
        "type": "prep|cook|rest|default" (optionnel, pour couleur),
        "progress": 0.5 (optionnel, 0-1)
    }

    Args:
        tasks: Liste des tâches
        title: Titre du chart
        start_hour: Heure de début (0-23)
        end_hour: Heure de fin (0-23)
        key: Clé unique
        height: Hauteur du composant
        show_legend: Afficher la légende
    """
    total_hours = end_hour - start_hour

    # Générer les heures du header
    hours_html = ""
    for h in range(start_hour, end_hour + 1):
        hours_html += f'<div class="gantt-hour">{h}:00</div>'

    # Générer les barres pour chaque tâche
    rows_html = ""
    for task in tasks:
        name = task.get("task", "Tâche")
        task_type = task.get("type", "default")

        # Parser les heures
        start_time = task.get("start", "09:00")
        end_time = task.get("end", "10:00")

        if isinstance(start_time, datetime | time):
            start_time = start_time.strftime("%H:%M")
        if isinstance(end_time, datetime | time):
            end_time = end_time.strftime("%H:%M")

        # Calculer la position
        start_parts = start_time.split(":")
        end_parts = end_time.split(":")
        start_minutes = int(start_parts[0]) * 60 + int(start_parts[1])
        end_minutes = int(end_parts[0]) * 60 + int(end_parts[1])

        # Position en pourcentage
        total_minutes = total_hours * 60
        left_pct = ((start_minutes - start_hour * 60) / total_minutes) * 100
        width_pct = ((end_minutes - start_minutes) / total_minutes) * 100

        duration = f"{start_time}-{end_time}"

        rows_html += f"""
        <div class="gantt-row">
            <div class="gantt-task-name" title="{name}">{name}</div>
            <div class="gantt-bar-container">
                <div class="gantt-bar type-{task_type}"
                     style="left: {left_pct}%; width: {width_pct}%;"
                     title="{name}: {duration}">
                    {duration}
                </div>
            </div>
        </div>
        """

    # Légende
    legend_html = ""
    if show_legend:
        legend_html = """
        <div class="gantt-legend">
            <div class="legend-item">
                <div class="legend-color" style="background: linear-gradient(135deg, #667eea, #764ba2);"></div>
                Préparation
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background: linear-gradient(135deg, #ed8936, #dd6b20);"></div>
                Cuisson
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background: linear-gradient(135deg, #48bb78, #38a169);"></div>
                Repos
            </div>
        </div>
        """

    html = _GANTT_HTML.format(
        title=title,
        hours_html=hours_html,
        rows_html=rows_html,
        legend_html=legend_html,
    )

    components.html(html, height=height)


# ═══════════════════════════════════════════════════════════
# KANBAN BOARD
# ═══════════════════════════════════════════════════════════

_KANBAN_HTML = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{
            font-family: 'Segoe UI', system-ui, sans-serif;
            background: transparent;
            margin: 0;
            padding: 8px;
        }}
        .kanban-container {{
            display: flex;
            gap: 16px;
            overflow-x: auto;
            padding-bottom: 8px;
        }}
        .kanban-column {{
            flex: 0 0 280px;
            background: rgba(45, 55, 72, 0.6);
            border-radius: 12px;
            padding: 12px;
            min-height: 400px;
        }}
        .column-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 8px;
            margin-bottom: 12px;
            border-bottom: 2px solid #4a5568;
        }}
        .column-title {{
            font-weight: 600;
            color: #667eea;
        }}
        .column-count {{
            background: rgba(102, 126, 234, 0.2);
            color: #667eea;
            padding: 2px 10px;
            border-radius: 12px;
            font-size: 12px;
        }}
        .card-list {{
            min-height: 300px;
        }}
        .kanban-card {{
            background: rgba(255, 255, 255, 0.08);
            border-radius: 8px;
            padding: 12px;
            margin-bottom: 10px;
            cursor: grab;
            transition: all 0.2s;
            border-left: 3px solid #667eea;
        }}
        .kanban-card:hover {{
            background: rgba(255, 255, 255, 0.12);
            transform: translateX(4px);
        }}
        .kanban-card.dragging {{
            opacity: 0.5;
        }}
        .card-title {{
            font-weight: 500;
            color: #e2e8f0;
            margin-bottom: 6px;
        }}
        .card-description {{
            font-size: 12px;
            color: #a0aec0;
            margin-bottom: 8px;
        }}
        .card-meta {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 11px;
            color: #718096;
        }}
        .card-tag {{
            background: rgba(102, 126, 234, 0.2);
            color: #667eea;
            padding: 2px 8px;
            border-radius: 4px;
        }}
        .card-priority-high {{ border-left-color: #f56565; }}
        .card-priority-medium {{ border-left-color: #ed8936; }}
        .card-priority-low {{ border-left-color: #48bb78; }}
        .drop-indicator {{
            height: 3px;
            background: #667eea;
            border-radius: 2px;
            margin: 4px 0;
            display: none;
        }}
        .card-list.drag-over .drop-indicator {{
            display: block;
        }}
    </style>
</head>
<body>
    <div class="kanban-container" id="kanban-{key}">
        {columns_html}
    </div>

    <script>
    (function() {{
        let kanbanData_{key} = {initial_data};
        let draggedCard = null;
        let sourceColumn = null;

        document.querySelectorAll('.kanban-card').forEach(card => {{
            card.draggable = true;

            card.addEventListener('dragstart', (e) => {{
                draggedCard = card;
                sourceColumn = card.closest('.kanban-column').dataset.column;
                card.classList.add('dragging');
            }});

            card.addEventListener('dragend', () => {{
                card.classList.remove('dragging');
                document.querySelectorAll('.drag-over').forEach(el => el.classList.remove('drag-over'));
                draggedCard = null;
            }});
        }});

        document.querySelectorAll('.card-list').forEach(list => {{
            list.addEventListener('dragover', (e) => {{
                e.preventDefault();
                list.classList.add('drag-over');
            }});

            list.addEventListener('dragleave', () => {{
                list.classList.remove('drag-over');
            }});

            list.addEventListener('drop', (e) => {{
                e.preventDefault();
                list.classList.remove('drag-over');

                if (draggedCard) {{
                    const targetColumn = list.closest('.kanban-column').dataset.column;
                    list.appendChild(draggedCard);

                    updateKanban_{key}(sourceColumn, targetColumn, draggedCard.dataset.id);
                }}
            }});
        }});

        function updateKanban_{key}(from, to, cardId) {{
            // Mettre à jour les données
            const card = kanbanData_{key}[from].find(c => c.id === cardId);
            if (card) {{
                kanbanData_{key}[from] = kanbanData_{key}[from].filter(c => c.id !== cardId);
                if (!kanbanData_{key}[to]) kanbanData_{key}[to] = [];
                kanbanData_{key}[to].push(card);

                // Mettre à jour les compteurs
                updateCounts_{key}();

                // Envoyer à Streamlit
                if (window.parent) {{
                    window.parent.postMessage({{
                        type: 'KANBAN_UPDATE',
                        key: '{key}',
                        data: kanbanData_{key}
                    }}, '*');
                }}
            }}
        }}

        function updateCounts_{key}() {{
            document.querySelectorAll('.kanban-column').forEach(col => {{
                const column = col.dataset.column;
                const count = col.querySelectorAll('.kanban-card').length;
                col.querySelector('.column-count').textContent = count;
            }});
        }}
    }})();
    </script>
</body>
</html>
"""


def kanban_board(
    columns: list[str],
    cards: dict[str, list[dict[str, Any]]],
    *,
    key: str = "kanban",
    height: int = 500,
    on_change: Callable[[dict[str, list[dict]]], None] | None = None,
) -> dict[str, list[dict[str, Any]]]:
    """Tableau Kanban interactif.

    Format des cartes:
    {
        "id": "unique_id",
        "title": "Titre de la tâche",
        "description": "Description optionnelle",
        "priority": "high|medium|low",
        "tag": "Tag optionnel",
        "due": "Date limite"
    }

    Args:
        columns: Liste des colonnes (ex: ["À faire", "En cours", "Fait"])
        cards: Dict colonne -> liste de cartes
        key: Clé unique
        height: Hauteur
        on_change: Callback sur modification

    Returns:
        Dict mis à jour
    """
    # Générer le HTML des colonnes
    columns_html = ""
    for col in columns:
        col_cards = cards.get(col, [])
        count = len(col_cards)

        cards_html = ""
        for card in col_cards:
            priority_class = f"card-priority-{card.get('priority', 'medium')}"
            tag_html = f'<span class="card-tag">{card["tag"]}</span>' if card.get("tag") else ""
            due_html = card.get("due", "")

            cards_html += f"""
            <div class="kanban-card {priority_class}" draggable="true" data-id="{card.get('id', '')}">
                <div class="card-title">{card.get('title', 'Sans titre')}</div>
                <div class="card-description">{card.get('description', '')}</div>
                <div class="card-meta">
                    {tag_html}
                    <span>{due_html}</span>
                </div>
            </div>
            """

        columns_html += f"""
        <div class="kanban-column" data-column="{col}">
            <div class="column-header">
                <span class="column-title">{col}</span>
                <span class="column-count">{count}</span>
            </div>
            <div class="card-list">
                {cards_html}
                <div class="drop-indicator"></div>
            </div>
        </div>
        """

    # State
    state_key = f"kanban_{key}"
    if state_key not in st.session_state:
        st.session_state[state_key] = cards.copy()

    html = _KANBAN_HTML.format(
        key=key,
        columns_html=columns_html,
        initial_data=json.dumps(cards),
    )

    components.html(html, height=height)

    return st.session_state.get(state_key, cards)


# ═══════════════════════════════════════════════════════════
# TIMELINE VIEW (bonus)
# ═══════════════════════════════════════════════════════════


def timeline_view(
    events: list[dict[str, Any]],
    *,
    key: str = "timeline",
    height: int = 300,
) -> None:
    """Affiche une timeline verticale d'événements.

    Format événements:
    {
        "time": "09:00" ou datetime,
        "title": "Titre",
        "description": "Description",
        "icon": "🍳" (optionnel)
    }
    """
    html = """
    <style>
        .timeline { padding: 20px; }
        .timeline-item {
            display: flex;
            gap: 16px;
            margin-bottom: 20px;
            position: relative;
        }
        .timeline-item::before {
            content: '';
            position: absolute;
            left: 39px;
            top: 30px;
            width: 2px;
            height: calc(100% + 10px);
            background: #4a5568;
        }
        .timeline-item:last-child::before { display: none; }
        .timeline-time {
            width: 60px;
            font-size: 14px;
            color: #667eea;
            font-weight: 500;
        }
        .timeline-icon {
            width: 40px;
            height: 40px;
            background: linear-gradient(135deg, #667eea, #764ba2);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 18px;
            z-index: 1;
        }
        .timeline-content {
            flex: 1;
            background: rgba(45, 55, 72, 0.5);
            padding: 12px 16px;
            border-radius: 8px;
        }
        .timeline-title { font-weight: 500; color: #e2e8f0; }
        .timeline-desc { font-size: 13px; color: #a0aec0; margin-top: 4px; }
    </style>
    <div class="timeline">
    """

    for event in events:
        time_str = event.get("time", "")
        if isinstance(time_str, datetime | time):
            time_str = time_str.strftime("%H:%M")

        icon = event.get("icon", "📍")
        title = event.get("title", "")
        desc = event.get("description", "")

        html += f"""
        <div class="timeline-item">
            <div class="timeline-time">{time_str}</div>
            <div class="timeline-icon">{icon}</div>
            <div class="timeline-content">
                <div class="timeline-title">{title}</div>
                <div class="timeline-desc">{desc}</div>
            </div>
        </div>
        """

    html += "</div>"
    components.html(html, height=height)


# ═══════════════════════════════════════════════════════════
# CLASSES WRAPPER (pour usage avancé)
# ═══════════════════════════════════════════════════════════


class DragDropPlanner:
    """Wrapper orienté objet pour le planning drag & drop."""

    def __init__(self, jours: list[str], key: str = "planner"):
        self.jours = jours
        self.key = key
        self._items: dict[str, list[str]] = {j: [] for j in jours}
        self._callbacks: list[Callable] = []

    def set_items(self, items: dict[str, list[str]]) -> DragDropPlanner:
        self._items = items
        return self

    def on_change(self, callback: Callable) -> DragDropPlanner:
        self._callbacks.append(callback)
        return self

    def render(self, height: int = 450) -> dict[str, list[str]]:
        def handle_change(data):
            for cb in self._callbacks:
                cb(data)

        return drag_drop_planning(
            self.jours,
            self._items,
            key=self.key,
            height=height,
            on_change=handle_change if self._callbacks else None,
        )


class GanttChart:
    """Wrapper orienté objet pour le Gantt chart."""

    def __init__(self, title: str = "Timeline", key: str = "gantt"):
        self.title = title
        self.key = key
        self._tasks: list[dict] = []
        self._start_hour = 8
        self._end_hour = 20

    def add_task(
        self,
        name: str,
        start: str,
        end: str,
        task_type: str = "default",
    ) -> GanttChart:
        self._tasks.append({"task": name, "start": start, "end": end, "type": task_type})
        return self

    def set_hours(self, start: int, end: int) -> GanttChart:
        self._start_hour = start
        self._end_hour = end
        return self

    def render(self, height: int = 400) -> None:
        gantt_chart(
            self._tasks,
            title=self.title,
            start_hour=self._start_hour,
            end_hour=self._end_hour,
            key=self.key,
            height=height,
        )


class KanbanBoard:
    """Wrapper orienté objet pour le Kanban board."""

    def __init__(self, columns: list[str], key: str = "kanban"):
        self.columns = columns
        self.key = key
        self._cards: dict[str, list[dict]] = {c: [] for c in columns}
        self._callbacks: list[Callable] = []

    def add_card(
        self,
        column: str,
        title: str,
        **kwargs,
    ) -> KanbanBoard:
        card = {"id": f"card_{len(self._cards.get(column, []))}", "title": title, **kwargs}
        if column not in self._cards:
            self._cards[column] = []
        self._cards[column].append(card)
        return self

    def on_change(self, callback: Callable) -> KanbanBoard:
        self._callbacks.append(callback)
        return self

    def render(self, height: int = 500) -> dict[str, list[dict]]:
        def handle_change(data):
            for cb in self._callbacks:
                cb(data)

        return kanban_board(
            self.columns,
            self._cards,
            key=self.key,
            height=height,
            on_change=handle_change if self._callbacks else None,
        )
