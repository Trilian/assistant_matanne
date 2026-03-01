"""
Paramètres - Configuration Crèche
Gestion des semaines de fermeture de la crèche de Jules.

Permet de configurer les 5 semaines annuelles de fermeture
(été, Noël, etc.) qui seront prises en compte dans le calendrier
familial et les jours spéciaux.

Persistée en base de données via PersistentState (sync session_state ↔ DB).
"""

import logging
from datetime import date, timedelta

import streamlit as st

from src.core.state import rerun
from src.core.state.persistent import PersistentState, persistent_state
from src.ui.feedback import afficher_erreur, afficher_succes
from src.ui.fragments import ui_fragment
from src.ui.keys import KeyNamespace

logger = logging.getLogger(__name__)

_keys = KeyNamespace("creche")

# Nombre max de semaines fermeture par an (standard crèche)
NB_SEMAINES_MAX = 7
NB_SEMAINES_DEFAUT = 5

# Templates courants de fermeture
TEMPLATES_FERMETURE = {
    "Été (3 semaines)": {"mois": 8, "nb_semaines": 3, "label": "Fermeture été"},
    "Noël (1 semaine)": {"mois": 12, "jour_debut": 24, "nb_jours": 8, "label": "Vacances Noël"},
    "Printemps (1 semaine)": {"mois": 4, "nb_semaines": 1, "label": "Vacances printemps"},
    "Pont Ascension": {"label": "Pont Ascension"},
    "Toussaint (1 semaine)": {"mois": 10, "jour_debut": 28, "nb_jours": 5, "label": "Toussaint"},
}


def _generer_dates_template(template: dict, annee: int) -> tuple[date, date] | None:
    """Génère les dates début/fin à partir d'un template."""
    try:
        mois = template.get("mois")
        if not mois:
            return None

        jour_debut = template.get("jour_debut", 1)
        debut = date(annee, mois, jour_debut)

        if "nb_semaines" in template:
            nb_jours = template["nb_semaines"] * 7 - 1
        elif "nb_jours" in template:
            nb_jours = template["nb_jours"] - 1
        else:
            nb_jours = 6  # 1 semaine par défaut

        fin = debut + timedelta(days=nb_jours)
        return debut, fin
    except (ValueError, TypeError):
        return None


def _compter_jours_ouvres(semaines: list[dict]) -> int:
    """Compte le nombre total de jours ouvrés de fermeture."""
    total = 0
    for s in semaines:
        try:
            debut = date.fromisoformat(s["debut"])
            fin = date.fromisoformat(s["fin"])
            current = debut
            while current <= fin:
                if current.weekday() < 5:  # Lundi-Vendredi
                    total += 1
                current += timedelta(days=1)
        except (KeyError, ValueError):
            pass
    return total


def _compter_semaines(nb_jours_ouvres: int) -> float:
    """Convertit les jours ouvrés en semaines."""
    return round(nb_jours_ouvres / 5, 1)


@ui_fragment
def afficher_creche_config():
    """Configuration des fermetures crèche."""
    from src.services.famille.jours_speciaux import obtenir_service_jours_speciaux

    st.markdown("### 🏫 Configuration Crèche")
    st.caption(
        "Configure les semaines de fermeture annuelle de la crèche. "
        "Ces dates apparaîtront dans le calendrier familial."
    )

    service = obtenir_service_jours_speciaux()

    # Année sélectionnée
    annee = st.selectbox(
        "Année",
        options=[date.today().year, date.today().year + 1],
        key=_keys("annee"),
    )

    # Charger la config existante via PersistentState

    # Accéder directement au PersistentState du service
    from src.services.famille.jours_speciaux import _obtenir_config_creche

    pstate: PersistentState = _obtenir_config_creche()
    config = pstate.get_all()

    nom_creche = config.get("nom_creche", "")
    semaines_existantes: list[dict] = config.get("semaines_fermeture", [])

    # Filtrer par année
    semaines_annee = [s for s in semaines_existantes if s.get("debut", "").startswith(str(annee))]
    semaines_autres = [
        s for s in semaines_existantes if not s.get("debut", "").startswith(str(annee))
    ]

    # ── Info crèche ──
    st.text_input(
        "Nom de la crèche",
        value=nom_creche,
        key=_keys("nom_creche"),
        placeholder="Ex: Crèche Les Petits Explorateurs",
    )

    # ── Résumé ──
    nb_jours = _compter_jours_ouvres(semaines_annee)
    nb_sem = _compter_semaines(nb_jours)

    col_m1, col_m2, col_m3 = st.columns(3)
    with col_m1:
        st.metric("📅 Périodes", len(semaines_annee))
    with col_m2:
        st.metric("📆 Jours ouvrés", nb_jours)
    with col_m3:
        delta_color = "normal" if nb_sem <= NB_SEMAINES_DEFAUT else "inverse"
        st.metric(
            "📊 Semaines",
            f"{nb_sem}/{NB_SEMAINES_DEFAUT}",
            delta=f"{nb_sem - NB_SEMAINES_DEFAUT:+.1f}" if nb_sem != NB_SEMAINES_DEFAUT else None,
            delta_color=delta_color,
        )

    st.divider()

    # ── Périodes existantes ──
    if semaines_annee:
        st.markdown(f"#### 📋 Fermetures {annee}")

        for i, semaine in enumerate(semaines_annee):
            col_info, col_del = st.columns([5, 1])
            with col_info:
                try:
                    d = date.fromisoformat(semaine["debut"])
                    f = date.fromisoformat(semaine["fin"])
                    label = semaine.get("label", "Fermeture")
                    jours = _compter_jours_ouvres([semaine])
                    st.markdown(
                        f"🏫 **{label}** — "
                        f"{d.strftime('%d/%m/%Y')} → {f.strftime('%d/%m/%Y')} "
                        f"({jours} jours ouvrés)"
                    )
                except (KeyError, ValueError):
                    st.markdown(f"⚠️ Entrée invalide: {semaine}")

            with col_del:
                if st.button("🗑️", key=_keys(f"del_{i}"), help="Supprimer cette période"):
                    semaines_annee.pop(i)
                    toutes = semaines_autres + semaines_annee
                    service.sauvegarder_fermetures_creche(
                        toutes, st.session_state.get(_keys("nom_creche"), nom_creche)
                    )
                    afficher_succes("Période supprimée")
                    rerun()
    else:
        st.info(f"Aucune fermeture configurée pour {annee}.")

    st.divider()

    # ── Ajout rapide via templates ──
    st.markdown("#### ⚡ Ajout rapide")
    st.caption("Ajouter des périodes types en un clic")

    cols_tpl = st.columns(3)
    for idx, (tpl_nom, tpl_data) in enumerate(TEMPLATES_FERMETURE.items()):
        with cols_tpl[idx % 3]:
            if st.button(f"➕ {tpl_nom}", key=_keys(f"tpl_{idx}"), use_container_width=True):
                dates = _generer_dates_template(tpl_data, annee)
                if dates:
                    nouvelle = {
                        "debut": dates[0].isoformat(),
                        "fin": dates[1].isoformat(),
                        "label": tpl_data["label"],
                    }
                    semaines_annee.append(nouvelle)
                    toutes = semaines_autres + semaines_annee
                    service.sauvegarder_fermetures_creche(
                        toutes, st.session_state.get(_keys("nom_creche"), nom_creche)
                    )
                    afficher_succes(f"✅ {tpl_nom} ajouté pour {annee}")
                    rerun()
                else:
                    afficher_erreur(f"Impossible de générer les dates pour: {tpl_nom}")

    st.divider()

    # ── Ajout manuel ──
    st.markdown("#### ✏️ Ajout manuel")

    with st.form("creche_ajout_form"):
        col1, col2 = st.columns(2)

        with col1:
            debut_input = st.date_input(
                "Date début",
                value=date(annee, 8, 1),
                min_value=date(annee, 1, 1),
                max_value=date(annee, 12, 31),
                key=_keys("debut_input"),
            )

        with col2:
            fin_input = st.date_input(
                "Date fin",
                value=date(annee, 8, 14),
                min_value=date(annee, 1, 1),
                max_value=date(annee, 12, 31),
                key=_keys("fin_input"),
            )

        label_input = st.text_input(
            "Label",
            value="Fermeture crèche",
            key=_keys("label_input"),
            placeholder="Ex: Fermeture été, Vacances Noël...",
        )

        submitted = st.form_submit_button(
            "💾 Ajouter cette période", type="primary", use_container_width=True
        )

        if submitted:
            if fin_input < debut_input:
                afficher_erreur("La date de fin doit être après la date de début.")
            else:
                nouvelle = {
                    "debut": debut_input.isoformat(),
                    "fin": fin_input.isoformat(),
                    "label": label_input or "Fermeture crèche",
                }
                semaines_annee.append(nouvelle)
                toutes = semaines_autres + semaines_annee
                service.sauvegarder_fermetures_creche(
                    toutes, st.session_state.get(_keys("nom_creche"), nom_creche)
                )
                afficher_succes(
                    f"✅ Fermeture ajoutée: {debut_input.strftime('%d/%m')} → {fin_input.strftime('%d/%m')}"
                )
                rerun()

    # ── Aperçu jours fériés ──
    with st.expander("📅 Aperçu jours fériés + fermetures crèche"):
        jours = service.tous_jours_speciaux(annee)
        if jours:
            # Trier par date puis afficher de façon compacte et lisible
            jours_sorted = sorted(jours, key=lambda x: x.date_jour)
            for j in jours_sorted:
                icone = {"ferie": "⭐", "creche": "🏫", "pont": "🌉"}.get(j.type, "📅")
                date_str = j.date_jour.strftime("%a %d/%m")
                # Mise en page: petite colonne pour icône, contenu principal pour détails
                c_icon, c_main = st.columns([0.6, 9])
                with c_icon:
                    st.markdown(
                        f"<div style='font-size:22px'>{icone}</div>", unsafe_allow_html=True
                    )
                with c_main:
                    st.write(f"**{date_str}** — {j.nom}")
                    tlabel = j.type.capitalize() if hasattr(j, "type") else ""
                    if tlabel:
                        st.caption(tlabel)
        else:
            st.caption("Aucun jour spécial configuré.")

    # ── Sync status ──
    with st.expander("🔄 État de la synchronisation"):
        st.json(pstate.get_all())
        sync_status = pstate.get_sync_status()
        if sync_status.get("last_sync"):
            st.caption(
                f"Dernière sync: {sync_status['last_sync'].strftime('%H:%M:%S')} "
                f"• {sync_status.get('sync_count', 0)} sync(s)"
            )
