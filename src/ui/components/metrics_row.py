"""
Composant de ligne de métriques réutilisable.

Élimine la duplication des affichages de métriques en colonnes.
Utilise ``StyleSheet`` pour la déduplication CSS et ``echapper_html`` pour la sécurité.

Usage:
    from src.ui.components.metrics_row import MetricConfig, afficher_metriques_row

    afficher_metriques_row([
        MetricConfig("Total", 42, delta=5),
        MetricConfig("Critique", 3, delta=-1, delta_color="inverse", icon="❌"),
    ])
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

import streamlit as st

from src.ui.engine import StyleSheet
from src.ui.tokens import Couleur
from src.ui.tokens_semantic import Sem
from src.ui.utils import echapper_html


@dataclass
class MetricConfig:
    """Configuration d'une métrique.

    Attributes:
        label: Label de la métrique
        value: Valeur à afficher
        delta: Variation optionnelle
        delta_color: "normal", "inverse", "off"
        help_text: Texte d'aide au survol
        icon: Emoji optionnel
        format_fn: Fonction de formatage optionnelle
    """

    label: str
    value: Any
    delta: Any = None
    delta_color: str = "normal"  # "normal", "inverse", "off"
    help_text: str = ""
    icon: str = ""
    format_fn: Callable | None = None

    def get_formatted_value(self) -> Any:
        """Retourne la valeur formatée."""
        if self.format_fn:
            return self.format_fn(self.value)
        return self.value

    def get_label(self) -> str:
        """Retourne le label avec icône."""
        if self.icon:
            return f"{self.icon} {self.label}"
        return self.label


def afficher_metriques_row(
    metriques: list[MetricConfig | dict],
    columns: int | None = None,
    border: bool = False,
) -> None:
    """Ligne de métriques génériques.

    Args:
        metriques: Liste de MetricConfig ou dicts avec keys label, value, delta, etc.
        columns: Nombre de colonnes (auto si None)
        border: Si True, ajoute une bordure autour des métriques

    Usage:
        afficher_metriques_row([
            MetricConfig("📦 Total", 42, delta=5),
            MetricConfig("❌ Critique", 3, delta=-1, delta_color="inverse"),
            {"label": "OK", "value": 39, "icon": "✅"},
        ])
    """
    if not metriques:
        return

    num_cols = columns or len(metriques)

    container = st.container(border=border) if border else st.container()

    with container:
        cols = st.columns(num_cols)

        for i, m in enumerate(metriques):
            with cols[i % num_cols]:
                # Convertir dict en MetricConfig si nécessaire
                if isinstance(m, dict):
                    m = MetricConfig(**m)

                st.metric(
                    label=m.get_label(),
                    value=m.get_formatted_value(),
                    delta=m.delta,
                    delta_color=m.delta_color,
                    help=m.help_text or None,
                )


def afficher_stats_cards(
    stats: list[dict],
    columns: int = 4,
) -> None:
    """Affiche des cartes de statistiques stylisées.

    Utilise ``StyleSheet.create_class`` pour la déduplication CSS
    et ``Text`` pour l'échappement automatique.

    Args:
        stats: Liste de dicts avec keys: title, value, subtitle, color, icon
        columns: Nombre de colonnes

    Usage:
        afficher_stats_cards([
            {"title": "Articles", "value": 42, "subtitle": "+5 ce mois", "color": "#4CAF50"},
            {"title": "Alertes", "value": 3, "subtitle": "À traiter", "color": "#f44336"},
        ])
    """
    if not stats:
        return

    cols = st.columns(columns)

    for i, stat in enumerate(stats):
        with cols[i % columns]:
            color = stat.get("color", Couleur.SUCCESS)
            icon = stat.get("icon", "")
            title = f"{icon} {stat.get('title', '')}" if icon else stat.get("title", "")

            # Classe CSS dédupliquée par couleur (seulement ~6 variantes en pratique)
            card_cls = StyleSheet.create_class(
                {
                    "background": f"linear-gradient(135deg, {color}22, {color}11)",
                    "border-left": f"4px solid {color}",
                    "padding": "1rem",
                    "border-radius": "8px",
                    "margin-bottom": "0.5rem",
                }
            )

            safe_title = echapper_html(str(title))
            safe_value = echapper_html(str(stat.get("value", "")))
            safe_subtitle = echapper_html(str(stat.get("subtitle", "")))

            title_html = f'<div style="font-size: 0.875rem; color: {Sem.ON_SURFACE_SECONDARY};">{safe_title}</div>'
            value_html = f'<div style="font-size: 1.25rem; font-weight: bold; color: {color};">{safe_value}</div>'
            subtitle_html = f'<div style="font-size: 0.75rem; color: {Sem.ON_SURFACE_MUTED};">{safe_subtitle}</div>'

            StyleSheet.inject()
            st.markdown(
                f'<div class="{card_cls}">{title_html}{value_html}{subtitle_html}</div>',
                unsafe_allow_html=True,
            )


def afficher_kpi_banner(
    kpis: list[dict],
    background_color: str = "#f8f9fa",
) -> None:
    """Bannière de KPIs horizontale.

    Utilise ``StyleSheet`` pour les classes CSS et ``echapper_html`` pour la sécurité.

    Args:
        kpis: Liste de dicts avec keys: label, value, trend (up/down/neutral)
        background_color: Couleur de fond

    Usage:
        afficher_kpi_banner([
            {"label": "Ventes", "value": "12.5K€", "trend": "up"},
            {"label": "Commandes", "value": "234", "trend": "down"},
        ])
    """
    if not kpis:
        return

    trend_icons = {"up": "📈", "down": "📉", "neutral": "➡️"}
    trend_colors = {
        "up": Couleur.SUCCESS,
        "down": Couleur.DANGER,
        "neutral": Couleur.TEXT_SECONDARY,
    }

    # Classe dédupliquée pour chaque item KPI
    item_cls = StyleSheet.create_class(
        {
            "display": "inline-block",
            "padding": "0.5rem 1.5rem",
            "text-align": "center",
            "border-right": f"1px solid {Sem.BORDER_SUBTLE}",
        }
    )

    kpi_html = ""
    for kpi in kpis:
        trend = kpi.get("trend", "neutral")
        icon = trend_icons.get(trend, "")
        color = trend_colors.get(trend, Couleur.TEXT_SECONDARY)

        safe_label = echapper_html(str(kpi.get("label", "")))
        safe_value = echapper_html(f"{kpi.get('value', '')} {icon}")

        label_html = f'<div style="font-size: 0.75rem; color: {Sem.ON_SURFACE_SECONDARY};">{safe_label}</div>'
        value_html = f'<div style="font-size: 1.125rem; font-weight: bold; color: {color};">{safe_value}</div>'

        kpi_html += f'<div class="{item_cls}">{label_html}{value_html}</div>'

    # Conteneur horizontal
    banner_cls = StyleSheet.create_class(
        {
            "background": str(Sem.SURFACE_ALT),
            "border-radius": "8px",
            "padding": "0.5rem",
            "overflow-x": "auto",
            "white-space": "nowrap",
        }
    )

    StyleSheet.inject()
    st.markdown(
        f'<div class="{banner_cls}">{kpi_html}</div>',
        unsafe_allow_html=True,
    )


def afficher_progress_metrics(
    metrics: list[dict],
    columns: int = 2,
) -> None:
    """Métriques avec barre de progression.

    Args:
        metrics: Liste de dicts avec keys: label, current, target, unit
        columns: Nombre de colonnes

    Usage:
        afficher_progress_metrics([
            {"label": "Budget", "current": 750, "target": 1000, "unit": "€"},
            {"label": "Objectif", "current": 8, "target": 10, "unit": " tâches"},
        ])
    """
    if not metrics:
        return

    cols = st.columns(columns)

    for i, m in enumerate(metrics):
        with cols[i % columns]:
            current = m.get("current", 0)
            target = m.get("target", 100)
            label = m.get("label", "")
            unit = m.get("unit", "")

            progress = min(current / target, 1.0) if target > 0 else 0
            percent = int(progress * 100)

            color = (
                Couleur.SUCCESS
                if percent >= 80
                else Couleur.WARNING
                if percent >= 50
                else Couleur.DANGER
            )

            st.markdown(f"**{label}**")
            st.progress(progress)
            st.caption(f"{current}{unit} / {target}{unit} ({percent}%)")


__all__ = [
    "MetricConfig",
    "afficher_metriques_row",
    "afficher_stats_cards",
    "afficher_kpi_banner",
    "afficher_progress_metrics",
]
