"""
Routes API pour les utilitaires.

CRUD pour: notes, journal de bord, contacts utiles, liens favoris,
mots de passe maison, relevÃ©s Ã©nergie.
"""

import json
from typing import Any, Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

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
    MinuteurCreate,
    MinuteurPatch,
    MotDePasseCreate,
    MotDePassePatch,
    NoteCreate,
    NotePatch,
)
from src.api.utils import executer_async, executer_avec_session, gerer_exception_api

router = APIRouter(prefix="/api/v1/utilitaires", tags=["Utilitaires"])

HistoriqueChatItem = dict[str, str]


def _chiffrer_valeur_mot_de_passe(valeur: str) -> str:
    """Chiffre une valeur sensible avant stockage en base."""
    from src.api.auth import _obtenir_api_secret
    from src.services.utilitaires import obtenir_mots_de_passe_service

    return obtenir_mots_de_passe_service().chiffrer(valeur, _obtenir_api_secret())


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# CHAT IA MULTI-CONTEXTE
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class MessageChatRequest(BaseModel):
    """RequÃªte de message chat."""

    message: str = Field(..., min_length=1, max_length=2000, description="Message de l'utilisateur")
    contexte: Literal["cuisine", "famille", "maison", "budget", "general"] = Field(
        default="general", description="Contexte du chat"
    )
    historique: list[HistoriqueChatItem] = Field(
        default_factory=list, description="Messages prÃ©cÃ©dents [{role, contenu}]"
    )


@router.post("/chat/message")
@gerer_exception_api
async def envoyer_message_chat(
    payload: MessageChatRequest,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Envoie un message au chat IA et retourne la rÃ©ponse."""
    from src.services.utilitaires.chat_ai import obtenir_chat_ai_service

    def _query():
        service = obtenir_chat_ai_service()
        reponse = service.envoyer_message(
            message=payload.message,
            contexte=payload.contexte,
            historique=payload.historique if payload.historique else None,
        )
        return reponse

    reponse = await executer_async(_query)

    return {
        "reponse": reponse or "DÃ©solÃ©, je n'ai pas pu gÃ©nÃ©rer de rÃ©ponse. RÃ©essayez.",
        "contexte": payload.contexte,
    }


@router.post("/chat/message/stream")
@gerer_exception_api
async def streamer_message_chat(
    payload: MessageChatRequest,
    user: dict[str, Any] = Depends(require_auth),
) -> StreamingResponse:
    """Diffuse la réponse du chat IA via SSE pour un rendu progressif."""
    from src.services.utilitaires.chat_ai import obtenir_chat_ai_service

    def _format_sse(data: dict[str, Any]) -> str:
        return f"data: {json.dumps(data, ensure_ascii=False)}\n\n"

    def _stream():
        service = obtenir_chat_ai_service()
        a_emis_du_contenu = False

        try:
            for chunk in service.streamer_message(
                message=payload.message,
                contexte=payload.contexte,
                historique=payload.historique if payload.historique else None,
            ):
                if not chunk:
                    continue

                a_emis_du_contenu = True
                yield _format_sse(
                    {
                        "type": "chunk",
                        "content": chunk,
                        "contexte": payload.contexte,
                    }
                )

            if not a_emis_du_contenu:
                reponse = service.envoyer_message(
                    message=payload.message,
                    contexte=payload.contexte,
                    historique=payload.historique if payload.historique else None,
                )
                if reponse:
                    yield _format_sse(
                        {
                            "type": "chunk",
                            "content": reponse,
                            "contexte": payload.contexte,
                        }
                    )

            yield _format_sse({"type": "done", "contexte": payload.contexte})
        except Exception as exc:
            yield _format_sse(
                {
                    "type": "error",
                    "message": str(exc) or "Erreur streaming chat IA",
                    "contexte": payload.contexte,
                }
            )

    return StreamingResponse(
        _stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/chat/actions-rapides")
@gerer_exception_api
async def obtenir_actions_rapides_chat(
    contexte: Literal["cuisine", "famille", "maison", "budget", "general"] = Query(
        "general", description="Contexte du chat"
    ),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Retourne les suggestions d'actions rapides pour un contexte."""
    from src.services.utilitaires.chat_ai import obtenir_chat_ai_service

    service = obtenir_chat_ai_service()
    actions = service.obtenir_actions_rapides(contexte)

    return {"contexte": contexte, "actions": actions}


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# NOTES
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@router.get("/notes", responses=REPONSES_LISTE)
@gerer_exception_api
async def lister_notes(
    categorie: str | None = Query(None),
    tag: str | None = Query(None),
    epingle: bool | None = Query(None),
    archive: bool = Query(False),
    search: str | None = Query(None),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Liste les notes mÃ©mo."""
    from src.core.models import NoteMemo

    def _query():
        safe_tag = tag.strip().lower() if tag else None
        with executer_avec_session() as session:
            query = session.query(NoteMemo)
            if categorie:
                query = query.filter(NoteMemo.categorie == categorie)
            if safe_tag:
                query = query.filter(NoteMemo.tags.isnot(None))
            if epingle is not None:
                query = query.filter(NoteMemo.epingle == epingle)
            query = query.filter(NoteMemo.archive == archive)
            if search:
                safe = search.replace("%", "\\%").replace("_", "\\_")
                query = query.filter(NoteMemo.titre.ilike(f"%{safe}%"))

            items = query.order_by(
                NoteMemo.epingle.desc(), NoteMemo.cree_le.desc()
            ).all()

            if safe_tag:
                items = [
                    n for n in items
                    if any(
                        str(t).strip().lower() == safe_tag
                        for t in (n.tags if isinstance(n.tags, list) else [])
                    )
                ]

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


@router.get("/notes/tags", responses=REPONSES_LISTE)
@gerer_exception_api
async def lister_tags_notes(
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Retourne le catalogue de tags disponibles pour les notes."""
    from src.core.models import NoteMemo

    def _query():
        with executer_avec_session() as session:
            rows = session.query(NoteMemo.tags).filter(NoteMemo.archive == False).all()  # noqa: E712
            compteur: dict[str, int] = {}
            for (tags,) in rows:
                tags_liste = tags if isinstance(tags, list) else []
                for tag in tags_liste:
                    valeur = str(tag).strip()
                    if not valeur:
                        continue
                    compteur[valeur] = compteur.get(valeur, 0) + 1

            items = [
                {"tag": tag, "count": count}
                for tag, count in sorted(compteur.items(), key=lambda item: (-item[1], item[0].lower()))
            ]
            return {"items": items, "total": len(items)}

    return await executer_async(_query)


@router.post("/notes", responses=REPONSES_CRUD_CREATION)
@gerer_exception_api
async def creer_note(
    donnees: NoteCreate,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """CrÃ©e une nouvelle note."""
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
    """Met Ã  jour partiellement une note."""
    from src.core.models import NoteMemo

    def _update():
        with executer_avec_session() as session:
            note = session.query(NoteMemo).filter(NoteMemo.id == note_id).first()
            if not note:
                raise HTTPException(status_code=404, detail="Note non trouvÃ©e")

            updates = patch.model_dump(exclude_unset=True)
            if not updates:
                raise HTTPException(status_code=422, detail="Aucun champ Ã  mettre Ã  jour")

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
                raise HTTPException(status_code=404, detail="Note non trouvÃ©e")
            session.delete(note)
            session.commit()
            return {"message": "Note supprimÃ©e", "id": note_id}

    return await executer_async(_delete)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# JOURNAL DE BORD
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@router.get("/journal", responses=REPONSES_LISTE)
@gerer_exception_api
async def lister_journal(
    humeur: str | None = Query(None),
    limit: int = Query(30, ge=1, le=365),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Liste les entrÃ©es du journal de bord."""
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
    """CrÃ©e une entrÃ©e dans le journal de bord."""
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
    """Met Ã  jour partiellement une entrÃ©e journal."""
    from src.core.models import EntreeJournal

    def _update():
        with executer_avec_session() as session:
            entree = session.query(EntreeJournal).filter(EntreeJournal.id == entree_id).first()
            if not entree:
                raise HTTPException(status_code=404, detail="EntrÃ©e non trouvÃ©e")

            updates = patch.model_dump(exclude_unset=True)
            if not updates:
                raise HTTPException(status_code=422, detail="Aucun champ Ã  mettre Ã  jour")

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
    """Supprime une entrÃ©e du journal."""
    from src.core.models import EntreeJournal

    def _delete():
        with executer_avec_session() as session:
            entree = session.query(EntreeJournal).filter(EntreeJournal.id == entree_id).first()
            if not entree:
                raise HTTPException(status_code=404, detail="EntrÃ©e non trouvÃ©e")
            session.delete(entree)
            session.commit()
            return {"message": "EntrÃ©e supprimÃ©e", "id": entree_id}

    return await executer_async(_delete)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# CONTACTS UTILES
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


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
    """CrÃ©e un nouveau contact utile."""
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
    """Met Ã  jour partiellement un contact."""
    from src.core.models import ContactUtile

    def _update():
        with executer_avec_session() as session:
            contact = session.query(ContactUtile).filter(ContactUtile.id == contact_id).first()
            if not contact:
                raise HTTPException(status_code=404, detail="Contact non trouvÃ©")

            updates = patch.model_dump(exclude_unset=True)
            if not updates:
                raise HTTPException(status_code=422, detail="Aucun champ Ã  mettre Ã  jour")

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
                raise HTTPException(status_code=404, detail="Contact non trouvÃ©")
            session.delete(contact)
            session.commit()
            return {"message": "Contact supprimÃ©", "id": contact_id}

    return await executer_async(_delete)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# LIENS FAVORIS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


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
    """CrÃ©e un nouveau lien favori."""
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
    """Met Ã  jour partiellement un lien."""
    from src.core.models import LienFavori

    def _update():
        with executer_avec_session() as session:
            lien = session.query(LienFavori).filter(LienFavori.id == lien_id).first()
            if not lien:
                raise HTTPException(status_code=404, detail="Lien non trouvÃ©")

            updates = patch.model_dump(exclude_unset=True)
            if not updates:
                raise HTTPException(status_code=422, detail="Aucun champ Ã  mettre Ã  jour")

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
                raise HTTPException(status_code=404, detail="Lien non trouvÃ©")
            session.delete(lien)
            session.commit()
            return {"message": "Lien supprimÃ©", "id": lien_id}

    return await executer_async(_delete)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# MOTS DE PASSE MAISON
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@router.get("/passwords", responses=REPONSES_LISTE)
@gerer_exception_api
async def lister_mots_de_passe(
    categorie: str | None = Query(None),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Liste les mots de passe maison (valeurs chiffrÃ©es)."""
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
    """CrÃ©e un nouveau mot de passe maison."""
    from src.core.models import MotDePasseMaison

    def _create():
        with executer_avec_session() as session:
            mdp = MotDePasseMaison(
                nom=donnees.nom,
                categorie=donnees.categorie,
                identifiant=donnees.identifiant,
                valeur_chiffree=_chiffrer_valeur_mot_de_passe(donnees.valeur),
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
    """Met Ã  jour un mot de passe maison."""
    from src.core.models import MotDePasseMaison

    def _update():
        with executer_avec_session() as session:
            mdp = session.query(MotDePasseMaison).filter(MotDePasseMaison.id == mdp_id).first()
            if not mdp:
                raise HTTPException(status_code=404, detail="Mot de passe non trouvÃ©")

            updates = patch.model_dump(exclude_unset=True)
            if not updates:
                raise HTTPException(status_code=422, detail="Aucun champ Ã  mettre Ã  jour")

            # Le champ "valeur" dans le schéma correspond à une valeur claire,
            # il doit donc être chiffré avant stockage dans le modèle.
            if "valeur" in updates:
                updates["valeur_chiffree"] = _chiffrer_valeur_mot_de_passe(updates.pop("valeur"))

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
                raise HTTPException(status_code=404, detail="Mot de passe non trouvÃ©")
            session.delete(mdp)
            session.commit()
            return {"message": "Mot de passe supprimÃ©", "id": mdp_id}

    return await executer_async(_delete)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# Ã‰NERGIE
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@router.get("/energie", responses=REPONSES_LISTE)
@gerer_exception_api
async def lister_releves_energie(
    type_energie: str | None = Query(None, description="electricite, gaz, eau"),
    annee: int | None = Query(None),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Liste les relevÃ©s Ã©nergie."""
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
    """CrÃ©e un relevÃ© Ã©nergie."""
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
    """Met Ã  jour un relevÃ© Ã©nergie."""
    from src.core.models import ReleveEnergie

    def _update():
        with executer_avec_session() as session:
            releve = session.query(ReleveEnergie).filter(ReleveEnergie.id == releve_id).first()
            if not releve:
                raise HTTPException(status_code=404, detail="RelevÃ© non trouvÃ©")

            updates = patch.model_dump(exclude_unset=True)
            if not updates:
                raise HTTPException(status_code=422, detail="Aucun champ Ã  mettre Ã  jour")

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
    """Supprime un relevÃ© Ã©nergie."""
    from src.core.models import ReleveEnergie

    def _delete():
        with executer_avec_session() as session:
            releve = session.query(ReleveEnergie).filter(ReleveEnergie.id == releve_id).first()
            if not releve:
                raise HTTPException(status_code=404, detail="RelevÃ© non trouvÃ©")
            session.delete(releve)
            session.commit()
            return {"message": "RelevÃ© supprimÃ©", "id": releve_id}

    return await executer_async(_delete)


# ═══════════════════════════════════════════════════════════
# MINUTEUR — Sessions de minuterie persistées
# ═══════════════════════════════════════════════════════════


@router.get("/minuteurs", responses=REPONSES_LISTE)
@gerer_exception_api
async def lister_minuteurs(
    actifs_uniquement: bool = Query(False, description="Ne retourner que les minuteurs actifs"),
    limite: int = Query(20, ge=1, le=100),
    user: dict[str, Any] = Depends(require_auth),
) -> list[dict[str, Any]]:
    """Liste les sessions de minuteur de l'utilisateur."""
    from src.core.models import MinuteurSession

    def _query():
        with executer_avec_session() as session:
            user_id = user.get("sub", "")
            query = session.query(MinuteurSession).filter(MinuteurSession.user_id == user_id)
            if actifs_uniquement:
                query = query.filter(MinuteurSession.active.is_(True))
            rows = query.order_by(MinuteurSession.cree_le.desc()).limit(limite).all()
            return [
                {
                    "id": r.id,
                    "label": r.label,
                    "duree_secondes": r.duree_secondes,
                    "recette_id": r.recette_id,
                    "date_debut": r.date_debut.isoformat() if r.date_debut else None,
                    "date_fin": r.date_fin.isoformat() if r.date_fin else None,
                    "terminee": r.terminee,
                    "active": r.active,
                }
                for r in rows
            ]

    return await executer_async(_query)


@router.post("/minuteurs", status_code=201, responses=REPONSES_CRUD_CREATION)
@gerer_exception_api
async def creer_minuteur(
    body: "MinuteurCreate",
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Crée une session de minuteur."""
    from datetime import datetime

    from src.api.schemas.utilitaires import MinuteurCreate as _MC  # noqa: F811
    from src.core.models import MinuteurSession

    def _create():
        with executer_avec_session() as session:
            row = MinuteurSession(
                user_id=user.get("sub", ""),
                label=body.label,
                duree_secondes=body.duree_secondes,
                recette_id=body.recette_id,
                date_debut=datetime.utcnow(),
                active=True,
            )
            session.add(row)
            session.commit()
            session.refresh(row)
            return {
                "id": row.id,
                "label": row.label,
                "duree_secondes": row.duree_secondes,
                "active": row.active,
            }

    return await executer_async(_create)


@router.patch("/minuteurs/{minuteur_id}", responses=REPONSES_CRUD_ECRITURE)
@gerer_exception_api
async def modifier_minuteur(
    minuteur_id: int,
    body: "MinuteurPatch",
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Modifie un minuteur (terminer, mettre en pause)."""
    from datetime import datetime

    from src.api.schemas.utilitaires import MinuteurPatch as _MP  # noqa: F811
    from src.core.models import MinuteurSession

    def _update():
        with executer_avec_session() as session:
            row = session.query(MinuteurSession).filter(
                MinuteurSession.id == minuteur_id,
                MinuteurSession.user_id == user.get("sub", ""),
            ).first()
            if not row:
                raise HTTPException(status_code=404, detail="Minuteur non trouvé")
            if body.label is not None:
                row.label = body.label
            if body.terminee is not None:
                row.terminee = body.terminee
                if body.terminee:
                    row.active = False
                    row.date_fin = datetime.utcnow()
            if body.active is not None:
                row.active = body.active
            session.commit()
            session.refresh(row)
            return {
                "id": row.id,
                "label": row.label,
                "terminee": row.terminee,
                "active": row.active,
            }

    return await executer_async(_update)


@router.delete("/minuteurs/{minuteur_id}", response_model=MessageResponse, responses=REPONSES_CRUD_SUPPRESSION)
@gerer_exception_api
async def supprimer_minuteur(
    minuteur_id: int,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Supprime un minuteur."""
    from src.core.models import MinuteurSession

    def _delete():
        with executer_avec_session() as session:
            row = session.query(MinuteurSession).filter(
                MinuteurSession.id == minuteur_id,
                MinuteurSession.user_id == user.get("sub", ""),
            ).first()
            if not row:
                raise HTTPException(status_code=404, detail="Minuteur non trouvé")
            session.delete(row)
            session.commit()
            return {"message": "Minuteur supprimé", "id": minuteur_id}

    return await executer_async(_delete)

