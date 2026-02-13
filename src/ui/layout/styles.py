"""
Styles CSS pour l'application.
"""

import streamlit as st


def injecter_css():
    """Injecte les styles CSS modernes dans l'application."""
    st.markdown(
        """
<style>
:root {
    --primary: #2d4d36;
    --secondary: #5e7a6a;
    --accent: #4caf50;
}

.main-header {
    padding: 1rem 0;
    border-bottom: 2px solid var(--accent);
    margin-bottom: 2rem;
}

.metric-card {
    background: white;
    padding: 1.5rem;
    border-radius: 12px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.04);
    transition: transform 0.2s;
}

.metric-card:hover {
    transform: translateY(-2px);
}

/* Cartes de navigation */
.nav-card {
    background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
    color: white;
    padding: 1.5rem;
    border-radius: 12px;
    text-align: center;
    cursor: pointer;
    transition: all 0.3s ease;
}

.nav-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 25px rgba(0,0,0,0.15);
}

/* Badges */
.badge {
    display: inline-block;
    padding: 0.25rem 0.75rem;
    border-radius: 20px;
    font-size: 0.85rem;
    font-weight: 500;
}

.badge-success {
    background: #d4edda;
    color: #155724;
}

.badge-warning {
    background: #fff3cd;
    color: #856404;
}

.badge-danger {
    background: #f8d7da;
    color: #721c24;
}

/* Masquer éléments Streamlit par défaut */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}

/* Responsive */
@media (max-width: 768px) {
    .main-header h1 {
        font-size: 1.5rem;
    }

    .metric-card {
        padding: 1rem;
    }
}
</style>
""",
        unsafe_allow_html=True,
    )
