import json
import re
from typing import List, Dict, Any
from .base_extractor import BaseExtractor
from app.utils.openai_client import OpenAIClient
import logging

logger = logging.getLogger(__name__)

class EducationExtractor(BaseExtractor):

    DEGREE_PATTERNS = [
        r'\b(?:Bachelor|B\.?S\.?|B\.?A\.?|B\.?Tech|B\.?E\.?|BE|BTech)\b',
        r'\b(?:Master|M\.?S\.?|M\.?A\.?|M\.?Tech|M\.?E\.?|MBA|MCA)\b',
        r'\b(?:Ph\.?D\.?|Doctorate|Doctor)\b',
        r'\b(?:Associate|A\.?S\.?|A\.?A\.?)\b',
        r'\b(?:Diploma)\b'
    ]

    GPA_PATTERN = re.compile(r'(?:GPA|CGPA|Grade)[\s:]*(\d+\.?\d*)\s*(?:/\s*(\d+\.?\d*))?')

    def __init__(self):
        self.llm = OpenAIClient()

    def extract(self, text: str) -> List[Dict[str, Any]]:
        try:
            prompt = f"""Extract all education details from the resume text below. Return a JSON array.

For each education entry, extract:
- degree (degree type like Bachelor of Science, MBA, etc.)
- field (field of study like Computer Science, Business Administration)
- institution (university/college name)
- location (city, state/country if available)
- graduation_date (format: YYYY-MM-DD or YYYY-MM or YYYY)
- gpa (numeric GPA value if mentioned)
- honors (array of honors/awards like Magna Cum Laude, Dean's List)

Resume text:
{text}

Return ONLY valid JSON array, no additional text."""

            result = self.llm.invoke(prompt, temperature=0.2).strip()

            result = re.sub(r'^```json\s*', '', result)
            result = re.sub(r'\s*```$', '', result)

            education = json.loads(result)

            if not isinstance(education, list):
                education = [education]

            return education

        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error in education extraction: {e}")
            return []
        except Exception as e:
            logger.error(f"Error extracting education: {e}")
            return []

    def validate(self, match: str) -> bool:
        return bool(match and len(match) > 0)

    def extract_gpa(self, text: str) -> Dict[str, Any]:
        matches = self.GPA_PATTERN.findall(text)
        if matches:
            gpa_value = float(matches[0][0])
            max_value = float(matches[0][1]) if matches[0][1] else 4.0
            return {"gpa": gpa_value, "max": max_value}
        return {}

