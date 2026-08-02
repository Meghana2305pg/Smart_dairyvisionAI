"""Unit tests for the centralized design system."""

from __future__ import annotations

import unittest

from webapp.ui import (
    BORDER,
    DANGER,
    FONT_BODY,
    FONT_FAMILY,
    FONT_PAGE_TITLE,
    PRIMARY,
    PRIMARY_HOVER,
    RADIUS_LARGE,
    RADIUS_MEDIUM,
    RADIUS_SMALL,
    SHADOW_CARD,
    SHADOW_SM,
    SPACING_LG,
    SPACING_MD,
    SPACING_SM,
    SPACING_XL,
    SPACING_XS,
    SUCCESS,
    TEXT_MUTED,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    WARNING,
    apply_global_theme,
    render_alert_card,
    render_empty_state,
    render_info_card,
    render_metric_card,
    render_page_header,
    render_recommendation_card,
    render_section_title,
    render_status_badge,
)


class DesignSystemTests(unittest.TestCase):
    """Test suite for the centralized design system design tokens and helper functions."""

    def test_semantic_colors_defined(self) -> None:
        """Verify semantic color tokens are defined."""
        self.assertEqual(PRIMARY, "#2563eb")
        self.assertEqual(PRIMARY_HOVER, "#1d4ed8")
        self.assertEqual(SUCCESS, "#15803d")
        self.assertEqual(WARNING, "#b45309")
        self.assertEqual(DANGER, "#b91c1c")
        self.assertEqual(TEXT_PRIMARY, "#0f172a")
        self.assertEqual(TEXT_SECONDARY, "#475569")

    def test_typography_scale_tokens_defined(self) -> None:
        """Verify typography scale tokens are defined."""
        self.assertIn("Avenir Next", FONT_FAMILY)
        self.assertTrue(FONT_PAGE_TITLE.startswith("clamp"))
        self.assertEqual(FONT_BODY, "0.95rem")

    def test_spacing_and_radius_tokens_defined(self) -> None:
        """Verify spacing scale and border radius tokens are defined."""
        self.assertEqual(SPACING_XS, "0.25rem")
        self.assertEqual(SPACING_SM, "0.5rem")
        self.assertEqual(SPACING_MD, "1rem")
        self.assertEqual(RADIUS_SMALL, "10px")
        self.assertEqual(RADIUS_MEDIUM, "16px")
        self.assertEqual(RADIUS_LARGE, "24px")

    def test_shadow_tokens_defined(self) -> None:
        """Verify shadow tokens are defined."""
        self.assertTrue("rgba" in SHADOW_SM)
        self.assertTrue("rgba" in SHADOW_CARD)

    def test_render_helpers_callable(self) -> None:
        """Verify helper rendering functions execute without raising errors."""
        try:
            apply_global_theme()
            render_page_header("Test Page", subtitle="Test Subtitle", badge="Test Badge")
            render_section_title("Section Title", subtitle="Section Subtitle")
            render_metric_card(title="Total Cows", value="40", subtitle="Active herd", icon="🐄", tone="success")
            render_info_card(title="Notice", content="System operating normally", footer="Updated 10m ago")
            render_status_badge(label="Healthy", status_type="success")
            render_alert_card(title="Heat Warning", message="THI elevated", severity="warning", timestamp="10:00 AM")
            render_recommendation_card(title="Increase Shade", description="Add shade cloth", priority="high")
            render_empty_state(title="No Alerts", message="Everything is normal", icon="✅")
        except Exception as exc:
            self.fail(f"Design system render helper raised an unexpected exception: {exc}")


if __name__ == "__main__":
    unittest.main()
