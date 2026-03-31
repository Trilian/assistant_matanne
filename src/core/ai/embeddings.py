"""Moteur embeddings local + recherche ANN légère pour le cache IA (I.31)."""

from __future__ import annotations

import hashlib
import math
import os
import re
from collections import Counter

import httpx

from src.core.config import obtenir_parametres

DIMENSION_DEFAUT = 192
BITS_SIGNATURE = 48


def _tokeniser(texte: str) -> list[str]:
    tokens = [t for t in re.findall(r"[a-z0-9à-ÿ]+", texte.lower()) if len(t) > 2]
    # Ajouter des bigrammes de tokens pour capter un peu plus de contexte.
    bigrammes = [f"{tokens[i]}_{tokens[i + 1]}" for i in range(max(0, len(tokens) - 1))]
    return tokens + bigrammes


def _indice_signe(token: str, dimension: int) -> tuple[int, float]:
    digest = hashlib.sha256(token.encode()).digest()
    indice = int.from_bytes(digest[:4], "big") % dimension
    signe = 1.0 if (digest[4] & 1) == 0 else -1.0
    return indice, signe


def embedder_texte_local(texte: str, dimension: int = DIMENSION_DEFAUT) -> list[float]:
    """Construit un embedding dense déterministe (sans dépendance externe)."""
    vecteur = [0.0 for _ in range(dimension)]
    poids = Counter(_tokeniser(texte))
    if not poids:
        return vecteur

    for token, freq in poids.items():
        indice, signe = _indice_signe(token, dimension)
        vecteur[indice] += float(freq) * signe

    norme = math.sqrt(sum(v * v for v in vecteur))
    if norme == 0:
        return vecteur
    return [v / norme for v in vecteur]


def embedder_texte_mistral(
    texte: str,
    timeout_s: int = 8,
) -> list[float] | None:
    """Récupère un embedding via l'API Mistral (optionnel)."""
    try:
        parametres = obtenir_parametres()
        api_key = parametres.MISTRAL_API_KEY
        base_url = parametres.MISTRAL_BASE_URL.rstrip("/")
    except Exception:
        return None

    if not api_key:
        return None

    modele = os.getenv("MISTRAL_EMBEDDINGS_MODEL", "mistral-embed")
    body = {
        "model": modele,
        "input": [texte],
    }
    try:
        with httpx.Client(timeout=timeout_s) as client:
            response = client.post(
                f"{base_url}/embeddings",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json=body,
            )
            response.raise_for_status()
            payload = response.json()

        data = payload.get("data") or []
        if not data:
            return None
        vecteur = data[0].get("embedding")
        if not isinstance(vecteur, list):
            return None
        return [float(v) for v in vecteur]
    except Exception:
        return None


def embedder_texte(
    texte: str,
    prefer_externe: bool = True,
    dimension_locale: int = DIMENSION_DEFAUT,
) -> tuple[list[float], str]:
    """Retourne (embedding, provider) avec fallback automatique."""
    if prefer_externe:
        vecteur = embedder_texte_mistral(texte)
        if vecteur:
            return vecteur, "mistral"

    return embedder_texte_local(texte, dimension=dimension_locale), "local"


def similarite_cosine(v1: list[float], v2: list[float]) -> float:
    if not v1 or not v2 or len(v1) != len(v2):
        return 0.0
    return sum(a * b for a, b in zip(v1, v2, strict=False))


def signature_ann(vecteur: list[float], bits: int = BITS_SIGNATURE) -> str:
    """Signature binaire compacte pour filtrage ANN par proximité."""
    if not vecteur:
        return ""

    pas = max(1, len(vecteur) // bits)
    morceaux: list[str] = []
    for i in range(0, len(vecteur), pas):
        if len(morceaux) >= bits:
            break
        somme = sum(vecteur[i : i + pas])
        morceaux.append("1" if somme >= 0 else "0")
    return "".join(morceaux)


def distance_hamming(s1: str, s2: str) -> int:
    if not s1 or not s2:
        return 999
    longueur = min(len(s1), len(s2))
    base = sum(1 for i in range(longueur) if s1[i] != s2[i])
    return base + abs(len(s1) - len(s2))
