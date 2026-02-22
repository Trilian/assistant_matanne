"""
Depenses Maison - Composants Cards & Formulaire

Affichage d'une dépense individuelle et formulaire d'ajout/édition.
"""

from src.core.session_keys import SK
from src.ui.keys import KeyNamespace

_keys = KeyNamespace("depenses")

from .crud import create_depense, delete_depense, update_depense
from .utils import CATEGORY_LABELS, MOIS_FR, Decimal, HouseExpense, Optional, date, st


def afficher_depense_card(depense: HouseExpense):
    """Affiche une card de depense"""
    with st.container(border=True):
        col1, col2, col3 = st.columns([2, 1, 1])

        with col1:
            cat_label = CATEGORY_LABELS.get(depense.categorie, depense.categorie)
            st.markdown(f"**{cat_label}**")

            if depense.note:
                st.caption(depense.note)

            if depense.consommation:
                unite = (
                    "kWh"
                    if depense.categorie == "electricite"
                    else "m³"
                    if depense.categorie in ["gaz", "eau"]
                    else ""
                )
                st.caption(f"📏 {depense.consommation} {unite}")

        with col2:
            st.metric("Montant", f"{depense.montant:.2f}€")

        with col3:
            col_edit, col_del = st.columns(2)
            with col_edit:
                if st.button("✏️", key=_keys("edit", depense.id), help="Modifier"):
                    st.session_state[SK.EDIT_DEPENSE_ID] = depense.id
                    st.rerun()
            with col_del:
                if st.button("🗑️", key=_keys("del", depense.id), help="Supprimer"):
                    delete_depense(depense.id)
                    st.rerun()


def afficher_formulaire(depense: Optional[HouseExpense] = None):
    """Formulaire d'ajout/edition"""
    is_edit = depense is not None
    prefix = "edit" if is_edit else "new"
    today = date.today()

    with st.form(f"form_depense_{prefix}"):
        col1, col2 = st.columns(2)

        with col1:
            categories = list(CATEGORY_LABELS.keys())
            cat_index = (
                categories.index(depense.categorie)
                if is_edit and depense.categorie in categories
                else 0
            )
            categorie = st.selectbox(
                "Categorie *",
                options=categories,
                format_func=lambda x: CATEGORY_LABELS.get(x, x),
                index=cat_index,
            )

            montant = st.number_input(
                "Montant (€) *",
                min_value=0.0,
                value=float(depense.montant) if is_edit else 0.0,
                step=0.01,
            )

            # Consommation (pour gaz, eau, electricite)
            if categorie in ["gaz", "eau", "electricite"]:
                unite = "kWh" if categorie == "electricite" else "m³"
                consommation = st.number_input(
                    f"Consommation ({unite})",
                    min_value=0.0,
                    value=float(depense.consommation) if is_edit and depense.consommation else 0.0,
                    step=1.0,
                )
            else:
                consommation = 0.0

        with col2:
            col_mois, col_annee = st.columns(2)
            with col_mois:
                mois = st.selectbox(
                    "Mois",
                    options=range(1, 13),
                    format_func=lambda x: MOIS_FR[x],
                    index=(depense.mois - 1) if is_edit else (today.month - 1),
                )
            with col_annee:
                annee = st.number_input(
                    "Annee",
                    min_value=2020,
                    max_value=2030,
                    value=depense.annee if is_edit else today.year,
                )

            note = st.text_area(
                "Note",
                value=depense.note if is_edit else "",
                placeholder="Commentaire, reference facture...",
            )

        submitted = st.form_submit_button(
            "💾 Enregistrer" if is_edit else "➕ Ajouter", use_container_width=True, type="primary"
        )

        if submitted:
            if montant <= 0:
                st.error("Le montant doit être superieur à 0!")
                return

            data = {
                "categorie": categorie,
                "montant": Decimal(str(montant)),
                "consommation": Decimal(str(consommation)) if consommation > 0 else None,
                "mois": mois,
                "annee": int(annee),
                "note": note or None,
            }

            if is_edit:
                update_depense(depense.id, data)
                st.success("✅ Depense mise à jour!")
            else:
                create_depense(data)
                st.success("✅ Depense ajoutee!")

            st.rerun()
