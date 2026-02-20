"""
Hooks V2 - Hooks Streamlit avancés avec typage strict.

Nouvelle génération de hooks inspirés de React Query et Zustand:
- use_state: État typé avec setter
- use_query: Data fetching avec cache et loading states
- use_form: Gestion de formulaires avec validation
- use_counter: Compteur incrémentable/décrémentable
- use_toggle: Booléen toggle
- use_list: Gestion de listes avec ajout/suppression
- use_mutation: Mutations asynchrones avec états loading/error

Usage:
    from src.ui.hooks_v2 import use_state, use_query, use_form, use_toggle
"""

from .use_extra import (
    CounterState,
    ListState,
    MutationState,
    ToggleState,
    use_counter,
    use_list,
    use_mutation,
    use_toggle,
)
from .use_form import FormState, use_form
from .use_query import QueryResult, QueryStatus, use_query
from .use_state import State, use_state

__all__ = [
    # State
    "State",
    "use_state",
    "use_toggle",
    "ToggleState",
    "use_counter",
    "CounterState",
    "use_list",
    "ListState",
    # Query
    "use_query",
    "use_mutation",
    "MutationState",
    "QueryResult",
    "QueryStatus",
    # Form
    "use_form",
    "FormState",
]
