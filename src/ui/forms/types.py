"""Types de données pour le système de formulaires."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Callable


class TypeChamp(StrEnum):
    """Types de champs supportés."""

    TEXT = "text"
    NUMBER = "number"
    FLOAT = "float"
    SELECT = "select"
    MULTISELECT = "multiselect"
    CHECKBOX = "checkbox"
    TEXTAREA = "textarea"
    DATE = "date"
    TIME = "time"
    DATETIME = "datetime"
    SLIDER = "slider"
    FILE = "file"
    COLOR = "color"
    PASSWORD = "password"


@dataclass
class ChampConfig:
    """Configuration d'un champ de formulaire."""

    name: str
    type_champ: TypeChamp
    label: str = ""
    help_text: str = ""
    required: bool = False
    default: Any = None
    placeholder: str = ""

    # Validation
    min_value: float | int | None = None
    max_value: float | int | None = None
    min_length: int | None = None
    max_length: int | None = None
    pattern: str | None = None
    validator: Callable[[Any], bool] | None = None
    error_message: str = ""

    # Options pour select/multiselect
    options: list[Any] = field(default_factory=list)
    format_func: Callable[[Any], str] | None = None

    # Options pour slider
    step: float | int = 1

    # Options pour file
    accepted_types: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.label:
            self.label = self.name.replace("_", " ").title()


@dataclass
class FormResult:
    """Résultat d'un formulaire soumis."""

    submitted: bool = False
    data: dict[str, Any] = field(default_factory=dict)
    errors: dict[str, str] = field(default_factory=dict)

    @property
    def is_valid(self) -> bool:
        """True si le formulaire est valide (soumis sans erreurs)."""
        return self.submitted and not self.errors

    def get(self, key: str, default: Any = None) -> Any:
        """Récupère une valeur du formulaire."""
        return self.data.get(key, default)

    def __getitem__(self, key: str) -> Any:
        return self.data[key]
