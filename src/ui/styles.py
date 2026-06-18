"""
Custom CSS styles for the dashboard UI.

Applies a clean, professional look suitable for a portfolio project.
"""

import streamlit as st

# Color palette used across the dashboard
PRIMARY_COLOR = "#1f77b4"
SUCCESS_COLOR = "#2ecc71"
DANGER_COLOR = "#e74c3c"
CARD_BACKGROUND = "#f8fafc"
BORDER_COLOR = "#e2e8f0"


def apply_custom_styles() -> None:
    """Inject custom CSS into the Streamlit app."""
    st.markdown(
        f"""
        <style>
            /* Main header styling */
            .dashboard-header {{
                background: linear-gradient(135deg, #1f77b4 0%, #1565c0 100%);
                padding: 1.5rem 2rem;
                border-radius: 12px;
                color: white;
                margin-bottom: 1.5rem;
            }}
            .dashboard-header h1 {{
                color: white !important;
                margin-bottom: 0.25rem;
            }}
            .dashboard-header p {{
                color: #e3f2fd;
                margin: 0;
            }}

            /* Statistics card container */
            .stat-card {{
                background: {CARD_BACKGROUND};
                border: 1px solid {BORDER_COLOR};
                border-radius: 10px;
                padding: 1rem 1.25rem;
                text-align: center;
                height: 100%;
            }}
            .stat-card .label {{
                font-size: 0.85rem;
                color: #64748b;
                margin-bottom: 0.25rem;
            }}
            .stat-card .value {{
                font-size: 1.4rem;
                font-weight: 700;
                color: #1e293b;
            }}
            .stat-card .delta-positive {{
                color: {SUCCESS_COLOR};
                font-size: 0.85rem;
            }}
            .stat-card .delta-negative {{
                color: {DANGER_COLOR};
                font-size: 0.85rem;
            }}

            /* Section headers */
            .section-header {{
                font-size: 1.1rem;
                font-weight: 600;
                color: #334155;
                border-left: 4px solid {PRIMARY_COLOR};
                padding-left: 0.75rem;
                margin: 1.5rem 0 1rem 0;
            }}

            /* Placeholder boxes for upcoming modules */
            .placeholder-box {{
                background: {CARD_BACKGROUND};
                border: 2px dashed {BORDER_COLOR};
                border-radius: 10px;
                padding: 2rem;
                text-align: center;
                color: #94a3b8;
            }}

            /* Sidebar section spacing */
            section[data-testid="stSidebar"] .block-container {{
                padding-top: 1rem;
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )
