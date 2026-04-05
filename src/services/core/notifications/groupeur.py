"""
Groupeur de notifications intelligentes.

Collecte les notifications pendantes et les regroupe en un seul
digest structuré au lieu d'envoyer N messages séparés.
"""

from __future__ import annotations

import logging
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class NotificationPendante:
    """Notification en attente de regroupement."""

    module: str
    titre: str
    message: str
    priorite: int = 3  # 1=critique, 5=info
    icone: str = ""


TYPE_ICONES = {
    "cuisine": "🍽️",
    "courses": "🛒",
    "famille": "👨‍👩‍👦",
    "maison": "🏡",
    "jardin": "🌱",
    "budget": "💰",
    "sante": "🏥",
    "entretien": "🔧",
    "rappel": "⏰",
    "meteo": "🌤️",
    "ia": "🤖",
}


@dataclass
class GroupeurNotifications:
    """Regroupe les notifications en un digest structuré."""

    _pendantes: list[NotificationPendante] = field(default_factory=list)

    def ajouter(
        self,
        module: str,
        titre: str,
        message: str,
        priorite: int = 3,
    ) -> None:
        """Ajoute une notification à regrouper."""
        icone = TYPE_ICONES.get(module, "📌")
        self._pendantes.append(
            NotificationPendante(
                module=module,
                titre=titre,
                message=message,
                priorite=priorite,
                icone=icone,
            )
        )

    def construire_digest(self, titre_digest: str = "📋 Récap du jour") -> str:
        """Construit le message digest regroupé en HTML (Telegram).

        Returns:
            Message HTML formaté regroupant toutes les notifications par module.
        """
        if not self._pendantes:
            return ""

        # Trier par priorité (critique d'abord)
        self._pendantes.sort(key=lambda n: n.priorite)

        # Regrouper par module
        par_module: dict[str, list[NotificationPendante]] = defaultdict(list)
        for notif in self._pendantes:
            par_module[notif.module].append(notif)

        # Construire le message
        lignes = [f"<b>{titre_digest}</b>", ""]

        # Section critique en premier
        critiques = [n for n in self._pendantes if n.priorite <= 2]
        if critiques:
            lignes.append("🚨 <b>À traiter en priorité :</b>")
            for n in critiques:
                lignes.append(f"  {n.icone} {n.titre}")
                if n.message:
                    lignes.append(f"     <i>{n.message[:100]}</i>")
            lignes.append("")

        # Autres par module
        for module, notifs in par_module.items():
            notifs_normales = [n for n in notifs if n.priorite > 2]
            if not notifs_normales:
                continue
            icone = TYPE_ICONES.get(module, "📌")
            lignes.append(f"{icone} <b>{module.capitalize()}</b> ({len(notifs_normales)})")
            for n in notifs_normales[:5]:  # Max 5 par module
                lignes.append(f"  • {n.titre}")
            if len(notifs_normales) > 5:
                lignes.append(f"  <i>... et {len(notifs_normales) - 5} autres</i>")
            lignes.append("")

        # Footer
        nb_total = len(self._pendantes)
        lignes.append(f"<i>{nb_total} notification{'s' if nb_total > 1 else ''} regroupée{'s' if nb_total > 1 else ''}</i>")

        return "\n".join(lignes)

    def vider(self) -> None:
        """Vide les notifications pendantes après envoi."""
        self._pendantes.clear()

    @property
    def nombre_pendantes(self) -> int:
        """Nombre de notifications en attente."""
        return len(self._pendantes)

    @property
    def a_des_critiques(self) -> bool:
        """Vérifie s'il y a des notifications critiques."""
        return any(n.priorite <= 2 for n in self._pendantes)
