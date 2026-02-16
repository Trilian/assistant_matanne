"""Styles CSS pour le module Jardin - Version gamifiée."""

CSS = """
<style>
/* Variables couleurs jardin */
:root {
    --jardin-primary: #27ae60;
    --jardin-secondary: #2ecc71;
    --jardin-accent: #f39c12;
    --jardin-danger: #e74c3c;
    --jardin-bg: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
    --jardin-gold: #FFD700;
    --jardin-silver: #C0C0C0;
    --jardin-bronze: #CD7F32;
}

/* Animations */
@keyframes grow {
    0% { transform: scale(0.8); opacity: 0; }
    100% { transform: scale(1); opacity: 1; }
}

@keyframes pulse-leaf {
    0% { transform: rotate(-5deg) scale(1); }
    50% { transform: rotate(5deg) scale(1.1); }
    100% { transform: rotate(-5deg) scale(1); }
}

@keyframes rainbow {
    0% { filter: hue-rotate(0deg); }
    100% { filter: hue-rotate(360deg); }
}

.animate-grow { animation: grow 0.5s ease-out; }
.pulse-leaf { animation: pulse-leaf 2s ease-in-out infinite; }

/* Score gamifié jardin */
.score-jardin-container {
    background: linear-gradient(135deg, #27ae60 0%, #2ecc71 100%);
    border-radius: 20px;
    padding: 2rem;
    text-align: center;
    box-shadow: 0 10px 40px rgba(39, 174, 96, 0.3);
    position: relative;
    overflow: hidden;
}

.score-jardin-container::before {
    content: "🌿";
    position: absolute;
    top: -20px;
    left: -20px;
    font-size: 100px;
    opacity: 0.1;
    transform: rotate(-15deg);
}

.score-jardin-ring {
    position: relative;
    display: inline-block;
}

.score-jardin-value {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    font-size: 2.5rem;
    font-weight: 800;
    color: white;
    text-shadow: 0 2px 10px rgba(0,0,0,0.2);
}

.score-jardin-label {
    color: rgba(255,255,255,0.9);
    font-size: 0.9rem;
    margin-top: 1rem;
    text-transform: uppercase;
    letter-spacing: 2px;
}

/* Jauge autonomie gamifiée */
.autonomie-gamifie {
    background: linear-gradient(135deg, #2d3748 0%, #1a202c 100%);
    border-radius: 16px;
    padding: 1.5rem;
    text-align: center;
    position: relative;
    overflow: hidden;
}

.autonomie-gamifie .percent {
    font-size: 3.5rem;
    font-weight: 900;
    background: linear-gradient(135deg, #27ae60 0%, #f39c12 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.autonomie-gamifie .label {
    color: #a0aec0;
    font-size: 0.85rem;
    margin-top: 0.5rem;
}

.autonomie-progress {
    height: 12px;
    background: #4a5568;
    border-radius: 6px;
    margin-top: 1rem;
    overflow: hidden;
}

.autonomie-progress-fill {
    height: 100%;
    border-radius: 6px;
    background: linear-gradient(90deg, #27ae60 0%, #2ecc71 50%, #f39c12 100%);
    transition: width 1s ease-out;
}

/* Badges jardin */
.badges-jardin-container {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1rem;
    padding: 1rem 0;
}

.badge-jardin {
    background: linear-gradient(145deg, #2d3748 0%, #1a202c 100%);
    border-radius: 12px;
    padding: 1rem;
    text-align: center;
    transition: all 0.3s;
    border: 2px solid transparent;
    cursor: default;
}

.badge-jardin:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 25px rgba(39, 174, 96, 0.3);
}

.badge-jardin.unlocked {
    border-color: var(--jardin-primary);
    background: linear-gradient(145deg, #27ae60 0%, #2ecc71 100%);
}

.badge-jardin.locked {
    opacity: 0.5;
    filter: grayscale(80%);
}

.badge-jardin .icon {
    font-size: 2rem;
    display: block;
    margin-bottom: 0.5rem;
}

.badge-jardin .name {
    font-weight: 600;
    font-size: 0.8rem;
    color: white;
}

.badge-jardin .status {
    font-size: 0.7rem;
    color: rgba(255,255,255,0.7);
    margin-top: 0.25rem;
}

/* Prévisions récoltes */
.prevision-recolte {
    background: linear-gradient(135deg, #f0fff4 0%, #c6f6d5 100%);
    border-radius: 12px;
    padding: 1rem 1.25rem;
    margin-bottom: 0.75rem;
    display: flex;
    align-items: center;
    gap: 1rem;
    border-left: 4px solid var(--jardin-primary);
    animation: grow 0.3s ease-out;
}

.prevision-recolte .emoji { font-size: 2rem; }

.prevision-recolte .details { flex: 1; }

.prevision-recolte .nom {
    font-weight: 600;
    color: #2d3748;
}

.prevision-recolte .quantite {
    font-size: 1.25rem;
    font-weight: 700;
    color: var(--jardin-primary);
}

.prevision-recolte .periode {
    font-size: 0.8rem;
    color: #718096;
    background: white;
    padding: 0.25rem 0.5rem;
    border-radius: 12px;
}

/* Planning jardin visuel */
.planning-jardin-item {
    background: white;
    border-radius: 10px;
    padding: 0.75rem 1rem;
    margin-bottom: 0.5rem;
    display: flex;
    align-items: center;
    gap: 1rem;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}

.planning-jardin-item.recolte { border-left: 3px solid #27ae60; }
.planning-jardin-item.plantation { border-left: 3px solid #3498db; }
.planning-jardin-item.semis { border-left: 3px solid #f39c12; }

.planning-jardin-item .mois-badge {
    background: var(--jardin-primary);
    color: white;
    padding: 0.25rem 0.75rem;
    border-radius: 12px;
    font-size: 0.75rem;
    font-weight: 600;
}

/* Header jardin */
.jardin-header {
    background: linear-gradient(135deg, #27ae60 0%, #2ecc71 100%);
    color: white;
    padding: 2rem;
    border-radius: 16px;
    margin-bottom: 1.5rem;
    box-shadow: 0 4px 15px rgba(39, 174, 96, 0.3);
}

.jardin-header h1 {
    margin: 0 0 0.5rem 0;
    font-size: 2rem;
    display: flex;
    align-items: center;
    gap: 0.75rem;
}

.jardin-header .meteo-badge {
    background: rgba(255,255,255,0.2);
    padding: 0.5rem 1rem;
    border-radius: 20px;
    font-size: 0.9rem;
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
}

.jardin-header .streak-badge {
    background: linear-gradient(135deg, #f39c12 0%, #e67e22 100%);
    padding: 0.25rem 0.75rem;
    border-radius: 12px;
    font-size: 0.85rem;
    margin-left: 0.5rem;
}

/* Card générique jardin */
.jardin-card {
    background: white;
    border-radius: 12px;
    padding: 1.25rem;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    border-left: 4px solid var(--jardin-primary);
    margin-bottom: 1rem;
    transition: transform 0.2s, box-shadow 0.2s;
}

.jardin-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.12);
}

.jardin-card.urgent {
    border-left-color: var(--jardin-danger);
    background: linear-gradient(to right, #fff5f5, white);
}

.jardin-card.highlight {
    border-left-color: var(--jardin-accent);
    background: linear-gradient(to right, #fffbf0, white);
}

/* Tâche jardin */
.tache-jardin {
    display: flex;
    align-items: flex-start;
    gap: 1rem;
    padding: 1rem;
    background: #f8fdf9;
    border-radius: 10px;
    margin-bottom: 0.75rem;
    border: 1px solid #e8f5e9;
}

.tache-jardin .icon {
    font-size: 1.5rem;
    background: white;
    width: 45px;
    height: 45px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
}

.tache-jardin .content { flex: 1; }
.tache-jardin .title { font-weight: 600; color: #2d3748; margin-bottom: 0.25rem; }
.tache-jardin .meta { font-size: 0.85rem; color: #718096; }
.tache-jardin .raison { font-size: 0.8rem; color: #27ae60; font-style: italic; margin-top: 0.25rem; }

/* Plante card */
.plante-card {
    background: white;
    border-radius: 12px;
    padding: 1rem;
    text-align: center;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    border: 2px solid transparent;
    transition: all 0.2s;
    cursor: pointer;
}

.plante-card:hover { border-color: var(--jardin-primary); transform: scale(1.02); }
.plante-card.selected { border-color: var(--jardin-primary); background: #f0fff4; }
.plante-card .emoji { font-size: 2.5rem; margin-bottom: 0.5rem; }
.plante-card .nom { font-weight: 600; color: #2d3748; }
.plante-card .variete { font-size: 0.8rem; color: #718096; }

/* Stats autonomie */
.autonomie-gauge {
    background: linear-gradient(to right, #e8f5e9, #c8e6c9);
    border-radius: 12px;
    padding: 1.5rem;
    text-align: center;
}

.autonomie-gauge .value { font-size: 3rem; font-weight: 700; color: var(--jardin-primary); }
.autonomie-gauge .label { color: #4a5568; font-size: 0.9rem; }

/* Calendrier jardin */
.calendrier-mois { display: flex; gap: 0.25rem; margin-top: 0.5rem; }
.calendrier-mois .mois {
    width: 20px; height: 20px; border-radius: 4px;
    font-size: 0.6rem; display: flex; align-items: center; justify-content: center;
    color: white; font-weight: 600;
}

.mois.semis { background: #f39c12; }
.mois.plantation { background: #3498db; }
.mois.recolte { background: #27ae60; }
.mois.inactif { background: #e0e0e0; color: #999; }

/* Plan jardin */
.plan-jardin {
    background: linear-gradient(145deg, #8d6e63 0%, #6d4c41 100%);
    border-radius: 12px;
    padding: 1.5rem;
    min-height: 400px;
    position: relative;
}

.zone-culture {
    background: #4a2c2a;
    border: 2px dashed #8d6e63;
    border-radius: 8px;
    padding: 1rem;
    margin: 0.5rem;
    min-height: 80px;
}

.zone-culture.active {
    background: linear-gradient(135deg, #2d5016 0%, #4a752c 100%);
    border-style: solid;
    border-color: #6b8e23;
}

/* Récolte */
.recolte-item {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 0.75rem 1rem;
    background: #f0fff4;
    border-radius: 8px;
    margin-bottom: 0.5rem;
}

.recolte-item .quantite { font-size: 1.25rem; font-weight: 700; color: var(--jardin-primary); }

/* Compagnons */
.compagnons-list { display: flex; flex-wrap: wrap; gap: 0.5rem; margin-top: 0.5rem; }
.compagnon-badge {
    padding: 0.25rem 0.5rem;
    border-radius: 12px;
    font-size: 0.75rem;
    display: flex;
    align-items: center;
    gap: 0.25rem;
}

.compagnon-badge.positif { background: #d4edda; color: #155724; }
.compagnon-badge.negatif { background: #f8d7da; color: #721c24; }

/* Animations */
@keyframes pulse-green {
    0% { box-shadow: 0 0 0 0 rgba(39, 174, 96, 0.4); }
    70% { box-shadow: 0 0 0 10px rgba(39, 174, 96, 0); }
    100% { box-shadow: 0 0 0 0 rgba(39, 174, 96, 0); }
}

.pulse-action { animation: pulse-green 2s infinite; }
</style>
"""
