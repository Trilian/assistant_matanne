import io
from types import SimpleNamespace

import pytest


def test_generer_pdf_checklist_minimal():
    """Vérifie que ServiceRapportsPDF.generer_pdf_checklist produit un BytesIO non vide.

    On monkeypatch `obtenir_service_checklists_crud` dans le module ciblé pour
    éviter la dépendance à la base de données.
    """

    from src.services.rapports import generation
    from src.services.rapports.generation import ServiceRapportsPDF

    # Fake checklist + items
    fake_checklist = SimpleNamespace(nom="Test Checklist")
    fake_items = [
        SimpleNamespace(libelle="Item 1", categorie="maison", fait=False),
        SimpleNamespace(libelle="Item 2", categorie="bagages", fait=True),
    ]

    class FakeService:
        def get_checklist_by_id(self, checklist_id: int):
            return fake_checklist

        def get_items(self, checklist_id: int):
            return fake_items

    # Monkeypatch the factory used inside the generation module
    original_factory = generation.obtenir_service_checklists_crud
    generation.obtenir_service_checklists_crud = lambda: FakeService()

    try:
        svc = ServiceRapportsPDF()
        # Appel direct à la fonction interne (décorateur @avec_session_db bypassé)
        pdf_buf = svc.generer_pdf_checklist.__wrapped__(svc, checklist_id=1, session=None)

        assert isinstance(pdf_buf, io.BytesIO)
        content = pdf_buf.getvalue()
        assert len(content) > 0

    finally:
        # restore
        generation.obtenir_service_checklists_crud = original_factory
