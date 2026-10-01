"""Pandas/Matplotlib reporting for the patient dataset."""

from __future__ import annotations

from pathlib import Path

from .models import Patient


def build_dataframe(patients: list[Patient]):
    """Convert Patient objects into a Pandas DataFrame."""
    import pandas as pd

    rows = []
    for patient in patients:
        rows.append({
            "Patient ID": patient.identification.patient_id,
            "Name": patient.info.name,
            "Department": patient.info.department,
            "Age": patient.info.age,
            "Gender": patient.info.gender,
            "Diagnosis": patient.visit.diagnosis,
            "Patient Type": patient.patient_type,
            "Charges": patient.billing.charges,
            "Payment": patient.billing.payment_method,
            "Status": patient.billing.discharge_status,
            "BMI": patient.vitals.bmi(),
        })
    return pd.DataFrame(rows)


def generate_reports(patients: list[Patient], reports_dir: Path) -> list[Path]:
    """Generate CSV statistics and two PNG charts."""
    if not patients:
        raise ValueError("No patients available for reporting.")

    reports_dir.mkdir(parents=True, exist_ok=True)
    df = build_dataframe(patients)
    generated: list[Path] = []

    stats_path = reports_dir / "patient_statistics.csv"
    df.describe(include="all").transpose().to_csv(stats_path)
    generated.append(stats_path)

    csv_path = reports_dir / "patients_from_pandas.csv"
    df.to_csv(csv_path, index=False)
    generated.append(csv_path)

    import matplotlib.pyplot as plt

    age_path = reports_dir / "patient_age_distribution.png"
    plt.figure(figsize=(8, 5))
    plt.hist(df["Age"], bins=8)
    plt.title("Patient Age Distribution")
    plt.xlabel("Age")
    plt.ylabel("Number of Patients")
    plt.tight_layout()
    plt.savefig(age_path)
    plt.close()
    generated.append(age_path)

    dept_counts = df["Department"].value_counts()
    dept_path = reports_dir / "department_distribution.png"
    plt.figure(figsize=(8, 5))
    dept_counts.plot(kind="bar")
    plt.title("Patients by Department")
    plt.xlabel("Department")
    plt.ylabel("Number of Patients")
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    plt.savefig(dept_path)
    plt.close()
    generated.append(dept_path)

    return generated
