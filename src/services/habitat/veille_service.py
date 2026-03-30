"""Service de veille immobiliere Habitat avec scraping HTTP reel."""

from __future__ import annotations

import hashlib
import json
import logging
import re
from dataclasses import dataclass
from statistics import median
from typing import Any
from urllib.parse import quote, urljoin, urlparse

import httpx
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session

from src.core.models import AnnonceHabitat, CritereImmoHabitat
from src.services.core.events import obtenir_bus
from src.services.core.notifications.notif_dispatcher import get_dispatcher_notifications
from src.services.core.registry import service_factory

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class AnnonceScrapee:
    source: str
    url_source: str
    titre: str
    prix: float | None = None
    surface_m2: float | None = None
    surface_terrain_m2: float | None = None
    nb_pieces: int | None = None
    ville: str | None = None
    code_postal: str | None = None
    departement: str | None = None
    photos: list[str] | None = None
    description_brute: str | None = None


class VeilleHabitatService:
    """Agrege des annonces depuis URLs de recherche et produit alertes + carte."""

    USER_AGENT = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
    )

    def _normaliser_prix(self, value: Any) -> float | None:
        if value in (None, ""):
            return None
        if isinstance(value, (int, float)):
            return float(value)
        text = str(value)
        digits = re.sub(r"[^\d,\.]", "", text).replace(",", ".")
        if digits.count(".") > 1:
            first, *rest = digits.split(".")
            digits = first + "".join(rest)
        try:
            return float(digits)
        except ValueError:
            return None

    def _normaliser_nombre(self, value: Any) -> float | None:
        return self._normaliser_prix(value)

    def _slug(self, value: str) -> str:
        return quote(value.lower().replace(" ", "-"))

    def _construire_urls_recherche(self, critere: CritereImmoHabitat) -> list[tuple[str, str]]:
        extra = critere.criteres_supplementaires or {}
        urls: list[tuple[str, str]] = []
        search_urls = extra.get("search_urls")
        if isinstance(search_urls, dict):
            for source, url in search_urls.items():
                if isinstance(url, str) and url.startswith("http"):
                    urls.append((str(source), url))
        elif isinstance(search_urls, list):
            for url in search_urls:
                if isinstance(url, str) and url.startswith("http"):
                    host = urlparse(url).netloc.replace("www.", "")
                    urls.append((host.split(".")[0], url))

        ville = (critere.villes or ["annecy"])[0]
        budget_min = int(float(critere.budget_min or 0)) if critere.budget_min else 0
        budget_max = int(float(critere.budget_max or 0)) if critere.budget_max else 0
        pieces = critere.nb_pieces_min or 0

        urls.append(
            (
                "leboncoin",
                "https://www.leboncoin.fr/recherche"
                f"?category=9&text={quote(ville)}&real_estate_type=1,2"
                f"&rooms={pieces if pieces else ''}&price={budget_min}-{budget_max if budget_max else ''}",
            )
        )
        urls.append(
            (
                "bienici",
                "https://www.bienici.com/recherche/achat/"
                f"{self._slug(ville)}?prix-max={budget_max if budget_max else ''}",
            )
        )

        uniques: list[tuple[str, str]] = []
        vus: set[str] = set()
        for source, url in urls:
            if url not in vus:
                vus.add(url)
                uniques.append((source, url))
        return uniques

    def _extraire_json_ld(self, html: str) -> list[dict[str, Any]]:
        soup = BeautifulSoup(html, "lxml")
        objets: list[dict[str, Any]] = []
        for script in soup.find_all("script", attrs={"type": "application/ld+json"}):
            contenu = script.string or script.text
            if not contenu:
                continue
            try:
                parsed = json.loads(contenu)
            except Exception:
                continue
            if isinstance(parsed, list):
                objets.extend(item for item in parsed if isinstance(item, dict))
            elif isinstance(parsed, dict):
                objets.append(parsed)
        return objets

    def _parser_depuis_json_ld(self, source: str, url: str, html: str) -> list[AnnonceScrapee]:
        items: list[AnnonceScrapee] = []
        for obj in self._extraire_json_ld(html):
            type_name = str(obj.get("@type", "")).lower()
            if type_name in {"itemlist", "collectionpage"}:
                for entry in obj.get("itemListElement", []) or []:
                    item = entry.get("item") if isinstance(entry, dict) else None
                    if not isinstance(item, dict):
                        continue
                    offer = item.get("offers") if isinstance(item.get("offers"), dict) else {}
                    address = item.get("address") if isinstance(item.get("address"), dict) else {}
                    annonce = AnnonceScrapee(
                        source=source,
                        url_source=item.get("url") or url,
                        titre=str(item.get("name") or "Annonce habitat"),
                        prix=self._normaliser_prix(offer.get("price") or item.get("price")),
                        surface_m2=self._normaliser_nombre(item.get("floorSize")),
                        ville=address.get("addressLocality"),
                        code_postal=address.get("postalCode"),
                        photos=[item.get("image")] if item.get("image") else [],
                        description_brute=item.get("description"),
                    )
                    items.append(annonce)
            elif type_name in {"product", "house", "apartment", "residence"}:
                offer = obj.get("offers") if isinstance(obj.get("offers"), dict) else {}
                address = obj.get("address") if isinstance(obj.get("address"), dict) else {}
                items.append(
                    AnnonceScrapee(
                        source=source,
                        url_source=obj.get("url") or url,
                        titre=str(obj.get("name") or "Annonce habitat"),
                        prix=self._normaliser_prix(offer.get("price") or obj.get("price")),
                        surface_m2=self._normaliser_nombre(obj.get("floorSize")),
                        ville=address.get("addressLocality"),
                        code_postal=address.get("postalCode"),
                        photos=[obj.get("image")] if obj.get("image") else [],
                        description_brute=obj.get("description"),
                    )
                )
        return items

    def _parser_generique_html(self, source: str, url: str, html: str) -> list[AnnonceScrapee]:
        soup = BeautifulSoup(html, "lxml")
        items: list[AnnonceScrapee] = []
        selectors = [
            "article",
            "[data-qa-id*='listing']",
            "[class*='listing']",
            "[class*='card']",
        ]

        elements = []
        for selector in selectors:
            found = soup.select(selector)
            if len(found) >= 2:
                elements = found[:30]
                break

        for element in elements:
            anchor = element.find("a", href=True)
            titre = anchor.get_text(" ", strip=True) if anchor else element.get_text(" ", strip=True)[:120]
            if len(titre) < 8:
                continue

            texte = element.get_text(" ", strip=True)
            prix_match = re.search(r"(\d[\d\s]{3,})\s?(?:€|eur)", texte, flags=re.IGNORECASE)
            surface_match = re.search(r"(\d+[\.,]?\d*)\s?m²", texte, flags=re.IGNORECASE)
            pieces_match = re.search(r"(\d+)\s?p[ièe]ces?", texte, flags=re.IGNORECASE)
            cp_match = re.search(r"\b(\d{5})\b", texte)

            items.append(
                AnnonceScrapee(
                    source=source,
                    url_source=urljoin(url, anchor["href"]) if anchor else url,
                    titre=titre[:500],
                    prix=self._normaliser_prix(prix_match.group(1) if prix_match else None),
                    surface_m2=self._normaliser_nombre(surface_match.group(1) if surface_match else None),
                    nb_pieces=int(pieces_match.group(1)) if pieces_match else None,
                    code_postal=cp_match.group(1) if cp_match else None,
                    description_brute=texte[:1500],
                )
            )
        return items

    def _scraper_url(self, source: str, url: str, limite: int) -> list[AnnonceScrapee]:
        try:
            with httpx.Client(timeout=20.0, follow_redirects=True, headers={"User-Agent": self.USER_AGENT}) as client:
                response = client.get(url)
            response.raise_for_status()
            html = response.text
        except Exception as exc:
            logger.warning("Scraping Habitat impossible pour %s: %s", url, exc)
            return []

        items = self._parser_depuis_json_ld(source, url, html)
        if not items:
            items = self._parser_generique_html(source, url, html)
        return items[:limite]

    def _construire_hash(self, annonce: AnnonceScrapee) -> str:
        base = "|".join(
            [
                annonce.source,
                annonce.url_source,
                annonce.titre or "",
                str(annonce.prix or ""),
                str(annonce.surface_m2 or ""),
                annonce.ville or "",
            ]
        )
        return hashlib.sha256(base.encode("utf-8")).hexdigest()

    def _calculer_score(self, critere: CritereImmoHabitat, annonce: AnnonceScrapee) -> float:
        score = 0.0
        total = 0.0

        if critere.budget_max:
            total += 0.3
            if annonce.prix and annonce.prix <= float(critere.budget_max):
                score += 0.3
            elif annonce.prix and annonce.prix <= float(critere.budget_max) * 1.08:
                score += 0.18

        if critere.surface_min_m2:
            total += 0.2
            if annonce.surface_m2 and annonce.surface_m2 >= float(critere.surface_min_m2):
                score += 0.2

        if critere.nb_pieces_min:
            total += 0.15
            if annonce.nb_pieces and annonce.nb_pieces >= critere.nb_pieces_min:
                score += 0.15

        if critere.villes:
            total += 0.2
            ville_annonce = (annonce.ville or "").lower()
            if any(ville_annonce == ville.lower() for ville in critere.villes):
                score += 0.2

        if critere.departements:
            total += 0.15
            if annonce.departement and annonce.departement in critere.departements:
                score += 0.15
            elif annonce.code_postal and annonce.code_postal[:2] in critere.departements:
                score += 0.15

        return round(score / total if total else 0.0, 4)

    def _estimer_prix_secteur(self, session: Session, annonce: AnnonceScrapee) -> float | None:
        if not annonce.ville:
            return None
        existantes = (
            session.query(AnnonceHabitat)
            .filter(AnnonceHabitat.ville == annonce.ville)
            .filter(AnnonceHabitat.prix_m2_secteur.isnot(None))
            .limit(30)
            .all()
        )
        valeurs = [float(item.prix_m2_secteur) for item in existantes if item.prix_m2_secteur is not None]
        if valeurs:
            return float(median(valeurs))
        if annonce.prix and annonce.surface_m2 and annonce.surface_m2 > 0:
            return round(annonce.prix / annonce.surface_m2, 2)
        return None

    def _enrichir_localisation(self, ville: str | None, code_postal: str | None) -> dict[str, Any]:
        if not ville and not code_postal:
            return {}
        params = {
            "nom": ville or "",
            "codePostal": code_postal or "",
            "fields": "nom,code,centre,codesPostaux,population",
            "boost": "population",
            "limit": 1,
        }
        try:
            with httpx.Client(timeout=10.0, headers={"User-Agent": self.USER_AGENT}) as client:
                response = client.get("https://geo.api.gouv.fr/communes", params=params)
            response.raise_for_status()
            data = response.json()
        except Exception:
            return {}

        if not isinstance(data, list) or not data:
            return {}
        commune = data[0]
        centre = commune.get("centre", {}).get("coordinates") or []
        return {
            "ville": commune.get("nom") or ville,
            "code_postal": (commune.get("codesPostaux") or [code_postal])[0],
            "latitude": centre[1] if len(centre) == 2 else None,
            "longitude": centre[0] if len(centre) == 2 else None,
        }

    def synchroniser_annonces(
        self,
        session: Session,
        *,
        user_id: str,
        critere_id: int | None = None,
        limite_par_source: int = 12,
        envoyer_alertes: bool = True,
    ) -> dict[str, Any]:
        criteres_query = session.query(CritereImmoHabitat).filter(CritereImmoHabitat.actif == True)  # noqa: E712
        if critere_id is not None:
            criteres_query = criteres_query.filter(CritereImmoHabitat.id == critere_id)
        criteres = criteres_query.all()

        annonces_creees = 0
        annonces_maj = 0
        alerts: list[dict[str, Any]] = []
        sources_utilisees: set[str] = set()

        for critere in criteres:
            for source, url in self._construire_urls_recherche(critere):
                sources_utilisees.add(source)
                for scraped in self._scraper_url(source, url, limite_par_source):
                    hash_dedup = self._construire_hash(scraped)
                    annonce = (
                        session.query(AnnonceHabitat)
                        .filter(
                            (AnnonceHabitat.hash_dedup == hash_dedup)
                            | (AnnonceHabitat.url_source == scraped.url_source)
                        )
                        .first()
                    )

                    score = self._calculer_score(critere, scraped)
                    prix_m2 = None
                    if scraped.prix and scraped.surface_m2 and scraped.surface_m2 > 0:
                        prix_m2 = round(scraped.prix / scraped.surface_m2, 2)
                    prix_secteur = self._estimer_prix_secteur(session, scraped) or prix_m2
                    ecart_prix_pct = None
                    if prix_m2 and prix_secteur:
                        ecart_prix_pct = round(((prix_m2 - prix_secteur) / prix_secteur) * 100, 2)

                    payload = {
                        "critere_id": critere.id,
                        "source": scraped.source,
                        "url_source": scraped.url_source,
                        "titre": scraped.titre,
                        "prix": scraped.prix,
                        "surface_m2": scraped.surface_m2,
                        "surface_terrain_m2": scraped.surface_terrain_m2,
                        "nb_pieces": scraped.nb_pieces,
                        "ville": scraped.ville,
                        "code_postal": scraped.code_postal,
                        "departement": scraped.departement or (scraped.code_postal[:2] if scraped.code_postal else None),
                        "photos": scraped.photos or [],
                        "description_brute": scraped.description_brute,
                        "score_pertinence": score,
                        "statut": "alerte" if score >= float(critere.seuil_alerte) else "nouveau",
                        "prix_m2_secteur": prix_secteur,
                        "ecart_prix_pct": ecart_prix_pct,
                        "hash_dedup": hash_dedup,
                    }

                    if annonce is None:
                        annonce = AnnonceHabitat(**payload)
                        session.add(annonce)
                        annonces_creees += 1
                    else:
                        for key, value in payload.items():
                            setattr(annonce, key, value)
                        annonces_maj += 1

                    if score >= float(critere.seuil_alerte) or (ecart_prix_pct is not None and ecart_prix_pct <= -10):
                        alerts.append(
                            {
                                "source": scraped.source,
                                "titre": scraped.titre,
                                "url_source": scraped.url_source,
                                "score": score,
                                "ville": scraped.ville,
                                "prix": scraped.prix,
                                "ecart_prix_pct": ecart_prix_pct,
                            }
                        )

        session.flush()

        if envoyer_alertes and alerts:
            dispatcher = get_dispatcher_notifications()
            top_alerts = sorted(alerts, key=lambda item: (item["score"], -(item.get("ecart_prix_pct") or 0)), reverse=True)[:3]
            lines = [
                f"{item['titre']} ({item.get('ville') or 'ville inconnue'}) - score {item['score']:.2f}"
                for item in top_alerts
            ]
            dispatcher.envoyer_evenement(
                user_id=user_id,
                type_evenement="tache_entretien_urgente",
                message="Nouvelles opportunites Habitat:\n" + "\n".join(lines),
                titre="Veille Habitat",
            )

        obtenir_bus().emettre(
            "habitat.veille.sync",
            {
                "criteres": len(criteres),
                "annonces_creees": annonces_creees,
                "annonces_mises_a_jour": annonces_maj,
                "alertes": len(alerts),
                "sources": sorted(sources_utilisees),
            },
            source="habitat",
        )

        return {
            "criteres": len(criteres),
            "annonces_creees": annonces_creees,
            "annonces_mises_a_jour": annonces_maj,
            "alertes": len(alerts),
            "sources": sorted(sources_utilisees),
            "top_alertes": alerts[:5],
        }

    def lister_alertes(self, session: Session) -> list[dict[str, Any]]:
        items = (
            session.query(AnnonceHabitat)
            .filter(AnnonceHabitat.score_pertinence.isnot(None))
            .order_by(AnnonceHabitat.score_pertinence.desc(), AnnonceHabitat.modifie_le.desc())
            .limit(12)
            .all()
        )
        alertes: list[dict[str, Any]] = []
        for annonce in items:
            score = float(annonce.score_pertinence or 0)
            ecart = float(annonce.ecart_prix_pct) if annonce.ecart_prix_pct is not None else None
            if score < 0.65 and (ecart is None or ecart > -5):
                continue
            alertes.append(
                {
                    "id": annonce.id,
                    "titre": annonce.titre,
                    "source": annonce.source,
                    "ville": annonce.ville,
                    "score": score,
                    "prix": float(annonce.prix) if annonce.prix is not None else None,
                    "ecart_prix_pct": ecart,
                    "url_source": annonce.url_source,
                    "statut": annonce.statut,
                }
            )
        return alertes

    def carte_annonces(self, session: Session) -> list[dict[str, Any]]:
        items = (
            session.query(AnnonceHabitat)
            .filter(AnnonceHabitat.ville.isnot(None))
            .order_by(AnnonceHabitat.score_pertinence.desc())
            .limit(40)
            .all()
        )
        groupes: dict[str, dict[str, Any]] = {}
        for annonce in items:
            key = f"{annonce.ville}|{annonce.code_postal or ''}"
            groupe = groupes.setdefault(
                key,
                {
                    "ville": annonce.ville,
                    "code_postal": annonce.code_postal,
                    "nb_annonces": 0,
                    "score_max": 0.0,
                    "prix_min": None,
                    "prix_max": None,
                    "latitude": None,
                    "longitude": None,
                },
            )
            prix = float(annonce.prix) if annonce.prix is not None else None
            groupe["nb_annonces"] += 1
            groupe["score_max"] = max(groupe["score_max"], float(annonce.score_pertinence or 0))
            groupe["prix_min"] = prix if groupe["prix_min"] is None else min(groupe["prix_min"], prix or groupe["prix_min"])
            groupe["prix_max"] = prix if groupe["prix_max"] is None else max(groupe["prix_max"], prix or groupe["prix_max"])

        for groupe in groupes.values():
            geo = self._enrichir_localisation(groupe.get("ville"), groupe.get("code_postal"))
            groupe["ville"] = geo.get("ville") or groupe["ville"]
            groupe["code_postal"] = geo.get("code_postal") or groupe["code_postal"]
            groupe["latitude"] = geo.get("latitude")
            groupe["longitude"] = geo.get("longitude")

        return sorted(groupes.values(), key=lambda item: (item["score_max"], item["nb_annonces"]), reverse=True)


@service_factory("habitat_veille", tags={"habitat", "scraping", "immo"})
def obtenir_service_veille_habitat() -> VeilleHabitatService:
    """Factory singleton du service de veille Habitat."""
    return VeilleHabitatService()