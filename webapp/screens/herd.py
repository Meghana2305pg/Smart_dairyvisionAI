"""Phase 1.4 - Professional Herd Management Workspace for DairyVision AI."""

from __future__ import annotations

from typing import Any

import pandas as pd
import streamlit as st

from webapp.digital_twin.cow_twin import CowTwin
from webapp.services.cow_service import CowService
from webapp.ui.design_system import render_empty_state
from webapp.utils.logging import log_error, log_event
from webapp.utils.validation import validate_cow_registration_form


def _normalize_cow(cow_data: Any) -> dict[str, Any]:
    """Normalize cow payloads from repository into a dictionary."""
    if isinstance(cow_data, dict) and "cow" in cow_data:
        cow_data = cow_data["cow"]
    return dict(cow_data or {})


def _get_or_create_twin(cow_service: CowService, cow_id: str, name: str | None = None) -> CowTwin:
    """Reuse an existing digital twin or create one from current cow record."""
    twin = cow_service._cow_twins.get(cow_id)
    if twin is None:
        twin = CowTwin(cow_id=cow_id, name=name or cow_id)
        cow_service._cow_twins[cow_id] = twin
    return twin


def _set_profile_view(cow_id: str, tab: str | None = None) -> None:
    """Route user to cow profile screen for selected cow."""
    st.session_state.selected_cow_id = cow_id
    st.session_state.active_section = "cow_profile"
    if tab:
        st.session_state.profile_tab = tab
    st.rerun()


def _status_to_badge(status_value: str) -> tuple[str, str]:
    """Normalize raw status string into management label and tone."""
    raw = str(status_value or "Healthy").strip().lower()
    if any(token in raw for token in ["critical", "alert", "risk", "diseased", "emergency"]):
        return "Critical", "danger"
    if any(token in raw for token in ["warning", "monitor", "inactive", "needs attention"]):
        return "Warning", "warning"
    return "Healthy", "success"


def render_herd() -> None:
    """Render the herd management workspace with Page Header, Action Toolbar, and Data Table."""
    st.markdown(
        """
        <style>
        .herd-workspace {
            padding: 0.1rem 0;
        }

        /* 1. Page Header */
        .herd-header-card {
            background: linear-gradient(135deg, rgba(255, 255, 255, 0.98) 0%, rgba(248, 250, 252, 0.94) 100%);
            border: 1px solid var(--dv-border);
            border-radius: var(--dv-radius-lg);
            padding: 1.25rem 1.4rem;
            margin-bottom: 1.25rem;
            box-shadow: var(--dv-shadow-sm);
        }
        .herd-header-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 1rem;
            flex-wrap: wrap;
        }
        .herd-header-title {
            font-size: clamp(1.4rem, 2.2vw, 2rem);
            font-weight: 800;
            letter-spacing: -0.03em;
            color: var(--dv-text);
            margin: 0;
            line-height: 1.2;
        }
        .herd-header-sub {
            color: var(--dv-muted);
            font-size: 0.92rem;
            margin-top: 0.25rem;
            font-weight: 500;
        }

        /* Summary Stats Pill Grid */
        .herd-stats-bar {
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 0.85rem;
            margin-bottom: 1.25rem;
        }
        .herd-stat-pill {
            background: var(--dv-surface);
            border: 1px solid var(--dv-border);
            border-radius: var(--dv-radius-md);
            padding: 0.85rem 1rem;
            box-shadow: var(--dv-shadow-sm);
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }
        .herd-stat-icon {
            width: 36px;
            height: 36px;
            border-radius: 10px;
            background: var(--dv-surface-alt);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.15rem;
            flex-shrink: 0;
        }
        .herd-stat-val {
            font-size: 1.25rem;
            font-weight: 800;
            color: var(--dv-text);
            line-height: 1.1;
        }
        .herd-stat-lbl {
            font-size: 0.76rem;
            color: var(--dv-muted);
            font-weight: 600;
        }

        /* 2. Action Toolbar */
        .herd-toolbar {
            background: var(--dv-surface);
            border: 1px solid var(--dv-border);
            border-radius: var(--dv-radius-md);
            padding: 0.85rem 1rem;
            margin-bottom: 1.25rem;
            box-shadow: var(--dv-shadow-sm);
        }

        /* Registration Form Panel */
        .herd-form-card {
            background: var(--dv-surface);
            border: 1px solid var(--dv-border);
            border-left: 4px solid var(--dv-accent);
            border-radius: var(--dv-radius-md);
            padding: 1.2rem;
            margin-bottom: 1.25rem;
            box-shadow: var(--dv-shadow-md);
        }

        /* 3. Herd Data Table */
        .herd-table-wrapper {
            background: var(--dv-surface);
            border: 1px solid var(--dv-border);
            border-radius: var(--dv-radius-md);
            box-shadow: var(--dv-shadow-sm);
            overflow: hidden;
            margin-bottom: 1.25rem;
        }
        .herd-table-hdr {
            display: grid;
            grid-template-columns: 1.1fr 1fr 1fr 0.65fr 1fr 1.2fr 0.85fr;
            gap: 0.75rem;
            align-items: center;
            background: var(--dv-surface-alt);
            border-bottom: 1px solid var(--dv-border-strong);
            padding: 0.8rem 1rem;
            font-size: 0.75rem;
            font-weight: 800;
            letter-spacing: 0.06em;
            text-transform: uppercase;
            color: var(--dv-muted);
            position: sticky;
            top: 0;
            z-index: 2;
        }
        .herd-table-row {
            display: grid;
            grid-template-columns: 1.1fr 1fr 1fr 0.65fr 1fr 1.2fr 0.85fr;
            gap: 0.75rem;
            align-items: center;
            padding: 0.75rem 1rem;
            border-bottom: 1px solid var(--dv-border);
            transition: background 150ms ease;
        }
        .herd-table-row:nth-child(even) {
            background: rgba(248, 250, 252, 0.6);
        }
        .herd-table-row:hover {
            background: var(--dv-accent-bg);
        }
        .herd-cell-id {
            font-weight: 700;
            color: var(--dv-text);
            font-size: 0.9rem;
        }
        .herd-cell-txt {
            font-size: 0.88rem;
            color: var(--dv-text);
        }

        @media (max-width: 1024px) {
            .herd-stats-bar { grid-template-columns: repeat(2, minmax(0, 1fr)); }
            .herd-table-hdr, .herd-table-row { grid-template-columns: 1.1fr 1fr 1fr 0.7fr 1fr 1fr 0.9fr; }
        }
        @media (max-width: 768px) {
            .herd-stats-bar { grid-template-columns: 1fr; }
            .herd-table-hdr { display: none; }
            .herd-table-row { grid-template-columns: 1fr 1fr; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    cow_service: CowService = st.session_state.cow_service
    raw_cows = cow_service.get_cows()
    cows = [_normalize_cow(item) for item in raw_cows]

    # ==============================================================================
    # 1. PAGE HEADER
    # ==============================================================================
    col_head_left, col_head_right = st.columns([3, 1])
    with col_head_left:
        st.markdown(
            """
            <div style="margin-bottom:0.85rem;">
                <div style="font-size:0.8rem; font-weight:700; color:var(--dv-accent); text-transform:uppercase; letter-spacing:0.06em;">
                    HERD MANAGEMENT WORKSPACE
                </div>
                <h1 style="font-size:clamp(1.5rem, 2.2vw, 2rem); font-weight:800; color:var(--dv-text); margin:0.1rem 0;">
                    My Herd
                </h1>
                <div style="color:var(--dv-muted); font-size:0.92rem;">
                    Manage, monitor and access all registered cows across your farm.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_head_right:
        st.markdown("<div style='margin-top: 0.75rem;'></div>", unsafe_allow_html=True)
        if st.button("➕ Register Cow", key="btn_open_register_top", type="primary", use_container_width=True):
            st.session_state.show_herd_form = not st.session_state.get("show_herd_form", False)

    # Empty State check
    if not cows:
        st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
        render_empty_state(
            title="No cows have been registered yet",
            message="Register your first cow to begin tracking health, milk output forecasts, and digital twins.",
            icon="🐄",
            action_label="Register First Cow",
            action_key="btn_register_first_cow_empty",
        )
        if st.session_state.get("btn_register_first_cow_empty"):
            st.session_state.show_herd_form = True

        # Render Form Panel when toggled on empty state
        if st.session_state.get("show_herd_form"):
            _render_registration_panel(cow_service, cows)
        return

    # Calculated Herd Summary Metrics
    total_cows = len(cows)
    healthy_cows = sum(1 for cow in cows if str(cow.get("status") or "Active").lower() == "active")
    under_observation = sum(1 for cow in cows if str(cow.get("status") or "Active").lower() != "active")

    # Render Summary Stats Bar
    st.markdown(
        f"""
        <div class="herd-stats-bar">
            <div class="herd-stat-pill">
                <div class="herd-stat-icon">🐄</div>
                <div>
                    <div class="herd-stat-val">{total_cows}</div>
                    <div class="herd-stat-lbl">Total Registered Cows</div>
                </div>
            </div>
            <div class="herd-stat-pill">
                <div class="herd-stat-icon">✅</div>
                <div>
                    <div class="herd-stat-val">{healthy_cows}</div>
                    <div class="herd-stat-lbl">Healthy / Active Status</div>
                </div>
            </div>
            <div class="herd-stat-pill">
                <div class="herd-stat-icon">🔍</div>
                <div>
                    <div class="herd-stat-val">{under_observation}</div>
                    <div class="herd-stat-lbl">Under Observation</div>
                </div>
            </div>
            <div class="herd-stat-pill">
                <div class="herd-stat-icon">💻</div>
                <div>
                    <div class="herd-stat-val">{len(cow_service._cow_twins)}</div>
                    <div class="herd-stat-lbl">Active Digital Twins</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Render Registration Form Panel when toggled
    if st.session_state.get("show_herd_form"):
        _render_registration_panel(cow_service, cows)

    # ==============================================================================
    # 2. ACTION TOOLBAR (Horizontal row with Search, Status, Breed, Sort, Clear, Export)
    # ==============================================================================
    status_options = ["All", "Active", "Inactive"]
    breed_options = sorted({str(cow.get("breed") or "Unknown") for cow in cows})
    breed_list = ["All"] + breed_options
    sort_options = ["Cow ID (Asc)", "Cow ID (Desc)", "Name", "Age (Youngest)", "Age (Oldest)", "Status"]

    selected_status_key = st.session_state.get("herd_status_filter", "All")
    if selected_status_key not in status_options:
        selected_status_key = "All"

    selected_breed_key = st.session_state.get("herd_breed_filter", "All")
    if selected_breed_key not in breed_list:
        selected_breed_key = "All"

    selected_sort_key = st.session_state.get("herd_sort_order", "Cow ID (Asc)")

    def _reset_herd_filters() -> None:
        st.session_state.herd_search_term = ""
        st.session_state.herd_status_filter = "All"
        st.session_state.herd_breed_filter = "All"
        st.session_state.herd_sort_order = "Cow ID (Asc)"

    st.markdown('<div class="herd-toolbar">', unsafe_allow_html=True)
    toolbar_cols = st.columns([2.2, 1.4, 1.4, 1.6, 1.1, 1.3], gap="small")

    with toolbar_cols[0]:
        search_term = st.text_input(
            "Search",
            value=st.session_state.get("herd_search_term", ""),
            placeholder="Search Cow ID or Name...",
            key="herd_search_term",
            label_visibility="collapsed",
        )

    with toolbar_cols[1]:
        selected_status = st.selectbox(
            "Status",
            status_options,
            index=status_options.index(selected_status_key),
            key="herd_status_filter",
            label_visibility="collapsed",
        )

    with toolbar_cols[2]:
        selected_breed = st.selectbox(
            "Breed",
            breed_list,
            index=breed_list.index(selected_breed_key),
            key="herd_breed_filter",
            label_visibility="collapsed",
        )

    with toolbar_cols[3]:
        selected_sort = st.selectbox(
            "Sort By",
            sort_options,
            index=sort_options.index(selected_sort_key) if selected_sort_key in sort_options else 0,
            key="herd_sort_order",
            label_visibility="collapsed",
        )

    with toolbar_cols[4]:
        st.button(
            "Refresh",
            key="btn_clear_herd_filters",
            use_container_width=True,
            type="secondary",
            on_click=_reset_herd_filters,
        )

    with toolbar_cols[5]:
        export_df = pd.DataFrame(
            [
                {
                    "cow_id": cow.get("cow_id"),
                    "name": cow.get("name", ""),
                    "breed": cow.get("breed", "N/A"),
                    "age_months": int(cow.get("age_months") or 0),
                    "status": cow.get("status", "Active"),
                    "last_observation": cow.get("last_observation") or "N/A",
                    "created_at": cow.get("created_at") or "",
                }
                for cow in cows
            ]
        )
        csv_bytes = export_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "📥 Export CSV",
            data=csv_bytes,
            file_name="herd_export.csv",
            mime="text/csv",
            use_container_width=True,
            type="secondary",
        )
    st.markdown("</div>", unsafe_allow_html=True)

    # Filter Cow dataset
    filtered_cows = []
    for cow in cows:
        cid = str(cow.get("cow_id") or "").lower()
        cname = str(cow.get("name") or "").lower()
        sterm = (search_term or "").lower().strip()

        if sterm and sterm not in cid and sterm not in cname:
            continue
        if selected_status != "All" and str(cow.get("status") or "Active").lower() != selected_status.lower():
            continue
        if selected_breed != "All" and str(cow.get("breed") or "Unknown").lower() != selected_breed.lower():
            continue
        filtered_cows.append(cow)

    # Sort Cow dataset
    if selected_sort == "Cow ID (Desc)":
        filtered_cows.sort(key=lambda x: str(x.get("cow_id", "")), reverse=True)
    elif selected_sort == "Name":
        filtered_cows.sort(key=lambda x: str(x.get("name", "")).lower())
    elif selected_sort == "Age (Youngest)":
        filtered_cows.sort(key=lambda x: int(x.get("age_months") or 0))
    elif selected_sort == "Age (Oldest)":
        filtered_cows.sort(key=lambda x: int(x.get("age_months") or 0), reverse=True)
    elif selected_sort == "Status":
        filtered_cows.sort(key=lambda x: str(x.get("status", "")))
    else:
        filtered_cows.sort(key=lambda x: str(x.get("cow_id", "")))

    if not filtered_cows:
        render_empty_state(
            title="No cows match your search or filter criteria",
            message="Try adjusting your search keywords, status filter, or click Refresh to reset active filters.",
            icon="🔎",
        )
        return

    # ==============================================================================
    # 3. HERD DATA TABLE
    # ==============================================================================
    st.markdown('<div class="herd-table-wrapper">', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="herd-table-hdr">
            <div>Cow ID</div>
            <div>Name</div>
            <div>Breed</div>
            <div>Age</div>
            <div>Health Status</div>
            <div>Last Observation</div>
            <div>Actions</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    for cow in filtered_cows:
        cow_id = str(cow.get("cow_id") or "")
        name = str(cow.get("name") or "Unnamed")
        breed = str(cow.get("breed") or "N/A")
        age_months = cow.get("age_months")
        age_text = f"{int(age_months)} mo" if age_months is not None else "N/A"
        status_value = str(cow.get("status") or "Active")
        badge_label, status_tone = _status_to_badge(status_value)
        last_observation = str(cow.get("last_observation") or cow.get("created_at") or "N/A")
        if len(last_observation) > 10:
            last_observation = last_observation[:10]

        with st.container():
            cols = st.columns([1.1, 1, 1, 0.65, 1, 1.2, 0.85], gap="small")
            with cols[0]:
                st.markdown(f"<div class='herd-cell-id'>🐄 {cow_id}</div>", unsafe_allow_html=True)
            with cols[1]:
                st.markdown(f"<div class='herd-cell-txt'>{name}</div>", unsafe_allow_html=True)
            with cols[2]:
                st.markdown(f"<div class='herd-cell-txt'>{breed}</div>", unsafe_allow_html=True)
            with cols[3]:
                st.markdown(f"<div class='herd-cell-txt'>{age_text}</div>", unsafe_allow_html=True)
            with cols[4]:
                st.markdown(f"<span class='status-badge {status_tone}'>{badge_label}</span>", unsafe_allow_html=True)
            with cols[5]:
                st.markdown(f"<div class='herd-cell-txt'>{last_observation}</div>", unsafe_allow_html=True)
            with cols[6]:
                with st.popover("Actions"):
                    if st.button("👤 View Profile", key=f"act_prof_{cow_id}", use_container_width=True):
                        _set_profile_view(cow_id)
                    if st.button("📝 Record Observation", key=f"act_obs_{cow_id}", use_container_width=True):
                        st.session_state.selected_cow_id = cow_id
                        st.session_state.daily_ops_cow = cow_id
                        st.session_state.active_section = "daily_operations"
                        st.rerun()
                    if st.button("💻 Open Digital Twin", key=f"act_dtwin_{cow_id}", use_container_width=True):
                        st.session_state.selected_cow_id = cow_id
                        st.session_state.active_section = "digital_twin"
                        st.rerun()
                    if st.button("📈 Prediction History", key=f"act_pred_{cow_id}", use_container_width=True):
                        _set_profile_view(cow_id, tab="Prediction History")
                    if st.button("🏥 Health History", key=f"act_hlth_{cow_id}", use_container_width=True):
                        _set_profile_view(cow_id, tab="Health")
                    if st.button("✏️ Edit", key=f"act_edit_{cow_id}", use_container_width=True):
                        st.session_state.editing_cow_id = cow_id
                        st.rerun()
                    if st.button("🗑️ Delete", key=f"act_del_{cow_id}", use_container_width=True):
                        st.session_state.confirm_delete_for = cow_id
                        st.rerun()

        # Confirmation Prompt for Deletion
        if st.session_state.get("confirm_delete_for") == cow_id:
            st.markdown("<div style='margin-top:0.4rem;'></div>", unsafe_allow_html=True)
            st.warning(f"⚠️ Are you sure you want to delete Cow {cow_id} ({name})? This action cannot be undone.")
            confirm_cols = st.columns([1, 1], gap="small")
            with confirm_cols[0]:
                if st.button("Confirm Delete", key=f"btn_confirm_del_{cow_id}", use_container_width=True, type="primary"):
                    if cow_service.delete_cow(cow_id):
                        if st.session_state.get("selected_cow_id") == cow_id:
                            st.session_state.selected_cow_id = None
                        st.session_state.confirm_delete_for = None
                        st.session_state.dashboard_needs_refresh = True
                        st.toast(f"Cow {cow_id} deleted successfully", icon="✅")
                        st.rerun()
            with confirm_cols[1]:
                if st.button("Cancel", key=f"btn_cancel_del_{cow_id}", use_container_width=True, type="secondary"):
                    st.session_state.confirm_delete_for = None
                    st.rerun()

        # Inline Edit Form
        if st.session_state.get("editing_cow_id") == cow_id:
            with st.expander(f"Edit Details for Cow #{cow_id}", expanded=True):
                edit_cols = st.columns(3, gap="medium")
                with edit_cols[0]:
                    updated_name = st.text_input("Name", value=name, key=f"input_edit_name_{cow_id}")
                with edit_cols[1]:
                    updated_breed = st.text_input("Breed", value=breed, key=f"input_edit_breed_{cow_id}")
                with edit_cols[2]:
                    updated_age = st.number_input("Age (months)", min_value=1, max_value=300, value=int(age_months or 24), key=f"input_edit_age_{cow_id}")

                save_cols = st.columns([1, 1], gap="small")
                with save_cols[0]:
                    if st.button("Save Changes", key=f"btn_save_edit_{cow_id}", use_container_width=True, type="primary"):
                        cow_service.update_cow(cow_id, name=updated_name, breed=updated_breed, age_months=int(updated_age))
                        st.session_state.editing_cow_id = None
                        st.session_state.dashboard_needs_refresh = True
                        st.toast("Cow details updated successfully", icon="✅")
                        st.rerun()
                with save_cols[1]:
                    if st.button("Cancel", key=f"btn_cancel_edit_{cow_id}", use_container_width=True, type="secondary"):
                        st.session_state.editing_cow_id = None
                        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


def _render_registration_panel(cow_service: CowService, cows: list[dict[str, Any]]) -> None:
    """Render expandable Registration Panel/Modal for adding a new cow."""
    st.markdown('<div class="herd-form-card">', unsafe_allow_html=True)
    st.markdown(
        """
        <div style="font-weight:700; font-size:1.05rem; color:var(--dv-text); margin-bottom:0.2rem;">
            ➕ Register New Cow
        </div>
        <div style="font-size:0.83rem; color:var(--dv-muted); margin-bottom:0.85rem;">
            Enter official herd identification, breed details, age, weight, and initial health status.
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.form("register_cow_modal_form"):
        col1, col2 = st.columns(2, gap="medium")
        with col1:
            new_cow_id = st.text_input("Cow ID", placeholder="e.g., cow-001")
        with col2:
            new_name = st.text_input("Name", placeholder="e.g., Bessie")

        col3, col4, col5 = st.columns(3, gap="medium")
        with col3:
            new_breed = st.text_input("Breed", placeholder="e.g., Holstein")
        with col4:
            new_age = st.number_input("Age (months)", min_value=1, max_value=300, value=24)
        with col5:
            new_weight = st.number_input("Weight (kg)", min_value=1.0, max_value=1500.0, value=450.0, step=0.5)

        col6, col7 = st.columns(2, gap="medium")
        with col6:
            new_status = st.selectbox("Health Status", ["Active", "Inactive"], index=0)
        with col7:
            new_notes = st.text_area("Notes", value="", placeholder="Enter notes or observations...")

        sub_col1, sub_col2 = st.columns([1, 1], gap="small")
        with sub_col1:
            register_submit = st.form_submit_button("Complete Registration", use_container_width=True, type="primary")
        with sub_col2:
            cancel_submit = st.form_submit_button("Cancel", use_container_width=True, type="secondary")

        if cancel_submit:
            st.session_state.show_herd_form = False
            st.rerun()

        if register_submit:
            errors = validate_cow_registration_form(new_cow_id, new_name)
            if errors:
                for err in errors:
                    st.error(err)
            else:
                existing_ids = {str(c.get("cow_id") or "").lower() for c in cows}
                if new_cow_id.lower() in existing_ids:
                    st.error(f"A cow with ID '{new_cow_id}' already exists.")
                else:
                    try:
                        cow_service.register_cow(
                            cow_id=new_cow_id,
                            name=new_name,
                            breed=new_breed or "Unknown",
                            age_months=int(new_age),
                            status=new_status,
                            weight=float(new_weight),
                            notes=new_notes,
                        )
                        st.session_state.show_herd_form = False
                        st.session_state.selected_cow_id = new_cow_id
                        st.session_state.last_selected_cow = new_cow_id
                        st.session_state.dashboard_needs_refresh = True
                        log_event("cow_registered", cow_id=new_cow_id, name=new_name)
                        st.toast(f"Cow {new_name} ({new_cow_id}) registered successfully!", icon="✅")
                        st.rerun()
                    except Exception as exc:
                        st.exception(exc)
                        raise
    st.markdown("</div>", unsafe_allow_html=True)
