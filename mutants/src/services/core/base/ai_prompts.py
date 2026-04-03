"""Mixin: builders de prompts structurés pour l'IA."""

from __future__ import annotations


class AIPromptsMixin:
    """Fournit build_json_prompt et build_system_prompt."""

    def build_json_prompt(
        self, context: str, task: str, json_schema: str, constraints: list[str] | None = None
    ) -> str:
        """Construit un prompt structuré pour réponse JSON"""
        prompt = f"{context}\n\n"
        prompt += f"TÂCHE: {task}\n\n"

        if constraints:
            prompt += "CONTRAINTES:\n"
            for constraint in constraints:
                prompt += f"- {constraint}\n"
            prompt += "\n"

        prompt += "FORMAT JSON ATTENDU:\n"
        prompt += f"{json_schema}\n\n"
        prompt += "IMPORTANT: Réponds UNIQUEMENT en JSON valide, sans texte avant ou après."

        return prompt

    def build_system_prompt(
        self, role: str, expertise: list[str], rules: list[str] | None = None
    ) -> str:
        """Construit un system prompt structuré"""
        prompt = f"Tu es {role}.\n\n"

        prompt += "EXPERTISE:\n"
        for exp in expertise:
            prompt += f"- {exp}\n"
        prompt += "\n"

        if rules:
            prompt += "RÈGLES:\n"
            for rule in rules:
                prompt += f"- {rule}\n"
            prompt += "\n"

        prompt += "Réponds toujours en français, de manière claire et structurée."

        return prompt
