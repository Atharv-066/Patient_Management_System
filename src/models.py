"""Domain classes for the Patient Management System."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class PatientInfo:
    name: str
    department: str
    age: int
    gender: str
    address: str
    contact: str


@dataclass
class PatientID:
    patient_id: int
    aadhaar: str
    insurance_id: int


@dataclass
class MedicalHistory:
    past_illness: str
    surgeries: str
    allergies: str
    diabetes: str
    asthma: str
    chronic_diseases: str = "None"


@dataclass
class TreatmentDetails:
    medicines: str
    tests: str
    procedures: str


@dataclass
class VisitInfo:
    visit_date: str
    symptoms: str
    diagnosis: str
    attending_doctor: str
    resident_doctor: str


@dataclass
class VitalSigns:
    temperature: float
    weight: float
    height: float
    pulse: int
    blood_pressure: str
    respiratory_rate: int = 16

    def bmi(self) -> float:
        """Calculate BMI using height in cm and weight in kg."""
        height_m = self.height / 100
        return round(self.weight / (height_m * height_m), 2)


@dataclass
class BillingDetails:
    charges: float
    payment_method: str
    insurance_claim: str
    discharge_status: str


@dataclass
class Patient:
    """Main patient object, composed of the same conceptual sections as the Java project."""

    info: PatientInfo
    identification: PatientID
    history: MedicalHistory
    treatment: TreatmentDetails
    visit: VisitInfo
    vitals: VitalSigns
    billing: BillingDetails
    patient_type: str = "General"
    created_at: str = ""

    def care_summary(self) -> str:
        """Polymorphic method overridden by specialized patient classes."""
        return f"General patient care for {self.info.name}."

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Patient":
        patient_type = data.get("patient_type", "General")
        common = dict(
            info=PatientInfo(**data["info"]),
            identification=PatientID(**data["identification"]),
            history=MedicalHistory(**data["history"]),
            treatment=TreatmentDetails(**data["treatment"]),
            visit=VisitInfo(**data["visit"]),
            vitals=VitalSigns(**data["vitals"]),
            billing=BillingDetails(**data["billing"]),
            patient_type=patient_type,
            created_at=data.get("created_at", ""),
        )
        if patient_type == "InPatient":
            return InPatient(**common)
        if patient_type == "OutPatient":
            return OutPatient(**common)
        return cls(**common)

    def display_lines(self) -> list[str]:
        """Return a readable complete record."""
        return [
            "\n========== PATIENT RECORD ==========",
            f"Patient Type       : {self.patient_type}",
            f"Patient ID         : {self.identification.patient_id}",
            f"Name               : {self.info.name}",
            f"Department         : {self.info.department}",
            f"Age / Gender       : {self.info.age} / {self.info.gender}",
            f"Address            : {self.info.address}",
            f"Contact            : {self.info.contact}",
            f"Aadhaar            : {self.identification.aadhaar}",
            f"Insurance ID       : {self.identification.insurance_id}",
            "\n--- Medical History ---",
            f"Past Illness       : {self.history.past_illness}",
            f"Surgeries          : {self.history.surgeries}",
            f"Allergies          : {self.history.allergies}",
            f"Diabetes           : {self.history.diabetes}",
            f"Asthma             : {self.history.asthma}",
            f"Chronic Diseases   : {self.history.chronic_diseases}",
            "\n--- Treatment ---",
            f"Medicines          : {self.treatment.medicines}",
            f"Tests              : {self.treatment.tests}",
            f"Procedures         : {self.treatment.procedures}",
            "\n--- Vital Signs ---",
            f"Temperature        : {self.vitals.temperature} °C",
            f"Weight             : {self.vitals.weight} kg",
            f"Height             : {self.vitals.height} cm",
            f"BMI                : {self.vitals.bmi()}",
            f"Pulse              : {self.vitals.pulse} /min",
            f"Blood Pressure     : {self.vitals.blood_pressure}",
            f"Respiratory Rate   : {self.vitals.respiratory_rate} /min",
            "\n--- Visit ---",
            f"Visit Date         : {self.visit.visit_date}",
            f"Symptoms           : {self.visit.symptoms}",
            f"Diagnosis          : {self.visit.diagnosis}",
            f"Attending Doctor   : {self.visit.attending_doctor}",
            f"Resident Doctor    : {self.visit.resident_doctor}",
            "\n--- Billing ---",
            f"Charges            : ₹{self.billing.charges:.2f}",
            f"Payment Method     : {self.billing.payment_method}",
            f"Insurance Claim    : {self.billing.insurance_claim}",
            f"Discharge Status   : {self.billing.discharge_status}",
            "\n--- Care Summary ---",
            self.care_summary(),
            "===================================",
        ]


@dataclass
class InPatient(Patient):
    """Specialized patient type demonstrating inheritance."""

    def care_summary(self) -> str:
        return (
            f"In-patient {self.info.name} requires ward/in-hospital monitoring "
            f"under {self.visit.attending_doctor}."
        )


@dataclass
class OutPatient(Patient):
    """Specialized patient type demonstrating inheritance."""

    def care_summary(self) -> str:
        return (
            f"Out-patient {self.info.name} is managed through scheduled consultation "
            f"with {self.visit.attending_doctor}."
        )
