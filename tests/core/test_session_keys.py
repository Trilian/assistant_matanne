"""Tests pour src.core.session_keys — registre centralisé de clés session_state."""

import pytest


class TestSessionKeys:
    """Tests pour la classe _SessionKeys (SK)."""

    def test_import_singleton(self):
        from src.core.session_keys import SK

        assert SK is not None

    def test_constantes_core(self):
        from src.core.session_keys import SK

        assert SK.ETAT_APP == "etat_app"
        assert SK.DEBUG_MODE == "debug_mode"

    def test_constantes_cuisine(self):
        from src.core.session_keys import SK

        assert SK.DETAIL_RECETTE_ID == "detail_recette_id"
        assert SK.BATCH_TYPE == "batch_type"

    def test_constantes_famille(self):
        from src.core.session_keys import SK

        assert SK.FAMILLE_PAGE == "famille_page"
        assert SK.JULES_SHOW_AI_ACTIVITIES == "jules_show_ai_activities"

    def test_constantes_maison(self):
        from src.core.session_keys import SK

        assert SK.MES_OBJETS_ENTRETIEN == "mes_objets_entretien"
        assert SK.MES_PLANTES_JARDIN == "mes_plantes_jardin"

    def test_slots_prevents_dynamic_attrs(self):
        """_SessionKeys utilise __slots__=() pour empêcher les attributs dynamiques."""
        from src.core.session_keys import SK

        with pytest.raises(AttributeError):
            SK.nouvelle_cle_inventee = "boom"

    # ── Templates dynamiques ────────────────────────

    def test_generated_image(self):
        from src.core.session_keys import SK

        assert SK.generated_image(42) == "generated_image_42"

    def test_show_alternatives(self):
        from src.core.session_keys import SK

        assert SK.show_alternatives("repas_lundi") == "show_alternatives_repas_lundi"

    def test_add_repas_midi(self):
        from src.core.session_keys import SK

        assert SK.add_repas_midi("s1") == "add_repas_s1_midi"

    def test_add_repas_soir(self):
        from src.core.session_keys import SK

        assert SK.add_repas_soir("s1") == "add_repas_s1_soir"

    def test_show_details_match(self):
        from src.core.session_keys import SK

        assert SK.show_details_match("m123") == "show_details_m123"

    def test_page_key(self):
        from src.core.session_keys import SK

        assert SK.page_key("recettes") == "recettes_page"

    def test_week_start(self):
        from src.core.session_keys import SK

        assert SK.week_start("cal") == "cal_start"

    def test_barcode_detected(self):
        from src.core.session_keys import SK

        assert SK.barcode_detected("scan") == "scan_detected"

    # ── Unicité des valeurs ─────────────────────────

    def test_pas_de_doublons(self):
        """Vérifie qu'aucune constante n'a la même valeur qu'une autre."""
        from src.core.session_keys import SK

        valeurs = []
        for attr in dir(SK):
            if attr.startswith("_") or callable(getattr(SK, attr)):
                continue
            valeurs.append(getattr(SK, attr))

        assert len(valeurs) == len(set(valeurs)), (
            f"Doublons détectés dans les clés de session: "
            f"{[v for v in valeurs if valeurs.count(v) > 1]}"
        )
