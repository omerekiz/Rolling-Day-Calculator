"""
Configuration and data loading/saving for residence tracker
"""

import json
import os
from pathlib import Path
from typing import Dict, List
import datetime


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
                # Check if travel_history.json exists in this folder
                if (folder / "travel_history.json").exists():
                    people.append(folder.name)
        return sorted(people)

    def load_person_data(self, person_id: str) -> Dict:
        """
        Load all data for a person

        Args:
            person_id: Person identifier (e.g., 'omer')

        Returns:
            Dict with person_name, buffer_days, travel_history
        """
        person_dir = self.data_dir / person_id
        history_file = person_dir / "travel_history.json"

        if not history_file.exists():
            raise FileNotFoundError(f"No travel history found for {person_id}")

        # Load travel history
        with open(history_file, 'r') as f:
            history_data = json.load(f)

        return {
            'person_name': history_data.get('person_name', person_id.title()),
            'buffer_days': history_data.get('buffer_days', 12),
            'travel_history': history_data.get('travel_history', [])
        }

    def save_person_data(self, person_id: str, data: Dict) -> None:
        """
        Save all data for a person

        Args:
            person_id: Person identifier (e.g., 'omer')
            data: Dict with person_name, buffer_days, travel_history
        """
        person_dir = self.data_dir / person_id
        person_dir.mkdir(exist_ok=True)

        history_file = person_dir / "travel_history.json"

        # Save travel history and settings
        history_data = {
            'person_name': data.get('person_name', person_id.title()),
            'buffer_days': data.get('buffer_days', 12),
            'travel_history': data.get('travel_history', [])
        }

        with open(history_file, 'w') as f:
            json.dump(history_data, f, indent=2)

    def create_new_person(self, person_id: str, person_name: str) -> None:
        """
        Create new person data folder and files

        Args:
            person_id: Person identifier (e.g., 'john')
            person_name: Display name (e.g., 'John')
        """
        data = {
            'person_name': person_name,
            'buffer_days': 12,
            'travel_history': []
        }
        self.save_person_data(person_id, data)
