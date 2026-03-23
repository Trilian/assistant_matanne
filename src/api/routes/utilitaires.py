"""
Routes API pour les utilitaires.

CRUD pour: notes, journal de bord, contacts utiles, liens favoris,
mots de passe maison, relevés énergie.
"""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query

from src.api.dependencies import require_auth
from src.api.schemas.common import MessageResponse
from src.api.schemas.errors import (
    REPONSES_CRUD_CREATION,
    REPONSES_CRUD_ECRITURE,
    REPONSES_CRUD_LECTURE,
    REPONSES_CRUD_SUPPRESSION,
    REPONSES_LISTE,
)
from src.api.schemas.utilitaires import (
    ContactCreate,
    ContactPatch,
    EnergieCreate,
    EnergiePatch,
    JournalCreate,
    JournalPatch,
    LienCreate,
    LienPatch,
    MotDePasseCreate,
    MotDePassePatch,
    NoteCreate,
    NotePatch,
)
from src.api.utils import executer_async, executer_avec_session, gerer_exception_api

router = APIRouter(prefix="/api/v1/utilitaires", tags=["Utilitaires"])


# ═══════════════════════════════════════════════════════════
# NOTES
# ═══════════════════════════════════════════════════════════


@router.get("/notes", responses=REPONSES_LISTE)
@gerer_exception_api
async def lister_notes(
    categorie: str | None = Query(None),
    epingle: bool | None = Query(None),
    archive: bool = Query(False),
    search: str | None = Query(None),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Liste les notes mémo."""
    from src.core.models import NoteMemo

    def _query():
        with executer_avec_session() as session:
            query = session.query(NoteMemo)
            if categorie:
                query = query.filter(NoteMemo.categorie == categorie)
            if epingle is not None:
                query = query.filter(NoteMemo.epingle == epingle)
            query = query.filter(NoteMemo.archive == archive)
            if search:
                safe = search.replace("%", "\\%").replace("_", "\\_")
                query = query.filter(NoteMemo.titre.ilike(f"%{safe}%"))

            items = query.order_by(
                NoteMemo.epingle.desc(), NoteMemo.cree_le.desc()
            ).all()

            return {
                "items": [
                    {
                        "id": n.id,
                        "titre": n.titre,
                        "contenu": n.contenu,
                        "categorie": n.categorie,
                        "couleur": n.couleur,
                        "epingle": n.epingle,
                        "est_checklist": n.est_checklist,
                        "items_checklist": n.items_checklist,
                        "tags": n.tags or [],
                        "archive": n.archive,
                        "cree_le": n.cree_le.isoformat() if n.cree_le else None,
                    }
                    for n in items
                ],
            }

    return await executer_async(_query)


@router.post("/notes", responses=REPONSES_CRUD_CREATION)
@gerer_exception_api
async def creer_note(
    donnees: NoteCreate,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Crée une nouvelle note."""
    from src.core.models import NoteMemo

    def _create():
        with executer_avec_session() as session:
            note = NoteMemo(**donnees.model_dump())
            session.add(note)
            session.commit()
            session.refresh(note)
            return {
                "id": note.id,
                "titre": note.titre,
                "contenu": note.contenu,
                "categorie": note.categorie,
                "couleur": note.couleur,
                "epingle": note.epingle,
                "est_checklist": note.est_checklist,
                "tags": note.tags or [],
                "cree_le": note.cree_le.isoformat() if note.cree_le else None,
            }

    return await executer_async(_create)


@router.patch("/notes/{note_id}", responses=REPONSES_CRUD_ECRITURE)
@gerer_exception_api
async def modifier_note(
    note_id: int,
    patch: NotePatch,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Met à jour partiellement une note."""
    from src.core.models import NoteMemo

    def _update():
        with executer_avec_session() as session:
            note = session.query(NoteMemo).filter(NoteMemo.id == note_id).first()
            if not note:
                raise HTTPException(status_code=404, detail="Note non trouvée")

            updates = patch.model_dump(exclude_unset=True)
            if not updates:
                raise HTTPException(status_code=422, detail="Aucun champ à mettre à jour")

            for key, value in updates.items():
                setattr(note, key, value)
            session.commit()
            session.refresh(note)

            return {
                "id": note.id,
                "titre": note.titre,
                "contenu": note.contenu,
                "categorie": note.categorie,
                "couleur": note.couleur,
                "epingle": note.epingle,
                "archive": note.archive,
                "tags": note.tags or [],
            }

    return await executer_async(_update)


@router.delete("/notes/{note_id}", response_model=MessageResponse, responses=REPONSES_CRUD_SUPPRESSION)
@gerer_exception_api
async def supprimer_note(
    note_id: int,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Supprime une note."""
    from src.core.models import NoteMemo

    def _delete():
        with executer_avec_session() as session:
            note = session.query(NoteMemo).filter(NoteMemo.id == note_id).first()
            if not note:
                raise HTTPException(status_code=404, detail="Note non trouvée")
            session.delete(note)
            session.commit()
            return {"message": "Note supprimée", "id": note_id}

    return await executer_async(_delete)


# ═══════════════════════════════════════════════════════════
# JOURNAL DE BORD
# ═══════════════════════════════════════════════════════════


@router.get("/journal", responses=REPONSES_LISTE)
@gerer_exception_api
async def lister_journal(
    humeur: str | None = Query(None),
    limit: int = Query(30, ge=1, le=365),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Liste les entrées du journal de bord."""
    from src.core.models import EntreeJournal

    def _query():
        with executer_avec_session() as session:
            query = session.query(EntreeJournal)
            if humeur:
                query = query.filter(EntreeJournal.humeur == humeur)
            items = query.order_by(EntreeJournal.date_entree.desc()).limit(limit).all()
            return {
                "items": [
                    {
                        "id": j.id,
                        "date_entree": j.date_entree.isoformat() if j.date_entree else None,
                        "contenu": j.contenu,
                        "humeur": j.humeur,
                        "energie": j.energie,
                        "gratitudes": j.gratitudes or [],
                        "tags": j.tags or [],
                        "cree_le": j.cree_le.isoformat() if j.cree_le else None,
                    }
                    for j in items
                ],
            }

    return await executer_async(_query)


@router.post("/journal", responses=REPONSES_CRUD_CREATION)
@gerer_exception_api
async def creer_entree_journal(
    donnees: JournalCreate,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Crée une entrée dans le journal de bord."""
    from datetime import date as date_type

    from src.core.models import EntreeJournal

    def _create():
        with executer_avec_session() as session:
            entree = EntreeJournal(
                date_entree=date_type.fromisoformat(donnees.date_entree),
                contenu=donnees.contenu,
                humeur=donnees.humeur,
                energie=donnees.energie,
                gratitudes=donnees.gratitudes,
                tags=donnees.tags,
            )
            session.add(entree)
            session.commit()
            session.refresh(entree)
            return {
                "id": entree.id,
                "date_entree": entree.date_entree.isoformat(),
                "contenu": entree.contenu,
                "humeur": entree.humeur,
                "energie": entree.energie,
                "gratitudes": entree.gratitudes or [],
                "tags": entree.tags or [],
            }

    return await executer_async(_create)


@router.patch("/journal/{entree_id}", responses=REPONSES_CRUD_ECRITURE)
@gerer_exception_api
async def modifier_entree_journal(
    entree_id: int,
    patch: JournalPatch,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Met à jour partiellement une entrée journal."""
    from src.core.models import EntreeJournal

    def _update():
        with executer_avec_session() as session:
            entree = session.query(EntreeJournal).filter(EntreeJournal.id == entree_id).first()
            if not entree:
                raise HTTPException(status_code=404, detail="Entrée non trouvée")

            updates = patch.model_dump(exclude_unset=True)
            if not updates:
                raise HTTPException(status_code=422, detail="Aucun champ à mettre à jour")

            for key, value in updates.items():
                setattr(entree, key, value)
            session.commit()
            session.refresh(entree)

            return {
                "id": entree.id,
                "date_entree": entree.date_entree.isoformat() if entree.date_entree else None,
                "contenu": entree.contenu,
                "humeur": entree.humeur,
                "energie": entree.energie,
                "gratitudes": entree.gratitudes or [],
                "tags": entree.tags or [],
            }

    return await executer_async(_update)


@router.delete("/journal/{entree_id}", response_model=MessageResponse, responses=REPONSES_CRUD_SUPPRESSION)
@gerer_exception_api
async def supprimer_entree_journal(
    entree_id: int,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Supprime une entrée du journal."""
    from src.core.models import EntreeJournal

    def _delete():
        with executer_avec_session() as session:
            entree = session.query(EntreeJournal).filter(EntreeJournal.id == entree_id).first()
            if not entree:
                raise HTTPException(status_code=404, detail="Entrée non trouvée")
            session.delete(entree)
            session.commit()
            return {"message": "Entrée supprimée", "id": entree_id}

    return await executer_async(_delete)


# ═══════════════════════════════════════════════════════════
# CONTACTS UTILES
# ═══════════════════════════════════════════════════════════


@router.get("/contacts", responses=REPONSES_LISTE)
@gerer_exception_api
async def lister_contacts(
    categorie: str | None = Query(None),
    favori: bool | None = Query(None),
    search: str | None = Query(None),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Liste les contacts utiles."""
    from src.core.models import ContactUtile

    def _query():
        with executer_avec_session() as session:
            query = session.query(ContactUtile)
            if categorie:
                query = query.filter(ContactUtile.categorie == categorie)
            if favori is not None:
                query = query.filter(ContactUtile.favori == favori)
            if search:
                safe = search.replace("%", "\\%").replace("_", "\\_")
                query = query.filter(ContactUtile.nom.ilike(f"%{safe}%"))

            items = query.order_by(ContactUtile.favori.desc(), ContactUtile.nom).all()

            return {
                "items": [
                    {
                        "id": c.id,
                        "nom": c.nom,
                        "categorie": c.categorie,
                        "specialite": c.specialite,
                        "telephone": c.telephone,
                        "email": c.email,
                        "adresse": c.adresse,
                        "horaires": c.horaires,
                        "favori": c.favori,
                    }
                    for c in items
                ],
            }

    return await executer_async(_query)


@router.post("/contacts", responses=REPONSES_CRUD_CREATION)
@gerer_exception_api
async def creer_contact(
    donnees: ContactCreate,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Crée un nouveau contact utile."""
    from src.core.models import ContactUtile

    def _create():
        with executer_avec_session() as session:
            contact = ContactUtile(**donnees.model_dump())
            session.add(contact)
            session.commit()
            session.refresh(contact)
            return {
                "id": contact.id,
                "nom": contact.nom,
                "categorie": contact.categorie,
                "specialite": contact.specialite,
                "telephone": contact.telephone,
                "email": contact.email,
                "adresse": contact.adresse,
                "favori": contact.favori,
            }

    return await executer_async(_create)


@router.patch("/contacts/{contact_id}", responses=REPONSES_CRUD_ECRITURE)
@gerer_exception_api
async def modifier_contact(
    contact_id: int,
    patch: ContactPatch,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Met à jour partiellement un contact."""
    from src.core.models import ContactUtile

    def _update():
        with executer_avec_session() as session:
            contact = session.query(ContactUtile).filter(ContactUtile.id == contact_id).first()
            if not contact:
                raise HTTPException(status_code=404, detail="Contact non trouvé")

            updates = patch.model_dump(exclude_unset=True)
            if not updates:
                raise HTTPException(status_code=422, detail="Aucun champ à mettre à jour")

            for key, value in updates.items():
                setattr(contact, key, value)
            session.commit()
            session.refresh(contact)

            return {
                "id": contact.id,
                "nom": contact.nom,
                "categorie": contact.categorie,
                "specialite": contact.specialite,
                "telephone": contact.telephone,
                "email": contact.email,
                "adresse": contact.adresse,
                "favori": contact.favori,
            }

    return await executer_async(_update)


@router.delete("/contacts/{contact_id}", response_model=MessageResponse, responses=REPONSES_CRUD_SUPPRESSION)
@gerer_exception_api
async def supprimer_contact(
    contact_id: int,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Supprime un contact."""
    from src.core.models import ContactUtile

    def _delete():
        with executer_avec_session() as session:
            contact = session.query(ContactUtile).filter(ContactUtile.id == contact_id).first()
            if not contact:
                raise HTTPException(status_code=404, detail="Contact non trouvé")
            session.delete(contact)
            session.commit()
            return {"message": "Contact supprimé", "id": contact_id}

    return await executer_async(_delete)


# ═══════════════════════════════════════════════════════════
# LIENS FAVORIS
# ═══════════════════════════════════════════════════════════


@router.get("/liens", responses=REPONSES_LISTE)
@gerer_exception_api
async def lister_liens(
    categorie: str | None = Query(None),
    favori: bool | None = Query(None),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Liste les liens favoris."""
    from src.core.models import LienFavori

    def _query():
        with executer_avec_session() as session:
            query = session.query(LienFavori)
            if categorie:
                query = query.filter(LienFavori.categorie == categorie)
            if favori is not None:
                query = query.filter(LienFavori.favori == favori)

            items = query.order_by(LienFavori.favori.desc(), LienFavori.titre).all()
            return {
                "items": [
                    {
                        "id": l.id,
                        "titre": l.titre,
                        "url": l.url,
                        "categorie": l.categorie,
                        "description": l.description,
                        "tags": l.tags or [],
                        "favori": l.favori,
                    }
                    for l in items
                ],
            }

    return await executer_async(_query)


@router.post("/liens", responses=REPONSES_CRUD_CREATION)
@gerer_exception_api
async def creer_lien(
    donnees: LienCreate,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Crée un nouveau lien favori."""
    from src.core.models import LienFavori

    def _create():
        with executer_avec_session() as session:
            lien = LienFavori(**donnees.model_dump())
            session.add(lien)
            session.commit()
            session.refresh(lien)
            return {
                "id": lien.id,
                "titre": lien.titre,
                "url": lien.url,
                "categorie": lien.categorie,
                "description": lien.description,
                "tags": lien.tags or [],
                "favori": lien.favori,
            }

    return await executer_async(_create)


@router.patch("/liens/{lien_id}", responses=REPONSES_CRUD_ECRITURE)
@gerer_exception_api
async def modifier_lien(
    lien_id: int,
    patch: LienPatch,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Met à jour partiellement un lien."""
    from src.core.models import LienFavori

    def _update():
        with executer_avec_session() as session:
            lien = session.query(LienFavori).filter(LienFavori.id == lien_id).first()
            if not lien:
                raise HTTPException(status_code=404, detail="Lien non trouvé")

            updates = patch.model_dump(exclude_unset=True)
            if not updates:
                raise HTTPException(status_code=422, detail="Aucun champ à mettre à jour")

            for key, value in updates.items():
                setattr(lien, key, value)
            session.commit()
            session.refresh(lien)

            return {
                "id": lien.id,
                "titre": lien.titre,
                "url": lien.url,
                "categorie": lien.categorie,
                "tags": lien.tags or [],
                "favori": lien.favori,
            }

    return await executer_async(_update)


@router.delete("/liens/{lien_id}", response_model=MessageResponse, responses=REPONSES_CRUD_SUPPRESSION)
@gerer_exception_api
async def supprimer_lien(
    lien_id: int,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Supprime un lien favori."""
    from src.core.models import LienFavori

    def _delete():
        with executer_avec_session() as session:
            lien = session.query(LienFavori).filter(LienFavori.id == lien_id).first()
            if not lien:
                raise HTTPException(status_code=404, detail="Lien non trouvé")
            session.delete(lien)
            session.commit()
            return {"message": "Lien supprimé", "id": lien_id}

    return await executer_async(_delete)


# ═══════════════════════════════════════════════════════════
# MOTS DE PASSE MAISON
# ═══════════════════════════════════════════════════════════


@router.get("/passwords", responses=REPONSES_LISTE)
@gerer_exception_api
async def lister_mots_de_passe(
    categorie: str | None = Query(None),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Liste les mots de passe maison (valeurs chiffrées)."""
    from src.core.models import MotDePasseMaison

    def _query():
        with executer_avec_session() as session:
            query = session.query(MotDePasseMaison)
            if categorie:
                query = query.filter(MotDePasseMaison.categorie == categorie)

            items = query.order_by(MotDePasseMaison.nom).all()
            return {
                "items": [
                    {
                        "id": m.id,
                        "nom": m.nom,
                        "categorie": m.categorie,
                        "identifiant": m.identifiant,
                        "valeur_chiffree": m.valeur_chiffree,
                        "notes": m.notes,
                    }
                    for m in items
                ],
            }

    return await executer_async(_query)


@router.post("/passwords", responses=REPONSES_CRUD_CREATION)
@gerer_exception_api
async def creer_mot_de_passe(
    donnees: MotDePasseCreate,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Crée un nouveau mot de passe maison."""
    from src.core.models import MotDePasseMaison

    def _create():
        with executer_avec_session() as session:
            mdp = MotDePasseMaison(
                nom=donnees.nom,
                categorie=donnees.categorie,
                identifiant=donnees.identifiant,
                valeur_chiffree=donnees.valeur,
                notes=donnees.notes,
            )
            session.add(mdp)
            session.commit()
            session.refresh(mdp)
            return {
                "id": mdp.id,
                "nom": mdp.nom,
                "categorie": mdp.categorie,
                "identifiant": mdp.identifiant,
                "valeur_chiffree": mdp.valeur_chiffree,
                "notes": mdp.notes,
            }

    return await executer_async(_create)


@router.patch("/passwords/{mdp_id}", responses=REPONSES_CRUD_ECRITURE)
@gerer_exception_api
async def modifier_mot_de_passe(
    mdp_id: int,
    patch: MotDePassePatch,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Met à jour un mot de passe maison."""
    from src.core.models import MotDePasseMaison

    def _update():
        with executer_avec_session() as session:
            mdp = session.query(MotDePasseMaison).filter(MotDePasseMaison.id == mdp_id).first()
            if not mdp:
                raise HTTPException(status_code=404, detail="Mot de passe non trouvé")

            updates = patch.model_dump(exclude_unset=True)
            if not updates:
                raise HTTPException(status_code=422, detail="Aucun champ à mettre à jour")

            # Le champ "valeur" dans le schema → "valeur_chiffree" dans le modèle
            if "valeur" in updates:
                updates["valeur_chiffree"] = updates.pop("valeur")

            for key, value in updates.items():
                setattr(mdp, key, value)
            session.commit()
            session.refresh(mdp)

            return {
                "id": mdp.id,
                "nom": mdp.nom,
                "categorie": mdp.categorie,
                "identifiant": mdp.identifiant,
                "valeur_chiffree": mdp.valeur_chiffree,
                "notes": mdp.notes,
            }

    return await executer_async(_update)


@router.delete("/passwords/{mdp_id}", response_model=MessageResponse, responses=REPONSES_CRUD_SUPPRESSION)
@gerer_exception_api
async def supprimer_mot_de_passe(
    mdp_id: int,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Supprime un mot de passe maison."""
    from src.core.models import MotDePasseMaison

    def _delete():
        with executer_avec_session() as session:
            mdp = session.query(MotDePasseMaison).filter(MotDePasseMaison.id == mdp_id).first()
            if not mdp:
                raise HTTPException(status_code=404, detail="Mot de passe non trouvé")
            session.delete(mdp)
            session.commit()
            return {"message": "Mot de passe supprimé", "id": mdp_id}

    return await executer_async(_delete)


# ═══════════════════════════════════════════════════════════
# ÉNERGIE
# ═══════════════════════════════════════════════════════════


@router.get("/energie", responses=REPONSES_LISTE)
@gerer_exception_api
async def lister_releves_energie(
    type_energie: str | None = Query(None, description="electricite, gaz, eau"),
    annee: int | None = Query(None),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Liste les relevés énergie."""
    from src.core.models import ReleveEnergie

    def _query():
        with executer_avec_session() as session:
            query = session.query(ReleveEnergie)
            if type_energie:
                query = query.filter(ReleveEnergie.type_energie == type_energie)
            if annee:
                query = query.filter(ReleveEnergie.annee == annee)

            items = query.order_by(
                ReleveEnergie.annee.desc(), ReleveEnergie.mois.desc()
            ).all()

            return {
                "items": [
                    {
                        "id": r.id,
                        "type_energie": r.type_energie,
                        "mois": r.mois,
                        "annee": r.annee,
                        "valeur_compteur": float(r.valeur_compteur) if r.valeur_compteur else None,
                        "consommation": float(r.consommation) if r.consommation else None,
                        "unite": r.unite,
                        "montant": float(r.montant) if r.montant else None,
                        "notes": r.notes,
                    }
                    for r in items
                ],
            }

    return await executer_async(_query)


@router.post("/energie", responses=REPONSES_CRUD_CREATION)
@gerer_exception_api
async def creer_releve_energie(
    donnees: EnergieCreate,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Crée un relevé énergie."""
    from src.core.models import ReleveEnergie

    def _create():
        with executer_avec_session() as session:
            releve = ReleveEnergie(**donnees.model_dump())
            session.add(releve)
            session.commit()
            session.refresh(releve)
            return {
                "id": releve.id,
                "type_energie": releve.type_energie,
                "mois": releve.mois,
                "annee": releve.annee,
                "consommation": float(releve.consommation) if releve.consommation else None,
                "montant": float(releve.montant) if releve.montant else None,
                "unite": releve.unite,
            }

    return await executer_async(_create)


@router.patch("/energie/{releve_id}", responses=REPONSES_CRUD_ECRITURE)
@gerer_exception_api
async def modifier_releve_energie(
    releve_id: int,
    patch: EnergiePatch,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Met à jour un relevé énergie."""
    from src.core.models import ReleveEnergie

    def _update():
        with executer_avec_session() as session:
            releve = session.query(ReleveEnergie).filter(ReleveEnergie.id == releve_id).first()
            if not releve:
                raise HTTPException(status_code=404, detail="Relevé non trouvé")

            updates = patch.model_dump(exclude_unset=True)
            if not updates:
                raise HTTPException(status_code=422, detail="Aucun champ à mettre à jour")

            for key, value in updates.items():
                setattr(releve, key, value)
            session.commit()
            session.refresh(releve)

            return {
                "id": releve.id,
                "type_energie": releve.type_energie,
                "mois": releve.mois,
                "annee": releve.annee,
                "consommation": float(releve.consommation) if releve.consommation else None,
                "montant": float(releve.montant) if releve.montant else None,
            }

    return await executer_async(_update)


@router.delete("/energie/{releve_id}", response_model=MessageResponse, responses=REPONSES_CRUD_SUPPRESSION)
@gerer_exception_api
async def supprimer_releve_energie(
    releve_id: int,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Supprime un relevé énergie."""
    from src.core.models import ReleveEnergie

    def _delete():
        with executer_avec_session() as session:
            releve = session.query(ReleveEnergie).filter(ReleveEnergie.id == releve_id).first()
            if not releve:
                raise HTTPException(status_code=404, detail="Relevé non trouvé")
            session.delete(releve)
            session.commit()
            return {"message": "Relevé supprimé", "id": releve_id}

    return await executer_async(_delete)
