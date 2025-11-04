from abc import ABC, abstractmethod
from typing import List, Dict, Any, Tuple

class BaseExtractor(ABC):

    @abstractmethod
    def extract(self, text: str) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def validate(self, match: str) -> bool:
        pass

    def clean_text(self, text: str) -> str:
        if not text:
            return text
        return text.strip()

    def remove_trailing_special_chars(self, text: str) -> str:
        if text and text[-1] in '.,;:!?-+=*"\'()[]{}':
            return text[:-1]
        return text

