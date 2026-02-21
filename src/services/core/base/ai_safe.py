"""Mixin: API Safe IA — retourne Result[T, ErrorInfo] au lieu de None."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pydantic import BaseModel

from src.services.core.base.async_utils import sync_wrapper

logger = logging.getLogger(__name__)


class AISafeCallsMixin:
    """Fournit safe_call_with_cache/parsing/list_parsing/json_parsing + sync wrappers.

    Attend sur ``self``: service_name, call_with_cache, call_with_parsing,
    call_with_list_parsing, call_with_json_parsing.
    """

    async def safe_call_with_cache(
        self,
        prompt: str,
        system_prompt: str = "",
        temperature: float | None = None,
        max_tokens: int = 1000,
        use_cache: bool = True,
        category: str | None = None,
    ):
        """Appel IA retournant Result au lieu de str|None.

        Returns:
            Success[str] si réponse, Failure[ErrorInfo] si erreur/rate limit
        """
        from src.core.errors_base import ErreurLimiteDebit
        from src.core.result import (
            ErrorCode,
            failure,
            from_exception,
            success,
        )

        try:
            response = await self.call_with_cache(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=temperature,
                max_tokens=max_tokens,
                use_cache=use_cache,
                category=category,
            )
            if response is None:
                return failure(
                    ErrorCode.AI_UNAVAILABLE,
                    "Client IA indisponible",
                    message_utilisateur="Le service IA est temporairement indisponible",
                    source=self.service_name,
                )
            return success(response)
        except ErreurLimiteDebit as e:
            return failure(
                ErrorCode.RATE_LIMITED,
                str(e),
                message_utilisateur=str(e),
                source=self.service_name,
            )
        except Exception as e:
            return from_exception(e, source=self.service_name)

    async def safe_call_with_parsing(
        self,
        prompt: str,
        response_model: type[BaseModel],
        system_prompt: str = "",
        temperature: float | None = None,
        max_tokens: int = 1000,
        use_cache: bool = True,
        fallback: dict | None = None,
    ):
        """Appel IA avec parsing Pydantic, retourne Result.

        Returns:
            Success[BaseModel] si parsé, Failure[ErrorInfo] si échec
        """
        from src.core.result import (
            ErrorCode,
            failure,
            from_exception,
            success,
        )

        try:
            parsed = await self.call_with_parsing(
                prompt=prompt,
                response_model=response_model,
                system_prompt=system_prompt,
                temperature=temperature,
                max_tokens=max_tokens,
                use_cache=use_cache,
                fallback=fallback,
            )
            if parsed is None:
                return failure(
                    ErrorCode.PARSING_ERROR,
                    f"Impossible de parser la réponse vers {response_model.__name__}",
                    source=self.service_name,
                )
            return success(parsed)
        except Exception as e:
            return from_exception(e, source=self.service_name)

    async def safe_call_with_list_parsing(
        self,
        prompt: str,
        item_model: type[BaseModel],
        list_key: str = "items",
        system_prompt: str = "",
        temperature: float | None = None,
        max_tokens: int = 2000,
        use_cache: bool = True,
        max_items: int | None = None,
    ):
        """Appel IA avec parsing liste, retourne Result.

        Returns:
            Success[list[BaseModel]], Failure[ErrorInfo] si erreur
        """
        from src.core.result import from_exception, success

        try:
            items = await self.call_with_list_parsing(
                prompt=prompt,
                item_model=item_model,
                list_key=list_key,
                system_prompt=system_prompt,
                temperature=temperature,
                max_tokens=max_tokens,
                use_cache=use_cache,
                max_items=max_items,
            )
            return success(items)
        except Exception as e:
            return from_exception(e, source=self.service_name)

    async def safe_call_with_json_parsing(
        self,
        prompt: str,
        response_model: type[BaseModel],
        system_prompt: str = "",
        temperature: float | None = None,
        max_tokens: int = 2000,
        use_cache: bool = True,
    ):
        """Appel IA avec parsing JSON, retourne Result.

        Returns:
            Success[BaseModel] si parsé, Failure[ErrorInfo] si échec
        """
        from src.core.result import (
            ErrorCode,
            failure,
            from_exception,
            success,
        )

        try:
            parsed = await self.call_with_json_parsing(
                prompt=prompt,
                response_model=response_model,
                system_prompt=system_prompt,
                temperature=temperature,
                max_tokens=max_tokens,
                use_cache=use_cache,
            )
            if parsed is None:
                return failure(
                    ErrorCode.PARSING_ERROR,
                    f"Impossible de parser JSON vers {response_model.__name__}",
                    source=self.service_name,
                )
            return success(parsed)
        except Exception as e:
            return from_exception(e, source=self.service_name)

    # Versions synchrones des méthodes safe
    safe_call_with_cache_sync = sync_wrapper(safe_call_with_cache)
    safe_call_with_parsing_sync = sync_wrapper(safe_call_with_parsing)
    safe_call_with_list_parsing_sync = sync_wrapper(safe_call_with_list_parsing)
    safe_call_with_json_parsing_sync = sync_wrapper(safe_call_with_json_parsing)
