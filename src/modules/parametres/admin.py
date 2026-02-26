"""
Paramètres - Tableau de bord Admin.

Santé système, journal d'activité, performances, erreurs récentes.
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta

import streamlit as st

from src.ui.fragments import ui_fragment
from src.ui.keys import KeyNamespace

logger = logging.getLogger(__name__)

_keys = KeyNamespace("param_admin")


def _badge_sante(statut_name: str) -> str:
    """Retourne un badge emoji selon le statut de santé."""
    badges = {
        "SAIN": "🟢",
        "DEGRADE": "🟡",
        "CRITIQUE": "🔴",
        "INCONNU": "⚪",
    }
    return badges.get(statut_name, "⚪")


@ui_fragment
def afficher_admin_dashboard():
    """Tableau de bord administrateur."""

    st.markdown("### 📊 Tableau de bord Admin")
    st.caption("Santé système, logs, performances")

    # ── Section 1: Santé système ──
    st.markdown("#### 🏥 Santé du système")

    try:
        from src.core.monitoring.health import verifier_sante_globale

        sante = verifier_sante_globale(inclure_db=True)
        sante_dict = sante.vers_dict()

        # Indicateur global
        statut_global = "🟢 Sain" if sante.sain else "🔴 Dégradé"
        st.metric("État global", statut_global)

        # Composants
        cols = st.columns(min(len(sante_dict.get("composants", {})), 4) or 1)
        for i, (nom, comp) in enumerate(sante_dict.get("composants", {}).items()):
            with cols[i % len(cols)]:
                badge = _badge_sante(comp["statut"])
                st.metric(
                    f"{badge} {nom.capitalize()}",
                    comp["statut"],
                    help=comp.get("message", ""),
                )
                if comp.get("duree_ms"):
                    st.caption(f"⏱️ {comp['duree_ms']:.1f} ms")
    except Exception as e:
        logger.error("Erreur health check: %s", e)
        st.warning(f"Impossible de vérifier la santé: {e}")

    # ── Section 2: Métriques de performance ──
    st.markdown("---")
    st.markdown("#### 📈 Métriques de performance")

    try:
        from src.core.monitoring.collector import obtenir_snapshot

        snapshot = obtenir_snapshot()
        metriques = snapshot.get("metriques", {})

        if metriques:
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                ia_appels = metriques.get("ia.appel", {})
                st.metric(
                    "🤖 Appels IA",
                    f"{ia_appels.get('total', 0):.0f}",
                )

            with col2:
                cache_hits = metriques.get("cache.hit", {})
                cache_miss = metriques.get("cache.miss", {})
                total_cache = cache_hits.get("total", 0) + cache_miss.get("total", 0)
                hit_rate = (
                    (cache_hits.get("total", 0) / total_cache * 100) if total_cache > 0 else 0
                )
                st.metric("💾 Cache hit rate", f"{hit_rate:.1f}%")

            with col3:
                db_requetes = metriques.get("db.requete", {})
                st.metric("🗄️ Requêtes DB", f"{db_requetes.get('total', 0):.0f}")

            with col4:
                erreurs = metriques.get("erreur", {})
                st.metric("❌ Erreurs", f"{erreurs.get('total', 0):.0f}")

            # Graphiques Plotly si données disponibles
            _afficher_graphiques_perf(metriques)
        else:
            st.info("Pas encore de métriques collectées.")

        # Uptime
        uptime = snapshot.get("uptime_seconds", 0)
        heures = int(uptime // 3600)
        minutes = int((uptime % 3600) // 60)
        st.caption(f"⏰ Uptime: {heures}h {minutes}min")

    except Exception as e:
        logger.error("Erreur métriques: %s", e)
        st.warning(f"Impossible de charger les métriques: {e}")

    # ── Section 3: Journal d'activité ──
    st.markdown("---")
    st.markdown("#### 📜 Journal d'activité")

    _afficher_journal_activite()

    # ── Section 4: Reruns Streamlit ──
    st.markdown("---")
    st.markdown("#### 🔄 Profil des reruns")

    try:
        from src.core.monitoring.rerun_profiler import obtenir_stats_rerun

        stats = obtenir_stats_rerun()
        if stats:
            col_r1, col_r2, col_r3 = st.columns(3)
            with col_r1:
                st.metric("Total reruns", stats.get("total_reruns", 0))
            with col_r2:
                st.metric("Durée moyenne", f"{stats.get('duree_moyenne_ms', 0):.0f} ms")
            with col_r3:
                st.metric("Module le plus lent", stats.get("module_le_plus_lent", "—"))
        else:
            st.info("Pas encore de données de rerun.")
    except Exception as e:
        logger.debug("Stats rerun non disponibles: %s", e)
        st.info("Profiler de reruns non disponible.")


def _afficher_graphiques_perf(metriques: dict) -> None:
    """Affiche les graphiques Plotly de performance."""
    try:
        import plotly.graph_objects as go

        # Graphique des durées par module
        durees = {}
        for nom, data in metriques.items():
            if "duree" in nom and data.get("statistiques"):
                stats = data["statistiques"]
                durees[nom.replace(".duree_ms", "")] = stats.get("moyenne", 0)

        if durees:
            fig = go.Figure(
                data=[
                    go.Bar(
                        x=list(durees.keys()),
                        y=list(durees.values()),
                        marker_color="#4CAF50",
                    )
                ]
            )
            fig.update_layout(
                title="Durée moyenne par module (ms)",
                xaxis_title="Module",
                yaxis_title="ms",
                height=300,
                margin={"t": 40, "b": 40, "l": 40, "r": 20},
            )
            st.plotly_chart(fig, use_container_width=True)
    except ImportError:
        pass  # Plotly optionnel
    except Exception as e:
        logger.debug("Erreur graphique perf: %s", e)


def _afficher_journal_activite() -> None:
    """Affiche le journal d'activité filtrable."""
    from src.core.decorators import avec_session_db
    from src.core.models.systeme import HistoriqueAction

    @avec_session_db
    def _charger_actions(
        limite: int = 50,
        filtre_type: str | None = None,
        filtre_user: str | None = None,
        *,
        db=None,
    ) -> list[dict]:
        query = db.query(HistoriqueAction).order_by(HistoriqueAction.cree_le.desc())

        if filtre_type and filtre_type != "Tous":
            query = query.filter(HistoriqueAction.action_type == filtre_type)
        if filtre_user and filtre_user != "Tous":
            query = query.filter(HistoriqueAction.user_name == filtre_user)

        actions = query.limit(limite).all()
        return [
            {
                "Date": a.cree_le.strftime("%Y-%m-%d %H:%M") if a.cree_le else "—",
                "Utilisateur": a.user_name,
                "Action": a.action_type,
                "Entité": f"{a.entity_type} #{a.entity_id}" if a.entity_id else a.entity_type,
                "Description": a.description[:100] if a.description else "—",
            }
            for a in actions
        ]

    # Filtres
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        filtre_type = st.selectbox(
            "Type d'action",
            [
                "Tous",
                "recette.created",
                "recette.updated",
                "recette.deleted",
                "inventaire.updated",
                "planning.created",
                "erreur",
            ],
            key=_keys("filtre_type"),
        )
    with col_f2:
        filtre_user = st.selectbox(
            "Utilisateur",
            ["Tous", "Anne", "Mathieu"],
            key=_keys("filtre_user"),
        )
    with col_f3:
        limite = st.number_input(
            "Nombre d'entrées",
            min_value=10,
            max_value=500,
            value=50,
            step=10,
            key=_keys("limite"),
        )

    try:
        actions = _charger_actions(
            limite=limite,
            filtre_type=filtre_type if filtre_type != "Tous" else None,
            filtre_user=filtre_user if filtre_user != "Tous" else None,
        )
        if actions:
            import pandas as pd

            df = pd.DataFrame(actions)
            st.dataframe(df, use_container_width=True, hide_index=True)

            # Export CSV
            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                "📥 Exporter en CSV",
                csv,
                "journal_activite.csv",
                "text/csv",
                key=_keys("export_csv"),
            )
        else:
            st.info("Aucune action enregistrée.")
    except Exception as e:
        logger.error("Erreur chargement journal: %s", e)
        st.warning(f"Impossible de charger le journal: {e}")
