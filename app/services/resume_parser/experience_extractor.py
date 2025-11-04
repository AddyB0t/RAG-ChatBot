import json
import re
from typing import List, Dict, Any
from .base_extractor import BaseExtractor
from app.utils.openai_client import OpenAIClient
import logging

logger = logging.getLogger(__name__)

class ExperienceExtractor(BaseExtractor):

    def __init__(self):
        self.llm = OpenAIClient()

    def extract(self, text: str) -> List[Dict[str, Any]]:
        try:
            prompt = f"""Extract all work experience from the resume text below. Return a JSON array of experiences.

For each experience, extract:
- title (job title/role)
- company (company name)
- location (city, state/country if available)
- start_date (format: YYYY-MM-DD or YYYY-MM or YYYY)
- end_date (format: YYYY-MM-DD or YYYY-MM or YYYY, or null if current)
- is_current (boolean, true if currently working)
- description (brief summary of role)
- achievements (array of key achievements with numbers/metrics)
- technologies (array of technologies/tools used)

Resume text:
{text}

Return ONLY valid JSON array, no additional text."""

            result = self.llm.invoke(prompt, temperature=0.2).strip()

            result = re.sub(r'^```json\s*', '', result)
            result = re.sub(r'\s*```$', '', result)

            experiences = json.loads(result)

            if not isinstance(experiences, list):
                experiences = [experiences]

            return experiences

        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error in experience extraction: {e}")
            return []
        except Exception as e:
            logger.error(f"Error extracting experience: {e}")
            return []

    def validate(self, match: str) -> bool:
        return bool(match and len(match) > 0)

