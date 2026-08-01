"""Export helpers for the analytics workspace."""
from __future__ import annotations

import io
from typing import Any

import pandas as pd
import streamlit as st


def _build_simple_pdf(content: str) -> bytes:
    """Generate a minimal PDF payload without introducing new dependencies."""
    escaped = content.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
    pdf_lines = [
        "%PDF-1.4",
        "1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj",
        "2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj",
        "3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >> endobj",
        "4 0 obj << /Length 0 >> stream\nendstream endobj",
        "5 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj",
    ]
    stream = f"BT /F1 12 Tf 72 720 Td ({escaped}) Tj ET"
    pdf_lines[3] = f"4 0 obj << /Length {len(stream.encode('latin-1'))} >> stream\n{stream}\nendstream endobj"
    objects = []
    offset = 0
    for line in pdf_lines:
        objects.append((offset, line))
        offset += len(line.encode("latin-1")) + 1
    pdf = b"".join(line.encode("latin-1") + b"\n" for _, line in objects)
    return pdf


def render_export_panel(frame: pd.DataFrame) -> None:
    """Render CSV and PDF export actions when data is available."""
    if frame.empty:
        return
    csv_bytes = frame.to_csv(index=False).encode("utf-8")
    st.download_button("Export CSV", data=csv_bytes, file_name="analytics_export.csv", mime="text/csv")
    pdf_bytes = _build_simple_pdf(frame.to_string(index=False))
    st.download_button("Export PDF", data=pdf_bytes, file_name="analytics_export.pdf", mime="application/pdf")
