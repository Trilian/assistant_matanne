"""
UI Primitives - Composants atomiques de base.

Fournit des primitives composables inspirées de Chakra UI / Radix:
- Box: Container universel avec props de layout
- Stack: Flex container (HStack/VStack)
- Text: Typographie avec variants

Usage:
    from src.ui.primitives import Box, HStack, VStack, Text

    with Box(p="1rem", bg=Couleur.BG_SURFACE, radius=Rayon.LG) as container:
        container.child(Text("Titre", size="lg", weight="bold").html())
        container.child(HStack(gap="0.5rem").child(badge1).child(badge2).html())
"""

from .box import Box, BoxProps
from .stack import HStack, Stack, VStack
from .text import Text, TextProps

__all__ = [
    "Box",
    "BoxProps",
    "Stack",
    "HStack",
    "VStack",
    "Text",
    "TextProps",
]
