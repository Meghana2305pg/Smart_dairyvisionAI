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

st.set_page_config(page_title="Model Comparison", page_icon="⚖️", layout="wide")
apply_app_theme()
render_sidebar()

render_page_header(
    "Model Comparison",
    "Benchmark outputs from the research workflow across competing models.",
    badge="Research",
    caption="This section compares research model artifacts and is reserved for evaluation purposes.",
)

st.markdown(
    """
    <div class="section-card">
      <strong>Cross-model comparison table and performance benchmarks.</strong>
    </div>
    """,
    unsafe_allow_html=True,
)

st.subheader("Model comparison table")
st.caption("Published benchmark outputs from the model evaluation workflow.")

comparison_path = OUTPUT_DIR / "paper_table_model_comparison.csv"
if comparison_path.exists():
    try:
        comparison_df = pd.read_csv(comparison_path)
        st.markdown(
            """
            <div class="section-card" style="background:#ecfdf3;border-color:#a7f3d0;">
              <div style="font-size:0.8rem;font-weight:700;color:#166534;">✓ Comparison data available</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.dataframe(comparison_df, use_container_width=True)
    except Exception as e:
        st.error(f"Error reading comparison file: {e}")
else:
    st.markdown(
        """
        <div class="section-card" style="background:#fef2f2;border-color:#fecaca;">
          <div style="font-size:0.8rem;font-weight:700;color:#991b1b;">⊘ Comparison data not available</div>
          <div style="margin-top:0.35rem;color:#475569;">Run the model evaluation workflow to generate comparison results.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
