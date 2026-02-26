"""
Composants Custom Streamlit (st.components.v1) — Innovation 2.1.

Composants JavaScript natifs pour les widgets lourds:
- Drag & Drop Planning — Glisser-déposer les repas sur un calendrier interactif
- Barcode Scanner WebRTC — Scanner directement depuis la caméra sans lib externe
- Plan Jardin 2D Canvas — Éditeur drag & drop avec zones et plantes

Usage:
    from src.ui.components.custom import (
        planning_drag_drop,
        barcode_scanner_webrtc,
        plan_jardin_2d,
    )

    # Planning interactif drag & drop
    result = planning_drag_drop(
        jours=["Lundi", "Mardi", ...],
        repas={"Lundi": {"midi": "Pasta", "soir": "Salade"}},
    )

    # Scanner de code-barres
    barcode = barcode_scanner_webrtc()
    if barcode:
        st.write(f"Code scanné: {barcode}")

    # Plan de jardin 2D
    plan = plan_jardin_2d(
        zones=[{"nom": "Potager", "x": 0, "y": 0, "w": 200, "h": 150}],
        plantes=[{"nom": "Tomate", "zone": "Potager", "x": 50, "y": 50}],
    )
"""

from __future__ import annotations

import json
import logging
from typing import Any

import streamlit as st
import streamlit.components.v1 as components

from src.ui.registry import composant_ui

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# 1. DRAG & DROP PLANNING — Calendrier interactif
# ═══════════════════════════════════════════════════════════

_PLANNING_HTML = """
<!DOCTYPE html>
<html>
<head>
<style>
* { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, sans-serif; }
body { background: transparent; }

.planning-grid {
    display: grid;
    grid-template-columns: 80px repeat(7, 1fr);
    gap: 2px;
    padding: 8px;
}
.planning-header {
    background: linear-gradient(135deg, #667eea 0%%, #764ba2 100%%);
    color: white;
    padding: 8px 4px;
    text-align: center;
    font-weight: 600;
    font-size: 0.85em;
    border-radius: 6px;
}
.planning-label {
    background: #f8f9fa;
    padding: 8px 6px;
    font-weight: 600;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.8em;
    border-radius: 4px;
    color: #495057;
}
.planning-cell {
    min-height: 60px;
    border: 2px dashed #dee2e6;
    border-radius: 6px;
    padding: 4px;
    transition: all 0.2s;
    background: white;
}
.planning-cell.drag-over {
    border-color: #667eea;
    background: #eef0ff;
    box-shadow: 0 0 8px rgba(102,126,234,0.3);
}
.meal-chip {
    background: linear-gradient(135deg, #f093fb 0%%, #f5576c 100%%);
    color: white;
    padding: 4px 8px;
    border-radius: 12px;
    font-size: 0.75em;
    cursor: grab;
    margin: 2px;
    display: inline-block;
    transition: transform 0.1s;
    user-select: none;
}
.meal-chip:hover { transform: scale(1.05); }
.meal-chip:active { cursor: grabbing; }
.meal-chip.dragging { opacity: 0.5; }
.add-btn {
    width: 100%%;
    border: none;
    background: none;
    color: #adb5bd;
    cursor: pointer;
    padding: 4px;
    font-size: 1.2em;
    border-radius: 4px;
}
.add-btn:hover { background: #f8f9fa; color: #667eea; }

.recipes-pool {
    margin-top: 12px;
    padding: 8px;
    background: #f8f9fa;
    border-radius: 8px;
    display: flex;
    flex-wrap: wrap;
    gap: 4px;
    min-height: 40px;
}
.recipes-pool-label {
    font-size: 0.85em;
    color: #6c757d;
    width: 100%%;
    margin-bottom: 4px;
}
</style>
</head>
<body>
<div class="planning-grid" id="grid"></div>
<div class="recipes-pool" id="pool">
    <div class="recipes-pool-label">📋 Recettes disponibles — glisser sur le planning</div>
</div>

<script>
const JOURS = %JOURS%;
const TYPES_REPAS = %TYPES_REPAS%;
const REPAS_INIT = %REPAS%;
const RECETTES_DISPO = %RECETTES%;

const grid = document.getElementById('grid');
const pool = document.getElementById('pool');
let planningData = JSON.parse(JSON.stringify(REPAS_INIT));

function buildGrid() {
    grid.innerHTML = '';
    // Corner
    grid.appendChild(el('div', 'planning-header', ''));
    // Headers
    JOURS.forEach(j => grid.appendChild(el('div', 'planning-header', j)));

    TYPES_REPAS.forEach(type => {
        grid.appendChild(el('div', 'planning-label', type));
        JOURS.forEach(jour => {
            const cell = el('div', 'planning-cell');
            cell.dataset.jour = jour;
            cell.dataset.type = type;

            const repas = (planningData[jour] || {})[type] || '';
            if (repas) {
                const chip = createChip(repas, jour, type);
                cell.appendChild(chip);
            }

            cell.appendChild(createAddBtn(jour, type));
            setupDropZone(cell);
            grid.appendChild(cell);
        });
    });
}

function el(tag, cls, text) {
    const e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text) e.textContent = text;
    return e;
}

function createChip(name, jour, type) {
    const chip = el('div', 'meal-chip', name);
    chip.draggable = true;
    chip.dataset.name = name;
    chip.dataset.fromJour = jour;
    chip.dataset.fromType = type;

    chip.addEventListener('dragstart', e => {
        e.dataTransfer.setData('text/plain', JSON.stringify({name, fromJour: jour, fromType: type}));
        chip.classList.add('dragging');
    });
    chip.addEventListener('dragend', () => chip.classList.remove('dragging'));

    // Double-click to remove
    chip.addEventListener('dblclick', () => {
        if (!planningData[jour]) planningData[jour] = {};
        planningData[jour][type] = '';
        sendUpdate();
        buildGrid();
    });

    return chip;
}

function createAddBtn(jour, type) {
    const btn = el('button', 'add-btn', '+');
    btn.title = 'Ajouter un repas';
    btn.addEventListener('click', () => {
        const name = prompt('Nom du repas:');
        if (name) {
            if (!planningData[jour]) planningData[jour] = {};
            planningData[jour][type] = name;
            sendUpdate();
            buildGrid();
        }
    });
    return btn;
}

function setupDropZone(cell) {
    cell.addEventListener('dragover', e => { e.preventDefault(); cell.classList.add('drag-over'); });
    cell.addEventListener('dragleave', () => cell.classList.remove('drag-over'));
    cell.addEventListener('drop', e => {
        e.preventDefault();
        cell.classList.remove('drag-over');

        try {
            const data = JSON.parse(e.dataTransfer.getData('text/plain'));
            const {name, fromJour, fromType} = data;
            const toJour = cell.dataset.jour;
            const toType = cell.dataset.type;

            // Remove from old position
            if (fromJour && fromType && planningData[fromJour]) {
                planningData[fromJour][fromType] = '';
            }
            // Place in new position
            if (!planningData[toJour]) planningData[toJour] = {};
            planningData[toJour][toType] = name;

            sendUpdate();
            buildGrid();
        } catch(err) { console.error(err); }
    });
}

function buildPool() {
    RECETTES_DISPO.forEach(r => {
        const chip = el('div', 'meal-chip', r);
        chip.draggable = true;
        chip.addEventListener('dragstart', e => {
            e.dataTransfer.setData('text/plain', JSON.stringify({name: r, fromJour: '', fromType: ''}));
            chip.classList.add('dragging');
        });
        chip.addEventListener('dragend', () => chip.classList.remove('dragging'));
        pool.appendChild(chip);
    });
}

function sendUpdate() {
    // Send to Streamlit
    if (window.parent) {
        window.parent.postMessage({type: 'streamlit:setComponentValue', value: planningData}, '*');
    }
}

buildGrid();
buildPool();
</script>
</body>
</html>
"""


@composant_ui(
    "custom",
    exemple="planning_drag_drop(jours=[...], repas={...})",
    tags=("custom", "planning", "dragdrop"),
)
def planning_drag_drop(
    jours: list[str] | None = None,
    types_repas: list[str] | None = None,
    repas: dict[str, dict[str, str]] | None = None,
    recettes_disponibles: list[str] | None = None,
    height: int = 450,
) -> dict[str, dict[str, str]] | None:
    """Planning interactif avec drag & drop des repas.

    Permet de glisser-déposer des recettes sur un calendrier hebdomadaire.

    Args:
        jours: Labels des jours (défaut: Lun-Dim)
        types_repas: Types de repas (défaut: Midi, Soir)
        repas: État initial {jour: {type: "nom_recette"}}
        recettes_disponibles: Pool de recettes à glisser
        height: Hauteur du composant

    Returns:
        Dict mis à jour {jour: {type: "nom_recette"}} ou None si pas de changement
    """
    if jours is None:
        jours = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
    if types_repas is None:
        types_repas = ["🌞 Midi", "🌙 Soir"]
    if repas is None:
        repas = {}
    if recettes_disponibles is None:
        recettes_disponibles = []

    html = (
        _PLANNING_HTML.replace("%JOURS%", json.dumps(jours, ensure_ascii=False))
        .replace("%TYPES_REPAS%", json.dumps(types_repas, ensure_ascii=False))
        .replace("%REPAS%", json.dumps(repas, ensure_ascii=False))
        .replace("%RECETTES%", json.dumps(recettes_disponibles, ensure_ascii=False))
    )

    result = components.html(html, height=height, scrolling=True)

    # Le composant retourne le planning mis à jour via postMessage
    return result


# ═══════════════════════════════════════════════════════════
# 2. BARCODE SCANNER WebRTC — Scan caméra natif
# ═══════════════════════════════════════════════════════════

_BARCODE_HTML = """
<!DOCTYPE html>
<html>
<head>
<style>
* { box-sizing: border-box; margin: 0; font-family: -apple-system, sans-serif; }
body { background: transparent; }
.scanner-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 12px;
    padding: 8px;
}
video {
    width: 100%%;
    max-width: 400px;
    border-radius: 12px;
    border: 3px solid #667eea;
}
canvas { display: none; }
.controls { display: flex; gap: 8px; }
.btn {
    padding: 8px 20px;
    border: none;
    border-radius: 8px;
    color: white;
    font-weight: 600;
    cursor: pointer;
    transition: transform 0.1s;
}
.btn:hover { transform: scale(1.05); }
.btn-start { background: linear-gradient(135deg, #667eea, #764ba2); }
.btn-stop { background: #dc3545; }
.result {
    padding: 12px 24px;
    background: linear-gradient(135deg, #11998e, #38ef7d);
    color: white;
    border-radius: 8px;
    font-size: 1.2em;
    font-weight: 700;
    display: none;
}
.status {
    font-size: 0.85em;
    color: #6c757d;
}
.scan-line {
    position: absolute;
    width: 80%%;
    height: 2px;
    background: #f5576c;
    animation: scan 2s infinite;
}
@keyframes scan {
    0%%, 100%% { top: 20%%; }
    50%% { top: 80%%; }
}
</style>
</head>
<body>
<div class="scanner-container">
    <div class="status" id="status">📷 Appuyez sur Démarrer pour scanner</div>
    <div style="position: relative; width: 100%%; max-width: 400px;">
        <video id="video" autoplay playsinline></video>
        <div class="scan-line" id="scanLine" style="display:none;"></div>
    </div>
    <canvas id="canvas"></canvas>
    <div class="controls">
        <button class="btn btn-start" id="startBtn" onclick="startScanning()">📷 Démarrer</button>
        <button class="btn btn-stop" id="stopBtn" onclick="stopScanning()" style="display:none;">⏹ Arrêter</button>
    </div>
    <div class="result" id="result"></div>
</div>

<script>
const video = document.getElementById('video');
const canvas = document.getElementById('canvas');
const ctx = canvas.getContext('2d');
const result = document.getElementById('result');
const status = document.getElementById('status');
let stream = null;
let scanning = false;

async function startScanning() {
    try {
        stream = await navigator.mediaDevices.getUserMedia({
            video: { facingMode: 'environment', width: { ideal: 640 }, height: { ideal: 480 } }
        });
        video.srcObject = stream;
        scanning = true;

        document.getElementById('startBtn').style.display = 'none';
        document.getElementById('stopBtn').style.display = 'inline-block';
        document.getElementById('scanLine').style.display = 'block';
        status.textContent = '🔍 Scan en cours... Présentez un code-barres';

        // Use BarcodeDetector API if available
        if ('BarcodeDetector' in window) {
            const detector = new BarcodeDetector({
                formats: ['ean_13', 'ean_8', 'upc_a', 'upc_e', 'code_128', 'code_39', 'qr_code']
            });
            detectLoop(detector);
        } else {
            status.textContent = '⚠️ BarcodeDetector non supporté. Utilisez Chrome 83+.';
        }
    } catch (err) {
        status.textContent = '❌ Accès caméra refusé: ' + err.message;
    }
}

async function detectLoop(detector) {
    if (!scanning) return;

    try {
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        ctx.drawImage(video, 0, 0);

        const barcodes = await detector.detect(canvas);
        if (barcodes.length > 0) {
            const code = barcodes[0].rawValue;
            result.textContent = '✅ ' + code;
            result.style.display = 'block';
            status.textContent = '✅ Code détecté!';

            // Send to Streamlit
            if (window.parent) {
                window.parent.postMessage({type: 'streamlit:setComponentValue', value: code}, '*');
            }

            stopScanning();
            return;
        }
    } catch (err) { /* continue scanning */ }

    requestAnimationFrame(() => detectLoop(detector));
}

function stopScanning() {
    scanning = false;
    if (stream) {
        stream.getTracks().forEach(t => t.stop());
        stream = null;
    }
    document.getElementById('startBtn').style.display = 'inline-block';
    document.getElementById('stopBtn').style.display = 'none';
    document.getElementById('scanLine').style.display = 'none';
    if (!result.textContent) {
        status.textContent = '📷 Scan arrêté';
    }
}
</script>
</body>
</html>
"""


@composant_ui(
    "custom",
    exemple="barcode = barcode_scanner_webrtc()",
    tags=("custom", "barcode", "scanner", "webrtc"),
)
def barcode_scanner_webrtc(height: int = 400) -> str | None:
    """Scanner de codes-barres WebRTC via la caméra.

    Utilise l'API BarcodeDetector native du navigateur (Chrome 83+)
    sans bibliothèque externe. Fallback gracieux si non supporté.

    Args:
        height: Hauteur du composant

    Returns:
        Code-barres détecté (str) ou None
    """
    result = components.html(_BARCODE_HTML, height=height)
    return result


# ═══════════════════════════════════════════════════════════
# 3. PLAN JARDIN 2D Canvas — Éditeur drag & drop
# ═══════════════════════════════════════════════════════════

_JARDIN_HTML = """
<!DOCTYPE html>
<html>
<head>
<style>
* { box-sizing: border-box; margin: 0; font-family: -apple-system, sans-serif; }
body { background: transparent; }
.editor-container { padding: 8px; }
.toolbar {
    display: flex; gap: 6px; margin-bottom: 8px; flex-wrap: wrap; align-items: center;
}
.tool-btn {
    padding: 6px 12px;
    border: 2px solid #e9ecef;
    border-radius: 8px;
    background: white;
    cursor: pointer;
    font-size: 0.85em;
    transition: all 0.2s;
}
.tool-btn:hover { border-color: #667eea; }
.tool-btn.active { border-color: #667eea; background: #eef0ff; }
.tool-sep { width: 1px; height: 24px; background: #dee2e6; margin: 0 4px; }

canvas {
    border: 2px solid #dee2e6;
    border-radius: 8px;
    cursor: crosshair;
    background: #f0f4e8;
    width: 100%%;
}

.plant-palette {
    display: flex; gap: 4px; flex-wrap: wrap; margin-top: 8px;
    padding: 8px; background: #f8f9fa; border-radius: 8px;
}
.plant-chip {
    padding: 4px 10px;
    border-radius: 12px;
    font-size: 0.8em;
    cursor: pointer;
    border: 2px solid transparent;
    transition: all 0.2s;
}
.plant-chip:hover { transform: scale(1.05); }
.plant-chip.selected { border-color: #333; }

.info-bar {
    display: flex; justify-content: space-between;
    font-size: 0.8em; color: #6c757d; margin-top: 4px;
}
</style>
</head>
<body>
<div class="editor-container">
    <div class="toolbar">
        <button class="tool-btn active" id="btnZone" onclick="setTool('zone')">📐 Zone</button>
        <button class="tool-btn" id="btnPlant" onclick="setTool('plant')">🌱 Planter</button>
        <button class="tool-btn" id="btnMove" onclick="setTool('move')">✋ Déplacer</button>
        <div class="tool-sep"></div>
        <button class="tool-btn" id="btnDelete" onclick="setTool('delete')">🗑️ Supprimer</button>
        <button class="tool-btn" onclick="clearAll()">🆕 Réinitialiser</button>
        <button class="tool-btn" onclick="exportPlan()">💾 Sauvegarder</button>
    </div>

    <canvas id="canvas" width="800" height="500"></canvas>

    <div class="plant-palette" id="palette"></div>
    <div class="info-bar">
        <span id="infoLeft">Outil: Zone</span>
        <span id="infoRight">Cliquez pour dessiner</span>
    </div>
</div>

<script>
const ZONES_INIT = %ZONES%;
const PLANTES_INIT = %PLANTES%;
const PLANTES_CATALOGUE = %CATALOGUE%;

const canvas = document.getElementById('canvas');
const ctx = canvas.getContext('2d');
const palette = document.getElementById('palette');

let currentTool = 'zone';
let selectedPlant = PLANTES_CATALOGUE[0] || {nom: 'Tomate', emoji: '🍅', couleur: '#e74c3c'};
let zones = JSON.parse(JSON.stringify(ZONES_INIT));
let plantes = JSON.parse(JSON.stringify(PLANTES_INIT));
let isDragging = false;
let dragStart = {x: 0, y: 0};
let dragItem = null;
let drawingZone = null;

// Couleurs prédéfinies pour les zones
const ZONE_COLORS = ['#8fbc8f55', '#deb88755', '#87ceeb55', '#f0e68c55', '#dda0dd55', '#98fb9855'];
let zoneColorIdx = 0;

function setTool(tool) {
    currentTool = tool;
    document.querySelectorAll('.tool-btn').forEach(b => b.classList.remove('active'));
    document.getElementById('btn' + tool.charAt(0).toUpperCase() + tool.slice(1))?.classList.add('active');
    document.getElementById('infoLeft').textContent = 'Outil: ' + tool;
    canvas.style.cursor = tool === 'move' ? 'grab' : tool === 'delete' ? 'not-allowed' : 'crosshair';
}

function buildPalette() {
    PLANTES_CATALOGUE.forEach((p, i) => {
        const chip = document.createElement('div');
        chip.className = 'plant-chip' + (i === 0 ? ' selected' : '');
        chip.style.background = p.couleur + '33';
        chip.textContent = p.emoji + ' ' + p.nom;
        chip.onclick = () => {
            selectedPlant = p;
            document.querySelectorAll('.plant-chip').forEach(c => c.classList.remove('selected'));
            chip.classList.add('selected');
        };
        palette.appendChild(chip);
    });
}

function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Grille
    ctx.strokeStyle = '#ccc';
    ctx.lineWidth = 0.5;
    for (let x = 0; x < canvas.width; x += 50) {
        ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, canvas.height); ctx.stroke();
    }
    for (let y = 0; y < canvas.height; y += 50) {
        ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(canvas.width, y); ctx.stroke();
    }

    // Zones
    zones.forEach(z => {
        ctx.fillStyle = z.couleur || ZONE_COLORS[0];
        ctx.fillRect(z.x, z.y, z.w, z.h);
        ctx.strokeStyle = '#555';
        ctx.lineWidth = 2;
        ctx.strokeRect(z.x, z.y, z.w, z.h);
        // Label
        ctx.fillStyle = '#333';
        ctx.font = 'bold 12px sans-serif';
        ctx.fillText(z.nom, z.x + 5, z.y + 15);
    });

    // Zone en cours de dessin
    if (drawingZone) {
        ctx.fillStyle = ZONE_COLORS[zoneColorIdx] || '#8fbc8f55';
        ctx.fillRect(drawingZone.x, drawingZone.y, drawingZone.w, drawingZone.h);
        ctx.strokeStyle = '#667eea';
        ctx.lineWidth = 2;
        ctx.setLineDash([5, 5]);
        ctx.strokeRect(drawingZone.x, drawingZone.y, drawingZone.w, drawingZone.h);
        ctx.setLineDash([]);
    }

    // Plantes
    plantes.forEach(p => {
        ctx.font = '24px serif';
        ctx.fillText(p.emoji || '🌱', p.x - 12, p.y + 8);
        ctx.font = '10px sans-serif';
        ctx.fillStyle = '#333';
        ctx.fillText(p.nom, p.x - 15, p.y + 22);
    });
}

canvas.addEventListener('mousedown', e => {
    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;
    const x = (e.clientX - rect.left) * scaleX;
    const y = (e.clientY - rect.top) * scaleY;

    if (currentTool === 'zone') {
        isDragging = true;
        dragStart = {x, y};
        drawingZone = {x, y, w: 0, h: 0};
    } else if (currentTool === 'plant') {
        plantes.push({nom: selectedPlant.nom, emoji: selectedPlant.emoji, x, y, couleur: selectedPlant.couleur});
        sendUpdate();
        draw();
    } else if (currentTool === 'delete') {
        // Trouver et supprimer la plante ou zone sous le curseur
        const pIdx = plantes.findIndex(p => Math.hypot(p.x - x, p.y - y) < 20);
        if (pIdx >= 0) { plantes.splice(pIdx, 1); sendUpdate(); draw(); return; }
        const zIdx = zones.findIndex(z => x >= z.x && x <= z.x + z.w && y >= z.y && y <= z.y + z.h);
        if (zIdx >= 0) { zones.splice(zIdx, 1); sendUpdate(); draw(); }
    } else if (currentTool === 'move') {
        const pIdx = plantes.findIndex(p => Math.hypot(p.x - x, p.y - y) < 20);
        if (pIdx >= 0) { isDragging = true; dragItem = {type: 'plant', idx: pIdx, offsetX: x - plantes[pIdx].x, offsetY: y - plantes[pIdx].y}; }
    }
});

canvas.addEventListener('mousemove', e => {
    if (!isDragging) return;
    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;
    const x = (e.clientX - rect.left) * scaleX;
    const y = (e.clientY - rect.top) * scaleY;

    if (currentTool === 'zone' && drawingZone) {
        drawingZone.w = x - dragStart.x;
        drawingZone.h = y - dragStart.y;
        draw();
    } else if (currentTool === 'move' && dragItem) {
        if (dragItem.type === 'plant') {
            plantes[dragItem.idx].x = x - dragItem.offsetX;
            plantes[dragItem.idx].y = y - dragItem.offsetY;
            draw();
        }
    }
});

canvas.addEventListener('mouseup', () => {
    if (currentTool === 'zone' && drawingZone && (Math.abs(drawingZone.w) > 20 || Math.abs(drawingZone.h) > 20)) {
        // Normaliser (support dessin inversé)
        const z = {
            nom: prompt('Nom de la zone:', 'Zone ' + (zones.length + 1)) || 'Zone ' + (zones.length + 1),
            x: Math.min(drawingZone.x, drawingZone.x + drawingZone.w),
            y: Math.min(drawingZone.y, drawingZone.y + drawingZone.h),
            w: Math.abs(drawingZone.w),
            h: Math.abs(drawingZone.h),
            couleur: ZONE_COLORS[zoneColorIdx %% ZONE_COLORS.length],
        };
        zoneColorIdx++;
        zones.push(z);
        sendUpdate();
    }
    isDragging = false;
    dragItem = null;
    drawingZone = null;
    draw();

    if (currentTool === 'move') sendUpdate();
});

function clearAll() {
    if (confirm('Réinitialiser le plan ?')) {
        zones = []; plantes = [];
        sendUpdate(); draw();
    }
}

function exportPlan() {
    sendUpdate();
    document.getElementById('infoRight').textContent = '💾 Plan sauvegardé!';
    setTimeout(() => { document.getElementById('infoRight').textContent = ''; }, 2000);
}

function sendUpdate() {
    const data = {zones, plantes};
    if (window.parent) {
        window.parent.postMessage({type: 'streamlit:setComponentValue', value: data}, '*');
    }
}

buildPalette();
draw();
</script>
</body>
</html>
"""


@composant_ui(
    "custom",
    exemple="plan_jardin_2d(zones=[...], plantes=[...])",
    tags=("custom", "jardin", "canvas", "2d"),
)
def plan_jardin_2d(
    zones: list[dict[str, Any]] | None = None,
    plantes: list[dict[str, Any]] | None = None,
    catalogue_plantes: list[dict[str, Any]] | None = None,
    height: int = 600,
) -> dict[str, Any] | None:
    """Éditeur de plan de jardin 2D avec Canvas.

    Permet de dessiner des zones et placer des plantes par drag & drop.

    Args:
        zones: Zones existantes [{nom, x, y, w, h, couleur}]
        plantes: Plantes existantes [{nom, emoji, x, y}]
        catalogue_plantes: Catalogue de plantes disponibles [{nom, emoji, couleur}]
        height: Hauteur du composant

    Returns:
        Dict {zones: [...], plantes: [...]} mis à jour ou None
    """
    if zones is None:
        zones = []
    if plantes is None:
        plantes = []
    if catalogue_plantes is None:
        catalogue_plantes = [
            {"nom": "Tomate", "emoji": "🍅", "couleur": "#e74c3c"},
            {"nom": "Carotte", "emoji": "🥕", "couleur": "#e67e22"},
            {"nom": "Salade", "emoji": "🥬", "couleur": "#27ae60"},
            {"nom": "Courgette", "emoji": "🥒", "couleur": "#2ecc71"},
            {"nom": "Fraise", "emoji": "🍓", "couleur": "#e74c3c"},
            {"nom": "Basilic", "emoji": "🌿", "couleur": "#16a085"},
            {"nom": "Menthe", "emoji": "🍃", "couleur": "#1abc9c"},
            {"nom": "Tournesol", "emoji": "🌻", "couleur": "#f1c40f"},
            {"nom": "Rose", "emoji": "🌹", "couleur": "#c0392b"},
            {"nom": "Lavande", "emoji": "💜", "couleur": "#8e44ad"},
        ]

    html = (
        _JARDIN_HTML.replace("%ZONES%", json.dumps(zones, ensure_ascii=False))
        .replace("%PLANTES%", json.dumps(plantes, ensure_ascii=False))
        .replace("%CATALOGUE%", json.dumps(catalogue_plantes, ensure_ascii=False))
    )

    result = components.html(html, height=height, scrolling=False)
    return result


__all__ = [
    "planning_drag_drop",
    "barcode_scanner_webrtc",
    "plan_jardin_2d",
]
