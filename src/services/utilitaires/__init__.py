"""Services utilitaires — CRUD notes, journal, contacts, énergie, etc."""

from src.services.utilitaires.service import (
    ContactsService,
    EnergieService,
    JournalService,
    LiensService,
    MotsDePasseService,
    NotesService,
    PressePapiersService,
    obtenir_contacts_service,
    obtenir_energie_service,
    obtenir_journal_service,
    obtenir_liens_service,
    obtenir_mots_de_passe_service,
    obtenir_notes_service,
    obtenir_presse_papiers_service,
)
from src.services.utilitaires.ocr_service import OCRService, obtenir_ocr_service
from src.services.utilitaires.briefing_matinal import (
    BriefingMatinalService,
    obtenir_service_briefing_matinal,
)
from src.services.utilitaires.inter_module_chat_contexte import (
    ChatContexteMultiModuleService,
    obtenir_service_chat_contexte,
)
from src.services.utilitaires.assistant_proactif import (
    AssistantProactifService,
    obtenir_service_assistant_proactif,
)

__all__ = [
    "NotesService",
    "JournalService",
    "ContactsService",
    "LiensService",
    "MotsDePasseService",
    "PressePapiersService",
    "EnergieService",
    "OCRService",
    "BriefingMatinalService",
    "ChatContexteMultiModuleService",
    "AssistantProactifService",
    "obtenir_notes_service",
    "obtenir_journal_service",
    "obtenir_contacts_service",
    "obtenir_liens_service",
    "obtenir_mots_de_passe_service",
    "obtenir_presse_papiers_service",
    "obtenir_energie_service",
    "obtenir_ocr_service",
    "obtenir_service_briefing_matinal",
    "obtenir_service_chat_contexte",
    "obtenir_service_assistant_proactif",
]
