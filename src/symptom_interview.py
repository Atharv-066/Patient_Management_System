"""Symptom-driven case-taking interview for the Programming Methodology project.

This module collects symptom history only. It does not diagnose or recommend treatment.
"""

from __future__ import annotations

from datetime import datetime
from dataclasses import dataclass, asdict
from typing import Any


@dataclass
class SymptomCase:
    case_id: int
    created_at: str
    main_symptom: str
    symptom_category: str
    answers: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SymptomCase":
        return cls(
            case_id=int(data["case_id"]),
            created_at=data["created_at"],
            main_symptom=data["main_symptom"],
            symptom_category=data["symptom_category"],
            answers=data.get("answers", {}),
        )

    def display_lines(self) -> list[str]:
        lines = [
            "\n========== SYMPTOM CASE ==========",
            f"Case ID            : {self.case_id}",
            f"Recorded           : {self.created_at}",
            f"Main symptom       : {self.main_symptom}",
            f"Symptom category   : {self.symptom_category}",
            "\n--- Case History ---",
        ]
        for question, answer in self.answers.items():
            lines.append(f"{question}: {answer}")
        lines.append("==================================")
        return lines


class SymptomInterview:
    """Runs a branching interview based on the patient's main symptom."""

    CATEGORIES = {
        "fever": "Fever / temperature",
        "headache": "Headache",
        "cough": "Cough / breathing",
        "chest pain": "Chest discomfort",
        "chest discomfort": "Chest discomfort",
        "stomach pain": "Abdominal pain",
        "abdominal pain": "Abdominal pain",
        "vomiting": "Vomiting / nausea",
        "nausea": "Vomiting / nausea",
        "diarrhea": "Diarrhea",
        "sore throat": "Sore throat",
        "throat pain": "Sore throat",
        "dizziness": "Dizziness",
        "back pain": "Back pain",
        "joint pain": "Joint pain",
        "rash": "Skin rash",
        "injury": "Injury / pain",
    }

    def __init__(self, input_fn=input, output_fn=print):
        self.input = input_fn
        self.output = output_fn

    def ask(self, question: str, allow_blank: bool = False) -> str:
        while True:
            value = self.input(f"{question}: ").strip()
            if value or allow_blank:
                return value
            self.output("Please enter an answer.")

    def ask_yes_no(self, question: str) -> str:
        while True:
            answer = self.ask(f"{question} (yes/no)").casefold()
            if answer in {"yes", "no"}:
                return answer
            self.output("Please answer yes or no.")

    def ask_scale(self, question: str) -> int:
        while True:
            try:
                value = int(self.ask(f"{question} (0-10)"))
                if 0 <= value <= 10:
                    return value
            except ValueError:
                pass
            self.output("Enter a whole number from 0 to 10.")

    def classify_symptom(self, text: str) -> str:
        """Classify common natural-language symptom descriptions using keywords."""
        keyword_groups = {
            "Fever / temperature": ("fever", "temperature", "hot"),
            "Headache": ("headache", "head pain", "migraine"),
            "Cough / breathing": ("cough", "breathless", "breathing", "wheez"),
            "Chest discomfort": ("chest pain", "chest discomfort", "chest tight", "chest pressure"),
            "Abdominal pain": ("stomach pain", "abdominal pain", "belly pain", "tummy pain"),
            "Vomiting / nausea": ("vomit", "vomiting", "nausea", "nauseous"),
            "Diarrhea": ("diarrhea", "loose motion", "loose stool"),
            "Sore throat": ("sore throat", "throat pain", "throat hurts"),
            "Dizziness": ("dizzy", "dizziness", "spinning", "vertigo"),
            "Back pain": ("back pain", "backache"),
            "Joint pain": ("joint pain", "knee pain", "shoulder pain", "ankle pain"),
            "Skin rash": ("rash", "hives", "skin irritation"),
            "Injury / pain": ("injury", "hurt", "pain", "swelling"),
        }
        for category_name, keywords in keyword_groups.items():
            if any(keyword in text for keyword in keywords):
                return category_name
        return "Other symptom"


    def common_questions(self) -> dict[str, Any]:
        answers: dict[str, Any] = {}
        answers["When did it start?"] = self.ask("When did the symptom start?")
        answers["Severity (0-10)"] = self.ask_scale("How severe is it")
        answers["Pattern"] = self.ask("Is it constant, or does it come and go?")
        answers["What makes it worse?"] = self.ask("What makes the symptom worse?", allow_blank=True)
        answers["What makes it better?"] = self.ask("What makes the symptom better?", allow_blank=True)
        answers["Previous episode"] = self.ask_yes_no("Have you had this symptom before?")
        return answers

    def interview(self, case_id: int) -> SymptomCase:
        self.output("\n========== SYMPTOM CASE TAKING ==========")
        self.output("Describe the main symptom. The program will ask related follow-up questions.")
        main_symptom = self.ask("What is the main symptom you are experiencing?")
        normalized = main_symptom.casefold()
        category = self.CATEGORIES.get(normalized, "Other symptom")
        if category == "Other symptom":
            category = self.classify_symptom(normalized)

        answers = self.common_questions()

        if category == "Fever / temperature":
            self._fever(answers)
        elif category == "Headache":
            self._headache(answers)
        elif category == "Cough / breathing":
            self._cough(answers)
        elif category == "Chest discomfort":
            self._chest(answers)
        elif category == "Abdominal pain":
            self._abdomen(answers)
        elif category == "Vomiting / nausea":
            self._vomiting(answers)
        elif category == "Diarrhea":
            self._diarrhea(answers)
        elif category == "Sore throat":
            self._throat(answers)
        elif category == "Dizziness":
            self._dizziness(answers)
        elif category == "Back pain":
            self._pain_location(answers, "back")
        elif category == "Joint pain":
            self._joint(answers)
        elif category == "Skin rash":
            self._rash(answers)
        elif category == "Injury / pain":
            self._injury(answers)
        else:
            self._other(answers)

        answers["Urgent warning symptoms"] = self._urgent_screen()

        return SymptomCase(
            case_id=case_id,
            created_at=datetime.now().isoformat(timespec="seconds"),
            main_symptom=main_symptom,
            symptom_category=category,
            answers=answers,
        )

    def _fever(self, a: dict[str, Any]) -> None:
        a["Measured temperature"] = self.ask("Have you measured your temperature? If yes, what was it?")
        a["Chills"] = self.ask_yes_no("Are you having chills or shivering?")
        a["Sweating"] = self.ask_yes_no("Are you sweating more than usual?")
        a["Body aches"] = self.ask_yes_no("Do you have body aches or unusual tiredness?")
        a["Other symptoms"] = self.ask("Any other symptoms such as cough, sore throat, vomiting, or diarrhea?", allow_blank=True)

    def _headache(self, a: dict[str, Any]) -> None:
        a["Location"] = self.ask("Where is the headache located?")
        a["Quality"] = self.ask("How does it feel (pressure, throbbing, sharp, or another description)?")
        a["Nausea"] = self.ask_yes_no("Do you feel nauseated or have you vomited?")
        a["Light sensitivity"] = self.ask_yes_no("Does bright light make it worse?")
        a["Vision changes"] = self.ask_yes_no("Have you noticed any change in your vision?")

    def _cough(self, a: dict[str, Any]) -> None:
        a["Cough type"] = self.ask("Is the cough dry or producing mucus?")
        a["Duration"] = self.ask("How long have you had the cough?")
        a["Breathlessness"] = self.ask_yes_no("Are you having difficulty breathing?")
        a["Wheezing"] = self.ask_yes_no("Are you wheezing or making a whistling sound while breathing?")
        a["Sore throat"] = self.ask_yes_no("Do you also have a sore throat?")
        a["Blood in mucus"] = self.ask_yes_no("Have you noticed blood in the mucus?")

    def _chest(self, a: dict[str, Any]) -> None:
        a["Location"] = self.ask("Where in the chest is the discomfort?")
        a["Quality"] = self.ask("How would you describe the discomfort (pressure, tightness, burning, sharp, etc.)?")
        a["Breathlessness"] = self.ask_yes_no("Are you having difficulty breathing?")
        a["Movement effect"] = self.ask_yes_no("Does movement or physical activity change it?")
        a["Dizziness or fainting"] = self.ask_yes_no("Have you felt faint or unusually dizzy with it?")
        a["Spread"] = self.ask("Does the discomfort spread anywhere else? If yes, where?", allow_blank=True)

    def _abdomen(self, a: dict[str, Any]) -> None:
        a["Location"] = self.ask("Where in the abdomen is the pain?")
        a["Pain type"] = self.ask("How would you describe the pain?")
        a["Food relation"] = self.ask("Does eating make it better or worse?")
        a["Nausea or vomiting"] = self.ask_yes_no("Do you have nausea or vomiting?")
        a["Bowel change"] = self.ask_yes_no("Have you noticed a change in bowel movements?")
        a["Urinary change"] = self.ask_yes_no("Have you noticed any change or pain while urinating?")

    def _vomiting(self, a: dict[str, Any]) -> None:
        a["Frequency"] = self.ask("How many times have you vomited, approximately?")
        a["Onset"] = self.ask("When did the vomiting or nausea begin?")
        a["Food or drink retained"] = self.ask_yes_no("Are you able to keep fluids down?")
        a["Abdominal pain"] = self.ask_yes_no("Do you also have abdominal pain?")
        a["Diarrhea"] = self.ask_yes_no("Do you also have diarrhea?")

    def _diarrhea(self, a: dict[str, Any]) -> None:
        a["Frequency"] = self.ask("Approximately how many loose stools have you had today?")
        a["Onset"] = self.ask("When did it start?")
        a["Vomiting"] = self.ask_yes_no("Do you also have vomiting?")
        a["Abdominal pain"] = self.ask_yes_no("Do you also have abdominal pain?")
        a["Blood or unusual appearance"] = self.ask_yes_no("Have you noticed blood or an unusual appearance in the stool?")
        a["Fluid intake"] = self.ask("Are you able to drink fluids normally?")

    def _throat(self, a: dict[str, Any]) -> None:
        a["Swallowing"] = self.ask("Is swallowing painful or difficult?")
        a["Fever"] = self.ask_yes_no("Do you also have fever?")
        a["Cough"] = self.ask_yes_no("Do you also have a cough?")
        a["Voice change"] = self.ask_yes_no("Has your voice changed?")
        a["Neck swelling"] = self.ask_yes_no("Have you noticed swelling in the neck?")

    def _dizziness(self, a: dict[str, Any]) -> None:
        a["Sensation"] = self.ask("Does it feel like the room is spinning, or more like you may faint?")
        a["On standing"] = self.ask_yes_no("Does it happen when you stand up?")
        a["Headache"] = self.ask_yes_no("Do you also have a headache?")
        a["Vision change"] = self.ask_yes_no("Have you noticed a change in vision?")
        a["Fainting"] = self.ask_yes_no("Have you actually fainted or lost consciousness?")

    def _pain_location(self, a: dict[str, Any], area: str) -> None:
        a["Exact location"] = self.ask(f"Where exactly is the {area} pain?")
        a["Movement effect"] = self.ask_yes_no("Does movement change the pain?")
        a["Numbness or tingling"] = self.ask_yes_no("Do you have numbness or tingling?")
        a["Weakness"] = self.ask_yes_no("Do you have unusual weakness?")

    def _joint(self, a: dict[str, Any]) -> None:
        a["Joint"] = self.ask("Which joint or joints are affected?")
        a["Swelling"] = self.ask_yes_no("Is there swelling?")
        a["Redness or warmth"] = self.ask_yes_no("Is the area red or warmer than usual?")
        a["Movement"] = self.ask("Does movement affect the pain?")
        a["Injury"] = self.ask_yes_no("Did the pain begin after an injury or unusual activity?")

    def _rash(self, a: dict[str, Any]) -> None:
        a["Location"] = self.ask("Where is the rash located?")
        a["Onset"] = self.ask("When did it appear?")
        a["Itching"] = self.ask_yes_no("Is it itchy?")
        a["Pain"] = self.ask_yes_no("Is it painful?")
        a["Spread"] = self.ask_yes_no("Is it spreading to other areas?")
        a["New exposure"] = self.ask("Any new food, medicine, product, plant, or other exposure before it appeared?", allow_blank=True)

    def _injury(self, a: dict[str, Any]) -> None:
        a["How it happened"] = self.ask("How did the injury happen?")
        a["Body area"] = self.ask("Which body area was injured?")
        a["Swelling"] = self.ask_yes_no("Is there swelling?")
        a["Movement"] = self.ask_yes_no("Can you move the affected area normally?")
        a["Numbness"] = self.ask_yes_no("Is there numbness or tingling?")

    def _other(self, a: dict[str, Any]) -> None:
        a["Location"] = self.ask("Where do you feel the symptom?")
        a["Description"] = self.ask("How would you describe the symptom?")
        a["Associated symptoms"] = self.ask("What other symptoms are happening at the same time?", allow_blank=True)

    def _urgent_screen(self) -> str:
        self.output("\n--- Safety screening ---")
        breathing = self.ask_yes_no("Are you having severe difficulty breathing right now?")
        fainting = self.ask_yes_no("Have you lost consciousness or are you about to faint?")
        rapidly_worse = self.ask_yes_no("Is the symptom suddenly becoming severe or rapidly worsening?")
        if "yes" in {breathing, fainting, rapidly_worse}:
            self.output("Important: this program is only a case-taking aid. A severe or rapidly worsening symptom should be assessed promptly by a qualified medical professional.")
            return "Yes - prompt medical assessment may be needed"
        return "No obvious urgent warning reported"
