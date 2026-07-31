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
from pathlib import Path

from webapp.config.settings import OUTPUT_DIR
from webapp.ui.section_header import apply_app_theme, render_page_header, render_sidebar

st.set_page_config(page_title="Model Performance", page_icon="📊", layout="wide")
apply_app_theme()
render_sidebar()

render_page_header(
    "Model Performance",
    "Review training and evaluation artifacts from the ML research workflow.",
    badge="Research",
    caption="This section displays published model-performance outputs and is not used for live predictions.",
)

st.markdown(
    """
    <div class="section-card">
      <strong>Cross-validation results, test metrics, and feature importance from the training pipeline.</strong>
    </div>
    """,
    unsafe_allow_html=True,
)

artifact_paths = {
    "cv_results": OUTPUT_DIR / "cv_results.csv",
    "test_metrics": OUTPUT_DIR / "test_metrics.csv",
    "feature_importance": OUTPUT_DIR / "feature_importance.csv",
    "predicted_vs_actual": OUTPUT_DIR / "predicted_vs_actual.png",
}

st.subheader("Training artifacts")
st.caption("Available research outputs from the model training and evaluation process.")

artifact_cols = st.columns(len(artifact_paths))
for idx, (name, path) in enumerate(artifact_paths.items()):
    with artifact_cols[idx]:
        if path.exists():
            st.markdown(
                f"""
                <div class="section-card" style="background:#ecfdf3;border-color:#a7f3d0;">
                  <div style="font-size:0.8rem;font-weight:700;color:#166534;">{name.replace('_', ' ').title()}</div>
                  <div style="margin-top:0.35rem;color:#166534;font-weight:600;">✓ Available</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f"""
                <div class="section-card" style="background:#fef2f2;border-color:#fecaca;">
                  <div style="font-size:0.8rem;font-weight:700;color:#991b1b;">{name.replace('_', ' ').title()}</div>
                  <div style="margin-top:0.35rem;color:#991b1b;font-weight:600;">⊘ Not generated</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

st.markdown("---")
st.markdown(
    """
    <div class="section-card">
      <div style="font-size:0.8rem;font-weight:700;color:#2f7d32;text-transform:uppercase;letter-spacing:0.04em;">Note</div>
      <div style="margin-top:0.35rem;color:#0f172a;">Run the training and evaluation workflow to generate or refresh these artifacts.</div>
    </div>
    """,
    unsafe_allow_html=True,
)
