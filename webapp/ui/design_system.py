"""DairyVision AI Centralized Design System.

Provides semantic design tokens, WCAG AA accessible styles, global theme injection,
and reusable UI helper components across the application.
"""

from __future__ import annotations

from html import escape

import streamlit as st

# ==============================================================================
# 1. SEMANTIC COLOR PALETTE (WCAG AA Compliant)
# ==============================================================================
PRIMARY = "#2563eb"          # Royal Blue (Primary actions, links)
PRIMARY_HOVER = "#1d4ed8"    # Darker Royal Blue (Hover states)
PRIMARY_BG = "#eff6ff"       # Tinted Light Blue Background

SECONDARY = "#475569"        # Slate Secondary Accent
SECONDARY_HOVER = "#334155"  # Darker Slate Accent
SECONDARY_BG = "#f8fafc"     # Slate Light Background

SUCCESS = "#15803d"          # Emerald Green (7:1 contrast on white)
SUCCESS_BG = "#f0fdf4"       # Light Tint Green
SUCCESS_BORDER = "rgba(21, 128, 61, 0.20)"

WARNING = "#b45309"          # Dark Amber/Brown (6.5:1 contrast on white)
WARNING_BG = "#fffbeb"       # Light Tint Amber
WARNING_BORDER = "rgba(180, 83, 9, 0.20)"

DANGER = "#b91c1c"           # Dark Red (7:1 contrast on white)
DANGER_BG = "#fef2f2"        # Light Tint Red
DANGER_BORDER = "rgba(185, 28, 28, 0.20)"

INFO = "#1d4ed8"             # Deep Blue Info Tone
INFO_BG = "#f0f9ff"          # Light Tint Cyan/Blue
INFO_BORDER = "rgba(29, 78, 216, 0.20)"

NEUTRAL = "#475569"          # Dark Slate Neutral Tone
NEUTRAL_BG = "#f8fafc"       # Light Tint Gray
NEUTRAL_BORDER = "rgba(71, 85, 105, 0.18)"

# Surfaces & Structural Colors
BACKGROUND = "#f8fafc"
SURFACE = "#ffffff"
SURFACE_ALT = "#f1f5f9"
SURFACE_CARD = "#ffffff"

# Typography Colors (High Contrast)
TEXT_PRIMARY = "#0f172a"     # Dark Slate (15:1 contrast ratio)
TEXT_SECONDARY = "#475569"   # Slate (7:1 contrast ratio - passes WCAG AA)
TEXT_MUTED = "#64748b"       # Muted Slate (4.5:1 contrast ratio)
TEXT_INVERSE = "#ffffff"     # Pure White

# Borders
BORDER = "rgba(15, 23, 42, 0.10)"
BORDER_STRONG = "rgba(15, 23, 42, 0.18)"
BORDER_FOCUS = "#2563eb"

# Status Specific Tokens
STATUS_STABLE = "#15803d"
STATUS_WATCH = "#b45309"
STATUS_SEVERE = "#b91c1c"

# Structural Heights & Widths
SIDEBAR_WIDTH = "260px"
TOPBAR_HEIGHT = "56px"
CONTAINER_MAX_WIDTH = "1320px"
INPUT_HEIGHT = "42px"
BUTTON_HEIGHT = "42px"

# ==============================================================================
# 2. TYPOGRAPHY SCALE TOKENS
# ==============================================================================
FONT_FAMILY = (
    '"Avenir Next", "Segoe UI Variable", "SF Pro Text", "Helvetica Neue", sans-serif'
)

FONT_PAGE_TITLE = "clamp(1.6rem, 2.2vw, 2.2rem)"
FONT_SECTION_TITLE = "1.25rem"
FONT_CARD_TITLE = "0.9rem"
FONT_METRIC_VALUE = "clamp(1.5rem, 2vw, 2rem)"
FONT_BODY = "0.95rem"
FONT_CAPTION = "0.8rem"

# ==============================================================================
# 3. SPACING SCALE TOKENS
# ==============================================================================
SPACING_XS = "0.25rem"    # 4px
SPACING_SM = "0.5rem"     # 8px
SPACING_MD = "1rem"       # 16px
SPACING_LG = "1.5rem"    # 24px
SPACING_XL = "2rem"      # 32px
SPACING_XXL = "3rem"     # 48px

# ==============================================================================
# 4. BORDER RADIUS TOKENS
# ==============================================================================
RADIUS_SMALL = "10px"
RADIUS_MEDIUM = "16px"
RADIUS_LARGE = "24px"

# ==============================================================================
# 5. SHADOW TOKENS
# ==============================================================================
SHADOW_SM = "0 4px 16px rgba(15, 23, 42, 0.04)"
SHADOW_MD = "0 12px 28px rgba(15, 23, 42, 0.06)"
SHADOW_LG = "0 18px 50px rgba(15, 23, 42, 0.08)"
SHADOW_CARD = "0 10px 22px rgba(15, 23, 42, 0.04)"
SHADOW_DIALOG = "0 20px 40px rgba(15, 23, 42, 0.12)"
SHADOW_DROPDOWN = "0 10px 25px rgba(15, 23, 42, 0.10)"
SHADOW_FLOATING = "0 14px 28px rgba(15, 23, 42, 0.08)"

# ==============================================================================
# 6. GLOBAL THEME INJECTION
# ==============================================================================
def apply_global_theme() -> None:
    """Inject the global CSS theme definitions into Streamlit."""
    st.markdown(
        f"""
        <style>
        :root {{
            --dv-bg: {BACKGROUND};
            --dv-surface: {SURFACE};
            --dv-surface-alt: {SURFACE_ALT};
            --dv-border: {BORDER};
            --dv-border-strong: {BORDER_STRONG};
            --dv-text: {TEXT_PRIMARY};
            --dv-muted: {TEXT_SECONDARY};
            --dv-muted-2: {TEXT_MUTED};
            --dv-accent: {PRIMARY};
            --dv-accent-strong: {PRIMARY_HOVER};
            --dv-success: {SUCCESS};
            --dv-success-bg: {SUCCESS_BG};
            --dv-warning: {WARNING};
            --dv-warning-bg: {WARNING_BG};
            --dv-danger: {DANGER};
            --dv-danger-bg: {DANGER_BG};
            --dv-info: {INFO};
            --dv-info-bg: {INFO_BG};
            --dv-radius-sm: {RADIUS_SMALL};
            --dv-radius-md: {RADIUS_MEDIUM};
            --dv-radius-lg: {RADIUS_LARGE};
            --dv-shadow-sm: {SHADOW_SM};
            --dv-shadow-md: {SHADOW_MD};
            --dv-shadow-lg: {SHADOW_LG};
            --dv-font-family: {FONT_FAMILY};
        }}

        html, body, [data-testid="stAppViewContainer"] {{
            background:
                radial-gradient(circle at top left, rgba(37, 99, 235, 0.06), transparent 28%),
                radial-gradient(circle at top right, rgba(21, 128, 61, 0.06), transparent 22%),
                linear-gradient(180deg, #f8fafc 0%, #f5f7fb 48%, #eef2f7 100%);
            color: var(--dv-text);
            font-family: var(--dv-font-family);
            font-size: {FONT_BODY};
            line-height: 1.5;
            -webkit-font-smoothing: antialiased;
        }}

        .stApp {{
            background: transparent;
        }}

        .block-container {{
            overflow-x: hidden !important;
        }}

        [data-testid="stHeader"],
        [data-testid="stToolbar"],
        [data-testid="stDecoration"] {{
            display: none !important;
        }}

        [data-testid="stSidebarNav"] {{
            display: none !important;
        }}

        /* Left Sidebar styling */
        section[data-testid="stSidebar"] {{
            background: transparent !important;
            min-width: 0 !important;
        }}

        section[data-testid="stSidebar"] > div:first-child {{
            padding-top: 0 !important;
            padding-bottom: 0 !important;
        }}

        section[data-testid="stSidebar"] > div {{
            width: {SIDEBAR_WIDTH} !important;
            background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
            border-right: 1px solid var(--dv-border-strong);
            padding: {SPACING_MD} {SPACING_SM};
            box-shadow: var(--dv-shadow-sm);
        }}

        .block-container {{
            width: 100% !important;
            max-width: {CONTAINER_MAX_WIDTH} !important;
            margin: 0 auto !important;
            padding-top: {SPACING_MD};
            padding-bottom: {SPACING_XL};
            padding-left: clamp(1rem, 1.8vw, 1.6rem) !important;
            padding-right: clamp(1rem, 1.8vw, 1.6rem) !important;
        }}

        h1, h2, h3, h4, h5, h6,
        [data-testid="stMarkdownContainer"] h1,
        [data-testid="stMarkdownContainer"] h2,
        [data-testid="stMarkdownContainer"] h3 {{
            color: var(--dv-text);
            letter-spacing: -0.02em;
            font-family: var(--dv-font-family);
            font-weight: 700;
        }}

        p, li, label, span, div {{
            color: var(--dv-text);
        }}

        /* Container Card Styles */
        .hero-card,
        .section-card,
        .metric-card,
        .dashboard-card,
        .recommendation-card,
        .alert-card,
        .timeline-item,
        .panel-card,
        .shell-topbar-card {{
            background: var(--dv-surface);\n            border: 1px solid var(--dv-border);
            border-radius: var(--dv-radius-md);
            box-shadow: var(--dv-shadow-sm);
            transition: border-color 180ms ease, box-shadow 180ms ease, transform 180ms ease;
            overflow: hidden;
            max-width: 100%;
            box-sizing: border-box;
        }}

        .section-heading,
        .card-title,
        .card-value,
        .card-caption,
        .metric-title,
        .metric-value,
        .metric-subtitle,
        .dash-title,
        .dash-subtitle {{
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}

        .hero-card {{
            border-radius: var(--dv-radius-lg);
            padding: {SPACING_LG};
            margin-bottom: {SPACING_MD};
            box-shadow: var(--dv-shadow-md);
            background: linear-gradient(135deg, rgba(255,255,255,0.98) 0%, rgba(248,250,252,0.94) 100%);
        }}

        .shell-topbar-card {{
            border-radius: var(--dv-radius-md);
            padding: {SPACING_SM} {SPACING_MD};
            margin-bottom: {SPACING_MD};
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(12px);
        }}

        .panel-card {{
            padding: {SPACING_MD};
            margin-bottom: {SPACING_MD};
        }}

        .metric-card {{
            padding: {SPACING_MD};
            min-height: 132px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }}

        .metric-card:hover,
        .dashboard-card:hover,
        .panel-card:hover {{
            box-shadow: var(--dv-shadow-md);
            border-color: var(--dv-border-strong);
        }}

        .metric-title {{
            font-size: {FONT_CARD_TITLE};
            font-weight: 700;
            letter-spacing: 0.05em;
            text-transform: uppercase;
            color: var(--dv-muted);
        }}

        .metric-value {{
            font-size: {FONT_METRIC_VALUE};
            font-weight: 800;
            letter-spacing: -0.04em;
            color: var(--dv-text);
            font-variant-numeric: tabular-nums;
            margin: {SPACING_XS} 0;
        }}

        .metric-subtitle {{
            font-size: {FONT_CAPTION};
            color: var(--dv-muted);
            font-weight: 500;
        }}

        /* Status Badges & Chips */
        .status-badge, .chip {{
            display: inline-flex;
            align-items: center;
            gap: 0.35rem;
            border-radius: 999px;
            padding: 0.3rem 0.65rem;
            font-size: {FONT_CAPTION};
            font-weight: 700;
            letter-spacing: 0.02em;
            line-height: 1.2;
            width: fit-content;
        }}

        .status-badge.success, .chip.success, .badge-success {{
            background: var(--dv-success-bg);
            color: var(--dv-success);
            border: 1px solid {SUCCESS_BORDER};
        }}

        .status-badge.warning, .chip.warning, .badge-warning {{
            background: var(--dv-warning-bg);
            color: var(--dv-warning);
            border: 1px solid {WARNING_BORDER};
        }}

        .status-badge.danger, .chip.danger, .badge-danger {{
            background: var(--dv-danger-bg);
            color: var(--dv-danger);
            border: 1px solid {DANGER_BORDER};
        }}

        .status-badge.info, .chip.info, .badge-info {{
            background: var(--dv-info-bg);
            color: var(--dv-info);
            border: 1px solid {INFO_BORDER};
        }}

        .status-badge.neutral, .chip.neutral, .badge-neutral {{
            background: {NEUTRAL_BG};
            color: {NEUTRAL};
            border: 1px solid {NEUTRAL_BORDER};
        }}

        /* Accessible Buttons */
        .stButton > button,
        [data-testid="stDownloadButton"] > button {{
            border-radius: var(--dv-radius-sm) !important;
            font-weight: 700 !important;
            height: {BUTTON_HEIGHT} !important;
            transition: all 180ms ease !important;
            border: 1px solid var(--dv-border-strong) !important;
            background: var(--dv-surface) !important;
            color: var(--dv-text) !important;
            box-shadow: none !important;
        }}

        .stButton > button:hover,
        [data-testid="stDownloadButton"] > button:hover {{
            transform: translateY(-1px) !important;
            box-shadow: var(--dv-shadow-sm) !important;
            background: var(--dv-surface-alt) !important;
        }}

        .stButton > button:focus-visible {{
            outline: 2px solid var(--dv-accent) !important;
            outline-offset: 2px !important;
        }}

        .stButton > button[kind="primary"] {{
            background: linear-gradient(135deg, var(--dv-accent) 0%, var(--dv-accent-strong) 100%) !important;
            color: {TEXT_INVERSE} !important;
            border: none !important;
        }}

        .section-heading,
        .card-title,
        .card-value,
        .card-caption,
        .metric-title,
        .metric-value,
        .metric-subtitle,
        .dash-title,
        .dash-subtitle,
        .status-badge,
        .chip,
        label,
        h1, h2, h3, h4, h5, h6 {{
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}

        .stTextInput > div > div > input,
        .stNumberInput > div > div > input,
        .stSelectbox > div > div > select,
        .stTextArea > div > div > textarea {{
            border-radius: 12px !important;
            border: 1px solid var(--dv-border-strong) !important;
            padding: 0.7rem 0.8rem !important;
            min-height: 44px !important;
            box-shadow: inset 0 1px 2px rgba(15, 23, 42, 0.03) !important;
        }}

        .stSpinner > div {{
            border-color: var(--dv-accent) transparent transparent transparent !important;
        }}

        /* Accessible Input Focus States */
        input:focus-visible, select:focus-visible, textarea:focus-visible {{
            outline: 2px solid var(--dv-accent) !important;
            outline-offset: 1px !important;
            border-color: var(--dv-accent) !important;
        }}

        @media (max-width: 900px) {{
            .block-container {{
                padding-left: 0.8rem !important;
                padding-right: 0.8rem !important;
            }}

            .hero-card {{
                padding: {SPACING_MD};
            }}
        }}

        /* Empty State Styling */
        .dv-empty-state {{
            background: linear-gradient(135deg, rgba(248,250,252,1), rgba(255,255,255,0.96));
            border: 1px dashed var(--dv-border-strong);
            border-radius: var(--dv-radius-md);
            padding: {SPACING_LG};
            text-align: center;
        }}
        .dv-empty-state-icon {{
            font-size: 1.8rem;
            margin-bottom: {SPACING_XS};
        }}
        .dv-empty-state-title {{
            font-weight: 700;
            font-size: 1rem;
            color: var(--dv-text);
            margin-bottom: {SPACING_XS};
        }}
        .dv-empty-state-copy {{
            color: var(--dv-muted);
            font-size: {FONT_BODY};
            line-height: 1.5;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


# ==============================================================================
# 7. REUSABLE UI HELPER COMPONENTS
# ==============================================================================
def render_page_header(
    title: str,
    subtitle: str = "",
    badge: str = "",
) -> None:
    """Render a unified top hero page header."""
    badge_html = f"<div class='status-badge info'>{escape(badge)}</div>" if badge else ""
    subtitle_html = f"<div style='color:var(--dv-muted);font-size:{FONT_BODY};margin-top:0.4rem;'>{escape(subtitle)}</div>" if subtitle else ""

    st.markdown(
        f"""
        <div class="hero-card">
            <div style='display:flex;justify-content:space-between;align-items:center;gap:1rem;flex-wrap:wrap;'>
                <div>
                    <h1 style='font-size:{FONT_PAGE_TITLE};margin:0;'>{escape(title)}</h1>
                    {subtitle_html}
                </div>
                {badge_html}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_section_title(
    title: str,
    subtitle: str = "",
    badge: str = "",
) -> None:
    """Render a section header with title and optional description."""
    badge_html = f"<span class='status-badge neutral'>{escape(badge)}</span>" if badge else ""
    subtitle_html = f"<p style='color:var(--dv-muted);font-size:{FONT_BODY};margin:0.2rem 0 0;'>{escape(subtitle)}</p>" if subtitle else ""

    st.markdown(
        f"""
        <div style='margin-bottom:0.75rem;padding-bottom:0.4rem;border-bottom:1px solid var(--dv-border);'>
            <div style='display:flex;align-items:center;justify-content:space-between;gap:0.5rem;flex-wrap:wrap;'>
                <h3 style='font-size:{FONT_SECTION_TITLE};font-weight:700;margin:0;color:var(--dv-text);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;'>{escape(title)}</h3>
                {badge_html}
            </div>
            {subtitle_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_metric_card(
    title: str,
    value: str,
    subtitle: str = "",
    icon: str = "",
    status: str | None = None,
    tone: str = "neutral",
    change_pct: str | None = None,
) -> None:
    """Render a standardized metric card using design system tokens."""
    icon_html = f"<span style='font-size:1.4rem;line-height:1;'>{escape(icon)}</span>" if icon else ""
    status_html = f"<div class='status-badge {tone}' style='margin-top:0.4rem;'>{escape(status)}</div>" if status else ""
    change_html = f"<span class='chip success' style='margin-left:0.4rem;'>{escape(change_pct)}</span>" if change_pct else ""

    st.markdown(
        f"""
        <div class="metric-card">
            <div style='display:flex;justify-content:space-between;align-items:flex-start;gap:0.5rem;'>
                <div class="metric-title">{escape(title)}</div>
                {icon_html}
            </div>
            <div>
                <div class="metric-value">{escape(value)}{change_html}</div>
                <div class="metric-subtitle">{escape(subtitle)}</div>
            </div>
            {status_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_info_card(
    title: str,
    content: str,
    footer: str = "",
    icon: str = "",
) -> None:
    """Render a standardized info card using design system tokens."""
    icon_html = f"<span style='font-size:1.1rem;line-height:1;margin-right:0.4rem;'>{escape(icon)}</span>" if icon else ""
    footer_html = (
        f"<div style='margin-top:{SPACING_SM};padding-top:{SPACING_SM};border-top:1px solid var(--dv-border);color:var(--dv-muted);font-size:{FONT_CAPTION};'>"
        f"{escape(footer)}</div>"
        if footer else ""
    )

    st.markdown(
        f"""
        <div class="dashboard-card" style='padding:{SPACING_MD};'>
            <div style='display:flex;align-items:center;margin-bottom:{SPACING_XS};'>
                {icon_html}
                <div class="metric-title" style='color:var(--dv-text);'>{escape(title)}</div>
            </div>
            <div style='font-size:{FONT_BODY};color:var(--dv-text);line-height:1.55;'>{escape(content)}</div>
            {footer_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_status_badge(
    label: str,
    status_type: str = "success",
) -> None:
    """Render an accessible status badge element."""
    st.markdown(
        f"<span class='status-badge {status_type}'>{escape(label)}</span>",
        unsafe_allow_html=True,
    )


def render_alert_card(
    title: str,
    message: str,
    severity: str = "info",
    timestamp: str = "",
) -> None:
    """Render a standardized alert card component."""
    severity_map = {
        "info": ("info", "ℹ️"),
        "warning": ("warning", "⚠️"),
        "danger": ("danger", "🚨"),
        "critical": ("danger", "🚨"),
        "success": ("success", "✅"),
    }
    tone, icon = severity_map.get(severity.lower(), ("info", "ℹ️"))
    timestamp_html = f"<div style='margin-top:{SPACING_XS};font-size:{FONT_CAPTION};color:var(--dv-muted);'>{escape(timestamp)}</div>" if timestamp else ""

    st.markdown(
        f"""
        <div class="alert-card" style='padding:{SPACING_MD};border-left:4px solid var(--dv-{tone});background:var(--dv-{tone}-bg);margin-bottom:{SPACING_SM};'>
            <div style='display:flex;align-items:center;gap:0.5rem;margin-bottom:0.35rem;'>
                <span style='font-size:1.1rem;'>{icon}</span>
                <div style='font-weight:700;color:var(--dv-text);font-size:0.95rem;'>{escape(title)}</div>
            </div>
            <div style='font-size:{FONT_BODY};color:var(--dv-text);line-height:1.45;'>{escape(message)}</div>
            {timestamp_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_recommendation_card(
    title: str,
    description: str,
    icon: str = "💡",
    priority: str = "medium",
) -> None:
    """Render a recommendation card component."""
    tone = "danger" if priority == "high" else "warning" if priority == "medium" else "info"

    st.markdown(
        f"""
        <div class="recommendation-card" style='padding:{SPACING_MD};border-left:4px solid var(--dv-{tone});margin-bottom:{SPACING_SM};'>
            <div style='display:flex;align-items:flex-start;gap:0.75rem;'>
                <div style='font-size:1.2rem;line-height:1;'>{escape(icon)}</div>
                <div style='flex:1;min-width:0;'>
                    <div style='font-weight:700;color:var(--dv-text);margin-bottom:0.25rem;'>{escape(title)}</div>
                    <div style='font-size:{FONT_BODY};color:var(--dv-muted);line-height:1.45;'>{escape(description)}</div>
                    <div class='status-badge {tone}' style='margin-top:0.4rem;'>{escape(priority.upper())} PRIORITY</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_empty_state(
    title: str,
    message: str,
    icon: str = "✨",
    action_label: str | None = None,
    action_key: str | None = None,
) -> None:
    """Render an accessible, clean empty state container."""
    st.markdown(
        f"""
        <div class="dv-empty-state">
            <div class="dv-empty-state-icon">{escape(icon)}</div>
            <div class="dv-empty-state-title">{escape(title)}</div>
            <div class="dv-empty-state-copy">{escape(message)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if action_label and action_key:
        st.markdown(f"<div style='margin-top:{SPACING_SM};'></div>", unsafe_allow_html=True)
        if st.button(action_label, key=action_key, use_container_width=True, type="primary"):
            st.rerun()


def render_loading_skeleton(label: str = "Loading operational data...") -> None:
    """Render a clean skeleton placeholder for asynchronous component rendering."""
    st.markdown(
        f"""
        <div class="dashboard-card" style="padding:{SPACING_MD}; border:1px dashed var(--dv-border-strong);">
            <div style="display:flex;align-items:center;gap:0.65rem;margin-bottom:0.7rem;">
                <div style="width:0.7rem;height:0.7rem;border-radius:999px;background:var(--dv-accent);opacity:0.85;"></div>
                <div style="height:0.7rem;width:55%;border-radius:999px;background:linear-gradient(90deg, rgba(37,99,235,0.12), rgba(37,99,235,0.25));"></div>
            </div>
            <div style="height:0.7rem;width:92%;border-radius:999px;background:linear-gradient(90deg, rgba(148,163,184,0.15), rgba(148,163,184,0.35));margin-bottom:0.45rem;"></div>
            <div style="height:0.7rem;width:74%;border-radius:999px;background:linear-gradient(90deg, rgba(148,163,184,0.15), rgba(148,163,184,0.35));margin-bottom:0.45rem;"></div>
            <div style="height:0.7rem;width:38%;border-radius:999px;background:linear-gradient(90deg, rgba(148,163,184,0.15), rgba(148,163,184,0.35));"></div>
            <div style="margin-top:0.9rem;font-size:0.86rem;font-weight:600;color:var(--dv-muted);">⏳ {escape(label)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_stat_chip(label: str, tone: str = "info") -> None:
    """Render a standardized inline stat pill/chip."""
    st.markdown(
        f"<span class='chip {tone}'>{escape(label)}</span>",
        unsafe_allow_html=True,
    )


def render_timeline_item(title: str, timestamp: str, description: str, icon: str = "📌") -> None:
    """Render a clean vertical timeline event item."""
    st.markdown(
        f"""
        <div class="timeline-item" style="padding:{SPACING_SM} {SPACING_MD}; border-left:3px solid var(--dv-accent); margin-bottom:{SPACING_SM}; background:var(--dv-surface-alt); border-radius:var(--dv-radius-sm);">
            <div style="font-weight:700; font-size:0.88rem; color:var(--dv-text);">{escape(icon)} {escape(title)}</div>
            <div style="font-size:{FONT_CAPTION}; color:var(--dv-muted-2); margin-top:0.1rem;">🕒 {escape(timestamp)}</div>
            <div style="font-size:{FONT_BODY}; color:var(--dv-muted); margin-top:0.2rem;">{escape(description)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_section_divider() -> None:
    """Render a standardized horizontal section divider line."""
    st.markdown(
        f"<div style='border-top:1px solid var(--dv-border); margin:{SPACING_MD} 0;'></div>",
        unsafe_allow_html=True,
    )


def render_form_section_header(title: str, subtitle: str = "") -> None:
    """Render a form section header with uppercase title and description."""
    sub_html = f"<div style='font-size:{FONT_CAPTION}; color:var(--dv-muted); margin-top:0.15rem;'>{escape(subtitle)}</div>" if subtitle else ""
    st.markdown(
        f"""
        <div style="margin-bottom:{SPACING_SM};">
            <div style="font-size:0.75rem; font-weight:800; letter-spacing:0.06em; text-transform:uppercase; color:var(--dv-muted);">{escape(title)}</div>
            {sub_html}
        </div>
        """,
        unsafe_allow_html=True,
    )
