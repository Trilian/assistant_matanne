"""
Service Barcode/QR Code Scanner

✅ Scanner codes-barres et QR codes
✅ Intégration avec inventaire
✅ Intégration avec recettes
✅ Validation et caching
"""

import logging
import re
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from src.core.decorators import avec_cache, avec_session_db
from src.core.errors_base import ErreurNonTrouve, ErreurValidation
from src.core.models import ArticleInventaire
from src.services.base import BaseService

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════
# SCHÉMAS PYDANTIC
# ═══════════════════════════════════════════════════════════


class BarcodeData(BaseModel):
    """Données scannées d'un code-barres"""

    code: str = Field(..., min_length=8)
    type_code: str = Field("EAN-13", pattern="^(EAN-13|EAN-8|UPC|QR|CODE128|CODE39)$")
    timestamp: datetime = Field(default_factory=datetime.now)
    source: str = Field("scanner", pattern="^(scanner|manuel|import)$")


class BarcodeArticle(BaseModel):
    """Association barcode → article inventaire"""

    barcode: str = Field(..., min_length=8)
    article_id: int
    nom_article: str
    quantite_defaut: float = Field(1.0, gt=0)
    unite_defaut: str = Field("unité")
    categorie: str
    prix_unitaire: float | None = None
    date_peremption_jours: int | None = None
    lieu_stockage: str = "Placard"


class BarcodeRecette(BaseModel):
    """Association barcode → recette"""

    barcode: str = Field(..., min_length=8)
    recette_id: int
    nom_recette: str
    ingredient_detecete: str | None = None


class ScanResultat(BaseModel):
    """Résultat d'un scan"""

    barcode: str
    type_scan: str = Field("article", pattern="^(article|recette|inconnu)$")
    details: dict
    timestamp: datetime = Field(default_factory=datetime.now)


# ═══════════════════════════════════════════════════════════
# SERVICE BARCODE/QR
# ═══════════════════════════════════════════════════════════


class BarcodeService(BaseService[ArticleInventaire]):
    """
    Service pour gestion des codes-barres et QR codes.

    Fonctionnalités:
    - Scan et validation de codes-barres
    - Liaison articles/recettes â†” codes
    - Scanner rapide pour ajout d'articles
    - Vérification stock par code
    """

    def __init__(self):
        super().__init__(ArticleInventaire, cache_ttl=3600)
        # Cache est statique, pas besoin d'instancier
        self.cache_ttl = 3600
        self.barcode_mappings = {}  # Cache local {barcode → article_id}

    # ═══════════════════════════════════════════════════════════
    # VALIDATION ET PARSING
    # ═══════════════════════════════════════════════════════════

    def valider_barcode(self, code: str) -> tuple[bool, str]:
        """
        Valide un code-barres selon son format.

        Args:
            code: Le code à valider

        Returns:
            (valide, type_code) ou (False, raison)
        """
        code = code.strip().upper()

        # EAN-13 (13 chiffres)
        if re.match(r"^\d{13}$", code):
            if self._valider_checksum_ean13(code):
                return True, "EAN-13"
            return False, "Checksum EAN-13 invalide"

        # EAN-8 (8 chiffres)
        if re.match(r"^\d{8}$", code):
            if self._valider_checksum_ean8(code):
                return True, "EAN-8"
            return False, "Checksum EAN-8 invalide"

        # UPC (12 chiffres)
        if re.match(r"^\d{12}$", code):
            if self._valider_checksum_upc(code):
                return True, "UPC"
            return False, "Checksum UPC invalide"

        # QR code (alphanumérique variable)
        if re.match(r"^[A-Z0-9\-_]{10,}$", code):
            return True, "QR"

        # CODE128 (alphanumérique)
        if re.match(r"^[A-Z0-9]{8,}$", code):
            return True, "CODE128"

        # CODE39 (alphanumérique et symboles)
        if re.match(r"^[A-Z0-9\-\.\$\/\+\%\ ]+$", code):
            return True, "CODE39"

        return False, f"Format barcode non reconnu: {code}"

    @staticmethod
    def _valider_checksum_ean13(code: str) -> bool:
        """Valide le checksum d'un EAN-13"""
        if len(code) != 13 or not code.isdigit():
            return False

        total = sum(int(code[i]) * (1 if i % 2 == 0 else 3) for i in range(12))
        checksum = (10 - (total % 10)) % 10
        return int(code[12]) == checksum

    @staticmethod
    def _valider_checksum_ean8(code: str) -> bool:
        """Valide le checksum d'un EAN-8"""
        if len(code) != 8 or not code.isdigit():
            return False

        total = sum(int(code[i]) * (3 if i % 2 == 0 else 1) for i in range(7))
        checksum = (10 - (total % 10)) % 10
        return int(code[7]) == checksum

    @staticmethod
    def _valider_checksum_upc(code: str) -> bool:
        """Valide le checksum d'un UPC"""
        if len(code) != 12 or not code.isdigit():
            return False

        total = sum(int(code[i]) * (3 if i % 2 == 0 else 1) for i in range(11))
        checksum = (10 - (total % 10)) % 10
        return int(code[11]) == checksum

    # ═══════════════════════════════════════════════════════════
    # SCAN ET DÉTECTION
    # ═══════════════════════════════════════════════════════════

    @avec_cache(ttl=3600)
    @avec_session_db
    def scanner_code(self, code: str, session: Session = None) -> ScanResultat:
        """
        Scanne et identifie un code-barres.

        Args:
            code: Code scanné
            session: Session DB

        Returns:
            Détails du scan (article, recette ou inconnu)
        """
        # Valider
        valide, type_code = self.valider_barcode(code)
        if not valide:
            raise ErreurValidation(f"Code invalide: {type_code}")

        # Vérifier si article connu
        article = (
            session.query(ArticleInventaire).filter(ArticleInventaire.code_barres == code).first()
        )

        if article:
            return ScanResultat(
                barcode=code,
                type_scan="article",
                details={
                    "id": article.id,
                    "nom": article.nom,
                    "quantite": article.quantite,
                    "unite": article.unite,
                    "prix_unitaire": article.prix_unitaire,
                    "date_peremption": article.date_peremption.isoformat()
                    if article.date_peremption
                    else None,
                    "emplacement": article.emplacement,
                },
            )

        # TODO: Vérifier recettes si implémenté

        return ScanResultat(
            barcode=code,
            type_scan="inconnu",
            details={"message": "Code non reconnu - doit être ajouté"},
        )

    # ═══════════════════════════════════════════════════════════
    # GESTION ARTICLES PAR BARCODE
    # ═══════════════════════════════════════════════════════════

    @avec_session_db
    def ajouter_article_par_barcode(
        self,
        code: str,
        nom: str,
        quantite: float = 1.0,
        unite: str = "unité",
        categorie: str = "Autre",
        prix_unitaire: float | None = None,
        date_peremption_jours: int | None = None,
        emplacement: str = "Placard",
        session: Session = None,
    ) -> ArticleInventaire:
        """
        Ajoute rapidement un article avec code-barres.

        Args:
            code: Code-barres
            nom: Nom de l'article
            quantite: Quantité
            unite: Unité
            categorie: Catégorie
            prix_unitaire: Prix unitaire
            date_peremption_jours: Jours avant péremption
            emplacement: Lieu de stockage
            session: Session DB

        Returns:
            Article créé
        """
        # Valider barcode
        valide, _ = self.valider_barcode(code)
        if not valide:
            raise ErreurValidation(f"Code-barres invalide: {code}")

        # Vérifier unicité
        existant = (
            session.query(ArticleInventaire).filter(ArticleInventaire.code_barres == code).first()
        )
        if existant:
            raise ErreurValidation(f"Ce code-barres est déjà assigné: {existant.nom}")

        # Créer article
        from datetime import timedelta

        article = ArticleInventaire(
            nom=nom,
            quantite=quantite,
            unite=unite,
            quantite_min=0,
            categorie=categorie,
            emplacement=emplacement,
            code_barres=code,
            prix_unitaire=prix_unitaire,
        )

        if date_peremption_jours:
            article.date_peremption = datetime.now() + timedelta(days=date_peremption_jours)

        session.add(article)
        session.commit()

        logger.info(f"✅ Article ajouté: {nom} (barcode: {code})")
        self.cache.invalidate()

        return article

    @avec_session_db
    def incrementer_stock_barcode(
        self, code: str, quantite: float = 1.0, session: Session = None
    ) -> ArticleInventaire:
        """
        Augmente rapidement le stock d'un article scanné.

        Args:
            code: Code-barres
            quantite: Quantité à ajouter
            session: Session DB

        Returns:
            Article mis à jour
        """
        article = (
            session.query(ArticleInventaire).filter(ArticleInventaire.code_barres == code).first()
        )

        if not article:
            raise ErreurNonTrouve(f"Article avec code-barres {code} non trouvé")

        article.quantite += quantite
        session.commit()

        logger.info(f"📦 Stock augmenté: {article.nom} → {article.quantite}{article.unite}")
        self.cache.invalidate()

        return article

    @avec_session_db
    def verifier_stock_barcode(self, code: str, session: Session = None) -> dict[str, Any]:
        """
        Vérifie le stock d'un article scanné.

        Args:
            code: Code-barres
            session: Session DB

        Returns:
            État du stock (OK, Faible, Critique)
        """
        article = (
            session.query(ArticleInventaire).filter(ArticleInventaire.code_barres == code).first()
        )

        if not article:
            raise ErreurNonTrouve(f"Article avec code-barres {code} non trouvé")

        # Déterminer état
        if article.quantite <= 0:
            etat = "CRITIQUE"
        elif article.quantite < article.quantite_min:
            etat = "FAIBLE"
        else:
            etat = "OK"

        # Vérifier péremption
        peremption_etat = "OK"
        if article.date_peremption:
            jours_restants = (article.date_peremption - datetime.now()).days
            if jours_restants <= 0:
                peremption_etat = "PÉRIMÉ"
            elif jours_restants <= 7:
                peremption_etat = "URGENT"
            elif jours_restants <= 30:
                peremption_etat = "BIENTÔT"

        return {
            "article_id": article.id,
            "nom": article.nom,
            "quantite": article.quantite,
            "unite": article.unite,
            "quantite_min": article.quantite_min,
            "etat_stock": etat,
            "peremption_etat": peremption_etat,
            "date_peremption": article.date_peremption.isoformat()
            if article.date_peremption
            else None,
            "prix_unitaire": article.prix_unitaire,
            "emplacement": article.emplacement,
        }

    # ═══════════════════════════════════════════════════════════
    # GESTION MAPPINGS BARCODE
    # ═══════════════════════════════════════════════════════════

    @avec_session_db
    def mettre_a_jour_barcode(
        self, article_id: int, nouveau_code: str, session: Session = None
    ) -> ArticleInventaire:
        """Remplace le code-barres d'un article"""

        valide, _ = self.valider_barcode(nouveau_code)
        if not valide:
            raise ErreurValidation(f"Code invalide: {nouveau_code}")

        article = (
            session.query(ArticleInventaire).filter(ArticleInventaire.id == article_id).first()
        )

        if not article:
            raise ErreurNonTrouve(f"Article {article_id} non trouvé")

        ancien_code = article.code_barres
        article.code_barres = nouveau_code
        session.commit()

        logger.info(f"🔄 Code-barres mis à jour: {ancien_code} → {nouveau_code}")
        self.cache.invalidate()

        return article

    @avec_cache(ttl=7200)
    @avec_session_db
    def lister_articles_avec_barcode(self, session: Session = None) -> list[dict]:
        """Liste tous les articles avec code-barres"""

        articles = (
            session.query(ArticleInventaire).filter(ArticleInventaire.code_barres.isnot(None)).all()
        )

        return [
            {
                "id": a.id,
                "nom": a.nom,
                "barcode": a.code_barres,
                "quantite": a.quantite,
                "unite": a.unite,
                "categorie": a.categorie,
            }
            for a in articles
        ]

    @avec_session_db
    def exporter_barcodes(self, session: Session = None) -> str:
        """
        Exporte tous les code-barres en format CSV.

        Returns:
            CSV (barcode,nom,quantite,unite,categorie)
        """
        import csv
        from io import StringIO

        articles = self.lister_articles_avec_barcode(session=session)

        output = StringIO()
        writer = csv.DictWriter(
            output, fieldnames=["barcode", "nom", "quantite", "unite", "categorie"]
        )
        writer.writeheader()
        writer.writerows(articles)

        return output.getvalue()

    @avec_session_db
    def importer_barcodes(self, csv_content: str, session: Session = None) -> dict[str, Any]:
        """
        Importe des code-barres depuis CSV.

        Args:
            csv_content: Contenu CSV
            session: Session DB

        Returns:
            Résumé importation
        """
        import csv
        from io import StringIO

        reader = csv.DictReader(StringIO(csv_content))
        resultats = {"success": 0, "errors": []}

        for row in reader:
            try:
                self.ajouter_article_par_barcode(
                    code=row["barcode"],
                    nom=row["nom"],
                    quantite=float(row.get("quantite", 1)),
                    unite=row.get("unite", "unité"),
                    categorie=row.get("categorie", "Autre"),
                    session=session,
                )
                resultats["success"] += 1
            except Exception as e:
                resultats["errors"].append({"barcode": row.get("barcode"), "erreur": str(e)})

        return resultats


# ═══════════════════════════════════════════════════════════
# FACTORY
# ═══════════════════════════════════════════════════════════

_service_instance: BarcodeService | None = None


def obtenir_service_codes_barres() -> BarcodeService:
    """Factory pour obtenir le service Barcode (convention française)."""
    global _service_instance
    if _service_instance is None:
        _service_instance = BarcodeService()
    return _service_instance


def get_barcode_service() -> BarcodeService:
    """Factory pour obtenir le service Barcode (alias anglais)."""
    return obtenir_service_codes_barres()
