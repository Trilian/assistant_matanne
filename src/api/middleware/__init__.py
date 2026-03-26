"""
Middleware package for FastAPI.

Includes:
- budget_guard: Budget guard middleware (blocks bets if limit reached)
"""

from src.api.middleware.budget_guard import BudgetGuardMiddleware

__all__ = [
    "BudgetGuardMiddleware",
]
