"""Mixin bridges maison — méthodes inter-modules liées à la maison."""

from __future__ import annotations

from datetime import date, timedelta
from typing import TYPE_CHECKING

from sqlalchemy import func
from sqlalchemy.orm import Session

from src.core.decorators import avec_gestion_erreurs, avec_session_db

if TYPE_CHECKING:
    pass


class MaisonBridgesMixin:
    """Bridges inter-modules liés à la maison (entretien, jardin, énergie, habitat)."""

    # ── Helpers artisans ───────────────────────────────────

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

    # ── Entretien échoué → Artisans ────────────────────────

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
            artisans.extend(db.query(Artisan).filter(Artisan.metier.ilike(f"%{metier}%")).all())

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

    # ── B5.5: Entretien récurrent → Planning unifié ────────

    @avec_gestion_erreurs(default_return=[])
    @avec_session_db
    def entretien_planning_unifie(self, nb_jours: int = 7, db: Session | None = None) -> list[dict]:
        """Récupère les tâches d'entretien planifiées pour les N prochains jours."""
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
                "jours_restants": (t.prochaine_fois - aujourd_hui).days
                if t.prochaine_fois
                else None,
                "type": "entretien",
            }
            for t in taches
        ]

    # ── B5.6: Récolte → Stock inventaire ───────────────────

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
            db.query(Ingredient).filter(func.lower(Ingredient.nom) == element.nom.lower()).first()
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

    # ── IM-5: Énergie HC/HP → Planning machines ───────────

    @avec_gestion_erreurs(default_return={})
    def energie_hc_hp_vers_planning_machines(self) -> dict:
        """IM-5: Propose la meilleure fenêtre HC/HP pour lancer les machines."""
        from src.services.maison.inter_modules.inter_module_energie_cuisine import (
            obtenir_service_energie_cuisine_interaction,
        )

        service = obtenir_service_energie_cuisine_interaction()
        recommandations = service.obtenir_suggestions_heures_creuses()
        return {
            "interaction": "IM-5",
            "description": "Tarif HC/HP vers planning machines",
            **recommandations,
        }

    # ── B5.8: Météo → Entretien maison ────────────────────

    @avec_gestion_erreurs(default_return=[])
    @avec_session_db
    def meteo_vers_entretien(self, conditions_meteo: dict, db: Session | None = None) -> list[dict]:
        """Génère des alertes entretien basées sur les conditions météo."""
        alertes = []
        temp = conditions_meteo.get("temperature", 15)
        vent = conditions_meteo.get("vent_kmh", 0)
        pluie = conditions_meteo.get("precipitations_mm", 0)

        if temp <= 0:
            alertes.append(
                {
                    "type": "gel",
                    "message": "🥶 Gel annoncé ! Protéger les plantes, purger les tuyaux extérieurs.",
                    "priorite": "haute",
                    "domaine": "jardin",
                }
            )
        if temp >= 35:
            alertes.append(
                {
                    "type": "canicule",
                    "message": "🌡️ Canicule ! Arroser le jardin tôt/tard, fermer les volets.",
                    "priorite": "haute",
                    "domaine": "jardin",
                }
            )
        if vent >= 80:
            alertes.append(
                {
                    "type": "vent_fort",
                    "message": "💨 Vent fort ! Rentrer les meubles de jardin, vérifier les fixations.",
                    "priorite": "moyenne",
                    "domaine": "exterieur",
                }
            )
        if pluie >= 50:
            alertes.append(
                {
                    "type": "pluie_forte",
                    "message": "🌧️ Pluie forte ! Vérifier les gouttières et évacuations.",
                    "priorite": "moyenne",
                    "domaine": "maison",
                }
            )

        return alertes

    # ── I5: Entretien terminé → Fiche saisonnière ─────────

    @avec_gestion_erreurs(default_return={})
    @avec_session_db
    def synchroniser_entretien_termine_vers_fiche(
        self,
        tache_id: int,
        db: Session | None = None,
    ) -> dict:
        """I5: met à jour la fiche d'entretien après validation d'une tâche."""
        from src.core.models.habitat import TacheEntretien
        from src.core.models.maison_extensions import EntretienSaisonnier

        tache = db.query(TacheEntretien).filter(TacheEntretien.id == tache_id).first()
        if not tache:
            return {}

        date_realisation = tache.derniere_fois or date.today()
        tokens = [
            mot for mot in (tache.nom or "").lower().replace("-", " ").split() if len(mot) >= 4
        ]
        fiches = db.query(EntretienSaisonnier).all()
        fiches_cibles = [
            fiche
            for fiche in fiches
            if fiche.nom and any(token in fiche.nom.lower() for token in tokens)
        ]

        if not fiches_cibles:
            mois = date_realisation.month
            if mois in {12, 1, 2}:
                saison = "hiver"
            elif mois in {3, 4, 5}:
                saison = "printemps"
            elif mois in {6, 7, 8}:
                saison = "ete"
            else:
                saison = "automne"

            categorie = (tache.categorie or "entretien").lower()
            if categorie not in {
                "chauffage",
                "plomberie",
                "toiture",
                "jardin",
                "piscine",
                "securite",
            }:
                categorie = (
                    "securite"
                    if "secur" in categorie
                    else "jardin"
                    if "jardin" in categorie
                    else "chauffage"
                )

            fiche = EntretienSaisonnier(
                nom=tache.nom,
                categorie=categorie,
                saison=saison,
                frequence="annuel",
                alerte_active=True,
            )
            db.add(fiche)
            db.flush()
            fiches_cibles = [fiche]

        correspondance_frequences = {
            "hebdomadaire": 7,
            "mensuel": 30,
            "trimestriel": 90,
            "semestriel": 180,
            "annuel": 365,
        }

        for fiche in fiches_cibles:
            fiche.date_derniere_realisation = date_realisation
            fiche.fait_cette_annee = date_realisation.year == date.today().year
            nb_jours = correspondance_frequences.get((fiche.frequence or "annuel").lower(), 365)
            fiche.date_prochaine = date_realisation + timedelta(days=nb_jours)
            note_auto = f"Mis à jour automatiquement depuis la tâche #{tache.id} ({tache.nom})"
            fiche.notes = note_auto if not fiche.notes else f"{fiche.notes}\n{note_auto}"

        db.commit()

        return {
            "tache_id": tache.id,
            "nb_fiches_mises_a_jour": len(fiches_cibles),
            "date_realisation": date_realisation.isoformat(),
            "message": f"{len(fiches_cibles)} fiche(s) d'entretien synchronisée(s).",
        }

    # ── P3-A4: Widget veille immobilière ───────────────────

    @avec_gestion_erreurs(default_return={})
    @avec_session_db
    def widget_veille_immo(self, db: Session | None = None) -> dict:
        """P3-A4: Données pour le widget veille immobilière du dashboard."""
        from src.core.models.habitat_projet import AnnonceHabitat

        annonces = db.query(AnnonceHabitat).order_by(AnnonceHabitat.id.desc()).limit(5).all()
        nb_total = db.query(func.count(AnnonceHabitat.id)).scalar() or 0

        annonces_liste = [
            {
                "id": a.id,
                "titre": a.titre or "",
                "prix": float(a.prix) if a.prix else 0,
                "surface_m2": float(a.surface_m2) if a.surface_m2 else None,
                "ville": a.ville or "",
                "score_pertinence": float(a.score_pertinence) if a.score_pertinence else None,
                "url_source": a.url_source,
            }
            for a in annonces
        ]

        prix_moyen_val = db.query(func.avg(AnnonceHabitat.prix)).scalar()
        prix_moyen = round(float(prix_moyen_val), 0) if prix_moyen_val else None

        return {
            "dernieres_annonces": annonces_liste,
            "nb_annonces_total": nb_total,
            "prix_moyen": prix_moyen,
            "tendance_prix_pct": None,
        }

    # ── P3-A5: Widget saison jardin ────────────────────────

    @avec_gestion_erreurs(default_return={})
    @avec_session_db
    def widget_saison_jardin(self, db: Session | None = None) -> dict:
        """P3-A5: Données saisonnières du jardin pour le widget dashboard."""
        from src.core.models.maison import ElementJardin

        aujourd_hui = date.today()
        mois = aujourd_hui.month
        saison_map = {
            1: "hiver",
            2: "hiver",
            3: "printemps",
            4: "printemps",
            5: "printemps",
            6: "été",
            7: "été",
            8: "été",
            9: "automne",
            10: "automne",
            11: "automne",
            12: "hiver",
        }
        saison = saison_map[mois]

        plantes = db.query(ElementJardin).filter(ElementJardin.statut != "retire").all()

        activites = []
        prochaines_recoltes = []

        for plante in plantes:
            if plante.statut == "plante" or plante.statut == "actif":
                activites.append(
                    {
                        "element": plante.nom,
                        "type_activite": "arrosage",
                        "priorite": "haute" if saison in ("été", "printemps") else "normale",
                        "conseil": f"Arroser {plante.nom} régulièrement" if saison == "été" else "",
                    }
                )

            if plante.date_recolte_prevue and plante.date_recolte_prevue >= aujourd_hui:
                jours_restants = (plante.date_recolte_prevue - aujourd_hui).days
                prochaines_recoltes.append(
                    {
                        "element": plante.nom,
                        "date_recolte": plante.date_recolte_prevue.isoformat(),
                        "jours_restants": jours_restants,
                    }
                )

        prochaines_recoltes.sort(key=lambda x: x["jours_restants"])

        return {
            "saison": saison,
            "activites": activites,
            "nb_plantes_actives": len(plantes),
            "prochaines_recoltes": prochaines_recoltes[:5],
        }

    # ── P3-A6: Activités Jules au potager ──────────────────

    @avec_gestion_erreurs(default_return={})
    @avec_session_db
    def activites_jules_potager(self, db: Session | None = None) -> dict:
        """P3-A6: Suggère des activités jardinage adaptées à Jules."""
        from src.core.models.famille import ProfilEnfant
        from src.core.models.maison import ElementJardin

        jules = db.query(ProfilEnfant).filter(ProfilEnfant.actif.is_(True)).first()
        age_mois = None
        if jules and jules.date_of_birth:
            delta = date.today() - jules.date_of_birth
            age_mois = delta.days // 30

        plantes = db.query(ElementJardin).filter(ElementJardin.statut != "retire").all()
        plantes_noms = [p.nom for p in plantes]

        activites = []
        for plante in plantes:
            if plante.statut in ("plante", "actif"):
                activites.append(
                    {
                        "activite": f"Arroser {plante.nom}",
                        "difficulte": "facile",
                        "duree_minutes": 10,
                        "description": f"Arroser doucement {plante.nom} avec un petit arrosoir",
                    }
                )
            if (
                plante.date_recolte_prevue
                and plante.date_recolte_prevue <= date.today() + timedelta(days=7)
            ):
                activites.append(
                    {
                        "activite": f"Récolter {plante.nom}",
                        "difficulte": "facile",
                        "duree_minutes": 15,
                        "description": f"Cueillir {plante.nom} ensemble — montrer les couleurs et les formes",
                    }
                )

        activites.append(
            {
                "activite": "Observer les insectes",
                "difficulte": "facile",
                "duree_minutes": 10,
                "description": "Chercher et observer les insectes dans le jardin",
            }
        )

        return {
            "activites": activites,
            "plantes_disponibles": plantes_noms,
            "age_jules_mois": age_mois,
        }
