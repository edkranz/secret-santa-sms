import random
from typing import List, Optional
from models import Participant, Couple, DrawResult


class DrawService:
    def __init__(self, participants: List[Participant], couples: Optional[List[Couple]] = None):
        self.participants = participants
        self.couples = couples or []
        self._validate_inputs()

    def _validate_inputs(self):
        if len(self.participants) < 2:
            raise ValueError("Need at least 2 participants for Secret Santa")
        
        all_participants = set(self.participants)
        for couple in self.couples:
            if couple.person1 not in all_participants:
                raise ValueError(f"Couple member {couple.person1.name} not in participants list")
            if couple.person2 not in all_participants:
                raise ValueError(f"Couple member {couple.person2.name} not in participants list")

    def _is_valid_draw(self, giver: Participant, receiver: Participant) -> bool:
        if giver == receiver:
            return False
        
        for couple in self.couples:
            if couple.contains(giver) and couple.contains(receiver):
                return False
        
        return True

    def _find_valid_receiver(self, giver: Participant, available_receivers: List[Participant]) -> Optional[Participant]:
        valid_receivers = [r for r in available_receivers if self._is_valid_draw(giver, r)]
        if not valid_receivers:
            return None
        return random.choice(valid_receivers)

    def draw(self) -> List[DrawResult]:
        if len(self.participants) == 2 and len(self.couples) > 0:
            couple = self.couples[0]
            if couple.contains(self.participants[0]) and couple.contains(self.participants[1]):
                raise ValueError("Cannot draw with only 2 participants who are a couple")
        
        givers = self.participants.copy()
        receivers = self.participants.copy()
        random.shuffle(givers)
        
        results = []
        available_receivers = receivers.copy()
        
        for giver in givers:
            receiver = self._find_valid_receiver(giver, available_receivers)
            
            if receiver is None:
                return self._retry_draw()
            
            results.append(DrawResult(giver=giver, receiver=receiver))
            available_receivers.remove(receiver)
        
        return results

    def _retry_draw(self, max_attempts: int = 1000) -> List[DrawResult]:
        for _ in range(max_attempts):
            try:
                givers = self.participants.copy()
                receivers = self.participants.copy()
                random.shuffle(givers)
                random.shuffle(receivers)
                
                results = []
                available_receivers = receivers.copy()
                
                for giver in givers:
                    receiver = self._find_valid_receiver(giver, available_receivers)
                    
                    if receiver is None:
                        break
                    
                    results.append(DrawResult(giver=giver, receiver=receiver))
                    available_receivers.remove(receiver)
                
                if len(results) == len(self.participants):
                    return results
            except Exception:
                continue
        
        raise RuntimeError("Could not generate valid Secret Santa draw after multiple attempts")

