"""
Service Inter-Modules — Bridges entre modules.

Connecte les modules via l'event bus et des helpers métier pour :
- B5.1: Récolte jardin → Recettes semaine suivante
- B5.2: Budget anomalie → Notification proactive
- B5.3: Documents expirés → Dashboard alerte
- B5.5: Entretien récurrent → Planning unifié
- B5.6: Voyages → Inventaire (déstockage)
- B5.7: Anniversaire proche → Suggestions cadeaux IA
- B5.8: Météo → Entretien maison
- S4: Entretien → artisans, récolte → stock, anniversaire → menu, jalon → journal
"""

import logging
from datetime import date, timedelta

from sqlalchemy import func
from sqlalchemy.orm import Session

from src.core.decorators import avec_gestion_erreurs, avec_session_db
from src.services.core.events.bus import EvenementDomaine
from src.services.core.registry import service_factory

logger = logging.getLogger(__name__)


class BridgesInterModulesService:
    """Service de bridges inter-modules."""

    def _detecter_metiers_depuis_tache(self, tache: object) -> list[str]:
        """Déduit les métiers d'artisans à partir d'une tâche d'entretien."""
        contenu = " ".join(
            str(getattr(tache, champ, "") or "")
            for champ in ("nom", "description", "categorie", "piece")
        ).lower()

        correspondances = {
            "plombier": ["plomb", "fuite", "robinet", "canalisation", "wc", "eau"],
            "plombier-chauffagiste": ["chaudiere", "chauffage", "radiateur", "chauffe-eau"],
            "électricien": ["electric", "prise", "tableau", "lum", "ampoule", "disjonct"],
            "couvreur": ["toit", "toiture", "gouttiere", "gouttière"],
            "menuisier": ["porte", "fenetre", "fenêtre", "volet", "placard"],
            "peintre": ["peinture", "mur", "plafond"],
            "serrurier": ["serrure", "verrou", "porte bloquee", "porte bloquée"],
            "jardinier": ["jardin", "haie", "pelouse", "taille", "arbre"],
        }

        metiers = [
            metier
            for metier, mots_cles in correspondances.items()
            if any(mot in contenu for mot in mots_cles)
        ]
        return metiers or ["artisan multi-services"]

    def _prioriser_artisans(self, artisans: list[object]) -> list[object]:
        """Ordonne les artisans recommandés par pertinence."""
        return sorted(
            artisans,
            key=lambda artisan: (
                not bool(getattr(artisan, "recommande", True)),
                -(getattr(artisan, "note", 0) or 0),
                str(getattr(artisan, "nom", "")).lower(),
            ),
        )

    # ── B5.1: Récolte jardin → Suggestions recettes ────────

    @avec_gestion_erreurs(default_return=[])
    @avec_session_db
    def recolte_vers_recettes(self, element_nom: str, db: Session | None = None) -> list[dict]:
        """Cherche des recettes utilisant un ingrédient récolté au jardin.

        Args:
            element_nom: Nom de l'élément récolté (tomate, basilic, etc.)

        Returns:
            Liste de recettes correspondantes
        """
        from src.core.models.recettes import Recette, Ingredient

        recettes = (
            db.query(Recette)
            .join(Ingredient, Ingredient.recette_id == Recette.id)
            .filter(Ingredient.nom.ilike(f"%{element_nom}%"))
            .limit(10)
            .all()
        )

        return [
            {
                "id": r.id,
                "nom": r.nom,
                "description": r.description,
                "temps_total": r.temps_total,
            }
            for r in recettes
        ]

    # ── B5.3: Documents expirés → Dashboard alerte ─────────

    @avec_gestion_erreurs(default_return=[])
    @avec_session_db
    def documents_expires_alertes(self, jours_avant: int = 30, db: Session | None = None) -> list[dict]:
        """Liste les documents qui expirent bientôt ou sont déjà expirés.

        Args:
            jours_avant: Nombre de jours avant expiration pour alerter

        Returns:
            Liste de documents avec statut expiration
        """
        from src.core.models import DocumentFamille

        seuil = date.today() + timedelta(days=jours_avant)

        documents = (
            db.query(DocumentFamille)
            .filter(
                DocumentFamille.actif.is_(True),
                DocumentFamille.date_expiration.isnot(None),
                DocumentFamille.date_expiration <= seuil,
            )
            .order_by(DocumentFamille.date_expiration)
            .all()
        )

        return [
            {
                "id": d.id,
                "titre": d.titre,
                "categorie": d.categorie,
                "membre_famille": d.membre_famille,
                "date_expiration": str(d.date_expiration),
                "jours_restants": d.jours_avant_expiration,
                "est_expire": d.est_expire,
                "niveau": "critique" if d.est_expire else (
                    "urgent" if d.jours_avant_expiration and d.jours_avant_expiration <= 7 else "attention"
                ),
            }
            for d in documents
        ]

    @avec_gestion_erreurs(default_return={})
    @avec_session_db
    def entretien_echoue_vers_artisans(
        self,
        tache_id: int,
        db: Session | None = None,
    ) -> dict:
        """Propose des artisans adaptés pour une tâche d'entretien en échec."""
        from src.core.models.abonnements import Artisan
        from src.core.models.habitat import TacheEntretien

        tache = db.query(TacheEntretien).filter(TacheEntretien.id == tache_id).first()
        if not tache:
            return {}

        metiers = self._detecter_metiers_depuis_tache(tache)
        artisans: list[Artisan] = []
        for metier in metiers:
            artisans.extend(
                db.query(Artisan).filter(Artisan.metier.ilike(f"%{metier}%")).all()
            )

        if not artisans and "artisan multi-services" not in metiers:
            artisans = db.query(Artisan).filter(Artisan.metier.ilike("%multi%")).all()

        artisans_uniques = list({artisan.id: artisan for artisan in artisans}.values())
        artisans_tries = self._prioriser_artisans(artisans_uniques)

        return {
            "tache": {
                "id": tache.id,
                "nom": tache.nom,
                "categorie": tache.categorie,
                "piece": tache.piece,
            },
            "metiers_recommandes": metiers,
            "artisans": [
                {
                    "id": artisan.id,
                    "nom": artisan.nom,
                    "entreprise": artisan.entreprise,
                    "metier": artisan.metier,
                    "specialite": artisan.specialite,
                    "telephone": artisan.telephone,
                    "email": artisan.email,
                    "note": artisan.note,
                    "recommande": artisan.recommande,
                }
                for artisan in artisans_tries[:5]
            ],
            "nb_artisans": len(artisans_tries),
        }

    # ── B5.5: Entretien récurrent → Planning unifié ─────────

    @avec_gestion_erreurs(default_return=[])
    @avec_session_db
    def entretien_planning_unifie(self, nb_jours: int = 7, db: Session | None = None) -> list[dict]:
        """Récupère les tâches d'entretien planifiées pour les N prochains jours.

        Returns:
            Liste de tâches avec dates et priorités
        """
        from src.core.models import TacheEntretien

        seuil = date.today() + timedelta(days=nb_jours)
        aujourd_hui = date.today()

        taches = (
            db.query(TacheEntretien)
            .filter(
                TacheEntretien.prochaine_fois <= seuil,
                TacheEntretien.fait.is_(False),
            )
            .order_by(TacheEntretien.prochaine_fois)
            .all()
        )

        return [
            {
                "id": t.id,
                "nom": t.nom,
                "prochaine_fois": str(t.prochaine_fois),
                "en_retard": t.prochaine_fois < aujourd_hui if t.prochaine_fois else False,
                "jours_restants": (t.prochaine_fois - aujourd_hui).days if t.prochaine_fois else None,
                "type": "entretien",
            }
            for t in taches
        ]

    # ── B5.2: Budget anomalie → Notification ────────────────

    def verifier_anomalies_budget_et_notifier(self) -> list[dict]:
        """Vérifie les anomalies budgétaires et émet des événements.

        Returns:
            Liste des anomalies détectées
        """
        from src.services.ia.prevision_budget import obtenir_service_prevision_budget
        from src.services.core.events import obtenir_bus

        service = obtenir_service_prevision_budget()
        anomalies = service.detecter_anomalies_budget(seuil_pct=80)

        bus = obtenir_bus()
        for anomalie in anomalies:
            bus.emettre("budget.depassement", {
                "categorie": anomalie["categorie"],
                "depense": anomalie["depense"],
                "budget_ref": anomalie["budget_ref"],
                "pourcentage": anomalie["pourcentage"],
                "niveau": anomalie["niveau"],
            })

        return anomalies

    @avec_gestion_erreurs(default_return={})
    @avec_session_db
    def recolte_vers_stock_inventaire(
        self,
        element_id: int,
        quantite: float = 1.0,
        emplacement: str = "Frigo",
        db: Session | None = None,
    ) -> dict:
        """Ajoute automatiquement une récolte jardin à l'inventaire."""
        from src.core.models import ArticleInventaire, ElementJardin, Ingredient

        element = db.query(ElementJardin).filter(ElementJardin.id == element_id).first()
        if not element:
            return {}

        ingredient = (
            db.query(Ingredient)
            .filter(func.lower(Ingredient.nom) == element.nom.lower())
            .first()
        )

        if ingredient is None:
            categorie = "Légumes"
            if "fruit" in (element.type or "").lower():
                categorie = "Fruits"
            ingredient = Ingredient(nom=element.nom, categorie=categorie, unite="pcs")
            db.add(ingredient)
            db.flush()

        article = (
            db.query(ArticleInventaire)
            .filter(ArticleInventaire.ingredient_id == ingredient.id)
            .first()
        )

        quantite_ajoutee = max(0.1, quantite)
        action = "mise_a_jour"
        if article:
            article.quantite = float(article.quantite or 0) + quantite_ajoutee
            article.emplacement = article.emplacement or emplacement
        else:
            article = ArticleInventaire(
                ingredient_id=ingredient.id,
                quantite=quantite_ajoutee,
                quantite_min=1.0,
                emplacement=emplacement,
            )
            db.add(article)
            action = "creation"

        db.commit()
        db.refresh(article)

        return {
            "element_id": element.id,
            "element_nom": element.nom,
            "ingredient_id": ingredient.id,
            "article_inventaire_id": article.id,
            "quantite_ajoutee": quantite_ajoutee,
            "quantite_totale": float(article.quantite or 0),
            "emplacement": article.emplacement,
            "action": action,
        }

    @avec_gestion_erreurs(default_return={})
    @avec_session_db
    def anniversaire_vers_menu_festif(
        self,
        jours_horizon: int = 14,
        db: Session | None = None,
    ) -> dict:
        """Suggère un menu festif pour l'anniversaire le plus proche."""
        from src.core.models import AnniversaireFamille
        from src.core.models.recettes import Recette

        anniversaires = sorted(
            [a for a in db.query(AnniversaireFamille).all() if 0 <= a.jours_restants <= jours_horizon],
            key=lambda anniversaire: anniversaire.jours_restants,
        )
        if not anniversaires:
            return {}

        cible = anniversaires[0]
        recettes = (
            db.query(Recette)
            .filter(
                func.lower(Recette.nom).contains("gateau")
                | func.lower(Recette.nom).contains("gâteau")
                | func.lower(Recette.nom).contains("tarte")
                | func.lower(Recette.categorie).contains("dessert")
            )
            .limit(6)
            .all()
        )

        suggestions = [
            {
                "id": recette.id,
                "nom": recette.nom,
                "categorie": recette.categorie,
                "type_repas": recette.type_repas,
                "temps_total": recette.temps_total,
            }
            for recette in recettes
        ]
        if not suggestions:
            suggestions = [
                {"id": None, "nom": "Gâteau maison festif", "categorie": "Dessert", "type_repas": "dessert", "temps_total": 90},
                {"id": None, "nom": "Buffet apéritif familial", "categorie": "Plat", "type_repas": "dîner", "temps_total": 45},
            ]

        return {
            "anniversaire": {
                "id": cible.id,
                "nom_personne": cible.nom_personne,
                "jours_restants": cible.jours_restants,
                "age": cible.age,
            },
            "menu_festif": suggestions,
        }

    @avec_gestion_erreurs(default_return={})
    @avec_session_db
    def jalon_vers_evenement_familial(
        self,
        jalon_id: int,
        db: Session | None = None,
    ) -> dict:
        """Crée un événement familial à partir d'un jalon Jules."""
        from src.core.models.famille import EvenementFamilial, Jalon, ProfilEnfant

        jalon = db.query(Jalon).filter(Jalon.id == jalon_id).first()
        if not jalon:
            return {}

        enfant = db.query(ProfilEnfant).filter(ProfilEnfant.id == jalon.child_id).first()
        titre = f"Jalon Jules: {jalon.titre}"

        evenement = (
            db.query(EvenementFamilial)
            .filter(
                EvenementFamilial.titre == titre,
                EvenementFamilial.date_evenement == jalon.date_atteint,
                EvenementFamilial.type_evenement == "jalon_jules",
            )
            .first()
        )

        if evenement is None:
            evenement = EvenementFamilial(
                titre=titre,
                date_evenement=jalon.date_atteint,
                type_evenement="jalon_jules",
                recurrence="unique",
                notes=jalon.description or jalon.notes,
                participants=[enfant.name] if enfant else ["Jules"],
            )
            db.add(evenement)
            db.commit()
            db.refresh(evenement)

        return {
            "jalon_id": jalon.id,
            "evenement_id": evenement.id,
            "titre": evenement.titre,
            "date_evenement": evenement.date_evenement.isoformat(),
        }

    # ── B5.8: Météo → Entretien maison ──────────────────────

    @avec_gestion_erreurs(default_return=[])
    @avec_session_db
    def meteo_vers_entretien(self, conditions_meteo: dict, db: Session | None = None) -> list[dict]:
        """Génère des alertes entretien basées sur les conditions météo.

        Args:
            conditions_meteo: Dict avec temperature, vent, precipitations

        Returns:
            Liste d'alertes avec conseils
        """
        alertes = []
        temp = conditions_meteo.get("temperature", 15)
        vent = conditions_meteo.get("vent_kmh", 0)
        pluie = conditions_meteo.get("precipitations_mm", 0)

        if temp <= 0:
            alertes.append({
                "type": "gel",
                "message": "🥶 Gel annoncé ! Protéger les plantes, purger les tuyaux extérieurs.",
                "priorite": "haute",
                "domaine": "jardin",
            })
        if temp >= 35:
            alertes.append({
                "type": "canicule",
                "message": "🌡️ Canicule ! Arroser le jardin tôt/tard, fermer les volets.",
                "priorite": "haute",
                "domaine": "jardin",
            })
        if vent >= 80:
            alertes.append({
                "type": "vent_fort",
                "message": "💨 Vent fort ! Rentrer les meubles de jardin, vérifier les fixations.",
                "priorite": "moyenne",
                "domaine": "exterieur",
            })
        if pluie >= 50:
            alertes.append({
                "type": "pluie_forte",
                "message": "🌧️ Pluie forte ! Vérifier les gouttières et évacuations.",
                "priorite": "moyenne",
                "domaine": "maison",
            })

        return alertes


# ═══════════════════════════════════════════════════════════
# EVENT HANDLERS (subscribers)
# ═══════════════════════════════════════════════════════════


def _on_jardin_recolte(event: EvenementDomaine) -> None:
    """Handler: Quand une récolte jardin est validée → suggérer des recettes."""
    try:
        nom = event.data.get("nom", "")
        if not nom:
            return

        service = obtenir_service_bridges()
        recettes = service.recolte_vers_recettes(nom)

        if recettes:
            logger.info(
                f"🌱→🍽️ Récolte '{nom}' → {len(recettes)} recette(s) trouvée(s): "
                f"{', '.join(r['nom'] for r in recettes[:3])}"
            )
            # Émettre un événement pour notification
            from src.services.core.events import obtenir_bus
            obtenir_bus().emettre("bridge.recolte_recettes", {
                "ingredient": nom,
                "recettes": recettes[:5],
                "nb_recettes": len(recettes),
            })
    except Exception as e:
        logger.warning(f"Erreur bridge récolte→recettes: {e}")


def _on_budget_modifie(event: EvenementDomaine) -> None:
    """Handler: Quand le budget est modifié → vérifier les anomalies."""
    try:
        service = obtenir_service_bridges()
        anomalies = service.verifier_anomalies_budget_et_notifier()
        if anomalies:
            logger.info(f"💰 {len(anomalies)} anomalie(s) budget détectée(s)")
    except Exception as e:
        logger.warning(f"Erreur bridge budget→notification: {e}")


# ═══════════════════════════════════════════════════════════
# FACTORY
# ═══════════════════════════════════════════════════════════


@service_factory("bridges_inter_modules", tags={"bridges"})
def obtenir_service_bridges() -> BridgesInterModulesService:
    """Factory singleton."""
    return BridgesInterModulesService()



def enregistrer_bridges_subscribers() -> None:
    """Enregistre tous les subscribers de bridges inter-modules dans le bus."""
    from src.services.core.events import obtenir_bus

    bus = obtenir_bus()
    bus.souscrire("jardin.recolte", _on_jardin_recolte)
    bus.souscrire("budget.modifie", _on_budget_modifie)

    logger.info("✅ Bridges inter-modules enregistrés (jardin→recettes, budget→notification)")
