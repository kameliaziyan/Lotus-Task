# Loads the training dataset from the JSON file and returns it as a list of DataRow objects.

import json
import os
from typing import List
from backend.models.data_row import DataRow

_DATASET_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "dataset.json")
_DATASET_PATH = os.path.normpath(_DATASET_PATH)


def load_dataset() -> List[DataRow]:
    with open(_DATASET_PATH) as data_file:
        raw = json.load(data_file)
    rows: List[DataRow] = []
    for item in raw:
        row = DataRow(
            sleep=float(item["sleep"]),
            meetings=int(item["meetings"]),
            weekends=str(item["weekends"]),
            stress=float(item["stress"]),
            outcome=str(item["outcome"]),

        )
        rows.append(row)
    return rows