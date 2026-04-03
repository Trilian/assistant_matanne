"""Tests du moteur embeddings (I.31 full)."""

from __future__ import annotations

from unittest.mock import MagicMock, patch


def test_embedder_local_non_vide() -> None:
    from src.core.ai.embeddings import embedder_texte_local

    vecteur = embedder_texte_local("menu familial rapide")
    assert isinstance(vecteur, list)
    assert len(vecteur) > 0


def test_embedder_wrapper_fallback_local() -> None:
    from src.core.ai.embeddings import embedder_texte

    with patch("src.core.ai.embeddings.embedder_texte_mistral", return_value=None):
        vecteur, provider = embedder_texte("planning de demain", prefer_externe=True)

    assert isinstance(vecteur, list)
    assert provider == "local"


def test_embedder_wrapper_utilise_mistral() -> None:
    from src.core.ai.embeddings import embedder_texte

    fake = [0.1, 0.2, 0.3]
    with patch("src.core.ai.embeddings.embedder_texte_mistral", return_value=fake):
        vecteur, provider = embedder_texte("planning de demain", prefer_externe=True)

    assert vecteur == fake
    assert provider == "mistral"


def test_embedder_mistral_parse_payload() -> None:
    from src.core.ai.embeddings import embedder_texte_mistral

    class _FakeParams:
        MISTRAL_API_KEY = "sk-123"
        MISTRAL_BASE_URL = "https://api.mistral.ai/v1"

    response = MagicMock()
    response.raise_for_status.return_value = None
    response.json.return_value = {"data": [{"embedding": [1.0, 2.0, 3.0]}]}

    client = MagicMock()
    client.post.return_value = response

    with patch("src.core.ai.embeddings.obtenir_parametres", return_value=_FakeParams()):
        with patch("src.core.ai.embeddings.httpx.Client") as client_ctor:
            client_ctor.return_value.__enter__.return_value = client
            vecteur = embedder_texte_mistral("test")

    assert vecteur == [1.0, 2.0, 3.0]
