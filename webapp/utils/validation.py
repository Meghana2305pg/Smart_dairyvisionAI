"""Validation helpers for onboarding and operations flows."""
from __future__ import annotations

import re
from typing import Any

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def validate_login_form(email: str, password: str) -> list[str]:
    """Validate credentials for the login workflow."""
    errors: list[str] = []
    if not email or not str(email).strip():
        errors.append("Email is required.")
    elif not EMAIL_PATTERN.match(str(email).strip()):
        errors.append("Please enter a valid email address.")
    if not password or not str(password).strip():
        errors.append("Password is required.")
    elif len(str(password).strip()) < 8:
        errors.append("Password must be at least 8 characters long.")
    return errors


def validate_registration_form(email: str, password: str, confirm_password: str, full_name: str) -> list[str]:
    """Validate account registration input."""
    errors = validate_login_form(email, password)
    if not full_name or not str(full_name).strip():
        errors.append("Please enter your full name.")
    if str(password or "").strip() and str(confirm_password or "").strip() and str(password) != str(confirm_password):
        errors.append("Passwords do not match.")
    return errors


def validate_farm_setup_form(name: str, location: str | None = None, farm_size: str | None = None) -> list[str]:
    """Validate farm onboarding input."""
    errors: list[str] = []
    if not name or not str(name).strip():
        errors.append("Farm name is required.")
    if location and not str(location).strip():
        errors.append("Location cannot be blank when provided.")
    if farm_size is not None and str(farm_size).strip():
        try:
            float(farm_size)
        except ValueError:
            errors.append("Farm size must be a number.")
    return errors


def validate_cow_registration_form(cow_id: str, name: str) -> list[str]:
    """Validate the cow registration form."""
    errors: list[str] = []
    if not cow_id or not str(cow_id).strip():
        errors.append("Cow ID is required.")
    elif len(str(cow_id).strip()) > 64:
        errors.append("Cow ID is too long. Use a shorter identifier.")
    if not name or not str(name).strip():
        errors.append("Cow name is required.")
    return errors


def validate_daily_operations_form(values: dict[str, Any]) -> list[str]:
    """Validate the daily operations form values."""
    errors: list[str] = []
    try:
        age = float(values.get("age", 0))
        if age <= 0:
            errors.append("Age must be greater than zero.")
    except (TypeError, ValueError):
        errors.append("Age must be numeric.")

    for field in ("weight", "feed"):
        try:
            value = float(values.get(field, 0))
            if value <= 0:
                errors.append(f"{field.replace('_', ' ').title()} must be greater than zero.")
        except (TypeError, ValueError):
            errors.append(f"{field.replace('_', ' ').title()} must be numeric.")

    for field in ("temperature", "humidity"):
        try:
            value = float(values.get(field, 0))
            if value < 0:
                errors.append(f"{field.replace('_', ' ').title()} cannot be negative.")
        except (TypeError, ValueError):
            errors.append(f"{field.replace('_', ' ').title()} must be numeric.")

    if values.get("cow_id") in {None, ""}:
        errors.append("Please select a cow before recording an observation.")
    notes = str(values.get("notes") or "").strip()
    if len(notes) > 200:
        errors.append("Observation notes are too long. Keep them under 200 characters.")
    return errors
