"""Constantes pour le module Diagnostics."""

TYPES_DIAGNOSTIC_LABELS = {
    "dpe": "🏠 DPE (Performance Énergétique)",
    "amiante": "⚠️ Amiante",
    "plomb": "🔴 Plomb (CREP)",
    "termites": "🐛 Termites",
    "electricite": "⚡ Électricité",
    "gaz": "🔥 Gaz",
    "erp": "📋 État des Risques (ERP)",
    "assainissement": "💧 Assainissement",
    "surface_carrez": "📐 Surface Carrez",
    "audit_energetique": "🌿 Audit Énergétique",
    "autre": "📄 Autre",
}

VALIDITE_DIAGNOSTICS = {
    "dpe": 10,
    "amiante": None,  # Illimité si négatif
    "plomb": None,  # Illimité si négatif
    "termites": 0.5,  # 6 mois
    "electricite": 6,
    "gaz": 6,
    "erp": 0.5,
    "assainissement": 3,
    "surface_carrez": None,
    "audit_energetique": 5,
}

SCORES_DPE = ["A", "B", "C", "D", "E", "F", "G"]

SOURCES_ESTIMATION = {
    "dvf": "📊 DVF (données publiques)",
    "agent": "🏢 Agent immobilier",
    "notaire": "📜 Notaire",
    "ia": "🤖 IA / Estimation en ligne",
    "banque": "🏦 Banque",
    "manuel": "✍️ Estimation manuelle",
}
