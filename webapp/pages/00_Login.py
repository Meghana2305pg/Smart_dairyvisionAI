from __future__ import annotations

import streamlit as st

st.set_page_config(page_title="DairyVision AI", page_icon="🐄", layout="wide")
st.warning("This onboarding experience is now handled by the main application shell.")
if st.button("Open DairyVision AI"):
    st.switch_page("app.py")
