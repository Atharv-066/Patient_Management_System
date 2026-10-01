"""Business operations for patient records."""

from __future__ import annotations

from datetime import datetime
from typing import Callable

from .models import Patient
from .storage import PatientRepository


class PatientManager:
    """Coordinates add/search/update/delete operations."""

    def __init__(self, repository: PatientRepository):
        self.repository = repository
        self.patients: list[Patient] = repository.load()

    def add_patient(self, patient: Patient) -> None:
        if self.find_by_id(patient.identification.patient_id) is not None:
            raise ValueError("A patient with this ID already exists.")
        if not patient.created_at:
            patient.created_at = datetime.now().isoformat(timespec="seconds")
        self.patients.append(patient)
        self.repository.save_all(self.patients)

    def find_by_id(self, patient_id: int) -> Patient | None:
        for patient in self.patients:
            if patient.identification.patient_id == patient_id:
                return patient
        return None

    def find_by_name(self, name: str) -> list[Patient]:
        matches: list[Patient] = []
        for patient in self.patients:
            if name.casefold() in patient.info.name.casefold():
                matches.append(patient)
        return matches

    def find_by_department(self, department: str) -> list[Patient]:
        return [
            patient for patient in self.patients
            if patient.info.department.casefold() == department.casefold()
        ]

    def update_patient(self, patient_id: int, updater: Callable[[Patient], None]) -> Patient:
        patient = self.find_by_id(patient_id)
        if patient is None:
            raise LookupError("Patient not found.")
        updater(patient)
        self.repository.save_all(self.patients)
        return patient

    def delete_patient(self, patient_id: int) -> Patient:
        for index, patient in enumerate(self.patients):
            if patient.identification.patient_id == patient_id:
                removed = self.patients.pop(index)
                self.repository.save_all(self.patients)
                return removed
        raise LookupError("Patient not found.")

    def departments(self) -> set[str]:
        return {patient.info.department for patient in self.patients}

    def diagnoses(self) -> set[str]:
        return {patient.visit.diagnosis for patient in self.patients}
