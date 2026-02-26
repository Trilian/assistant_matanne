"""Services utilitaires — CRUD notes, journal, contacts, énergie, etc."""

from src.services.utilitaires.service import (
    ContactsService,
    EnergieService,
    JournalService,
    LiensService,
    MotsDePasseService,
    NotesService,
    PressePapiersService,
    get_contacts_service,
    get_energie_service,
    get_journal_service,
    get_liens_service,
    get_mots_de_passe_service,
    get_notes_service,
    get_presse_papiers_service,
)

__all__ = [
    "NotesService",
    "JournalService",
    "ContactsService",
    "LiensService",
    "MotsDePasseService",
    "PressePapiersService",
    "EnergieService",
    "get_notes_service",
    "get_journal_service",
    "get_contacts_service",
    "get_liens_service",
    "get_mots_de_passe_service",
    "get_presse_papiers_service",
    "get_energie_service",
]
