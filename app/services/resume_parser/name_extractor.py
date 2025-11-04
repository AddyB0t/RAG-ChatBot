from typing import List, Dict, Any, Optional
from .base_extractor import BaseExtractor
from .models.flair_loader import get_flair_model
import logging

logger = logging.getLogger(__name__)

class NameExtractor(BaseExtractor):

    def __init__(self):
        self.tagger = None
        self.flair_available = False

    def _ensure_model_loaded(self):
        if self.tagger is None:
            self.tagger = get_flair_model()
            self.flair_available = self.tagger is not None

    def extract(self, text: str) -> Dict[str, Any]:
        self._ensure_model_loaded()

        if not self.flair_available:
            logger.warning("Flair not available, returning empty name data")
            return {"full_name": None, "first_name": None, "last_name": None}

        try:
            from flair.data import Sentence

            lines = text.split('\n')[:10]
            top_text = ' '.join(lines)

            sentence = Sentence(top_text)
            self.tagger.predict(sentence)

            names = []
            for entity in sentence.get_spans('ner'):
                if entity.tag == 'PER':
                    names.append(entity.text)

            if names:
                full_name = names[0]
                name_parts = full_name.split()

                first_name = name_parts[0] if len(name_parts) > 0 else None
                last_name = name_parts[-1] if len(name_parts) > 1 else None

                return {
                    "full_name": full_name,
                    "first_name": first_name,
                    "last_name": last_name
                }

            return {"full_name": None, "first_name": None, "last_name": None}

        except Exception as e:
            logger.error(f"Error extracting name: {e}")
            return {"full_name": None, "first_name": None, "last_name": None}

    def validate(self, match: str) -> bool:
        if not match:
            return False
        return len(match.split()) >= 1 and len(match) <= 100

