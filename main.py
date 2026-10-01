"""Command-line entry point for the Programming Methodology mini project."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from src.models import (
    BillingDetails,
    InPatient,
    MedicalHistory,
    OutPatient,
    Patient,
    PatientID,
    PatientInfo,
    TreatmentDetails,
    VisitInfo,
    VitalSigns,
)
from src.reports import generate_reports
from src.services import PatientManager
from src.storage import PatientRepository
from src.symptom_interview import SymptomCase, SymptomInterview
from src.validation import (
    parse_date,
    positive_number,
    require_text,
    validate_aadhaar,
    validate_age,
    validate_discharge,
    validate_gender,
    validate_mobile,
    validate_patient_id,
    validate_payment,
)

ROOT = Path(__file__).resolve().parent
DATA_FILE = ROOT / "data" / "patients.json"
REPORTS_DIR = ROOT / "reports"
CASE_FILE = ROOT / "data" / "symptom_cases.json"


def seed_sample_data(repository: PatientRepository) -> None:
    """Create fictional records on first run so the project is immediately testable."""
    if repository.load():
        return

    samples = [
        InPatient(
            info=PatientInfo("Aarav Sharma", "Cardiology", 45, "Male", "Nagpur", "9876543210"),
            identification=PatientID(101, "123456789012", 501),
            history=MedicalHistory("Hypertension", "None", "Penicillin", "No", "No", "Hypertension"),
            treatment=TreatmentDetails("Aspirin", "ECG", "Observation"),
            visit=VisitInfo("15-09-2026", "Chest discomfort", "Hypertension", "Dr. Mehta", "Dr. Patil"),
            vitals=VitalSigns(37.1, 72, 171, 78, "128/82", 16),
            billing=BillingDetails(8500, "upi", "Pending", "Admitted"),
            patient_type="InPatient",
            created_at=datetime.now().isoformat(timespec="seconds"),
        ),
        OutPatient(
            info=PatientInfo("Isha Verma", "General Medicine", 29, "Female", "Amravati", "9123456780"),
            identification=PatientID(102, "987654321098", 502),
            history=MedicalHistory("None", "None", "None", "No", "No", "None"),
            treatment=TreatmentDetails("Paracetamol", "CBC", "None"),
            visit=VisitInfo("18-09-2026", "Fever", "Viral infection", "Dr. Kulkarni", "Dr. Joshi"),
            vitals=VitalSigns(38.0, 58, 160, 84, "118/76", 18),
            billing=BillingDetails(1200, "cash", "Not Required", "Discharged"),
            patient_type="OutPatient",
            created_at=datetime.now().isoformat(timespec="seconds"),
        ),
    ]
    repository.save_all(samples)


def ask(prompt: str, validator=None, default=None):
    """Read input repeatedly until the validator accepts it."""
    while True:
        raw = input(prompt).strip()
        if not raw and default is not None:
            return default
        try:
            return validator(raw) if validator else raw
        except (ValueError, TypeError) as error:
            print(f"Invalid input: {error}")
            continue
        else:
            break


def ask_int(prompt: str, validator=None, default=None) -> int:
    def convert(value: str) -> int:
        return int(value)
    return ask(prompt, lambda value: validator(convert(value)) if validator else convert(value), default)


def ask_float(prompt: str, validator=None, default=None) -> float:
    def convert(value: str) -> float:
        return float(value)
    return ask(prompt, lambda value: validator(convert(value)) if validator else convert(value), default)


def collect_patient() -> Patient:
    print("\n========== ADD PATIENT ==========")
    patient_id = ask_int("Patient ID: ", validate_patient_id)
    name = ask("Name: ", lambda v: require_text(v, "Name"))
    department = ask("Department: ", lambda v: require_text(v, "Department"))
    age = ask_int("Age: ", validate_age)
    gender = ask("Gender (Male/Female/Other): ", validate_gender)
    address = ask("Address: ", lambda v: require_text(v, "Address"))
    contact = ask("Mobile (10 digits): ", validate_mobile)

    aadhaar = ask("Aadhaar (12 digits): ", validate_aadhaar)
    insurance_id = ask_int("Insurance ID: ", lambda v: v if v > 0 else (_ for _ in ()).throw(ValueError("Insurance ID must be positive.")))

    print("\n--- Medical History ---")
    past_illness = ask("Past illness: ", lambda v: require_text(v, "Past illness"))
    surgeries = ask("Surgeries: ", lambda v: require_text(v, "Surgeries"))
    allergies = ask("Allergies: ", lambda v: require_text(v, "Allergies"))
    diabetes = ask("Diabetes (Yes/No): ", lambda v: require_text(v, "Diabetes"))
    asthma = ask("Asthma (Yes/No): ", lambda v: require_text(v, "Asthma"))
    chronic = ask("Other chronic diseases: ", lambda v: require_text(v, "Chronic diseases"))

    print("\n--- Treatment ---")
    medicines = ask("Medicines: ", lambda v: require_text(v, "Medicines"))
    tests = ask("Tests: ", lambda v: require_text(v, "Tests"))
    procedures = ask("Procedures: ", lambda v: require_text(v, "Procedures"))

    print("\n--- Vital Signs ---")
    temperature = ask_float("Temperature (°C): ", lambda v: positive_number(v, "Temperature"))
    weight = ask_float("Weight (kg): ", lambda v: positive_number(v, "Weight"))
    height = ask_float("Height (cm): ", lambda v: positive_number(v, "Height"))
    pulse = ask_int("Pulse (/min): ", lambda v: v if v > 0 else (_ for _ in ()).throw(ValueError("Pulse must be positive.")))
    blood_pressure = ask("Blood pressure (e.g. 120/80): ", lambda v: require_text(v, "Blood pressure"))
    respiratory_rate = ask_int("Respiratory rate (/min): ", lambda v: v if v > 0 else (_ for _ in ()).throw(ValueError("Respiratory rate must be positive.")))

    print("\n--- Visit ---")
    visit_date = ask("Visit/admission date (DD-MM-YYYY): ", parse_date)
    symptoms = ask("Symptoms: ", lambda v: require_text(v, "Symptoms"))
    diagnosis = ask("Diagnosis: ", lambda v: require_text(v, "Diagnosis"))
    attending = ask("Attending doctor: ", lambda v: require_text(v, "Attending doctor"))
    resident = ask("Resident doctor: ", lambda v: require_text(v, "Resident doctor"))

    print("\n--- Billing ---")
    charges = ask_float("Treatment charges: ", lambda v: 0 if v >= 0 else (_ for _ in ()).throw(ValueError("Charges cannot be negative.")))
    payment = ask("Payment method (cash/card/upi): ", validate_payment)
    claim = ask("Insurance claim: ", lambda v: require_text(v, "Insurance claim"))
    discharge = ask("Discharge status (Admitted/Discharged): ", validate_discharge)
    patient_type = ask("Patient type (InPatient/OutPatient/General): ", lambda v: require_text(v, "Patient type")).title()
    if patient_type not in {"Inpatient", "Outpatient", "General"}:
        print("Unknown patient type; using General.")
        patient_type = "General"
    elif patient_type == "Inpatient":
        patient_type = "InPatient"
    elif patient_type == "Outpatient":
        patient_type = "OutPatient"

    common = dict(
        info=PatientInfo(name, department, age, gender, address, contact),
        identification=PatientID(patient_id, aadhaar, insurance_id),
        history=MedicalHistory(past_illness, surgeries, allergies, diabetes, asthma, chronic),
        treatment=TreatmentDetails(medicines, tests, procedures),
        visit=VisitInfo(visit_date, symptoms, diagnosis, attending, resident),
        vitals=VitalSigns(temperature, weight, height, pulse, blood_pressure, respiratory_rate),
        billing=BillingDetails(charges, payment, claim, discharge),
        patient_type=patient_type,
        created_at=datetime.now().isoformat(timespec="seconds"),
    )

    if patient_type == "InPatient":
        return InPatient(**common)
    if patient_type == "OutPatient":
        return OutPatient(**common)
    return Patient(**common)


def print_patients(patients: list[Patient]) -> None:
    if not patients:
        print("No patient records found.")
        return
    for patient in patients:
        print(*patient.display_lines(), sep="\n")


def show_summary(manager: PatientManager) -> None:
    patients = manager.patients
    if not patients:
        print("No patient records available.")
        return
    ages = [p.info.age for p in patients]
    total_charges = sum(p.billing.charges for p in patients)
    departments = manager.departments()
    print("\n--- SYSTEM SUMMARY ---")
    print(f"Total patients       : {len(patients)}")
    print(f"Average age          : {sum(ages) / len(ages):.2f}")
    print(f"Total billed amount  : ₹{total_charges:.2f}")
    print(f"Departments          : {', '.join(sorted(departments))}")
    print(f"Unique diagnoses     : {len(manager.diagnoses())}")



def load_symptom_cases() -> list[SymptomCase]:
    """Load symptom cases from JSON without requiring the old patient form."""
    import json
    if not CASE_FILE.exists():
        return []
    try:
        data = json.loads(CASE_FILE.read_text(encoding="utf-8"))
        return [SymptomCase.from_dict(item) for item in data]
    except (json.JSONDecodeError, TypeError, KeyError):
        return []


def save_symptom_cases(cases: list[SymptomCase]) -> None:
    import json
    CASE_FILE.parent.mkdir(parents=True, exist_ok=True)
    CASE_FILE.write_text(
        json.dumps([case.to_dict() for case in cases], indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def next_case_id(cases: list[SymptomCase]) -> int:
    return max((case.case_id for case in cases), default=1000) + 1


def run_symptom_case() -> None:
    cases = load_symptom_cases()
    case_id = next_case_id(cases)
    interview = SymptomInterview()
    case = interview.interview(case_id)
    cases.append(case)
    save_symptom_cases(cases)
    print("\nSymptom case saved successfully.")
    print(*case.display_lines(), sep="\n")


def search_symptom_case() -> None:
    cases = load_symptom_cases()
    if not cases:
        print("No symptom cases found.")
        return
    try:
        case_id = int(input("Enter Case ID: ").strip())
    except ValueError:
        print("Invalid Case ID.")
        return
    for case in cases:
        if case.case_id == case_id:
            print(*case.display_lines(), sep="\n")
            return
    print("Case not found.")


def list_symptom_cases() -> None:
    cases = load_symptom_cases()
    if not cases:
        print("No symptom cases found.")
        return
    for case in cases:
        print(f"Case {case.case_id}: {case.main_symptom} [{case.symptom_category}] - {case.created_at}")


def symptom_case_menu() -> None:
    """Menu for the new symptom-driven case-taking workflow."""
    while True:
        print("""
================ SYMPTOM CASE TAKING =================
1. Start New Symptom Interview
2. Search Symptom Case
3. List Symptom Cases
4. Back to Main Menu
=======================================================""")
        choice = input("Enter choice number: ").strip()
        if choice == "1":
            run_symptom_case()
        elif choice == "2":
            search_symptom_case()
        elif choice == "3":
            list_symptom_cases()
        elif choice == "4":
            break
        else:
            print("Invalid choice. Please enter 1, 2, 3 or 4.")


def menu() -> None:
    repository = PatientRepository(DATA_FILE)
    seed_sample_data(repository)
    manager = PatientManager(repository)

    while True:
        print("""
================ PATIENT MANAGEMENT SYSTEM ================
1. Symptom-Driven Case Taking
2. Add Full Patient Record (legacy form)
3. Search by Patient ID
4. Search by Name
5. List All Patients
6. Update Patient Diagnosis
7. Delete Patient
8. System Summary
9. Export CSV
10. Generate Pandas/Matplotlib Reports
11. Exit
============================================================""")
        choice = input("Enter choice number: ").strip()

        if choice == "1":
            symptom_case_menu()
        elif choice == "2":
            try:
                patient = collect_patient()
                manager.add_patient(patient)
                print("Patient added successfully.")
            except ValueError as error:
                print(f"Could not add patient: {error}")
        elif choice == "3":
            patient_id = ask_int("Enter Patient ID: ", validate_patient_id)
            patient = manager.find_by_id(patient_id)
            if patient is None:
                print("Patient not found.")
            else:
                print_patients([patient])
        elif choice == "4":
            name = ask("Enter name: ", lambda v: require_text(v, "Name"))
            matches = manager.find_by_name(name)
            print_patients(matches)
        elif choice == "5":
            print_patients(manager.patients)
        elif choice == "6":
            patient_id = ask_int("Enter Patient ID: ", validate_patient_id)
            new_diagnosis = ask("New diagnosis: ", lambda v: require_text(v, "Diagnosis"))
            try:
                manager.update_patient(patient_id, lambda p: setattr(p.visit, "diagnosis", new_diagnosis))
                print("Diagnosis updated successfully.")
            except LookupError as error:
                print(error)
        elif choice == "7":
            patient_id = ask_int("Enter Patient ID: ", validate_patient_id)
            try:
                removed = manager.delete_patient(patient_id)
                print(f"Deleted patient: {removed.info.name}")
            except LookupError as error:
                print(error)
        elif choice == "8":
            show_summary(manager)
        elif choice == "9":
            output = REPORTS_DIR / "patients.csv"
            repository.export_csv(manager.patients, output)
            print(f"CSV exported to: {output}")
        elif choice == "10":
            try:
                generated = generate_reports(manager.patients, REPORTS_DIR)
                print("Generated reports:")
                for path in generated:
                    print(f"- {path}")
            except ImportError:
                print("Install dependencies first with: pip install -r requirements.txt")
        elif choice == "11":
            print("Exiting the Patient Management System.")
            break
        else:
            print("Invalid choice. Please enter a number from 1 to 11.")

        print("\nReturning to the main menu...")


if __name__ == "__main__":
    menu()
