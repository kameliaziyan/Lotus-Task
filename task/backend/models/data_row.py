# Data model representing a single row of input features and its burnout outcome.

from dataclasses import dataclass

@dataclass
class DataRow:
    sleep: float
    meetings: int
    weekends: str
    stress: float
    outcome: str

    # class-level sets so they're shared constants, not per-instance fields
    valid_outcomes = {"Healthy", "Risk of burnout", "Vacation required", "Critical condition"}
    valid_weekends = {"Yes", "No"}
    