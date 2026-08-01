"""Herd management screen for DairyVision AI."""
from __future__ import annotations

from typing import Any

import pandas as pd
import streamlit as st

from webapp.digital_twin.cow_twin import CowTwin
from webapp.services.cow_service import CowService
from webapp.utils.logging import log_error, log_event
from webapp.utils.validation import validate_cow_registration_form


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


def _status_to_badge(status_value: str) -> tuple[str, str]:
    """Normalize a raw status string into a management-friendly label and tone."""
    raw = str(status_value or "Healthy").strip().lower()
    if any(token in raw for token in ["critical", "alert", "risk", "diseased", "emergency"]):
        return "Critical", "danger"
    if any(token in raw for token in ["warning", "monitor", "inactive", "needs attention"]):
        return "Warning", "warning"
    return "Healthy", "success"


def render_herd() -> None:
    """Render the herd management screen with a polished management workspace."""
    st.markdown(
        """
        <style>
        .herd-page {
            padding-top: 0.25rem;
        }
        .herd-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 1rem;
            flex-wrap: wrap;
            margin-bottom: 1rem;
        }
        .herd-header-title {
            font-size: clamp(1.8rem, 2vw, 2.2rem);
            font-weight: 800;
            letter-spacing: -0.04em;
            margin: 0;
            color: #0f172a;
        }
        .herd-header-subtitle {
            color: #64748b;
            font-size: 0.96rem;
            margin-top: 0.25rem;
        }
        .herd-actions {
            display: flex;
            gap: 0.75rem;
            align-items: center;
            flex-wrap: wrap;
        }
        .herd-summary-grid {
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 0.85rem;
            margin-bottom: 1rem;
        }
        .summary-card {
            background: rgba(255,255,255,0.96);
            border: 1px solid rgba(148,163,184,0.16);
            border-radius: 18px;
            padding: 1rem 1rem 0.8rem;
            box-shadow: 0 10px 22px rgba(15, 23, 42, 0.04);
            min-height: 128px;
            transition: transform 180ms ease, box-shadow 180ms ease;
        }
        .summary-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 14px 28px rgba(15, 23, 42, 0.08);
        }
        .summary-card .label {
            color: #64748b;
            font-size: 0.72rem;
            letter-spacing: 0.07em;
            font-weight: 800;
            text-transform: uppercase;
        }
        .summary-card .value {
            font-size: clamp(1.4rem, 1.8vw, 1.9rem);
            font-weight: 800;
            letter-spacing: -0.04em;
            color: #0f172a;
            margin: 0.5rem 0 0.35rem;
        }
        .summary-card .meta {
            font-size: 0.82rem;
            color: #475569;
        }
        .summary-card .icon {
            width: 2.2rem;
            height: 2.2rem;
            border-radius: 12px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            font-size: 1.05rem;
            margin-bottom: 0.75rem;
            background: rgba(37,99,235,0.08);
            color: #1d4ed8;
        }
        .summary-card.green .icon { background: rgba(21,128,61,0.10); color: #15803d; }
        .summary-card.amber .icon { background: rgba(245,158,11,0.12); color: #b45309; }
        .summary-card.red .icon { background: rgba(239,68,68,0.10); color: #b91c1c; }
        .filters-shell {
            background: rgba(255,255,255,0.96);
            border: 1px solid rgba(148,163,184,0.16);
            border-radius: 18px;
            box-shadow: 0 10px 22px rgba(15, 23, 42, 0.04);
            padding: 0.9rem 1rem;
            margin-bottom: 1rem;
        }
        div[data-testid="stTextInput"] > div > div > input,
        div[data-testid="stSelectbox"] > div > div,
        div[data-testid="stNumberInput"] > div > div > input {
            border-radius: 12px !important;
            border: 1px solid rgba(148,163,184,0.45) !important;
            background: rgba(248,250,252,0.9) !important;
            box-shadow: none !important;
        }
        div[data-testid="stTextInput"] > div > div > input:focus,
        div[data-testid="stSelectbox"] > div > div:focus,
        div[data-testid="stNumberInput"] > div > div > input:focus {
            border-color: rgba(37,99,235,0.55) !important;
            box-shadow: 0 0 0 0.2rem rgba(37,99,235,0.14) !important;
        }
        .table-shell {
            background: rgba(255,255,255,0.96);
            border: 1px solid rgba(148,163,184,0.16);
            border-radius: 18px;
            box-shadow: 0 12px 24px rgba(15, 23, 42, 0.04);
            overflow: hidden;
        }
        .herd-table-header {
            display: grid;
            grid-template-columns: 1.1fr 1fr 1fr 0.6fr 1fr 1.2fr 0.8fr;
            gap: 0.75rem;
            align-items: center;
            background: #f8fafc;
            border-bottom: 1px solid rgba(148,163,184,0.15);
            padding: 0.8rem 1rem;
            font-size: 0.75rem;
            font-weight: 800;
            letter-spacing: 0.07em;
            text-transform: uppercase;
            color: #475569;
            position: sticky;
            top: 0;
            z-index: 2;
        }
        .herd-table-row {
            display: grid;
            grid-template-columns: 1.1fr 1fr 1fr 0.6fr 1fr 1.2fr 0.8fr;
            gap: 0.75rem;
            align-items: center;
            padding: 0.8rem 1rem;
            border-bottom: 1px solid rgba(148,163,184,0.12);
            transition: background 180ms ease;
        }
        .herd-table-row:nth-child(even) { background: rgba(248,250,252,0.8); }
        .herd-table-row:hover { background: rgba(239,246,255,0.70); }
        .herd-cell {
            color: #0f172a;
            font-size: 0.93rem;
            line-height: 1.4;
        }
        .herd-row-id {
            font-weight: 700;
            color: #0f172a;
        }
        .status-badge {
            display: inline-flex;
            align-items: center;
            border-radius: 999px;
            padding: 0.35rem 0.6rem;
            font-size: 0.72rem;
            font-weight: 700;
        }
        .status-badge.success { background: rgba(21,128,61,0.10); color: #15803d; }
        .status-badge.warning { background: rgba(245,158,11,0.12); color: #b45309; }
        .status-badge.danger { background: rgba(239,68,68,0.10); color: #b91c1c; }
        .status-badge.neutral { background: rgba(148,163,184,0.12); color: #475569; }
        .empty-state {
            background: linear-gradient(135deg, rgba(248,250,252,1), rgba(255,255,255,0.96));
            border: 1px dashed rgba(148,163,184,0.35);
            border-radius: 22px;
            padding: 2rem 1.2rem;
            text-align: center;
            margin-top: 1rem;
        }
        .empty-state-icon {
            font-size: 2.7rem;
            margin-bottom: 0.6rem;
        }
        .empty-state-title {
            font-size: 1.8rem;
            font-weight: 800;
            letter-spacing: -0.04em;
            color: #0f172a;
            margin-bottom: 0.3rem;
        }
        .empty-state-copy {
            color: #64748b;
            font-size: 1rem;
            max-width: 620px;
            margin: 0 auto 1rem;
            line-height: 1.6;
        }
        .form-card {
            background: rgba(255,255,255,0.96);
            border: 1px solid rgba(148,163,184,0.16);
            border-radius: 20px;
            box-shadow: 0 12px 24px rgba(15, 23, 42, 0.04);
            padding: 1rem 1rem 0.3rem;
            margin-bottom: 1rem;
        }
        .section-divider {
            border-top: 1px solid rgba(148,163,184,0.18);
            margin: 1rem 0 0.8rem;
        }
        .section-label {
            font-size: 0.74rem;
            font-weight: 800;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            color: #475569;
            margin-bottom: 0.6rem;
        }
        @media (max-width: 1100px) {
            .herd-summary-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
            .herd-table-header, .herd-table-row { grid-template-columns: 1.1fr 1fr 1fr 0.7fr 1fr 1fr 0.9fr; }
        }
        @media (max-width: 760px) {
            .herd-summary-grid { grid-template-columns: 1fr; }
            .herd-header { align-items: flex-start; }
            .herd-table-header { display: none; }
            .herd-table-row {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 0.5rem;
                padding: 0.9rem 0.8rem;
            }
            .herd-table-row > div:nth-child(1), .herd-table-row > div:nth-child(2), .herd-table-row > div:nth-child(3), .herd-table-row > div:nth-child(4), .herd-table-row > div:nth-child(5), .herd-table-row > div:nth-child(6), .herd-table-row > div:nth-child(7) {
                padding: 0.05rem 0;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    cow_service: CowService = st.session_state.cow_service
    raw_cows = cow_service.get_cows()
    cows = [_normalize_cow(item) for item in raw_cows]

    if not cows:
        st.markdown('<div class="herd-page">', unsafe_allow_html=True)
        st.markdown(
            """
            <div class="herd-header">
                <div>
                    <h1 class="herd-header-title">Herd Management</h1>
                    <div class="herd-header-subtitle">Manage, monitor and organize your dairy herd.</div>
                </div>
                <div class="herd-actions">
                    <button style="display:none"></button>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(
            """
            <div class="empty-state">
                <div class="empty-state-icon">🐄</div>
                <div class="empty-state-title">Your herd is empty.</div>
                <div class="empty-state-copy">Register your first cow to begin monitoring health, milk prediction and digital twins.</div>
                <button type='button' onclick='window.scrollTo(0,0)'></button>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if not st.session_state.get("show_herd_form"):
            if st.button("Register First Cow", key="register_first_cow_empty", use_container_width=True, type="primary"):
                st.session_state.show_herd_form = True
        if st.session_state.get("show_herd_form"):
            st.markdown('<div class="form-card">', unsafe_allow_html=True)
            with st.form("register_cow_empty_form"):
                st.markdown('<div class="section-label">Identity</div>', unsafe_allow_html=True)
                col1, col2 = st.columns(2, gap="medium")
                with col1:
                    new_cow_id = st.text_input("Cow ID", placeholder="e.g., cow-001")
                with col2:
                    new_name = st.text_input("Name", placeholder="e.g., Bessie")
                st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
                st.markdown('<div class="section-label">Breed</div>', unsafe_allow_html=True)
                new_breed = st.text_input("Breed", placeholder="e.g., Holstein")
                st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
                st.markdown('<div class="section-label">Age & Weight</div>', unsafe_allow_html=True)
                col3, col4 = st.columns(2, gap="medium")
                with col3:
                    new_age = st.number_input("Age (months)", min_value=1, max_value=300, value=24)
                with col4:
                    new_weight = st.number_input("Weight (kg)", min_value=1.0, max_value=1500.0, value=450.0, step=0.5)
                st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
                st.markdown('<div class="section-label">Health & Notes</div>', unsafe_allow_html=True)
                col5, col6 = st.columns(2, gap="medium")
                with col5:
                    new_status = st.selectbox("Health Status", ["Active", "Inactive"], index=0)
                with col6:
                    new_notes = st.text_area("Notes", value="", placeholder="Enter any notes for this cow")
                submit_col, cancel_col = st.columns([1, 1], gap="small")
                with submit_col:
                    register_submit = st.form_submit_button("Register Cow", use_container_width=True, type="primary")
                with cancel_col:
                    cancel_submit = st.form_submit_button("Cancel", use_container_width=True, type="secondary")
                if cancel_submit:
                    st.session_state.show_herd_form = False
            if register_submit:
                errors = validate_cow_registration_form(new_cow_id, new_name)
                if errors:
                    for error in errors:
                        st.error(error)
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
                        st.session_state.active_section = "cow_profile"
                        log_event("cow_registered", cow_id=new_cow_id, name=new_name)
                        st.success(f"Cow {new_name} registered successfully!")
                    except Exception as exc:
                        log_error("cow_registration_failed", cow_id=new_cow_id, error=str(exc))
                        st.error("Cow registration could not be completed. Please try again shortly.")
            st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        return

    status_options = ["All", "Active", "Inactive"]
    breed_options = sorted({str(cow.get("breed") or "Unknown") for cow in cows})
    selected_status_key = st.session_state.get("herd_status_filter", "All")
    if selected_status_key not in status_options:
        selected_status_key = "All"
    selected_breed_key = st.session_state.get("herd_breed_filter", "All")
    breed_list = ["All"] + breed_options
    if selected_breed_key not in breed_list:
        selected_breed_key = "All"
    search_term = st.session_state.get("herd_search_term", "")

    total_cows = len(cows)
    healthy_cows = sum(1 for cow in cows if str(cow.get("status") or "Active").lower() == "active")
    under_observation = sum(1 for cow in cows if str(cow.get("status") or "Active").lower() == "inactive")
    recent_added = 0
    for cow in cows:
        created_at = str(cow.get("created_at") or "")
        if created_at:
            try:
                from datetime import datetime
                if (datetime.utcnow() - datetime.fromisoformat(created_at[:19].replace("Z", "+00:00")).replace(tzinfo=None)).days <= 7:
                    recent_added += 1
            except Exception:
                pass

    st.markdown('<div class="herd-page">', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="herd-header">
            <div>
                <h1 class="herd-header-title">Herd Management</h1>
                <div class="herd-header-subtitle">Manage, monitor and organize your dairy herd.</div>
            </div>
            <div class="herd-actions">
                <div>
                    <button type='button'> </button>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    header_buttons = st.columns([1.3, 1], gap="small")
    with header_buttons[0]:
        if not st.session_state.get("show_herd_form"):
            if st.button("+ Register Cow", key="herd_register_primary", use_container_width=True, type="primary"):
                st.session_state.show_herd_form = True
    with header_buttons[1]:
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
        st.download_button("Export CSV", data=csv_bytes, file_name="herd_export.csv", mime="text/csv", use_container_width=True, type="secondary")

    st.markdown(
        """
        <div class="herd-summary-grid">
            <div class="summary-card">
                <div class="icon">🐄</div>
                <div class="label">Total Cows</div>
                <div class="value">{}</div>
                <div class="meta">Tracked herd size</div>
            </div>
            <div class="summary-card green">
                <div class="icon">✅</div>
                <div class="label">Healthy Cows</div>
                <div class="value">{}</div>
                <div class="meta">Currently in good health</div>
            </div>
            <div class="summary-card amber">
                <div class="icon">👀</div>
                <div class="label">Under Observation</div>
                <div class="value">{}</div>
                <div class="meta">Requires follow-up</div>
            </div>
            <div class="summary-card red">
                <div class="icon">🆕</div>
                <div class="label">Recently Added</div>
                <div class="value">{}</div>
                <div class="meta">Within the last 7 days</div>
            </div>
        </div>
        """.format(total_cows, healthy_cows, under_observation, recent_added),
        unsafe_allow_html=True,
    )

    st.markdown('<div class="filters-shell">', unsafe_allow_html=True)
    filter_cols = st.columns([2.2, 2.2, 1.5, 1.5, 1.1], gap="small")
    with filter_cols[0]:
        search_term = st.text_input("Search by Cow ID", value=search_term, placeholder="e.g., cow-001", key="herd_search_term")
    with filter_cols[1]:
        name_search = st.text_input("Search by Name", value=st.session_state.get("herd_name_filter", ""), key="herd_name_filter", placeholder="e.g., Bessie")
    with filter_cols[2]:
        selected_status = st.selectbox("Health Status", status_options, index=status_options.index(selected_status_key), key="herd_status_filter")
    with filter_cols[3]:
        selected_breed = st.selectbox("Breed", breed_list, index=breed_list.index(selected_breed_key), key="herd_breed_filter")
    with filter_cols[4]:
        if st.button("Clear Filters", key="herd_clear_filters", use_container_width=True, type="secondary"):
            st.session_state.herd_search_term = ""
            st.session_state.herd_name_filter = ""
            st.session_state.herd_status_filter = "All"
            st.session_state.herd_breed_filter = "All"
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    if st.session_state.get("show_herd_form"):
        st.markdown('<div class="form-card">', unsafe_allow_html=True)
        with st.form("register_cow_form"):
            st.markdown('<div class="section-label">Section 1 · Identity</div>', unsafe_allow_html=True)
            identity_cols = st.columns(2, gap="medium")
            with identity_cols[0]:
                new_cow_id = st.text_input("Cow ID", placeholder="e.g., cow-001")
            with identity_cols[1]:
                new_name = st.text_input("Name", placeholder="e.g., Bessie")
            st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
            st.markdown('<div class="section-label">Section 2 · Breed</div>', unsafe_allow_html=True)
            new_breed = st.text_input("Breed", placeholder="e.g., Holstein")
            st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
            st.markdown('<div class="section-label">Section 3 · Age</div>', unsafe_allow_html=True)
            age_cols = st.columns(2, gap="medium")
            with age_cols[0]:
                new_age = st.number_input("Age (months)", min_value=1, max_value=300, value=24)
            with age_cols[1]:
                new_weight = st.number_input("Weight (kg)", min_value=1.0, max_value=1500.0, value=450.0, step=0.5)
            st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
            st.markdown('<div class="section-label">Section 4 · Health Status & Notes</div>', unsafe_allow_html=True)
            health_cols = st.columns(2, gap="medium")
            with health_cols[0]:
                new_status = st.selectbox("Health Status", ["Active", "Inactive"], index=0)
            with health_cols[1]:
                new_notes = st.text_area("Notes", value="", placeholder="Enter any notes for this cow")
            submit_col, cancel_col = st.columns([1, 1], gap="small")
            with submit_col:
                submitted_register = st.form_submit_button("Register Cow", type="primary", use_container_width=True)
            with cancel_col:
                cancel_submit = st.form_submit_button("Cancel", type="secondary", use_container_width=True)
            if cancel_submit:
                st.session_state.show_herd_form = False
        if submitted_register and not cancel_submit:
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
                            weight=float(new_weight),
                            notes=new_notes,
                        )
                        st.session_state.show_herd_form = False
                        st.session_state.selected_cow_id = new_cow_id
                        st.session_state.last_selected_cow = new_cow_id
                        st.session_state.dashboard_needs_refresh = True
                        st.session_state.active_section = "cow_profile"
                        log_event("cow_registered", cow_id=new_cow_id, name=new_name)
                        st.success(f"Cow {new_name} registered successfully!")
                    except Exception as exc:
                        log_error("cow_registration_failed", cow_id=new_cow_id, error=str(exc))
                        st.error("Cow registration could not be completed. Please try again shortly.")
        st.markdown('</div>', unsafe_allow_html=True)

    filtered_cows = []
    for cow in cows:
        if search_term and search_term.lower() not in str(cow.get("cow_id", "")).lower() and search_term.lower() not in str(cow.get("name", "")).lower():
            continue
        if name_search and name_search.lower() not in str(cow.get("name", "")).lower():
            continue
        if selected_status != "All" and str(cow.get("status") or "Active").lower() != selected_status.lower():
            continue
        if selected_breed != "All" and str(cow.get("breed") or "Unknown").lower() != selected_breed.lower():
            continue
        filtered_cows.append(cow)

    if not filtered_cows:
        st.markdown(
            """
            <div class="empty-state">
                <div class="empty-state-icon">🔎</div>
                <div class="empty-state-title">No cows match your filters.</div>
                <div class="empty-state-copy">Try a different search term or clear the selected filters to see the full herd.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    st.markdown('<div class="table-shell">', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="herd-table-header">
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
        last_observation = "N/A"
        if cow.get("last_observation"):
            last_observation = str(cow.get("last_observation"))
        elif cow.get("created_at"):
            last_observation = str(cow.get("created_at"))[:10]

        with st.container():
            cols = st.columns([1.1, 1, 1, 0.6, 1, 1.2, 0.8], gap="small")
            with cols[0]:
                st.markdown(f"<div class='herd-cell herd-row-id'>{cow_id}</div>", unsafe_allow_html=True)
            with cols[1]:
                st.markdown(f"<div class='herd-cell'>{name}</div>", unsafe_allow_html=True)
            with cols[2]:
                st.markdown(f"<div class='herd-cell'>{breed}</div>", unsafe_allow_html=True)
            with cols[3]:
                st.markdown(f"<div class='herd-cell'>{age_text}</div>", unsafe_allow_html=True)
            with cols[4]:
                st.markdown(f"<span class='status-badge {status_tone}'>{badge_label}</span>", unsafe_allow_html=True)
            with cols[5]:
                st.markdown(f"<div class='herd-cell'>{last_observation}</div>", unsafe_allow_html=True)
            with cols[6]:
                with st.popover("Actions"):
                    if st.button("View Profile", key=f"herd_view_{cow_id}", use_container_width=True, type="secondary"):
                        _set_profile_view(cow_id)
                    if st.button("Record Observation", key=f"herd_observe_{cow_id}", use_container_width=True, type="secondary"):
                        st.session_state.selected_cow_id = cow_id
                        st.session_state.daily_ops_cow = cow_id
                        st.session_state.active_section = "daily_operations"
                        st.rerun()
                    if st.button("Open Digital Twin", key=f"herd_twin_{cow_id}", use_container_width=True, type="secondary"):
                        st.session_state.selected_cow_id = cow_id
                        st.session_state.active_section = "digital_twin"
                        st.rerun()
                    if st.button("Prediction History", key=f"herd_pred_hist_{cow_id}", use_container_width=True, type="secondary"):
                        st.session_state.selected_cow_id = cow_id
                        _set_profile_view(cow_id, tab="Prediction History")
                    if st.button("Health History", key=f"herd_health_hist_{cow_id}", use_container_width=True, type="secondary"):
                        st.session_state.selected_cow_id = cow_id
                        _set_profile_view(cow_id, tab="Health")
                    if st.button("Edit", key=f"herd_edit_{cow_id}", use_container_width=True, type="secondary"):
                        st.session_state.editing_cow_id = cow_id
                    if st.button("Delete", key=f"herd_delete_{cow_id}", use_container_width=True, type="secondary"):
                        st.session_state.confirm_delete_for = cow_id

        if st.session_state.get("confirm_delete_for") == cow_id:
            st.warning("Please confirm deletion of this cow.")
            confirm_cols = st.columns([1, 1], gap="small")
            with confirm_cols[0]:
                if st.button("Confirm Delete", key=f"confirm_delete_{cow_id}", use_container_width=True, type="primary"):
                    if cow_service.delete_cow(cow_id):
                        if st.session_state.get("selected_cow_id") == cow_id:
                            st.session_state.selected_cow_id = None
                        st.session_state.confirm_delete_for = None
                        st.session_state.dashboard_needs_refresh = True
                        st.success(f"Cow {cow_id} deleted successfully")
                        st.rerun()
            with confirm_cols[1]:
                if st.button("Cancel", key=f"cancel_delete_{cow_id}", use_container_width=True, type="secondary"):
                    st.session_state.confirm_delete_for = None
                    st.rerun()

        if st.session_state.get("editing_cow_id") == cow_id:
            with st.expander(f"Edit {name}", expanded=True):
                edit_cols = st.columns(3, gap="medium")
                with edit_cols[0]:
                    updated_name = st.text_input("Name", value=name, key=f"edit_name_{cow_id}")
                with edit_cols[1]:
                    updated_breed = st.text_input("Breed", value=breed, key=f"edit_breed_{cow_id}")
                with edit_cols[2]:
                    updated_age = st.number_input("Age (months)", min_value=1, max_value=300, value=int(age_months or 24), key=f"edit_age_{cow_id}")
                save_cols = st.columns([1, 1], gap="small")
                with save_cols[0]:
                    if st.button("Save", key=f"save_edit_{cow_id}", use_container_width=True, type="primary"):
                        cow_service.update_cow(cow_id, name=updated_name, breed=updated_breed, age_months=int(updated_age))
                        st.session_state.editing_cow_id = None
                        st.session_state.dashboard_needs_refresh = True
                        st.success("Cow details updated")
                        st.rerun()
                with save_cols[1]:
                    if st.button("Cancel", key=f"cancel_edit_{cow_id}", use_container_width=True, type="secondary"):
                        st.session_state.editing_cow_id = None
                        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

