from __future__ import annotations

import sys
from pathlib import Path

current_path = Path(__file__).resolve()
project_root = None
for candidate in [current_path.parent, current_path.parent.parent]:
    if (candidate / "webapp").exists() and (candidate / "webapp" / "app.py").exists():
        project_root = candidate
        break
if project_root is None:
    project_root = current_path.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import streamlit as st

from webapp.ui.section_header import apply_app_theme, render_page_header, render_sidebar

st.set_page_config(page_title="About Project", page_icon="ℹ️", layout="wide")
apply_app_theme()
render_sidebar()

render_page_header(
    "About Project",
    "DairyVision Digital Twin: A SaaS-style platform for farm operations and research.",
    badge="Information",
    caption="This application is organized into two operational workspaces: live forecasting and research evaluation.",
)

st.markdown(
    """
    <div class="section-card">
      <strong>A commercial operations platform built on machine learning, feature engineering, and explainability.</strong>
    </div>
    """,
    unsafe_allow_html=True,
)

col1, col2 = st.columns(2)

with col1:
    st.markdown(
        """
        <div class="section-card">
          <h4 style="margin-top:0;color:#2f7d32;text-transform:uppercase;letter-spacing:0.04em;font-size:0.85rem;">Interactive Digital Twin</h4>
          <div style="margin-top:0.35rem;color:#0f172a;">
            <p><strong>Prediction</strong> – Compute fresh milk-yield forecasts from current inputs.</p>
            <p><strong>Digital Twin</strong> – Run what-if scenarios for feed, temperature, and environmental stress.</p>
            <p><strong>Health Alerts</strong> – Generate live recommendations from current conditions.</p>
            <p><strong>Explainability</strong> – Inspect feature contributions for the current scenario.</p>
          </div>
          <div style="margin-top:0.45rem;color:#475569;font-size:0.9rem;">
            All pages recompute everything from current user input and do not reuse training artifacts.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        """
        <div class="section-card">
          <h4 style="margin-top:0;color:#2f7d32;text-transform:uppercase;letter-spacing:0.04em;font-size:0.85rem;">Research & Evaluation</h4>
          <div style="margin-top:0.35rem;color:#0f172a;">
            <p><strong>Model Performance</strong> – Training and evaluation artifacts.</p>
            <p><strong>Model Comparison</strong> – Benchmark outputs and cross-validation results.</p>
            <p><strong>Dataset Overview</strong> – Dataset-level summaries and feature analysis.</p>
            <p><strong>About Project</strong> – Architecture context and project information.</p>
          </div>
          <div style="margin-top:0.45rem;color:#475569;font-size:0.9rem;">
            These pages display training and evaluation artifacts for research purposes only.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("---")

st.subheader("Technology stack")
st.caption("The platform is built on proven open-source libraries and a production-ready ML backend.")

tech_col1, tech_col2, tech_col3, tech_col4 = st.columns(4)
with tech_col1:
    st.markdown(
        """
        <div class="section-card">
          <div style="font-size:0.8rem;font-weight:700;color:#2f7d32;text-transform:uppercase;letter-spacing:0.04em;">Frontend</div>
          <div style="margin-top:0.35rem;color:#0f172a;font-size:0.9rem;">Streamlit 1.60</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with tech_col2:
    st.markdown(
        """
        <div class="section-card">
          <div style="font-size:0.8rem;font-weight:700;color:#2f7d32;text-transform:uppercase;letter-spacing:0.04em;">ML</div>
          <div style="margin-top:0.35rem;color:#0f172a;font-size:0.9rem;">XGBoost, scikit-learn</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with tech_col3:
    st.markdown(
        """
        <div class="section-card">
          <div style="font-size:0.8rem;font-weight:700;color:#2f7d32;text-transform:uppercase;letter-spacing:0.04em;">Explainability</div>
          <div style="margin-top:0.35rem;color:#0f172a;font-size:0.9rem;">SHAP, feature importance</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with tech_col4:
    st.markdown(
        """
        <div class="section-card">
          <div style="font-size:0.8rem;font-weight:700;color:#2f7d32;text-transform:uppercase;letter-spacing:0.04em;">Visualization</div>
          <div style="margin-top:0.35rem;color:#0f172a;font-size:0.9rem;">Plotly, pandas</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
