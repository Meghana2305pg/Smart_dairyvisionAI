from __future__ import annotations

import io
from typing import Any

import pandas as pd
import streamlit as st

from webapp.services.cow_service import CowService


def _normalize_cow(cow_data: Any) -> dict[str, Any]:
    """Normalize cow payloads from the repository into a dictionary."""
    if isinstance(cow_data, dict) and "cow" in cow_data:
        cow_data = cow_data["cow"]
    return dict(cow_data or {})


def render_herd_management() -> None:
    """Render the herd management interface for viewing, adding, and managing cows."""
    st.markdown("<div class='section-heading'>Manage Your Herd</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='card-caption'>View all registered cows, monitor their status, and manage the herd profile.</div>",
        unsafe_allow_html=True,
    )

    cow_service: CowService = st.session_state.cow_service
    raw_cows = cow_service.get_cows()
    cows = [_normalize_cow(item) for item in raw_cows]

    search_term = st.text_input("Search by cow ID", placeholder="e.g., cow-001").strip()
    col1, col2, col3 = st.columns([0.5, 0.25, 0.25])
    with col1:
        st.write("")
    with col2:
        if st.button("Add Cow", use_container_width=True):
            st.session_state.show_add_cow_form = True
            st.rerun()
    with col3:
        if st.button("Refresh", use_container_width=True):
            st.rerun()

    if st.session_state.get("show_add_cow_form"):
        st.markdown("---")
        st.markdown("<div class='section-heading'>Register New Cow</div>", unsafe_allow_html=True)
        with st.form("add_cow_form"):
            cow_id = st.text_input("Cow ID", placeholder="e.g., cow-001")
            cow_name = st.text_input("Name", placeholder="e.g., Bessie")
            breed = st.text_input("Breed", placeholder="e.g., Holstein")
            age_months = st.number_input("Age (months)", min_value=1, max_value=300, value=24)
            submitted = st.form_submit_button("Register Cow")

        if submitted:
            if not cow_id or not cow_name:
                st.error("Cow ID and Name are required.")
            else:
                try:
                    cow_service.register_cow(
                        cow_id=cow_id,
                        name=cow_name,
                        breed=breed or "Unknown",
                        age_months=int(age_months),
                    )
                    st.session_state.show_add_cow_form = False
                    st.success(f"Cow {cow_name} registered successfully!")
                    st.rerun()
                except Exception as exc:
                    st.error(f"Failed to register cow: {exc}")
        st.markdown("---")

    if not cows:
        st.info("No cows registered yet. Click 'Add Cow' to register your first cow.")
        return

    filtered_cows = [
        cow for cow in cows if not search_term or search_term.lower() in str(cow.get("cow_id", "")).lower() or search_term.lower() in str(cow.get("name", "")).lower()
    ]

    if not filtered_cows:
        st.warning(f"No cows found matching '{search_term}'")
        return

    st.markdown(f"**{len(filtered_cows)} cow(s) found**")
    table = pd.DataFrame(
        [
            {
                "Cow ID": cow.get("cow_id", "N/A"),
                "Name": cow.get("name", "N/A"),
                "Breed": cow.get("breed", "N/A"),
                "Age (months)": cow.get("age_months", "N/A"),
                "Status": cow.get("status", "Active"),
            }
            for cow in filtered_cows
        ]
    )
    st.dataframe(table, use_container_width=True, hide_index=True)

    export_buffer = io.StringIO()
    table.to_csv(export_buffer, index=False)
    st.download_button(
        "Export herd",
        data=export_buffer.getvalue(),
        file_name="herd_export.csv",
        mime="text/csv",
        use_container_width=True,
    )

    for cow in filtered_cows:
        cow_id = cow.get("cow_id")
        if not cow_id:
            continue
        col1, col2, col3, col4 = st.columns([0.3, 0.35, 0.2, 0.15])
        with col1:
            st.markdown(f"**{cow.get('name', 'Unknown')}**")
            st.caption(f"ID: {cow_id}")
        with col2:
            st.caption(f"Breed: {cow.get('breed', 'N/A')}")
            st.caption(f"Registered: {cow.get('created_at', 'N/A')}")
        with col3:
            if st.button("View Profile", key=f"view_{cow_id}", use_container_width=True):
                st.session_state.selected_cow_id = cow_id
                st.session_state.active_section = "herd"
                st.rerun()
        with col4:
            if st.button("Delete", key=f"del_{cow_id}", use_container_width=True):
                if cow_service.delete_cow(cow_id):
                    st.success("Cow deleted.")
                    st.rerun()
        st.markdown("---")
