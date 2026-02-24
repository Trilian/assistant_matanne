"""Styles CSS pour le module Projets."""

import streamlit as st


def injecter_css_projets():
    """Injecte le CSS spécifique au module Projets."""
    st.markdown(
        """
        <style>
        .projet-card {
            border: 1px solid #e0e0e0;
            border-radius: 10px;
            padding: 1rem;
            margin-bottom: 0.8rem;
            background: var(--background-color, white);
            transition: transform 0.2s ease;
        }
        .projet-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        }
        .projet-badge {
            display: inline-block;
            padding: 2px 10px;
            border-radius: 12px;
            font-size: 0.75rem;
            font-weight: 600;
        }
        .badge-haute { background: #ffe0e0; color: #c62828; }
        .badge-moyenne { background: #fff3e0; color: #e65100; }
        .badge-basse { background: #e8f5e9; color: #2e7d32; }
        .badge-en_cours { background: #e3f2fd; color: #1565c0; }
        .badge-termine { background: #e8f5e9; color: #2e7d32; }
        .badge-annule { background: #f5f5f5; color: #616161; }
        .materiel-item {
            display: flex;
            justify-content: space-between;
            padding: 4px 0;
            border-bottom: 1px solid #f0f0f0;
        }
        .roi-card {
            text-align: center;
            padding: 1.2rem;
            border-radius: 10px;
            background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
