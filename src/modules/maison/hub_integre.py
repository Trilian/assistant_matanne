"""
Hub Maison Intégré - Centre de contrôle complet.

Assemble les composants UI pour :
- Plan interactif maison (multi-étages)
- Plan jardin avec zones
- Chronomètre entretien
- Dashboard temps passé
- Gestion statuts objets x courses x budget

Architecture:
┌──────────────────────────────────────────────────────────────┐
│                    🏠 HUB MAISON                              │
├──────────┬──────────┬──────────┬──────────┬─────────────────┤
│ Plan     │ Jardin   │ Chrono   │ Temps    │ Objets          │
│ Maison   │ Zones    │ Entretien│ Dashboard│ à remplacer     │
└──────────┴──────────┴──────────┴──────────┴─────────────────┘
"""

import streamlit as st

from src.core.database import obtenir_contexte_db

# ═══════════════════════════════════════════════════════════
# CONSTANTES
# ═══════════════════════════════════════════════════════════

TABS_CONFIG = [
    ("🏠", "Plan Maison", "plan_maison"),
    ("🌳", "Jardin", "jardin"),
    ("⏱️", "Chronomètre", "chrono"),
    ("📊", "Temps", "temps"),
    ("🔧", "Objets", "objets"),
]

# Styles CSS personnalisés
CSS_STYLES = """
<style>
.hub-header {
    background: linear-gradient(135deg, #2d3436 0%, #636e72 100%);
    color: white;
    padding: 1rem 1.5rem;
    border-radius: 12px;
    margin-bottom: 1.5rem;
}
.hub-header h1 {
    margin: 0;
    font-size: 1.8rem;
}
.metric-card {
    background: white;
    border-radius: 12px;
    padding: 1rem;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    border-left: 4px solid #3498db;
}
.metric-value {
    font-size: 1.8rem;
    font-weight: bold;
    color: #2c3e50;
}
.metric-label {
    font-size: 0.85rem;
    color: #7f8c8d;
}
.alert-badge {
    display: inline-block;
    padding: 4px 10px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
}
.alert-urgent { background: #e74c3c; color: white; }
.alert-warn { background: #f39c12; color: white; }
.alert-ok { background: #27ae60; color: white; }
</style>
"""


# ═══════════════════════════════════════════════════════════
# COMPOSANT: EN-TÊTE
# ═══════════════════════════════════════════════════════════


def render_header():
    """Affiche l'en-tête avec métriques rapides."""
    st.markdown(CSS_STYLES, unsafe_allow_html=True)

    # Récupérer les métriques
    metriques = _obtenir_metriques_rapides()

    # Header
    st.markdown(
        """
        <div class="hub-header">
            <h1>🏠 Centre de Contrôle Maison</h1>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Métriques en colonnes
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "🔧 Objets à changer",
            metriques.get("objets_a_changer", 0),
            delta=None,
            help="Objets marqués 'à changer' ou 'à acheter'",
        )

    with col2:
        st.metric(
            "⏱️ Temps ce mois",
            f"{metriques.get('temps_mois_heures', 0):.1f}h",
            delta=None,
            help="Temps d'entretien ce mois",
        )

    with col3:
        st.metric(
            "🌱 Plantes",
            metriques.get("nb_plantes", 0),
            delta=None,
            help="Nombre de plantes suivies",
        )

    with col4:
        st.metric(
            "💰 Budget travaux",
            f"{metriques.get('budget_travaux', 0):,.0f}€",
            delta=None,
            help="Coûts travaux ce mois",
        )


def _obtenir_metriques_rapides() -> dict[str, int | float]:
    """Récupère les métriques pour le header."""
    from datetime import date

    metriques: dict[str, int | float] = {
        "objets_a_changer": 0,
        "temps_mois_heures": 0.0,
        "nb_plantes": 0,
        "budget_travaux": 0.0,
    }

    try:
        from src.core.models import CoutTravaux, ObjetMaison, PlanteJardin, SessionTravail

        today = date.today()

        with obtenir_contexte_db() as db:
            # Objets à changer
            metriques["objets_a_changer"] = (
                db.query(ObjetMaison)
                .filter(ObjetMaison.statut.in_(["a_changer", "a_acheter", "a_reparer"]))
                .count()
            )

            # Temps ce mois
            from sqlalchemy import extract, func

            temps_total = (
                db.query(func.sum(SessionTravail.duree_minutes))
                .filter(
                    extract("month", SessionTravail.debut) == today.month,
                    extract("year", SessionTravail.debut) == today.year,
                    SessionTravail.fin.isnot(None),
                )
                .scalar()
            )
            metriques["temps_mois_heures"] = (temps_total or 0) / 60

            # Plantes
            metriques["nb_plantes"] = db.query(PlanteJardin).count()

            # Budget travaux mois
            budget = (
                db.query(func.sum(CoutTravaux.montant))
                .filter(
                    extract("month", CoutTravaux.created_at) == today.month,
                    extract("year", CoutTravaux.created_at) == today.year,
                )
                .scalar()
            )
            metriques["budget_travaux"] = float(budget or 0)

    except Exception:
        pass  # Retourne les valeurs par défaut

    return metriques


# ═══════════════════════════════════════════════════════════
# TAB: PLAN MAISON
# ═══════════════════════════════════════════════════════════


def tab_plan_maison():
    """Affiche le plan interactif de la maison."""
    try:
        from decimal import Decimal

        from src.core.models import ObjetMaison, PieceMaison
        from src.ui.maison.plan_maison import (
            ICONES_PIECES,
            ObjetData,
            PieceData,
            PlanMaisonInteractif,
        )

        # Charger les données depuis la BD
        with obtenir_contexte_db() as db:
            pieces_db = db.query(PieceMaison).order_by(PieceMaison.etage, PieceMaison.nom).all()

            if not pieces_db:
                st.info("Aucune pièce enregistrée.")
                _afficher_fallback_pieces()
                return

            # Convertir en PieceData
            pieces_data = []
            objets_par_piece: dict[int, list] = {}

            for piece in pieces_db:
                # Récupérer les objets de cette pièce
                objets = db.query(ObjetMaison).filter(ObjetMaison.piece_id == piece.id).all()

                nb_a_changer = sum(1 for o in objets if o.statut == "a_changer")
                nb_a_acheter = sum(1 for o in objets if o.statut == "a_acheter")
                valeur = sum(float(o.prix_achat or 0) for o in objets)

                # Mapper l'étage
                etage_label = (
                    "RDC"
                    if piece.etage == 0
                    else f"{piece.etage}er"
                    if piece.etage == 1
                    else f"{piece.etage}e"
                )

                # Icône basée sur le type
                icone = ICONES_PIECES.get(piece.type_piece or "", ICONES_PIECES["default"])

                piece_data = PieceData(
                    id=piece.id,
                    nom=piece.nom,
                    etage=etage_label,
                    icone=icone,
                    superficie_m2=float(piece.superficie_m2) if piece.superficie_m2 else None,
                    nb_objets=len(objets),
                    nb_a_changer=nb_a_changer,
                    nb_a_acheter=nb_a_acheter,
                    valeur_totale=Decimal(str(valeur)),
                )
                pieces_data.append(piece_data)

                # Objets
                objets_data = []
                for obj in objets:
                    objets_data.append(
                        ObjetData(
                            id=obj.id,
                            nom=obj.nom,
                            categorie=obj.categorie or "autre",
                            statut=obj.statut or "fonctionne",
                            prix_achat=Decimal(str(obj.prix_achat)) if obj.prix_achat else None,
                            cout_remplacement=Decimal(str(obj.prix_remplacement_estime))
                            if obj.prix_remplacement_estime
                            else None,
                        )
                    )
                objets_par_piece[piece.id] = objets_data

        plan = PlanMaisonInteractif(pieces=pieces_data, objets_par_piece=objets_par_piece)
        plan.render()

    except ImportError:
        st.warning("Module Plan Maison non disponible")
        _afficher_fallback_pieces()
    except Exception as e:
        st.error(f"Erreur chargement plan: {e}")
        _afficher_fallback_pieces()


def _afficher_fallback_pieces():
    """Affichage simplifié des pièces si UI non disponible."""
    try:
        from typing import Any

        from src.core.models import PieceMaison

        with obtenir_contexte_db() as db:
            pieces = db.query(PieceMaison).order_by(PieceMaison.etage, PieceMaison.nom).all()

        if not pieces:
            st.info("Aucune pièce enregistrée. Ajoutez vos pièces !")
            return

        # Grouper par étage
        par_etage: dict[int, list[Any]] = {}
        for piece in pieces:
            etage = piece.etage or 0
            if etage not in par_etage:
                par_etage[etage] = []
            par_etage[etage].append(piece)

        for etage in sorted(par_etage.keys(), reverse=True):
            nom_etage = (
                "RDC" if etage == 0 else f"{etage}er étage" if etage == 1 else f"{etage}e étage"
            )
            st.subheader(f"📍 {nom_etage}")

            cols = st.columns(3)
            for i, piece in enumerate(par_etage[etage]):
                with cols[i % 3]:
                    superficie = f"{piece.superficie_m2}m²" if piece.superficie_m2 else "-"
                    st.markdown(
                        f"""
                        <div style="
                            background: linear-gradient(135deg, #3498db, #2980b9);
                            padding: 1rem;
                            border-radius: 10px;
                            color: white;
                            margin-bottom: 0.5rem;
                        ">
                            <strong>{piece.nom}</strong><br>
                            <small>{superficie}</small>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

    except Exception as e:
        st.error(f"Erreur chargement pièces: {e}")


# ═══════════════════════════════════════════════════════════
# TAB: JARDIN
# ═══════════════════════════════════════════════════════════


def tab_jardin():
    """Affiche le plan du jardin avec zones."""
    try:
        from src.core.models import PlanteJardin, ZoneJardin
        from src.ui.maison.plan_jardin import (
            COULEURS_ZONES,
            PlanJardinInteractif,
            PlanteData,
            ZoneJardinData,
        )

        with obtenir_contexte_db() as db:
            zones_db = db.query(ZoneJardin).all()

            if not zones_db:
                st.info("Aucune zone jardin créée.")
                _afficher_fallback_jardin()
                return

            # Convertir en ZoneJardinData
            zones_data = []
            plantes_par_zone: dict[int, list] = {}

            for zone in zones_db:
                # Compter les plantes
                plantes = db.query(PlanteJardin).filter(PlanteJardin.zone_id == zone.id).all()

                zone_data = ZoneJardinData(
                    id=zone.id,
                    nom=zone.nom,
                    type_zone=zone.type_zone,
                    superficie_m2=float(zone.superficie_m2) if zone.superficie_m2 else None,
                    exposition=zone.exposition,
                    type_sol=zone.type_sol,
                    arrosage_auto=zone.arrosage_auto or False,
                    nb_plantes=len(plantes),
                    couleur=COULEURS_ZONES.get(zone.type_zone, "#22c55e"),
                )
                zones_data.append(zone_data)

                # Plantes
                plantes_data = []
                for plante in plantes:
                    plantes_data.append(
                        PlanteData(
                            id=plante.id,
                            nom=plante.nom,
                            variete=plante.variete,
                            etat=plante.etat or "bon",
                            date_plantation=plante.date_plantation,
                        )
                    )
                plantes_par_zone[zone.id] = plantes_data

        plan = PlanJardinInteractif(zones=zones_data, plantes_par_zone=plantes_par_zone)
        plan.render()

    except ImportError:
        st.warning("Module Plan Jardin non disponible")
        _afficher_fallback_jardin()
    except Exception as e:
        st.error(f"Erreur chargement jardin: {e}")
        _afficher_fallback_jardin()


def _afficher_fallback_jardin():
    """Affichage simplifié du jardin."""
    try:
        from src.core.models import PlanteJardin, ZoneJardin

        with obtenir_contexte_db() as db:
            zones = db.query(ZoneJardin).all()

        if not zones:
            st.info("Aucune zone jardin créée.")
            return

        for zone in zones:
            with st.expander(f"🌱 {zone.nom} ({zone.type_zone})", expanded=True):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Surface", f"{zone.superficie_m2 or 0}m²")
                with col2:
                    st.metric("Exposition", zone.exposition or "-")
                with col3:
                    arrosage = "✅ Auto" if zone.arrosage_auto else "🖐️ Manuel"
                    st.metric("Arrosage", arrosage)

                # Plantes dans cette zone
                with obtenir_contexte_db() as db:
                    plantes = db.query(PlanteJardin).filter(PlanteJardin.zone_id == zone.id).all()

                if plantes:
                    st.markdown("**Plantes :**")
                    for plante in plantes:
                        etat_icon = {
                            "excellent": "🟢",
                            "bon": "🟡",
                            "attention": "🟠",
                            "probleme": "🔴",
                        }.get(plante.etat, "⚪")
                        st.write(
                            f"- {etat_icon} {plante.nom} ({plante.variete or 'variété non spécifiée'})"
                        )

    except Exception as e:
        st.error(f"Erreur chargement jardin: {e}")


# ═══════════════════════════════════════════════════════════
# TAB: CHRONOMÈTRE
# ═══════════════════════════════════════════════════════════


def tab_chrono():
    """Affiche le chronomètre d'entretien."""
    try:
        from datetime import datetime

        from src.core.models import SessionTravail
        from src.ui.maison.temps_ui import chronometre_widget

        # Vérifier si session active
        session_active = None
        with obtenir_contexte_db() as db:
            session_en_cours = (
                db.query(SessionTravail)
                .filter(SessionTravail.fin.is_(None))
                .order_by(SessionTravail.debut.desc())
                .first()
            )
            if session_en_cours:
                session_active = {
                    "id": session_en_cours.id,
                    "type_activite": session_en_cours.type_activite,
                    "debut": session_en_cours.debut,
                }

        def on_start(type_activite: str):
            """Callback démarrage session."""
            with obtenir_contexte_db() as db:
                nouvelle_session = SessionTravail(
                    type_activite=type_activite,
                    debut=datetime.now(),
                )
                db.add(nouvelle_session)
                db.commit()
            st.rerun()

        def on_stop(session_id: int):
            """Callback arrêt session."""
            with obtenir_contexte_db() as db:
                session = db.query(SessionTravail).filter(SessionTravail.id == session_id).first()
                if session:
                    session.fin = datetime.now()
                    duree = session.fin - session.debut
                    session.duree_minutes = int(duree.total_seconds() / 60)
                    db.commit()
            st.success("Session terminée!")
            st.rerun()

        def on_cancel(session_id: int):
            """Callback annulation session."""
            with obtenir_contexte_db() as db:
                db.query(SessionTravail).filter(SessionTravail.id == session_id).delete()
                db.commit()
            st.info("Session annulée")
            st.rerun()

        chronometre_widget(
            session_active=session_active,
            on_start=on_start,
            on_stop=on_stop,
            on_cancel=on_cancel,
        )

    except ImportError:
        st.warning("Module Chronomètre non disponible")
        _afficher_fallback_chrono()
    except Exception as e:
        st.error(f"Erreur chronomètre: {e}")
        _afficher_fallback_chrono()


def _afficher_fallback_chrono():
    """Chronomètre simplifié."""
    from datetime import datetime

    st.subheader("⏱️ Chronomètre Entretien")

    # État session
    if "chrono_debut" not in st.session_state:
        st.session_state.chrono_debut = None
        st.session_state.chrono_type = None

    # Sélection type activité
    types_activite = [
        "Ménage général",
        "Aspirateur",
        "Tonte",
        "Arrosage",
        "Taille",
        "Bricolage",
        "Autre",
    ]

    col1, col2 = st.columns([2, 1])

    with col1:
        type_activite = st.selectbox(
            "Type d'activité",
            types_activite,
            key="chrono_type_select",
            disabled=st.session_state.chrono_debut is not None,
        )

    with col2:
        if st.session_state.chrono_debut is None:
            if st.button("▶️ Démarrer", type="primary", use_container_width=True):
                st.session_state.chrono_debut = datetime.now()
                st.session_state.chrono_type = type_activite
                st.rerun()
        else:
            if st.button("⏹️ Arrêter", type="secondary", use_container_width=True):
                duree = datetime.now() - st.session_state.chrono_debut
                minutes = int(duree.total_seconds() / 60)
                st.success(f"Session terminée : {minutes} minutes")

                # Enregistrer en BD
                _enregistrer_session(
                    st.session_state.chrono_type,
                    st.session_state.chrono_debut,
                    datetime.now(),
                    minutes,
                )

                st.session_state.chrono_debut = None
                st.session_state.chrono_type = None
                st.rerun()

    # Affichage temps en cours
    if st.session_state.chrono_debut:
        duree = datetime.now() - st.session_state.chrono_debut
        minutes = int(duree.total_seconds() / 60)
        secondes = int(duree.total_seconds() % 60)

        st.markdown(
            f"""
            <div style="
                background: linear-gradient(135deg, #27ae60, #2ecc71);
                padding: 2rem;
                border-radius: 15px;
                text-align: center;
                color: white;
                margin: 1rem 0;
            ">
                <div style="font-size: 0.9rem; opacity: 0.9;">
                    En cours : {st.session_state.chrono_type}
                </div>
                <div style="font-size: 3rem; font-weight: bold;">
                    {minutes:02d}:{secondes:02d}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def _enregistrer_session(type_activite: str, debut, fin, duree_minutes: int):
    """Enregistre une session de travail en BD."""
    try:
        from src.core.models import SessionTravail

        with obtenir_contexte_db() as db:
            session = SessionTravail(
                type_activite=type_activite.lower().replace(" ", "_"),
                debut=debut,
                fin=fin,
                duree_minutes=duree_minutes,
            )
            db.add(session)
            db.commit()
    except Exception as e:
        st.error(f"Erreur enregistrement: {e}")


# ═══════════════════════════════════════════════════════════
# TAB: DASHBOARD TEMPS
# ═══════════════════════════════════════════════════════════


def tab_temps():
    """Affiche le dashboard temps passé."""
    try:
        from datetime import date, timedelta

        from sqlalchemy import extract, func

        from src.core.models import SessionTravail
        from src.ui.maison.temps_ui import dashboard_temps

        today = date.today()
        debut_semaine = today - timedelta(days=today.weekday())

        with obtenir_contexte_db() as db:
            # Stats de la semaine
            sessions_semaine = (
                db.query(SessionTravail)
                .filter(
                    SessionTravail.debut >= debut_semaine,
                    SessionTravail.fin.isnot(None),
                )
                .all()
            )

            # Calculs par catégorie
            temps_jardin = sum(
                s.duree_minutes or 0
                for s in sessions_semaine
                if s.type_activite
                in ["arrosage", "tonte", "taille", "desherbage", "plantation", "recolte"]
            )
            temps_menage = sum(
                s.duree_minutes or 0
                for s in sessions_semaine
                if s.type_activite
                in ["menage_general", "aspirateur", "lavage_sol", "poussiere", "vitres", "lessive"]
            )
            temps_bricolage = sum(
                s.duree_minutes or 0
                for s in sessions_semaine
                if s.type_activite in ["bricolage", "peinture", "plomberie", "electricite"]
            )
            temps_total = sum(s.duree_minutes or 0 for s in sessions_semaine)

            resume_semaine = {
                "temps_total_minutes": temps_total,
                "temps_jardin_minutes": temps_jardin,
                "temps_menage_minutes": temps_menage,
                "temps_bricolage_minutes": temps_bricolage,
            }

            # Stats par activité
            stats_par_activite = (
                db.query(
                    SessionTravail.type_activite,
                    func.count(SessionTravail.id).label("nb_sessions"),
                    func.sum(SessionTravail.duree_minutes).label("total_minutes"),
                )
                .filter(
                    SessionTravail.debut >= debut_semaine,
                    SessionTravail.fin.isnot(None),
                )
                .group_by(SessionTravail.type_activite)
                .all()
            )

            stats_activites = [
                {
                    "type_activite": stat.type_activite,
                    "nb_sessions": stat.nb_sessions,
                    "total_minutes": stat.total_minutes or 0,
                }
                for stat in stats_par_activite
            ]

        dashboard_temps(
            resume_semaine=resume_semaine,
            stats_activites=stats_activites,
        )

    except ImportError:
        st.warning("Module Dashboard Temps non disponible")
        _afficher_fallback_temps()
    except Exception as e:
        st.error(f"Erreur dashboard: {e}")
        _afficher_fallback_temps()


def _afficher_fallback_temps():
    """Dashboard temps simplifié."""
    from datetime import date, timedelta

    from sqlalchemy import extract, func

    st.subheader("📊 Temps d'Entretien")

    try:
        from src.core.models import SessionTravail

        today = date.today()

        with obtenir_contexte_db() as db:
            # Stats du mois
            stats_mois = (
                db.query(
                    SessionTravail.type_activite,
                    func.count(SessionTravail.id).label("nb_sessions"),
                    func.sum(SessionTravail.duree_minutes).label("total_minutes"),
                )
                .filter(
                    extract("month", SessionTravail.debut) == today.month,
                    extract("year", SessionTravail.debut) == today.year,
                    SessionTravail.fin.isnot(None),
                )
                .group_by(SessionTravail.type_activite)
                .all()
            )

        if not stats_mois:
            st.info("Aucune session enregistrée ce mois.")
            return

        # Afficher par type
        total_heures = 0
        for stat in stats_mois:
            heures = (stat.total_minutes or 0) / 60
            total_heures += heures

            st.markdown(
                f"""
                <div style="
                    display: flex;
                    justify-content: space-between;
                    padding: 0.8rem 1rem;
                    background: #f8f9fa;
                    border-radius: 8px;
                    margin-bottom: 0.5rem;
                ">
                    <span><strong>{stat.type_activite}</strong></span>
                    <span>{stat.nb_sessions} sessions • {heures:.1f}h</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("---")
        st.metric("**Total du mois**", f"{total_heures:.1f} heures")

    except Exception as e:
        st.error(f"Erreur chargement stats: {e}")


# ═══════════════════════════════════════════════════════════
# TAB: OBJETS À REMPLACER
# ═══════════════════════════════════════════════════════════


def tab_objets():
    """Affiche les objets à remplacer avec intégration courses/budget."""
    st.subheader("🔧 Objets à Remplacer")

    try:
        from src.core.models import ObjetMaison, PieceMaison

        with obtenir_contexte_db() as db:
            objets = (
                db.query(ObjetMaison, PieceMaison.nom.label("piece_nom"))
                .join(PieceMaison, ObjetMaison.piece_id == PieceMaison.id)
                .filter(ObjetMaison.statut.in_(["a_changer", "a_acheter", "a_reparer"]))
                .order_by(
                    # Tri par priorité
                    ObjetMaison.statut,
                    ObjetMaison.priorite_remplacement,
                )
                .all()
            )

        if not objets:
            st.success("✅ Aucun objet à remplacer actuellement")
            return

        # Statistiques
        nb_total = len(objets)
        budget_total = sum(float(o[0].prix_remplacement_estime or 0) for o in objets)

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Objets à remplacer", nb_total)
        with col2:
            st.metric("Budget estimé", f"{budget_total:,.0f}€")

        st.markdown("---")

        # Liste des objets
        for objet, piece_nom in objets:
            statut_icon = {
                "a_changer": "🔴",
                "a_acheter": "🟠",
                "a_reparer": "🟡",
            }.get(objet.statut, "⚪")

            priorite_badge = {
                "urgente": ("🔥 Urgent", "#e74c3c"),
                "haute": ("⚡ Haute", "#e67e22"),
                "normale": ("📋 Normale", "#3498db"),
                "basse": ("📦 Basse", "#95a5a6"),
            }.get(objet.priorite_remplacement or "normale", ("📋", "#95a5a6"))

            prix = (
                f"{objet.prix_remplacement_estime:,.0f}€" if objet.prix_remplacement_estime else "-"
            )

            with st.container():
                col1, col2, col3, col4 = st.columns([3, 2, 2, 2])

                with col1:
                    st.markdown(f"**{statut_icon} {objet.nom}**")
                    st.caption(f"📍 {piece_nom}")

                with col2:
                    st.markdown(
                        f"""<span style="
                            background: {priorite_badge[1]};
                            color: white;
                            padding: 4px 10px;
                            border-radius: 12px;
                            font-size: 0.8rem;
                        ">{priorite_badge[0]}</span>""",
                        unsafe_allow_html=True,
                    )

                with col3:
                    st.markdown(f"💰 {prix}")

                with col4:
                    # Actions
                    col_a, col_b = st.columns(2)
                    with col_a:
                        if st.button("🛒", key=f"courses_{objet.id}", help="Ajouter aux courses"):
                            _ajouter_aux_courses(objet)
                    with col_b:
                        if st.button("📊", key=f"budget_{objet.id}", help="Ajouter au budget"):
                            _ajouter_au_budget(objet)

                st.markdown("---")

    except Exception as e:
        st.error(f"Erreur chargement objets: {e}")


def _ajouter_aux_courses(objet):
    """Ajoute un objet à la liste de courses."""
    try:
        from src.core.models import ArticleCourses

        with obtenir_contexte_db() as db:
            article = ArticleCourses(
                nom=objet.nom,
                categorie="Maison",
                quantite=1,
                unite="pièce",
                notes=f"Remplacement - {objet.marque or ''} {objet.modele or ''}".strip(),
            )
            db.add(article)
            db.commit()
        st.success(f"✅ '{objet.nom}' ajouté aux courses")
    except Exception as e:
        st.error(f"Erreur: {e}")


def _ajouter_au_budget(objet):
    """Ajoute un objet au budget prévisionnel."""
    try:
        from datetime import date

        from src.core.models import Depense

        today = date.today()

        with obtenir_contexte_db() as db:
            depense = Depense(
                libelle=f"Remplacement: {objet.nom}",
                montant=float(objet.prix_remplacement_estime or 0),
                categorie="Maison",
                date=today,
                type_depense="previsionnel",
                notes=f"Objet marqué '{objet.statut}'",
            )
            db.add(depense)
            db.commit()
        st.success(f"✅ '{objet.nom}' ajouté au budget ({objet.prix_remplacement_estime or 0}€)")
    except Exception as e:
        st.error(f"Erreur: {e}")


# ═══════════════════════════════════════════════════════════
# POINT D'ENTRÉE
# ═══════════════════════════════════════════════════════════


def app():
    """Point d'entrée du module Hub Maison Intégré."""
    # Header avec métriques
    render_header()

    # Tabs navigation
    tab_icons = [t[0] for t in TABS_CONFIG]
    tab_names = [t[1] for t in TABS_CONFIG]

    tabs = st.tabs([f"{icon} {name}" for icon, name in zip(tab_icons, tab_names, strict=False)])

    with tabs[0]:
        tab_plan_maison()

    with tabs[1]:
        tab_jardin()

    with tabs[2]:
        tab_chrono()

    with tabs[3]:
        tab_temps()

    with tabs[4]:
        tab_objets()


# Exécution directe pour test
if __name__ == "__main__":
    app()
