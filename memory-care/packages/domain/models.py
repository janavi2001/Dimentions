from dataclasses import dataclass
from typing import List, Dict, Optional
@dataclass
class Person:
    person_id: str
    full_name: str
    relationship_note: str = ''
    caregiver_contacts: Optional[List[Dict[str,str]]] = None
