# DairyVision AI — UI / UX Architectural Audit

> **Audit date:** 2026-08-02  
> **Auditor:** UI/UX & Product Design Review  
> **Target Audience Persona:** First-Time Dairy Farmer / Farm Manager  
> **Repository:** `Smart_dairyvisionAI` · **Version:** v2.3.1  
> **Mode:** Read-Only Analysis — NO code modified.

---

## Table of Contents

1. [Executive Summary & User Persona](#1-executive-summary--user-persona)
2. [Global UI/UX & Streamlit Framework Limitations](#2-global-uiux--streamlit-framework-limitations)
3. [Screen-by-Screen UX Audit](#3-screen-by-screen-ux-audit)
   - 3.1 [Login Screen](#31-login-screen)
   - 3.2 [Register Screen](#32-register-screen)
   - 3.3 [Farm Setup Screen](#33-farm-setup-screen)
   - 3.4 [Dashboard](#34-dashboard)
   - 3.5 [My Herd](#35-my-herd)
   - 3.6 [Cow Profile](#36-cow-profile)
   - 3.7 [Daily Operations](#37-daily-operations)
   - 3.8 [Digital Twin Workspace](#38-digital-twin-workspace)
   - 3.9 [Health Alerts](#39-health-alerts)
   - 3.10 [Analytics Workspace](#310-analytics-workspace)
   - 3.11 [Explainability (SHAP)](#311-explainability-shap)
   - 3.12 [Settings Workspace](#312-settings-workspace)
   - 3.13 [Command Centre (Operations Center)](#313-command-centre-operations-center)
4. [Cross-Screen Consistency Matrix](#4-cross-screen-consistency-matrix)
5. [Summary of UX Deficiencies](#5-summary-of-ux-deficiencies)

---

## 1. Executive Summary & User Persona

### User Persona: Ramesh — First-Time Dairy Farmer
- **Background:** Manages a 40-cow herd in rural Karnataka/Karnataka border. Uses an Android smartphone or basic tablet in outdoor/barn conditions.
- **Goals:** Wants quick daily milk forecasts, immediate heat stress warnings, clear feeding recommendations, and straightforward cow health logs.
- **Tech Literacy:** Comfortable with WhatsApp and basic farm apps, but easily overwhelmed by complex machine learning terminology (SHAP values, R² boxplots, THI polynomials, feature importance vectors).
- **Key Needs:** One-tap navigation, high contrast readability outdoors, clear actionable advice, instant error feedback, and offline resiliency.

### Summary of Audit Findings
While DairyVision AI features an impressive CSS theme (`--dv-*` visual tokens, glassmorphism cards, custom topbar/sidebar components), the user interface suffers from severe usability gaps when evaluated from Ramesh's perspective:
1. **High Cognitive Load:** Jargon-dense ML metrics (SHAP, R², baseline yield formulas) presented directly to farmers without clear contextual explanations.
2. **Workflow Friction:** Multi-step daily operations require excessive typing and manual copying of values that should be auto-populated.
3. **Inconsistent UI Controls:** Mix of custom HTML inline cards and standard Streamlit widgets (selectbox, tabs, form submit buttons) resulting in mismatched visual styles and broken layouts on mobile.
4. **Non-functional UI Elements:** Static elements disguised as interactive controls (e.g. non-clickable topbar notification bell, non-functional settings preferences, non-persisted user preferences).

---

## 2. Global UI/UX & Streamlit Framework Limitations

The application relies heavily on Streamlit (`streamlit==1.x`). While Streamlit enables rapid Python dashboarding, its architectural defaults create several professional UI/UX bottlenecks:

### Framework Artifacts & Professionalism Penalties

```
+-----------------------------------------------------------------------------+
| [Top Bar: 🏡 Green Pastures  |  🌤️ 28°C  |  🔔 (Static)  |  [R] Ramesh  | [Logout] ] |
+-----------------------------------------------------------------------------+
| Streamlit Default UI Limitations:                                           |
| 1. Full-page WebSocket re-renders on EVERY button click / dropdown selection |
| 2. Screen scroll position resets or jumps on rerun                          |
| 3. st.markdown(unsafe_allow_html=True) causes CSS leaking & DOM mismatch   |
| 4. Native Streamlit Tabs & Buttons lack theme harmony with custom HTML cards |
| 5. st.query_params.clear() strips URL routing (cannot bookmark screen views)  |
+-----------------------------------------------------------------------------+
```

1. **Page Re-render Flicker & Scroll Resets:**
   - Every input interaction (selecting a cow from a dropdown, toggling a filter tab) triggers a full-page Python script execution.
   - Screen content momentarily flashes or resets scroll position, making the application feel clunky compared to modern single-page web apps (React/Vue).

2. **Styling Fractures (`unsafe_allow_html=True`):**
   - Theme styling is injected via `st.markdown('<style>...</style>')` in `section_header.py` and individual screen files.
   - Standard Streamlit elements (`st.selectbox`, `st.button`, `st.tabs`, `st.dataframe`) do not inherit custom HTML card styles cleanly, leading to visual inconsistency (e.g. square default inputs inside rounded glassmorphic containers).

3. **Static Fake UI Primitives:**
   - The topbar notification bell icon (`🔔`) is rendered as a static HTML string. Clicking it does nothing, misleading users who expect a notification drawer.
   - The user avatar in the topbar (`[R]`) is non-clickable (cannot open profile menu).

4. **URL Navigation Stripping:**
   - `app.py` executes `st.query_params.clear()` on every session refresh to prevent query string pollution.
   - Result: Users cannot bookmark specific screens (e.g. `?screen=daily_operations`), share cow profile links, or use browser back/forward buttons reliably.

5. **Accessibility Failures:**
   - Light gray text on semi-transparent white backgrounds (`#64748b` on `rgba(255,255,255,0.78)`) fails WCAG AA contrast standards (ratio ~3.4:1 instead of 4.5:1 minimum).
   - Dynamic HTML blocks lack ARIA labels, role attributes, and keyboard focus states.

---

## 3. Screen-by-Screen UX Audit

---

### 3.1 Login Screen

*File:* `webapp/app.py` -> `render_login_screen()`

```
+-------------------------------------------------------------+
|                             🐄                              |
|                       DairyVision AI                        |
|           Intelligent dairy farm management platform        |
|                                                             |
|   +-----------------------------------------------------+   |
|   | Email                                               |   |
|   | [                                               ]   |   |
|   | Password                                            |   |
|   | [                                               ]   |   |
|   | [                 Sign In (Button)              ]   |   |
|   +-----------------------------------------------------+   |
|                                                             |
|   [                 Create Account (Button)         ]   |
+-------------------------------------------------------------+
```

| Dimension | Deficiencies & Findings |
|-----------|-------------------------|
| **Confusing Layout** | Single-column form centered on desktop with vast empty margins (`columns([1, 2, 1])`). Feels sparse and disconnected from the brand. |
| **Poor Navigation** | No option to reset forgotten password. If Ramesh forgets his password, he is permanently locked out. |
| **Unnecessary Clicks** | Focus is not automatically set to the Email input field upon page load. |
| **Inconsistent Spacing** | Hardcoded pixel margins (`padding: 40px 20px;`, `margin-top: 32px;`) mixed with REM units elsewhere. |
| **Inconsistent Colors** | Login submit button uses standard Streamlit secondary gray until hovered, contrasting with main app blue (`#2563eb`). |
| **Poor Hierarchy** | "Create Account" button is rendered outside the main form container, appearing floating at the bottom. |
| **Poor Typography** | Title font size (`28px`) uses generic system font stacks without custom line-height scaling. |
| **Unnecessary Info** | Generic subtitle "Intelligent dairy farm management platform" provides no clear value prop to a farmer. |
| **Missing Info** | No "Remember Me" checkbox, no login assistance, no support contact, no language selector (Kannada/Hindi/English). |
| **Slow Workflows** | Invalid credentials trigger a full-page reload before displaying error text. |
| **Accessibility Issues** | Input text labels have no explicitly linked HTML `for` IDs; low contrast subtitle (`#475569`). |
| **Responsiveness Issues** | On mobile screens (<480px), centered column forced padding compresses inputs horizontally. |

---

### 3.2 Register Screen

*File:* `webapp/app.py` -> `render_register_screen()`

| Dimension | Deficiencies & Findings |
|-----------|-------------------------|
| **Confusing Layout** | Long form asking for Full Name, Email, Phone, Password, Confirm Password all in one vertical stack without section grouping. |
| **Poor Navigation** | "Back to Login" is placed at the very bottom of the page below form submit. If user landed by mistake, they must scroll past all fields. |
| **Unnecessary Clicks** | Requires typing password twice on mobile keyboards without a password-toggle ("show password") button. |
| **Inconsistent Spacing** | 32px bottom margin on header, 0px between form inputs. |
| **Inconsistent Colors** | Error messages appear in Streamlit's default bright red banner (`st.error`), breaking the app's soft aesthetic. |
| **Poor Hierarchy** | Equal visual weight given to secondary fields (Phone) and mandatory fields (Email/Password). |
| **Poor Typography** | Input labels use Streamlit standard 14px default text; no visual indication of required (`*`) vs optional fields. |
| **Unnecessary Info** | Asks for phone number during registration but phone number is never validated via OTP or used anywhere in the app. |
| **Missing Info** | No password strength meter, no terms of service / privacy policy checkbox, no farm role selector (Owner vs Worker). |
| **Slow Workflows** | Exception handling prints full Python traceback on screen (`traceback.print_exc()`, `st.exception(exc)`) if Supabase signup fails. Extremely unpolished for end users. |
| **Accessibility Issues** | Native Streamlit form submit button lacks keyboard tab order optimization. |
| **Responsiveness Issues** | Full height exceeds vertical viewport on smaller phones, requiring scroll to see submission button. |

---

### 3.3 Farm Setup Screen

*File:* `webapp/app.py` -> `render_farm_setup_screen()`

| Dimension | Deficiencies & Findings |
|-----------|-------------------------|
| **Confusing Layout** | Minimalist 3-field form ("Farm Name", "Location", "Farm Size") presented in isolation with zero guidance on what values to enter. |
| **Poor Navigation** | Dead end: No "Skip for now" option or demo data loader. First-time users are forced to create a farm before exploring the platform. |
| **Unnecessary Clicks** | Requires manually typing location string (e.g. "Bengaluru, IN") instead of providing a location picker or GPS detect button. |
| **Inconsistent Spacing** | 40px top padding pushes form down unnaturally on tablet screens. |
| **Inconsistent Colors** | Form submit button container uses standard grey border (`rgba(148,163,184,0.32)`). |
| **Poor Hierarchy** | "Create Farm" button looks identical to standard form submit buttons rather than an important onboarding milestone. |
| **Poor Typography** | Placeholders use generic text ("e.g., Green Pastures Farm", "e.g., 50") without specifying units (Hectares vs Acres). |
| **Unnecessary Info** | Asks for "Farm Size (hectares)" which is never used in any predictive model or calculation in the system. |
| **Missing Info** | No currency/region selection, no herd size estimate input, no breed selection during setup. |
| **Slow Workflows** | Submitting farm creation re-initializes all background services, causing a noticeable multi-second delay. |
| **Accessibility Issues** | Placeholder text (`#94a3b8`) fails contrast ratio standards on light background. |
| **Responsiveness Issues** | Header title line breaks awkwardly on screens narrower than 360px. |

---

### 3.4 Dashboard

*File:* `webapp/screens/dashboard.py` (~598 lines)

```
+----------------------------------------------------------------------------+
|  Good Morning, Green Pastures Farm                    Operational Overview  |
|  Today's farm summary: 0 cows tracked, 0.0 L predicted output...           |
+----------------------------------------------------------------------------+
| [Total Cows: 0] [Pred Yield: 0.0L] [Healthy: 0] [Alerts: 0] [28°C] [Obs: 0]|
+----------------------------------------------------------------------------+
| AI Recommendations                   | Critical Alerts                     |
| (Empty State Card)                   | (Empty State Card)                  |
|                                      |                                     |
| Recent Activity                      | Quick Actions                       |
| (Timeline Item)                      | [Add Cow] [Record Obs] [Twin] [Anal]|
+----------------------------------------------------------------------------+
```

| Dimension | Deficiencies & Findings |
|-----------|-------------------------|
| **Confusing Layout** | 6 KPI cards crammed into a single row (`repeat(6, 1fr)`). On medium laptops, numbers wrap awkwardly and cards look crushed. |
| **Poor Navigation** | Quick action buttons ("Add Cow", "Record Observation") are tucked away at the bottom right of the page instead of top-level hero CTA. |
| **Unnecessary Clicks** | To view why an alert is critical, Ramesh cannot click the alert card; he must navigate via sidebar to "Health Alerts". |
| **Inconsistent Spacing** | Top hero banner uses `1.1rem 1.2rem` padding, KPI cards use `0.9rem 1.0rem`, panel cards use `1rem 1rem 0.5rem`. |
| **Inconsistent Colors** | Tone colors are mixed: `dash-card-icon` uses `#1d4ed8` blue, `chip success` uses `#15803d` green, `alert-item` uses hardcoded RGBA borders. |
| **Poor Hierarchy** | Hero title "Green Pastures Farm" is smaller visually than metric values inside the KPI grid (`1.8rem` vs `1.5rem` clamp). |
| **Poor Typography** | Uppercase micro-labels (`dash-card-label`) use `0.72rem` (11.5px), which is illegible on mobile devices or in bright sunlight. |
| **Unnecessary Info** | Displaying "0 Cows", "0.0 L predicted output" on a fresh account without a prominent call to action to import sample data. |
| **Missing Info** | No historical trend indicators (e.g. "+2.4% vs yesterday"), no morning vs evening milking breakdown. |
| **Slow Workflows** | Dashboard recalculates health alerts and predictions synchronously on every page render. |
| **Accessibility Issues** | Dark text `#0f172a` on light blue background chips has low contrast for visual impairments. |
| **Responsiveness Issues** | On tablet screen (768px-1024px), the 6 KPI cards break into 3x2 grid with uneven card heights. |

---

### 3.5 My Herd

*File:* `webapp/screens/herd.py` (~697 lines)

| Dimension | Deficiencies & Findings |
|-----------|-------------------------|
| **Confusing Layout** | Add Cow form, search input, status filter, and breed filter are all stacked vertically above the cow table, pushing the actual herd list far down the screen. |
| **Poor Navigation** | Clicking a cow row does not open details directly; user must click an explicit inline "View Profile" button on the right edge of each card. |
| **Unnecessary Clicks** | Adding a cow requires expanding an inline section, filling fields, submitting, then manually closing the form. |
| **Inconsistent Spacing** | Search inputs use native Streamlit padding (`margin-bottom: 1rem`), while cow cards use custom CSS grids (`gap: 0.75rem`). |
| **Inconsistent Colors** | Cow health status badges use custom class names (`success`, `warning`, `danger`) that clash with standard Streamlit badge tints. |
| **Poor Hierarchy** | Search bar and filter dropdowns have higher visual weight than the "Add New Cow" primary action button. |
| **Poor Typography** | Cow ID ("COW-001") is displayed in small gray monospace font (`0.8rem`), making it hard for farmers to read tag numbers quickly. |
| **Unnecessary Info** | Displays internal UUID keys or database IDs if cow name is blank. |
| **Missing Info** | No batch selection checkboxes (cannot select 5 cows to record observations at once), no sorting options (sort by milk yield, age, or health risk). |
| **Slow Workflows** | Typing in the search input box triggers a full page re-render on every keystroke/blur. |
| **Accessibility Issues** | Table view uses small font sizes (`0.85rem`) with dense row height (`padding: 0.5rem`). |
| **Responsiveness Issues** | Multi-column table overflows horizontally on mobile devices without smooth touch scrolling. |

---

### 3.6 Cow Profile

*File:* `webapp/screens/cow_profile.py` (~467 lines)

```
+----------------------------------------------------------------------------+
|  🐄 Cow Profile: COW-001 (Lakshmi)                     [ Back to Herd ]    |
|  Holstein Friesian · 36 Months · 450 kg · Stable Status                   |
+----------------------------------------------------------------------------+
| [Overview]  [Observation History]  [Digital Twin]  [Prediction Analysis]  |
+----------------------------------------------------------------------------+
|  Current Metrics                     | AI Health Assessment                |
|  Yield: 24.5 L                       | Severity: Low                       |
|  Feed: 20.0 kg                       | Category: No Alert                  |
|  THI: 72.4 (Moderate)                | Recommendation: Maintain plan       |
+----------------------------------------------------------------------------+
```

| Dimension | Deficiencies & Findings |
|-----------|-------------------------|
| **Confusing Layout** | Uses standard Streamlit tabs (`st.tabs`) inside custom HTML container. Tabs render with default Streamlit red/orange underline theme, breaking blue/green design. |
| **Poor Navigation** | "Back to Herd" button uses `st.button`, which triggers a page rerun and resets herd search filters. |
| **Unnecessary Clicks** | Switching between "Overview" and "Digital Twin" tab requires waiting for tab re-render. |
| **Inconsistent Spacing** | Tab contents have no internal padding from tab header bar (`margin-top: 0`). |
| **Inconsistent Colors** | Tab 3 ("Digital Twin") renders twin status in purple `#8b5cf6` while main dashboard uses blue `#2563eb`. |
| **Poor Hierarchy** | Cow name and ID have equal font size (`1.25rem`); tag ID should be secondary. |
| **Poor Typography** | Metric values (e.g. "24.5 L") use standard paragraph text size (`1rem`) inside some sub-panels. |
| **Unnecessary Info** | Displays raw Python datetime ISO strings (e.g. `2026-08-02T02:20:41.123456`) in observation history instead of human-readable "Today, 8:30 AM". |
| **Missing Info** | No lineage/pedigree information, no lactation cycle chart (days in milk), no photo upload placeholder for physical cow identification. |
| **Slow Workflows** | Loading a cow profile recalculates live SHAP explanations for that cow synchronously. |
| **Accessibility Issues** | Tab labels lack keyboard visual focus rings in custom CSS override. |
| **Responsiveness Issues** | 4 horizontal tabs wrap onto 2 messy rows on mobile screens. |

---

### 3.7 Daily Operations

*File:* `webapp/screens/operations.py` (~432 lines)

```
+----------------------------------------------------------------------------+
|  Daily Operations & Observation Workflow                                   |
|  Step 1: Select Cow -> Step 2: Observation -> Step 3: Review -> Step 4/5  |
+----------------------------------------------------------------------------+
|  Select Cow: [ COW-001 (Lakshmi)                              v ]          |
|  Age (Months): [ 36.0 ]      Weight (kg): [ 450.0 ]                       |
|  Feed Intake (kg): [ 20.0 ]  Temp (°C): [ 28.0 ]   Humidity (%): [ 65.0 ]  |
|  Health Status Code: [ 0 ] (0=Normal, 1=Sick)                              |
|  Notes: [ Routine observation                                 ]            |
|  [                     Submit Observation (Button)                     ]   |
+----------------------------------------------------------------------------+
```

| Dimension | Deficiencies & Findings |
|-----------|-------------------------|
| **Confusing Layout** | Advertised as a "5-Step Guided Workflow" with step pills (`(1) Select Cow (2) Observation (3) Review...`), but steps 1 & 2 are displayed together in one static form. The progress bar is decorative rather than interactive. |
| **Poor Navigation** | After submitting an observation, user is taken to "Results" phase; to log another cow, they must click a small "Record Another Observation" button at the bottom. |
| **Unnecessary Clicks** | Requires manually typing ambient Temperature (°C) and Humidity (%) even though live weather is already available in the topbar. |
| **Inconsistent Spacing** | Form field columns use unequal gap settings (`gap="small"` vs `gap="medium"`). |
| **Inconsistent Colors** | Step indicator pills use dark navy `#0f172a` for active step and washed-out gray `#e2e8f0` for pending steps. |
| **Poor Hierarchy** | "Health Status Code" input asks for an integer (`0` or `1`) — highly technical and non-intuitive for a farmer who expects "Healthy / Sick / Injured" dropdown. |
| **Poor Typography** | Numerical step indicators use small `0.75rem` bold text inside small circles. |
| **Unnecessary Info** | Requires entering cow's age and weight on *every single daily observation*, even though age and weight change very slowly. |
| **Missing Info** | No auto-fill button ("Use current weather"), no option to attach a visual symptom image, no voice note input option. |
| **Slow Workflows** | Submission triggers sequential calls to prediction, health, SHAP explainability, and memory snapshot creation, taking 2-4 seconds. |
| **Accessibility Issues** | Health status integer input (`0` vs `1`) provides no onscreen explanation of what other status codes exist. |
| **Responsiveness Issues** | 3-column input layout (`Age | Weight | Feed`) collapses into narrow single columns on mobile with excessive vertical scrolling. |

---

### 3.8 Digital Twin Workspace

*File:* `webapp/screens/digital_twin.py` (~406 lines)

| Dimension | Deficiencies & Findings |
|-----------|-------------------------|
| **Confusing Layout** | Screen attempts to display twin status, real-time telemetry, snapshot memory history, and what-if simulation all on one page. Extremely overwhelming. |
| **Poor Navigation** | Simulation controls (Feed Slider, Temp Slider) are placed below snapshot history, forcing users to scroll past long lists to run a scenario. |
| **Unnecessary Clicks** | User must select a cow from a dropdown even if they already selected a cow in the Herd management screen (state not automatically linked). |
| **Inconsistent Spacing** | Telemetry grid uses custom CSS flexbox while simulation results use Streamlit dataframe wrapper (`st.dataframe`). |
| **Inconsistent Colors** | Twin status uses non-standard terms ("Stressed", "At Risk", "Emerging Risk") with colors (purple, amber, red) that differ from main Dashboard alert tones. |
| **Poor Hierarchy** | Conceptual state JSON dump ("Context Metadata") is displayed in an expanded expander card with technical key-value pairs. |
| **Poor Typography** | Terminology like "Immutable Snapshot Vector" and "Telemetry Synchronization" sounds like software developer jargon, not farm management terminology. |
| **Unnecessary Info** | Displays internal snapshot IDs (e.g. `COW-001:20260802022041123456`) in the main UI. |
| **Missing Info** | No visual 3D or 2D graphical representation of a "Twin" (only text metrics and tables), no historical twin state timeline comparison. |
| **Slow Workflows** | Changing simulation sliders re-runs interval Random Forest predictions across 30 grid points dynamically. |
| **Accessibility Issues** | Streamlit default dataframe table inside twin memory tab has small 12px text and poor screen-reader support. |
| **Responsiveness Issues** | Simulation heatmap image / Plotly chart scales down on mobile, making axis text unreadable. |

---

### 3.9 Health Alerts

*File:* `webapp/screens/health.py` (~305 lines)

| Dimension | Deficiencies & Findings |
|-----------|-------------------------|
| **Confusing Layout** | Screen presents a large table of alerts with top filter buttons ("All", "Critical", "Warning", "Healthy"). Filter buttons look like standard buttons rather than toggle tabs. |
| **Poor Navigation** | Clicking on an alert row does not open the affected cow's profile or daily operations form. The table is static. |
| **Unnecessary Clicks** | Filtering by severity requires clicking a button, which triggers a full-page rerun. |
| **Inconsistent Spacing** | Alert summary cards have `margin-bottom: 1.2rem` while filter buttons have `margin-bottom: 0.5rem`. |
| **Inconsistent Colors** | Uses 3 different red shades for "Critical" (`#b91c1c`, `#ef4444`, `rgba(239,68,68,0.7)`). |
| **Poor Hierarchy** | Metric counts at the top ("0 Critical", "0 Warning") have the same size as section headers. |
| **Poor Typography** | Alert recommendations are displayed in generic italic text without actionable bolding. |
| **Unnecessary Info** | Displays THI formula calculations (e.g., `THI = 78.4 (Formula: NRC 2001)`) directly inside alert cards. |
| **Missing Info** | No "Acknowledge Alert" or "Mark as Resolved" action buttons. Farmers cannot clear alerts once addressed. |
| **Slow Workflows** | Alert list reads from in-memory snapshots; if no observations logged, screen shows empty states without actionable setup links. |
| **Accessibility Issues** | Red warning text on light red background (`#b91c1c` on `rgba(239,68,68,0.1)`) can be difficult for color-blind users (protanopia/deuteranopia). |
| **Responsiveness Issues** | Filter button group wraps awkwardly into multiple lines on mobile screens. |

---

### 3.10 Analytics Workspace

*File:* `webapp/screens/analytics.py` (~308 lines)

```
+----------------------------------------------------------------------------+
|  Analytics & Research Insights                                             |
|  [ Date Range: 7 Days v ]  [ Cow: All v ]  [ Breed: All v ]  [ Export Data ]|
+----------------------------------------------------------------------------+
|  Milk Production Trend (Plotly Chart)                                      |
|  [ Line chart showing Predicted vs Actual Yield over time ]                |
+----------------------------------------------------------------------------+
|  Weather Impact Analysis (THI vs Milk Output)                              |
|  [ Scatter plot / Dual axis chart ]                                        |
+----------------------------------------------------------------------------+
```

| Dimension | Deficiencies & Findings |
|-----------|-------------------------|
| **Confusing Layout** | Screen is a vertical stack of 4 heavy Plotly charts with dense filter controls at the top. Requires endless vertical scrolling. |
| **Poor Navigation** | No jump-links or sticky sub-navigation to skip directly to "Weather Correlation" or "Herd Trends". |
| **Unnecessary Clicks** | Date range filter requires selecting start date and end date via standard Streamlit date pickers (2 separate calendar popups). |
| **Inconsistent Spacing** | Plotly charts have built-in margins that clash with surrounding CSS panel card padding. |
| **Inconsistent Colors** | Plotly chart lines use default Plotly blue/orange palette, which differs from the app's custom `--dv-accent` hex code (`#2563eb`). |
| **Poor Hierarchy** | Chart titles inside Plotly frames (`font-size: 14px`) are smaller than panel container headers (`0.9rem` bold). |
| **Poor Typography** | Axis labels on Plotly charts use default sans-serif font rather than matching app CSS font family (`Avenir Next` / system stack). |
| **Unnecessary Info** | Shows raw statistical metrics ($R^2$, $MAE$, $RMSE$) in research export view — meaningless to a farmer who just wants yield trends. |
| **Missing Info** | No comparative benchmark (e.g. "Your herd average vs regional benchmark"), no feed conversion efficiency chart. |
| **Slow Workflows** | Rendering 4 interactive Plotly charts on every page load consumes significant browser memory and causes layout shift. |
| **Accessibility Issues** | Interactive Plotly tooltips are difficult to trigger on touch screens (smartphones/tablets). |
| **Responsiveness Issues** | Chart legend labels overlap chart titles on narrow mobile screens. |

---

### 3.11 Explainability (SHAP)

*File:* `webapp/screens/explainability.py` (~252 lines)

```
+----------------------------------------------------------------------------+
|  Explainability & Model Transparency (SHAP Analysis)                       |
|  Understanding key factors driving milk yield predictions                  |
+----------------------------------------------------------------------------+
|  Feature Contribution Breakdown (Waterfall / Bar Chart)                    |
|  1. Feed Intake (+3.2 L)                                                   |
|  2. THI Index (-1.8 L)                                                     |
|  3. Age (-0.4 L)                                                           |
+----------------------------------------------------------------------------+
|  Global Feature Importance (SHAP Summary PNG)                              |
|  [ Pre-rendered matplotlib image embedded ]                                |
+----------------------------------------------------------------------------+
```

| Dimension | Deficiencies & Findings |
|-----------|-------------------------|
| **Confusing Layout** | Combines live per-cow feature contribution bars with pre-rendered static PNG images from offline training runs (`shap_summary.png`). Confusing mix of live vs static data. |
| **Poor Navigation** | No explanation of how to interpret positive vs negative SHAP contribution values. |
| **Unnecessary Clicks** | User must select a cow, submit, then scroll down to see the SHAP waterfall chart. |
| **Inconsistent Spacing** | Static PNG image container has different border radius than interactive HTML contribution bars. |
| **Inconsistent Colors** | Matplotlib static PNG uses default `coolwarm` color scale (pink/blue), while live bars use blue/green theme. |
| **Poor Hierarchy** | Scientific terminology ("SHAP Value", "Mean Absolute SHAP Magnitude") occupies primary heading real estate. |
| **Poor Typography** | Technical feature column names (`feed_thi_interaction`, `feed_weight_ratio`, `thi_squared`) displayed directly without translation into plain English ("Feed-Heat Interaction", "Feed per Body Weight"). |
| **Unnecessary Info** | Exposes raw mathematical feature interaction terms ($THI^2$, $Feed \times THI$) to end users. |
| **Missing Info** | No actionable guidance explaining *how* the farmer can change a negative feature (e.g., "Increase feed by 2kg to counter heat impact"). |
| **Slow Workflows** | Calculating SHAP values dynamically via `TreeExplainer` on input change introduces a 1-3 second delay. |
| **Accessibility Issues** | Embedded PNG images (`shap_summary.png`) have non-descriptive alt text and cannot be scaled or read by screen readers. |
| **Responsiveness Issues** | Static Matplotlib PNG images shrink on mobile screens, rendering text axis labels unreadable. |

---

### 3.12 Settings Workspace

*File:* `webapp/screens/settings.py` (~87 lines)

| Dimension | Deficiencies & Findings |
|-----------|-------------------------|
| **Confusing Layout** | Displays read-only user/farm information cards at top, followed by 3 tabs ("Application Preferences", "Notifications", "About"). |
| **Poor Navigation** | Dead UI controls: Dropdowns for Theme ("Light", "Dark"), Layout Density, and Notification Checkboxes are non-functional (changes are not saved to database or session state). |
| **Unnecessary Clicks** | Interacting with settings dropdowns causes a full page rerun without persisting choices. |
| **Inconsistent Spacing** | Settings panels use hardcoded `padding: 1rem` inside tabs that already have container padding. |
| **Inconsistent Colors** | Tab bar uses default Streamlit underline style instead of matching app navigation pills. |
| **Poor Hierarchy** | Read-only info (Farm ID) is given more prominence than editable preferences. |
| **Poor Typography** | Labels use 14px default text with no descriptive subtext explaining what each setting does. |
| **Unnecessary Info** | Displays internal environment string ("Environment: Current workspace configuration"). |
| **Missing Info** | No password change option, no farm location update form, no team member management / user role configuration. |
| **Slow Workflows** | Toggling any checkbox triggers full app re-render. |
| **Accessibility Issues** | Form controls inside tabs lack explicit group labels. |
| **Responsiveness Issues** | 2-column grid (`settings-grid`) collapses awkwardly on medium screens. |

---

### 3.13 Command Centre (Operations Center)

*File:* `webapp/screens/command_centre.py` (~298 lines)

| Dimension | Deficiencies & Findings |
|-----------|-------------------------|
| **Confusing Layout** | Multi-panel dashboard attempting to combine Live Feed, Alert Buckets, System Health, and Weather Monitor into a 2-column grid. Cluttered visual appearance. |
| **Poor Navigation** | "Live Feed" items are not clickable links (cannot click an event to open corresponding cow or observation). |
| **Unnecessary Clicks** | Must manually refresh page to see updated events (no real-time WebSocket event streaming). |
| **Inconsistent Spacing** | Column gaps differ between top metric cards and lower feeds (`gap="medium"` vs hardcoded CSS gaps). |
| **Inconsistent Colors** | System status badges use custom inline CSS colors (`#15803d` vs `#1d4ed8`) that differ slightly from Dashboard status pills. |
| **Poor Hierarchy** | "System Health" (Model status, Supabase connection) is shown prominently at top right — technical info that is irrelevant to a dairy farmer. |
| **Poor Typography** | Activity feed timestamps use generic ISO time format (`14:22:01`) without date context. |
| **Unnecessary Info** | Displays technical system status ("Supabase Status: Connected (In-Memory)") which reveals backend implementation details to users. |
| **Missing Info** | No emergency broadcast button, no quick-dispatch action for barn workers, no live video/camera stream integration placeholder. |
| **Slow Workflows** | Assembles telemetry from all registered cow twins simultaneously on every refresh. |
| **Accessibility Issues** | High visual noise with competing badges, indicators, and colored border accents on a single screen. |
| **Responsiveness Issues** | 2-column grid breaks into long single column on mobile, hiding Weather and System Health at the bottom. |

---

## 4. Cross-Screen Consistency Matrix

| UX Element | Dashboard | My Herd | Daily Ops | Digital Twin | Health Alerts | Analytics | Explainability | Settings | Command Centre |
|------------|-----------|---------|-----------|--------------|---------------|-----------|----------------|----------|----------------|
| **Header Style** | Custom Hero | Custom H1 | Step Header | Custom H1 | Page Header | Page Header | Page Header | Page Header | Page Header |
| **Card Container** | `.dashboard-card` | `.cow-card` | `.ops-card` | `.twin-card` | `.alert-item` | `.panel-card` | `.panel-card` | `.settings-panel` | `.panel-card` |
| **Status Badges** | Custom CSS | Custom CSS | Step Pills | Custom CSS | HTML Badges | Plotly Legend | HTML Bars | Native Select | Inline Spans |
| **Primary Action** | Button | Button | Form Submit | Slider | None | Date Picker | Dropdown | Checkbox | Button |
| **Form Inputs** | None | Native | Native | Native | Native | Native | Native | Native | None |
| **Tab Control** | None | None | None | None | Buttons | None | None | `st.tabs` | None |
| **Color Theme** | Blue/Green | Blue/Slate | Blue/Slate | Blue/Purple | Red/Amber | Plotly Default | Pink/Blue PNG | Default | Blue/Navy |

> **Key Finding:** Every screen re-invents its own container card styles, headers, and status badges. There is no single unified UI component library being reused across screens.

---

## 5. Summary of UX Deficiencies

### Top 10 High-Impact UX Issues to Address in Future Iterations

1. **In-Memory Fake Persistence Warning:** Users are not warned that data entered in forms will disappear on server restart.
2. **Jargon-Heavy Interface:** Exposing technical ML parameters ($R^2$, SHAP values, $THI^2$, `feed_thi_interaction`) directly to dairy farmers without plain-language translations.
3. **Non-Interactive Alert Cards:** Health alerts cannot be clicked to open cow profiles or acknowledged/cleared.
4. **Manual Weather Entry in Daily Ops:** Users must type temperature/humidity manually despite live weather data existing in the topbar.
5. **No Password Reset / Account Management:** Locked out users cannot recover accounts; settings preferences are dead UI controls.
6. **Form Inputs Lack Biological Validation:** Free-text inputs for breeds, status codes (`0` vs `1`), and unconstrained numerical values.
7. **Mobile Responsiveness Breaks:** 6-column KPI grids, multi-column tables, and static PNG images break on mobile viewports (<480px).
8. **Static Fake UI Primitives:** Topbar notification bell and user profile avatar are non-clickable decorative icons.
9. **Full-Page Reruns & Scroll Resets:** Native Streamlit interaction model causes visible page flicker on every dropdown or tab change.
10. **Duplicated Screen Logic:** Observation normalization and twin rendering logic copied 4× across screen files.

---

*End of UI/UX Audit — `docs/project_audit/02_ui_ux_audit.md`*  
*Generated by architectural evaluation of all webapp screen files. No code was modified.*
