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
import pandas as pd

from webapp.config.settings import OUTPUT_DIR
from webapp.ui.section_header import apply_app_theme, render_page_header, render_sidebar

st.set_page_config(page_title="Dataset Overview", page_icon="🗂️", layout="wide")
apply_app_theme()
render_sidebar()

render_page_header(
    "Dataset Overview",
    "Dataset-level summaries and research artifacts from the training pipeline.",
    badge="Research",
    caption="Use this page to inspect training-related dataset summaries and exported research tables.",
)

st.markdown(
    """
    <div class="section-card">
      <strong>Engineered features, dataset statistics, and training data insights.</strong>
    </div>
    """,
    unsafe_allow_html=True,
)

st.subheader("Available dataset artifacts")
st.caption("Research outputs generated during the data engineering and exploration phase.")

artifact_names = ["engineered_dataset.csv"]

for artifact_name in artifact_names:
    path = OUTPUT_DIR / artifact_name
    if path.exists():
        try:
            df_preview = pd.read_csv(path, nrows=50)
            st.markdown(
                f"""
                <div class="section-card" style="background:#ecfdf3;border-color:#a7f3d0;">
                  <div style="font-size:0.8rem;font-weight:700;color:#166534;">✓ {artifact_name}</div>
                  <div style="margin-top:0.35rem;color:#166534;">{len(df_preview)} rows available</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            with st.expander(f"Preview {artifact_name}"):
                st.dataframe(df_preview, use_container_width=True)
        except Exception as e:
            st.error(f"Error reading {artifact_name}: {e}")
    else:
        st.markdown(
            f"""
            <div class="section-card" style="background:#fef2f2;border-color:#fecaca;">
              <div style="font-size:0.8rem;font-weight:700;color:#991b1b;">⊘ {artifact_name}</div>
              <div style="margin-top:0.35rem;color:#475569;">Artifact not yet generated.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
