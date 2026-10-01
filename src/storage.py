"""JSON persistence and CSV export."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Iterable

from .models import Patient


class PatientRepository:
    """Stores Patient objects in a JSON file."""

    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.file_path.exists():
            self._write([])

    def _write(self, patients: list[Patient]) -> None:
        with self.file_path.open("w", encoding="utf-8") as file:
            json.dump([patient.to_dict() for patient in patients], file, indent=4)

    def load(self) -> list[Patient]:
        try:
            with self.file_path.open("r", encoding="utf-8") as file:
                raw_data = json.load(file)
            return [Patient.from_dict(item) for item in raw_data]
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def save_all(self, patients: list[Patient]) -> None:
        self._write(patients)

    def export_csv(self, patients: Iterable[Patient], output_path: Path) -> None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        fields = [
            "patient_id", "name", "department", "age", "gender", "diagnosis",
            "visit_date", "patient_type", "charges", "payment_method",
            "discharge_status", "bmi",
        ]
        with output_path.open("w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=fields)
            writer.writeheader()
            for patient in patients:
                writer.writerow({
                    "patient_id": patient.identification.patient_id,
                    "name": patient.info.name,
                    "department": patient.info.department,
                    "age": patient.info.age,
                    "gender": patient.info.gender,
                    "diagnosis": patient.visit.diagnosis,
                    "visit_date": patient.visit.visit_date,
                    "patient_type": patient.patient_type,
                    "charges": patient.billing.charges,
                    "payment_method": patient.billing.payment_method,
                    "discharge_status": patient.billing.discharge_status,
                    "bmi": patient.vitals.bmi(),
                })
