from abc import ABC, abstractmethod
from typing import List
from models import DrawResult


class NotificationService(ABC):
    @abstractmethod
    def send_notification(self, recipient: str, recipient_name: str, receiver_name: str) -> bool:
        pass

    @abstractmethod
    def send_draw_results(self, results: List[DrawResult]) -> None:
        pass

