from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Participant:
    name: str
    phone_number: Optional[str] = None
    email: Optional[str] = None

    def __hash__(self):
        return hash((self.name, self.phone_number, self.email))

    def __eq__(self, other):
        if not isinstance(other, Participant):
            return False
        return self.name == other.name and self.phone_number == other.phone_number and self.email == other.email


@dataclass
class Couple:
    person1: Participant
    person2: Participant

    def contains(self, participant: Participant) -> bool:
        return participant == self.person1 or participant == self.person2

    def get_partner(self, participant: Participant) -> Optional[Participant]:
        if participant == self.person1:
            return self.person2
        elif participant == self.person2:
            return self.person1
        return None


@dataclass
class DrawResult:
    giver: Participant
    receiver: Participant

