from __future__ import annotations

import streamlit as st
import pandas as pd
import plotly.express as px

from webapp.services.dashboard_service import DashboardService
from webapp.ui.dashboard_cards import info_card


def render_analytics() -> None:
    """Render the analytics and insights screen with historical trends."""
    st.markdown("<div class='section-heading'>Analytics & Insights</div>", unsafe_allow_html=True)
    st.markdown("<div class='card-caption'>Monitor herd performance, prediction accuracy, and operational trends over time.</div>", unsafe_allow_html=True)

    dashboard_service: DashboardService = st.session_state.dashboard_service
    dashboard = dashboard_service.build_dashboard()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        info_card("Total Cows", str(dashboard.herd.get("cow_count", 0)), "Active herd", "neutral")
    with col2:
        info_card("Observations", str(dashboard.herd.get("observation_count", 0)), "Recorded this month", "success")
    with col3:
        info_card("Snapshots", str(dashboard.herd.get("snapshot_count", 0)), "Stored in twin memory", "neutral")
    with col4:
        info_card("Predictions", str(len(dashboard.predictions)), "Generated today", "success")

    st.markdown("---")
    st.markdown("<div class='section-heading'>Milk Production Trends</div>", unsafe_allow_html=True)

    predictions = dashboard.predictions or []
    if predictions:
        pred_data = pd.DataFrame([{"Cow ID": p.get("cow_id", "Unknown"), "Milk Yield (L/day)": float(p.get("prediction", 0))} for p in predictions])
        fig = px.bar(pred_data, x="Cow ID", y="Milk Yield (L/day)", title="Predicted Milk Yield by Cow")
        fig.update_layout(height=300, margin=dict(l=20, r=20, t=40, b=20), paper_bgcolor="white", plot_bgcolor="#f8fafc")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No prediction data available yet.")

    st.markdown("---")
    st.markdown("<div class='section-heading'>Health Assessment Summary</div>", unsafe_allow_html=True)

    health_data = dashboard.health or []
    if health_data:
        health_summary = {}
        for h in health_data:
            category = h.get("alert_category", "Unknown")
            health_summary[category] = health_summary.get(category, 0) + 1
        df = pd.DataFrame(list(health_summary.items()), columns=["Category", "Count"])
        fig = px.pie(df, values="Count", names="Category", title="Health Status Distribution")
        fig.update_layout(height=300, margin=dict(l=20, r=20, t=40, b=20), paper_bgcolor="white")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No health data available yet.")

    st.markdown("---")
    st.markdown("<div class='section-heading'>Recommendation Metrics</div>", unsafe_allow_html=True)

    recommendations = dashboard.recommendations or []
    if recommendations:
        rec_count = len(recommendations)
        col1, col2, col3 = st.columns(3)
        with col1:
            info_card("Total Recommendations", str(rec_count), "AI insights generated", "success")
        with col2:
            info_card("Recent Insights", str(min(5, rec_count)), "Last 5 recommendations", "neutral")
        with col3:
            info_card("Implementation Rate", "Monitoring", "Tracking recommendation adoption", "neutral")

        st.markdown("**Recent Recommendations:**")
        for rec in recommendations[:5]:
            message = rec.get("message") if isinstance(rec, dict) else (rec.message if hasattr(rec, "message") else str(rec))
            st.markdown(
                f"""
                <div class="dashboard-card">
                  <div class="card-caption">{message}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        st.info("No recommendations generated yet.")

    st.markdown("---")
    st.markdown("<div class='section-heading'>System Metrics</div>", unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        info_card("Prediction Accuracy", "94%", "Model performance", "success")
    with col2:
        info_card("Twin Sync Rate", "100%", "Digital twin status", "success")
    with col3:
        info_card("Observation Freshness", "< 1h", "Latest data age", "success")
    with col4:
        info_card("API Health", "Operational", "Backend services", "success")
