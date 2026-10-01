"""Input validation helpers for the Patient Management System."""

from datetime import date, datetime

ALLOWED_GENDERS = ("Male", "Female", "Other")
ALLOWED_PAYMENTS = ("cash", "card", "upi")
ALLOWED_DISCHARGE = ("Admitted", "Discharged")


def require_text(value: str, field_name: str) -> str:
    """Return stripped text or raise ValueError for an empty value."""
    value = value.strip()
    if not value:
        raise ValueError(f"{field_name} cannot be empty.")
    return value


def validate_patient_id(value: int) -> int:
    if value <= 0:
        raise ValueError("Patient ID must be a positive integer.")
    return value


def validate_age(value: int) -> int:
    if value < 0 or value > 120:
        raise ValueError("Age must be between 0 and 120.")
    return value


def validate_mobile(value: str) -> str:
    value = value.strip()
    if not (value.isdigit() and len(value) == 10):
        raise ValueError("Mobile number must contain exactly 10 digits.")
    return value


def validate_aadhaar(value: str) -> str:
    value = value.strip()
    if not (value.isdigit() and len(value) == 12):
        raise ValueError("Aadhaar number must contain exactly 12 digits.")
    return value


def validate_gender(value: str) -> str:
    normalized = value.strip().title()
    if normalized not in ALLOWED_GENDERS:
        raise ValueError(f"Gender must be one of: {', '.join(ALLOWED_GENDERS)}")
    return normalized


def validate_payment(value: str) -> str:
    normalized = value.strip().lower()
    if normalized not in ALLOWED_PAYMENTS:
        raise ValueError(f"Payment method must be one of: {', '.join(ALLOWED_PAYMENTS)}")
    return normalized


def validate_discharge(value: str) -> str:
    normalized = value.strip().title()
    if normalized not in ALLOWED_DISCHARGE:
        raise ValueError(f"Discharge status must be one of: {', '.join(ALLOWED_DISCHARGE)}")
    return normalized


def parse_date(value: str) -> str:
    """Validate DD-MM-YYYY and return it in the same display format."""
    value = value.strip()
    parsed = datetime.strptime(value, "%d-%m-%Y").date()
    if parsed > date.today():
        raise ValueError("Visit/admission date cannot be in the future.")
    return parsed.strftime("%d-%m-%Y")


def positive_number(value: float, field_name: str) -> float:
    if value <= 0:
        raise ValueError(f"{field_name} must be greater than zero.")
    return value
