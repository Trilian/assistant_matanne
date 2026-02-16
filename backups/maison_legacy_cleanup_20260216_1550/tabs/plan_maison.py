"""Tab Plan Maison - Vue interactive des pièces et objets."""

from decimal import Decimal

import streamlit as st

from src.core.database import obtenir_contexte_db


def tab_plan_maison():
    """Affiche le plan interactif de la maison."""
    try:
        from src.core.models import ObjetMaison, PieceMaison
        from src.ui.maison.plan_maison import (
            ICONES_PIECES,
            ObjetData,
            PieceData,
            PlanMaisonInteractif,
        )

        with obtenir_contexte_db() as db:
            pieces_db = db.query(PieceMaison).order_by(PieceMaison.etage, PieceMaison.nom).all()

            if not pieces_db:
                _afficher_fallback_pieces()
                return

            pieces_data = []
            objets_par_piece: dict[int, list] = {}

            for piece in pieces_db:
                objets = db.query(ObjetMaison).filter(ObjetMaison.piece_id == piece.id).all()

                nb_a_changer = sum(1 for o in objets if o.statut == "a_changer")
                nb_a_acheter = sum(1 for o in objets if o.statut == "a_acheter")
                valeur = sum(float(o.prix_achat or 0) for o in objets)

                etage_label = (
                    "RDC"
                    if piece.etage == 0
                    else f"{piece.etage}er"
                    if piece.etage == 1
                    else f"{piece.etage}e"
                )

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
