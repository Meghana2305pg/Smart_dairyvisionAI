# Project Polaris Design System

## 1. Brand Vision

### Product Identity

DairyVision AI is a premium, intelligent operations platform for modern dairy farms. It should feel trustworthy, calm, and data-driven while remaining approachable for farm operators, analysts, and decision-makers.

The product identity combines:

- agricultural practicality
- analytical clarity
- modern software elegance
- reassuring confidence in high-stakes decisions

### Design Goals

- Create a consistent, professional visual language across all screens.
- Make complex farm data understandable at a glance.
- Support fast operational decisions with clear hierarchy and prioritization.
- Balance technical sophistication with usability for non-technical users.
- Establish a foundation that can scale into future product extensions.

### User Experience Goals

- Reduce cognitive load during daily monitoring and analysis.
- Make critical information visible quickly.
- Emphasize actionable insights over noise.
- Provide a calm, structured experience for high-focus decision-making.
- Keep interactions predictable, professional, and accessible.

---

## 2. Color System

### Core Palette

- Primary: Deep Navy #0F172A
- Secondary: Slate Blue #334155
- Accent: Farm Green #2F7D32
- Success: Fresh Green #16A34A
- Warning: Amber #D97706
- Error: Rose Red #DC2626
- Neutral: Cool Gray #64748B

### Extended Palette

- Primary Light: #E2E8F0
- Secondary Light: #F8FAFC
- Accent Light: #EAF7EC
- Success Light: #ECFDF3
- Warning Light: #FFF7ED
- Error Light: #FEF2F2
- Neutral Light: #F1F5F9

### Usage Rules

- Primary is used for main navigation, headings, and dense UI surfaces.
- Accent is used for key actions, positive states, and important data emphasis.
- Success marks healthy outcomes and completed actions.
- Warning emphasizes attention needed or elevated risk.
- Error highlights critical issues or failed states.
- Neutral supports supporting text, borders, and subtle backgrounds.

---

## 3. Typography

### Display

- Font family: Inter, Segoe UI, Arial, sans-serif
- Style: Semi-bold / Bold
- Use for hero titles and large section headers
- Size: 32–40px

### H1

- Size: 24–28px
- Weight: 700
- Line height: 1.2
- Purpose: Major page title

### H2

- Size: 20–22px
- Weight: 700
- Line height: 1.25
- Purpose: Section headers

### H3

- Size: 16–18px
- Weight: 600
- Line height: 1.3
- Purpose: Subsection and card titles

### Card Titles

- Size: 14–16px
- Weight: 600
- Color: Primary / Secondary
- Purpose: Clear concise labels inside cards

### Labels

- Size: 12–13px
- Weight: 600
- Letter spacing: 0.04em
- Uppercase treatment for compact metadata where appropriate

### Body Text

- Size: 14–15px
- Weight: 400–500
- Line height: 1.5
- Color: Secondary / Neutral

### Typography Rules

- Avoid overly decorative fonts.
- Use strong hierarchy to guide scanning.
- Maintain generous line spacing for readability.
- Keep labels concise and action-oriented.

---

## 4. Layout System

### Grid

- Use a 12-column responsive grid for page layouts.
- Primary content should align to a clear left-to-right information hierarchy.
- Sidebar or supporting content should remain secondary in visual prominence.

### Page Spacing

- Page padding: 24px desktop, 16px tablet, 12px mobile
- Section spacing: 24px between major sections
- Component spacing: 12px–16px between related controls or cards

### Card Spacing

- Card padding: 16px–20px
- Card radius: 16px–20px
- Card border: 1px soft neutral border
- Card shadow: subtle depth only, not heavy or dramatic

### Responsive Rules

- On desktop: multi-column layouts for dashboard summaries and comparisons
- On tablet: reflow to two-column layouts where appropriate
- On mobile: stack vertically and prioritize the most important metric first
- Maintain consistent padding and spacing at every break point

---

## 5. Component Library

### KPI Cards

Purpose: highlight a single important metric.

Structure:

- Label
- Value
- Supporting detail
- Optional change indicator

Visual treatment:

- Soft background
- Strong value emphasis
- Clean border or subtle shadow

### Chart Cards

Purpose: present trends, distributions, or comparisons.

Structure:

- Card shell
- Chart title
- Legend or caption
- Optional insights note

Visual treatment:

- Neutral card background
- Spacious chart area
- Minimal chart chrome

### Tables

Purpose: support dense structured data and comparisons.

Structure:

- Header row
- Centered or left-aligned content
- Alternating row states only if necessary

Visual treatment:

- Rounded corners
- Light header background
- Clean borders and readable spacing

### Timeline Cards

Purpose: show chronological state changes or event progression.

Structure:

- Event title
- Timestamp or phase label
- Supporting detail

Visual treatment:

- Horizontal or vertical flow with soft connectors
- Emphasize most recent state

### Recommendation Cards

Purpose: present operational actions or next steps.

Structure:

- Short title
- Clear recommendation text
- Optional priority indicator

Visual treatment:

- Accent or warning tint depending on urgency
- Friendly but authoritative tone

### Alert Cards

Purpose: communicate health, weather, or risk issues.

Structure:

- Alert title
- Short explanation
- Severity marker

Visual treatment:

- Strong color tint for urgency
- Clear icon support
- Minimal clutter

### Buttons

Primary button:

- Accent fill
- Strong contrast
- Used for primary action

Secondary button:

- Soft neutral fill or border
- Used for supporting action

Ghost button:

- Low emphasis, no heavy fill
- Used for lightweight or tertiary action

### Chips

Purpose: show quick filters or compact selections.

Visual treatment:

- Rounded pill shape
- Soft background
- Strong text contrast

### Status Badges

Purpose: show health, risk, or state.

Examples:

- Healthy / Stable / Warning / Critical
- Use color and text pairing consistently

---

## 6. Chart Design Rules

- Use Plotly-style visual clarity with minimal decorative noise.
- Keep charts readable, calm, and precise.
- Favor clean axes, generous whitespace, and clearly labeled series.
- Use accent color for emphasis and neutral tones for supporting data.
- Use consistent chart titles and consistent axis labeling across the product.
- Avoid overly dense legends and unnecessary 3D effects.
- Ensure charts remain readable in light themes and accessible contrast.
- Keep line colors, fill colors, and marker styles consistent per chart family.

### Recommended Chart Usage

- Trend charts: line or area charts for temporal changes
- Comparison charts: bar charts for categorical comparison
- Distribution charts: bar or pie charts where appropriate
- Forecast views: simple line charts with clear emphasis on the forecast path

---

## 7. Icon System

### Style Direction

- Use simple, modern, outline-style icons that align with a professional SaaS product.
- Icons should feel practical and dependable rather than playful.

### Icon Categories

- Monitoring: temperature, weather, health, alerts
- Analytics: chart, trend, insights, compare
- Operations: feed, cow, barn, recommendation
- Status: check, warning, error, info

### Rules

- Use icons sparingly and consistently.
- Icons should support meaning, not replace labels.
- Favor one visual style across the product.

---

## 8. Navigation Design

### Principles

- Navigation should feel predictable and low-friction.
- Primary navigation should remain visually quiet but clearly structured.
- Active state should be clearly identifiable without being visually noisy.

### Navigation Patterns

- Top-level categories should be grouped by intent: Dashboard, Digital Twin, Analytics, Health, Scenario Studio, and Settings.
- Secondary navigation should remain concise and aligned to the current workspace.
- Use consistent spacing, icon pairing, and active states across all screens.

---

## 9. Animation Guidelines

### Intent

Animation should support understanding rather than decoration.

### Principles

- Use subtle transitions for panels, cards, and metric updates.
- Avoid excessive motion or distracting effects.
- Preferred motion: fade, slide, and gentle scale.

### Recommended Timing

- Entry: 180–250ms
- Hover: 120–180ms
- Page transition: 200–300ms

### Future Use Cases

- Dashboard cards updating
- Scenario result transitions
- Timeline progression
- Recommendation reveal states

---

## 10. Accessibility Guidelines

### Core Requirements

- Maintain WCAG AA contrast for text and interactive elements.
- Ensure all interactive controls are keyboard accessible.
- Provide clear focus states for buttons, links, and form elements.
- Do not rely on color alone to communicate state.
- Support screen-reader-friendly labels and semantic structure.

### Content Accessibility

- Use plain language in labels and recommendations.
- Keep layouts scalable and readable.
- Ensure charts include textual summaries or captions when needed.

### Component Accessibility Rules

- Buttons must have visible focus and clear hover states.
- Form controls must have descriptive labels.
- Alerts must support both color and icon or text cues.

---

## 11. Dashboard Template

### Purpose

Provide a concise executive overview of herd operations, key metrics, and urgent signals.

### Structure

- Page header with title and context
- KPI row for core metrics
- Primary chart area for performance trends
- Secondary cards for alerts and recommendations
- Supporting table or list for operational detail

### Visual Priorities

1. Top KPI summary
2. Important trends or anomalies
3. Actionable recommendations
4. Supporting detail

---

## 12. Digital Twin Template

### Purpose

Present the live digital twin state and the current health, prediction, and operational context of a selected cow.

### Structure

- Header with selected cow context
- Summary cards for prediction, health, weather, and risk
- Detail panels for observations and state changes
- Timeline or snapshot history section
- Optional recommendation panel

### Visual Priorities

1. Live state snapshot
2. Health and prediction context
3. Timeline or recent changes
4. Operational next steps

---

## 13. Scenario Studio Template

### Purpose

Support structured what-if analysis without disrupting live operations.

### Structure

- Header with scenario context
- Control panel for input changes
- Live comparison panel
- Scenario result cards
- Change summary and recommendation comparison
- Future playback or history area

### Visual Priorities

1. Control clarity
2. Comparison readability
3. Scenario outcome visibility
4. Recommendation understanding

---

## 14. Analytics Template

### Purpose

Present deeper performance and insight analysis across observations, health, and predictions.

### Structure

- Page header and filter context
- KPI summary row
- Multi-card chart layout
- Supporting ranking or comparison tables
- Insight and recommendation section

### Visual Priorities

1. Trend visibility
2. Comparative clarity
3. Insight extraction
4. Actionable follow-up

---

## 15. Command Centre Template

### Purpose

Provide a fast operational control surface for farm actions, alerts, and prioritization.

### Structure

- Header and current status summary
- Priority alert cards
- Actionable recommendation tiles
- Supporting operational tools or summaries

### Visual Priorities

1. Urgency and risk visibility
2. Clear operational next steps
3. Efficient scanning of tasks

---

## 16. Health Alerts Template

### Purpose

Surface health issues, risk levels, and intervention guidance clearly.

### Structure

- Header and alert summary
- Alert cards grouped by severity
- Supporting context for affected cows or conditions
- Action or follow-up guidance

### Visual Priorities

1. Severity clarity
2. Immediate action visibility
3. Supporting context for decisions

---

## Design Principles Summary

- Be calm, clear, and trustworthy.
- Prioritize operational clarity over visual noise.
- Make data understandable at a glance.
- Maintain consistency across every screen.
- Prepare the system for future growth and refinement.
