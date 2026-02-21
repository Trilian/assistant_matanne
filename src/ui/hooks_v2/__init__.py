"""
Hooks V2 - Hooks Streamlit avancés avec typage strict.

Système de hooks unifié inspiré de React / TanStack Query / Zustand:

État:
- use_state: État typé générique avec setter et update
- use_toggle: Booléen toggle avec set_true/set_false
- use_counter: Compteur avec increment/decrement/reset
- use_list: Gestion de listes avec append/remove/clear

Data fetching:
- use_query: Requêtes avec cache, stale_time, retry, loading states
- use_mutation: Mutations avec invalidation automatique des queries

Formulaires:
- use_form: Formulaires avec validation, dirty/touched tracking

Services:
- use_service: Injection de service avec cache session

Cycle de vie:
- use_memo: Mémorisation de calculs coûteux avec dépendances
- use_effect: Effets de bord avec cleanup automatique
- use_callback: Mémorisation de fonctions callback
- use_previous: Accès à la valeur précédente d'une variable

Usage:
    from src.ui.hooks_v2 import use_state, use_query, use_form, use_service
"""

from .use_extra import (
    CounterState,
    ListState,
    ToggleState,
    use_counter,
    use_list,
    use_toggle,
)
from .use_form import FormState, use_form
from .use_lifecycle import use_callback, use_effect, use_memo, use_previous
from .use_query import MutationState, QueryResult, QueryStatus, use_mutation, use_query
from .use_service import use_service
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
    # Query & Mutation
    "use_query",
    "use_mutation",
    "MutationState",
    "QueryResult",
    "QueryStatus",
    # Form
    "use_form",
    "FormState",
    # Service
    "use_service",
    # Lifecycle
    "use_memo",
    "use_effect",
    "use_callback",
    "use_previous",
]
