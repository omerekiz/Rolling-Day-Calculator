"""
Configuration and data loading/saving for residence tracker
"""

import json
import os
from pathlib import Path
from typing import Dict, List
import datetime

DATA_FILE = "travel_data.json"


class DataManager:
    """Manage loading and saving of travel data"""

    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)

    def get_available_people(self) -> List[str]:
        """Get list of people with data folders"""
        people = []
        for folder in self.data_dir.iterdir():
            if folder.is_dir() and not folder.name.startswith('.'):
                if (folder / DATA_FILE).exists():
                    people.append(folder.name)
        return sorted(people)

    def _get_file(self, person_id: str) -> Path:
        return self.data_dir / person_id / DATA_FILE

    def load_person_data(self, person_id: str) -> Dict:
        """Load all data for a person (travel history + planned trips)"""
        data_file = self._get_file(person_id)

        if not data_file.exists():
            raise FileNotFoundError(f"No travel data found for {person_id}")

        with open(data_file, 'r') as f:
            data = json.load(f)

        return {
            'person_name': data.get('person_name', person_id.title()),
            'buffer_days': data.get('buffer_days', 12),
            'travel_history': data.get('travel_history', []),
            'planned_trips': data.get('planned_trips', [])
        }

    def save_person_data(self, person_id: str, data: Dict) -> None:
        """Save all data for a person (travel history + planned trips)"""
        person_dir = self.data_dir / person_id
        person_dir.mkdir(exist_ok=True)

        save_data = {
            'person_name': data.get('person_name', person_id.title()),
            'buffer_days': data.get('buffer_days', 12),
            'travel_history': data.get('travel_history', []),
            'planned_trips': data.get('planned_trips', [])
        }

        with open(self._get_file(person_id), 'w') as f:
            json.dump(save_data, f, indent=2)

    def create_new_person(self, person_id: str, person_name: str) -> None:
        """Create new person data folder and files"""
        data = {
            'person_name': person_name,
            'buffer_days': 12,
            'travel_history': [],
            'planned_trips': []
        }
        self.save_person_data(person_id, data)
