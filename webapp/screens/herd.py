"""Herd management screen for DairyVision AI."""
from __future__ import annotations

from typing import Any

import pandas as pd
import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

from webapp.digital_twin.cow_twin import CowTwin
from webapp.services.cow_service import CowService
from webapp.utils.logging import log_error, log_event
from webapp.utils.validation import validate_cow_registration_form
from webapp.ui.section_header import render_page_header, render_section_header


def _normalize_cow(cow_data: Any) -> dict[str, Any]:
    """Normalize cow payloads from the repository into a dictionary."""
    if isinstance(cow_data, dict) and "cow" in cow_data:
        cow_data = cow_data["cow"]
    return dict(cow_data or {})


def _get_or_create_twin(cow_service: CowService, cow_id: str, name: str | None = None) -> CowTwin:
    """Reuse an existing digital twin or create one from the current cow record."""
    twin = cow_service._cow_twins.get(cow_id)
    if twin is None:
        twin = CowTwin(cow_id=cow_id, name=name or cow_id)
        cow_service._cow_twins[cow_id] = twin
    return twin


def _set_profile_view(cow_id: str, tab: str | None = None) -> None:
    """Route the user to the cow profile for the selected cow."""
    st.session_state.selected_cow_id = cow_id
    st.session_state.active_section = "cow_profile"
    if tab:
        st.session_state.profile_tab = tab
    st.rerun()


def render_herd() -> None:
    """Render the herd management screen with search, registration, and actions."""
    render_page_header("My Herd", "Register new cows, inspect each animal workspace, and jump into the associated profile in a single click.", badge="Herd")

    cow_service: CowService = st.session_state.cow_service
    raw_cows = cow_service.get_cows()
    cows = [_normalize_cow(item) for item in raw_cows]

    status_options = ["All", "Active", "Inactive"]
    breed_options = sorted({str(cow.get("breed") or "Unknown") for cow in cows})
    selected_status_key = st.session_state.get("herd_status_filter", "All")
    if selected_status_key not in status_options:
        selected_status_key = "All"
    selected_breed_key = st.session_state.get("herd_breed_filter", "All")
    breed_list = ["All"] + breed_options
    if selected_breed_key not in breed_list:
        selected_breed_key = "All"

    c1, c2, c3 = st.columns([1, 1, 1], gap="small")
    with c1:
        selected_status = st.selectbox("Status", status_options, index=status_options.index(selected_status_key), key="herd_status_filter")
    with c2:
        selected_breed = st.selectbox("Breed", breed_list, index=breed_list.index(selected_breed_key), key="herd_breed_filter")
    with c3:
        search_term = st.text_input("Search by Cow ID or Name", value=st.session_state.get("herd_search_term", ""), placeholder="e.g., cow-001, Bessie", key="herd_search_term")

    c1, c2 = st.columns([1.5, 1], gap="small")
    with c1:
        if st.button("Register Cow", key="herd_toggle_register_form", use_container_width=True):
            st.session_state.show_herd_form = not st.session_state.get("show_herd_form", False)
    with c2:
        if st.button("Refresh", key="herd_refresh", use_container_width=True):
            st.rerun()

    cow_rows = [
        {
            "cow_id": cow.get("cow_id"),
            "name": cow.get("name", ""),
            "breed": cow.get("breed", "N/A"),
            "age_months": int(cow.get("age_months") or 0),
            "status": cow.get("status", "Active"),
            "registered": (cow.get("created_at") or "")[:10] if cow.get("created_at") else "",
        }
        for cow in cows
    ]
    df = pd.DataFrame(cow_rows, columns=["cow_id", "name", "breed", "age_months", "status", "registered"])

    if search_term and not df.empty:
        df = df[df.apply(lambda r: search_term.lower() in str(r["cow_id"]).lower() or search_term.lower() in str(r["name"]).lower(), axis=1)]
    if selected_status != "All" and not df.empty:
        df = df[df["status"].str.lower() == selected_status.lower()]
    if selected_breed != "All" and not df.empty:
        df = df[df["breed"].fillna("Unknown").str.lower() == selected_breed.lower()]
    if df.empty:
        st.info("No cows match the current filters. Adjust search or status/breed selection.", icon="ℹ️")
    export_df = df.copy()
    csv_bytes = export_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Export CSV",
        data=csv_bytes,
        file_name="herd_export.csv",
        mime="text/csv",
        use_container_width=True,
    )

    # Registration UI using expander (no plain form)
    if st.session_state.get("show_herd_form"):
        with st.expander("Register New Cow", expanded=True):
            render_section_header("Register New Cow", "Add a new animal to the herd and attach basic metadata.")
            cols = st.columns(3, gap="medium")
            with cols[0]:
                new_cow_id = st.text_input("Cow ID", placeholder="e.g., cow-001")
                new_breed = st.text_input("Breed", placeholder="e.g., Holstein")
            with cols[1]:
                new_name = st.text_input("Name", placeholder="e.g., Bessie")
                new_age = st.number_input("Age (months)", min_value=1, max_value=300, value=24)
            with cols[2]:
                new_status = st.selectbox("Status", ["Active", "Inactive"], index=0)
                submitted_register = st.button("Register Cow", key="herd_submit_register", use_container_width=True)
                if st.button("Cancel", key="herd_cancel_register", use_container_width=True):
                    st.session_state.show_herd_form = False

            if submitted_register:
                errors = validate_cow_registration_form(new_cow_id, new_name)
                if errors:
                    for error in errors:
                        st.error(error)
                else:
                    existing_ids = {cow.get("cow_id", "").lower() for cow in cows}
                    if new_cow_id.lower() in existing_ids:
                        st.error("A cow with this ID already exists.")
                    else:
                        try:
                            cow_service.register_cow(
                                cow_id=new_cow_id,
                                name=new_name,
                                breed=new_breed or "Unknown",
                                age_months=int(new_age),
                                status=new_status,
                            )
                            st.session_state.show_herd_form = False
                            st.session_state.selected_cow_id = new_cow_id
                            st.session_state.last_selected_cow = new_cow_id
                            st.session_state.dashboard_needs_refresh = True
                            st.session_state.active_section = "cow_profile"
                            log_event("cow_registered", cow_id=new_cow_id, name=new_name)
                            st.success(f"Cow {new_name} registered successfully!")
                            st.rerun()
                        except Exception as exc:
                            log_error("cow_registration_failed", cow_id=new_cow_id, error=str(exc))
                            st.error("Cow registration could not be completed. Please try again shortly.")

    if not cows:
        st.info("No cows registered yet. Add the first cow to get started.", icon="ℹ️")
        return

    # Build a DataFrame for AG Grid
    df = pd.DataFrame(
        [
            {
                "cow_id": cow.get("cow_id"),
                "name": cow.get("name", ""),
                "breed": cow.get("breed", "N/A"),
                "age_months": int(cow.get("age_months") or 0),
                "status": cow.get("status", "Active"),
                "registered": (cow.get("created_at") or "")[:10] if cow.get("created_at") else "",
            }
            for cow in cows
        ]
    )

    if search_term:
        df = df[df.apply(lambda r: search_term.lower() in str(r["cow_id"]).lower() or search_term.lower() in str(r["name"]).lower(), axis=1)]

    # Metrics
    total_cows = len(df)
    active_cows = int((df["status"] == "Active").sum()) if not df.empty else 0
    avg_age = round(df["age_months"].mean(), 1) if total_cows else 0
    m1, m2, m3 = st.columns(3, gap="medium")
    with m1:
        st.metric("Total cows", total_cows)
    with m2:
        st.metric("Active cows", active_cows)
    with m3:
        st.metric("Average age", f"{avg_age} mo")

    st.markdown("<div style='margin-top: 14px;'></div>", unsafe_allow_html=True)

    # Configure AG Grid
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_selection(selection_mode="single", use_checkbox=False)
    gb.configure_columns(["cow_id", "name"], header_checkbox_selection=False)
    gb.configure_grid_options(domLayout="normal")
    grid_options = gb.build()

    grid_response = AgGrid(df, gridOptions=grid_options, enable_enterprise_modules=False, update_mode=GridUpdateMode.SELECTION_CHANGED, fit_columns_on_grid_load=True)

    selected = grid_response.get("selected_rows") or []
    selected_cow = selected[0] if selected else None

    # Auto-open profile when a row is clicked (user requested behavior)
    if selected_cow:
        cow_id_auto = selected_cow.get("cow_id")
        last = st.session_state.get("last_selected_cow")
        if cow_id_auto and last != cow_id_auto:
            st.session_state.last_selected_cow = cow_id_auto
            st.session_state.selected_cow_id = cow_id_auto
            st.session_state.active_section = "cow_profile"
            st.rerun()

    # Action panel for selected row
    if selected_cow:
        cow_id = selected_cow.get("cow_id")
        st.markdown(f"<div style='margin-top:12px; font-weight:700;'>Actions for {selected_cow.get('name')} · {cow_id}</div>", unsafe_allow_html=True)
        with st.container():
            a1, a2, a3, a4 = st.columns([1, 1, 1, 1], gap="small")
            with a1:
                if st.button("👁 Open Profile", key=f"open_profile_{cow_id}", use_container_width=True):
                    _set_profile_view(cow_id)
            with a2:
                if st.button("✏ Edit", key=f"edit_{cow_id}", use_container_width=True):
                    st.session_state.editing_cow_id = cow_id
            with a3:
                if st.button("📝 Record Observation", key=f"observe_{cow_id}", use_container_width=True):
                    st.session_state.selected_cow_id = cow_id
                    st.session_state.daily_ops_cow = cow_id
                    st.session_state.active_section = "daily_operations"
                    st.rerun()
            with a4:
                if st.button("🧠 Twin", key=f"twin_{cow_id}", use_container_width=True):
                    st.session_state.selected_cow_id = cow_id
                    st.session_state.active_section = "digital_twin"
                    st.rerun()

        with st.container():
            b1, b2, b3, b4 = st.columns([1, 1, 1, 1], gap="small")
            with b1:
                if st.button("📈 Prediction History", key=f"pred_hist_{cow_id}", use_container_width=True):
                    st.session_state.selected_cow_id = cow_id
                    _set_profile_view(cow_id, tab="Prediction History")
            with b2:
                if st.button("❤️ Health History", key=f"health_hist_{cow_id}", use_container_width=True):
                    st.session_state.selected_cow_id = cow_id
                    _set_profile_view(cow_id, tab="Health")
            with b3:
                if st.button("📋 Recommendations", key=f"recs_{cow_id}", use_container_width=True):
                    st.session_state.selected_cow_id = cow_id
                    _set_profile_view(cow_id, tab="Recommendations")
            with b4:
                if st.button("🧪 Prediction Center", key=f"pred_center_{cow_id}", use_container_width=True):
                    st.session_state.selected_cow_id = cow_id
                    st.session_state.active_section = "prediction_center"
                    st.rerun()

        if st.session_state.get("confirm_delete_for") == cow_id:
            st.warning("Please confirm deletion of the selected cow.")
            c1, c2 = st.columns(2, gap="small")
            with c1:
                if st.button("Confirm Delete", key=f"confirm_delete_{cow_id}"):
                    if cow_service.delete_cow(cow_id):
                        if st.session_state.get("selected_cow_id") == cow_id:
                            st.session_state.selected_cow_id = None
                        st.session_state.confirm_delete_for = None
                        # notify dashboard to refresh metrics
                        st.session_state.dashboard_needs_refresh = True
                        st.success(f"Cow {cow_id} deleted successfully")
                        st.rerun()
            with c2:
                if st.button("Cancel", key=f"cancel_delete_{cow_id}"):
                    st.session_state.confirm_delete_for = None
                    st.rerun()

    # Edit flow using expander
    if st.session_state.get("editing_cow_id"):
        ecow = st.session_state.editing_cow_id
        # find cow record
        rec = next((c for c in cows if c.get("cow_id") == ecow), None)
        if rec:
            with st.expander(f"Edit {rec.get('name')} · {ecow}", expanded=True):
                cols = st.columns(3, gap="medium")
                with cols[0]:
                    updated_name = st.text_input("Name", value=rec.get("name", ""), key=f"edit_name_{ecow}")
                with cols[1]:
                    updated_breed = st.text_input("Breed", value=rec.get("breed", ""), key=f"edit_breed_{ecow}")
                with cols[2]:
                    updated_age = st.number_input("Age (months)", min_value=1, max_value=300, value=int(rec.get("age_months") or 24), key=f"edit_age_{ecow}")
                s1, s2 = st.columns([1, 1], gap="small")
                with s1:
                    if st.button("Save", key=f"save_edit_{ecow}", use_container_width=True):
                        cow_service.update_cow(ecow, name=updated_name, breed=updated_breed, age_months=int(updated_age))
                        st.session_state.editing_cow_id = None
                        st.session_state.dashboard_needs_refresh = True
                        st.success("Cow details updated")
                        st.rerun()
                with s2:
                    if st.button("Cancel", key=f"cancel_edit_{ecow}", use_container_width=True):
                        st.session_state.editing_cow_id = None
                        st.rerun()

