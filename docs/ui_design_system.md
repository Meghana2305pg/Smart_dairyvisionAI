# DairyVision AI UI/UX Design System Specification

## 1. Design Philosophy
The DairyVision AI Design System is built to deliver a modern, high-density, SaaS-grade application interface modeled after industry benchmarks such as **Linear**, **Notion**, **Vercel**, **Stripe Dashboard**, and **Supabase**.

### Core Principles:
1. **High Information Density**: Present operational metrics and herd analytics clearly without clutter or unnecessary whitespace.
2. **Visual Hierarchy & Rhythm**: Guide the farmer's eye seamlessly from top-level farm summaries to actionable insights and low-level data points.
3. **Accessibility (WCAG AA Compliant)**: Enforce high contrast text ratios (minimum 4.5:1 for body text, 7:1 for headers) and clear keyboard focus states (`outline: 2px solid var(--dv-accent)`).
4. **Consistency**: Use centralized design tokens for colors, typography, spacing, radius, and shadows instead of hardcoded hex values or ad-hoc margins.

---

## 2. Directory & Architecture Structure
```
Smart_dairyvisionAI/
├── webapp/
│   ├── ui/
│   │   ├── __init__.py            # Exported design tokens & helper functions
│   │   ├── design_system.py       # Centralized design tokens, CSS theme, & UI helpers
│   │   └── section_header.py      # Legacy backward-compatibility wrapper
│   ├── components/
│   │   ├── cards.py               # Reusable card component abstractions
│   │   └── ...
│   └── layout/
│       ├── shell.py               # Application shell orchestrator
│       ├── sidebar.py             # Fixed left SaaS navigation sidebar
│       └── topbar.py              # Compact SaaS header navigation bar
└── docs/
    └── ui_design_system.md        # Comprehensive design system specification
```

---

## 3. Design Tokens Catalog

### Color Tokens
| Token Name | Hex Value | Usage / Description |
| :--- | :--- | :--- |
| `PRIMARY` | `#2563eb` | Primary CTA buttons, active state indicators, link text |
| `PRIMARY_HOVER` | `#1d4ed8` | Hover state for primary buttons and interactive elements |
| `PRIMARY_BG` | `#eff6ff` | Tinted background for active navigation items and highlights |
| `SECONDARY` | `#475569` | Secondary actions, neutral accents, secondary button borders |
| `SUCCESS` | `#15803d` | Healthy status badges, positive metrics, success alerts |
| `SUCCESS_BG` | `#f0fdf4` | Background tint for success cards and badges |
| `WARNING` | `#b45309` | Warning status badges, attention recommendations, amber alerts |
| `WARNING_BG` | `#fffbeb` | Background tint for warning cards and badges |
| `DANGER` | `#b91c1c` | Critical alerts, disease status badges, destructive action buttons |
| `DANGER_BG` | `#fef2f2` | Background tint for critical alert cards and badges |
| `INFO` | `#1d4ed8` | Informational badges, neutral notifications |
| `INFO_BG` | `#f0f9ff` | Background tint for info cards and badges |
| `BACKGROUND` | `#f8fafc` | Base application viewport background gradient |
| `SURFACE` | `#ffffff` | Primary container surface color for cards and panels |
| `SURFACE_ALT` | `#f1f5f9` | Secondary container surface color for nested lists & inputs |
| `TEXT_PRIMARY` | `#0f172a` | High-contrast body text and headers (15:1 contrast) |
| `TEXT_SECONDARY`| `#475569` | Subtitles, captions, and secondary label text (7:1 contrast) |
| `TEXT_MUTED` | `#64748b` | Muted captions and metadata timestamps (4.5:1 contrast) |
| `BORDER` | `rgba(15,23,42,0.10)` | Default subtle card and divider border |
| `BORDER_STRONG` | `rgba(15,23,42,0.18)` | Prominent container and input focus borders |

---

### Typography Scale Tokens
- **Font Family**: `"Avenir Next", "Segoe UI Variable", "SF Pro Text", "Helvetica Neue", sans-serif`
- **Page Title (`FONT_PAGE_TITLE`)**: `clamp(1.6rem, 2.2vw, 2.2rem)` (Weight: 800)
- **Section Title (`FONT_SECTION_TITLE`)**: `1.25rem` (Weight: 700)
- **Card Title (`FONT_CARD_TITLE`)**: `0.9rem` (Weight: 700, Uppercase, 0.05em letter spacing)
- **Metric Value (`FONT_METRIC_VALUE`)**: `clamp(1.5rem, 2vw, 2rem)` (Weight: 800, Tabular nums)
- **Body Text (`FONT_BODY`)**: `0.95rem` (Weight: 500/600, Line height: 1.5)
- **Caption (`FONT_CAPTION`)**: `0.8rem` (Weight: 500)

---

### Spacing Scale Tokens
| Token | Scale Value | Pixel Equivalent |
| :--- | :--- | :--- |
| `SPACING_XS` | `0.25rem` | 4px |
| `SPACING_SM` | `0.5rem` | 8px |
| `SPACING_MD` | `1rem` | 16px |
| `SPACING_LG` | `1.5rem` | 24px |
| `SPACING_XL` | `2rem` | 32px |
| `SPACING_XXL` | `3rem` | 48px |

---

### Border Radius & Shadow Tokens
- **Radius Small (`RADIUS_SMALL`)**: `10px` (Inputs, chips, status badges)
- **Radius Medium (`RADIUS_MEDIUM`)**: `16px` (Standard cards, panels, topbar)
- **Radius Large (`RADIUS_LARGE`)**: `24px` (Hero header cards, dialog containers)
- **Shadow Small (`SHADOW_SM`)**: `0 4px 16px rgba(15, 23, 42, 0.04)`
- **Shadow Medium (`SHADOW_MD`)**: `0 12px 28px rgba(15, 23, 42, 0.06)`
- **Shadow Large (`SHADOW_LG`)**: `0 18px 50px rgba(15, 23, 42, 0.08)`

---

## 4. Reusable UI Components Catalog

### 1. Page Header (`render_page_header`)
Renders a top hero banner with page title, description, and optional status badge.

### 2. Section Header (`render_section_title`)
Renders a structured section heading with an uppercase title, optional subtitle, and badge.

### 3. Metric Card (`render_metric_card`)
Renders KPI metric cards with top-right icons, numerical values, change chips, and status badges.

### 4. Info Card (`render_info_card`)
Displays structured informative content inside a styled container card with optional footer text.

### 5. Status Badge (`render_status_badge`) & Stat Chip (`render_stat_chip`)
Pill badges for status indicators (`success`, `warning`, `danger`, `neutral`, `info`).

### 6. Alert Card (`render_alert_card`)
Alert panels styled with left severity borders (`danger`, `warning`, `info`) and timestamps.

### 7. Recommendation Card (`render_recommendation_card`)
Actionable recommendation cards displaying priority badges (`HIGH`, `MEDIUM`, `LOW`).

### 8. Empty State (`render_empty_state`)
Accessible empty state containers with an icon, title, description, and primary CTA button.

### 9. Timeline Item (`render_timeline_item`)
Vertical timeline event items for activity logs and cow history.

---

## 5. Global Layout System

- **Fixed Sidebar Width (`SIDEBAR_WIDTH`)**: `260px`
- **Compact Topbar Height (`TOPBAR_HEIGHT`)**: `56px`
- **Centered Content Width (`CONTAINER_MAX_WIDTH`)**: `1320px`
- **Input & Button Height (`INPUT_HEIGHT`, `BUTTON_HEIGHT`)**: `42px`

---

## 6. Guidelines for Future Component Extensions

1. **Import Tokens Centralized**: Always import design tokens from `webapp.ui` or `webapp.ui.design_system` instead of writing hardcoded hex values.
2. **Preserve WCAG Contrast**: When creating new badge tones, ensure text has at least 4.5:1 contrast against its background.
3. **No Direct DOM Mutations**: Keep component rendering wrapped inside pure Python helper functions rendering clean HTML/CSS snippets via `st.markdown`.
