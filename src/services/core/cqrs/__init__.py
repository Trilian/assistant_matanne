"""
CQRS Léger — Command Query Responsibility Segregation.

Sépare les opérations de lecture (Query) et d'écriture (Command) pour:
- Optimisation ciblée (cache pour queries, validation pour commands)
- Audit natif des modifications
- Scalabilité future vers event sourcing

Usage:
    from src.services.core.cqrs import Query, Command, obtenir_dispatcher

    # Définir une Query
    @dataclass(frozen=True)
    class RecherchRecettesQuery(Query[list[Recette]]):
        terme: str
        limit: int = 50

        def execute(self) -> Result[list[Recette], ErrorInfo]:
            ...

    # Exécuter via dispatcher (avec cache automatique)
    dispatcher = obtenir_dispatcher()
    result = dispatcher.dispatch_query(RecherchRecettesQuery(terme="tarte"))

    # Définir une Command
    @dataclass
    class CreerRecetteCommand(Command[Recette]):
        nom: str
        ingredients: list[dict]

        def validate(self) -> Result[None, ErrorInfo]:
            if not self.nom:
                return Failure(ErrorInfo(code=ErrorCode.VALIDATION_ERROR, message="Nom requis"))
            return Success(None)

        def execute(self) -> Result[Recette, ErrorInfo]:
            ...

    # Exécuter (avec validation et audit automatiques)
    result = dispatcher.dispatch_command(CreerRecetteCommand(nom="Tarte", ingredients=[...]))
"""

from .commands import (
    Command,
    CommandHandler,
    CommandResult,
)
from .dispatcher import (
    CQRSDispatcher,
    obtenir_dispatcher,
)
from .queries import (
    Query,
    QueryHandler,
)

__all__ = [
    # Queries
    "Query",
    "QueryHandler",
    # Commands
    "Command",
    "CommandHandler",
    "CommandResult",
    # Dispatcher
    "CQRSDispatcher",
    "obtenir_dispatcher",
]
