import json
from typing import List, Optional
from models import Participant, Couple


def load_participants_from_json(json_path: str) -> tuple[List[Participant], Optional[List[Couple]]]:
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    participants_data = data.get('participants', [])
    if not participants_data:
        raise ValueError("JSON file must contain a 'participants' array")
    
    participants = [
        Participant(name=p['name'], phone_number=p['phone_number'])
        for p in participants_data
    ]
    
    couples_data = data.get('couples', [])
    couples = None
    if couples_data:
        participants_by_name = {p.name: p for p in participants}
        couples = []
        for couple_data in couples_data:
            name1 = couple_data.get('person1')
            name2 = couple_data.get('person2')
            
            if name1 not in participants_by_name:
                raise ValueError(f"Couple member '{name1}' not found in participants")
            if name2 not in participants_by_name:
                raise ValueError(f"Couple member '{name2}' not found in participants")
            
            couples.append(Couple(
                person1=participants_by_name[name1],
                person2=participants_by_name[name2]
            ))
    
    return participants, couples

