import json
import re
from typing import List, Dict, Any
from .base_extractor import BaseExtractor
from app.utils.openrouter_client import OpenRouterClient
import logging

logger = logging.getLogger(__name__)

class CertificationsExtractor(BaseExtractor):

    COMMON_CERTS = [
        "AWS", "Azure", "GCP", "PMP", "CISSP", "CEH", "CISM", "CISA", "CFA", "CPA",
        "Scrum Master", "Product Owner", "Six Sigma", "ITIL", "CompTIA", "Cisco"
    ]

    DATE_PATTERN = re.compile(
        r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}\b|\b\d{4}\b'
    )

    def __init__(self):
        self.llm = OpenRouterClient()

    def extract(self, text: str) -> List[Dict[str, Any]]:
        try:
            prompt = f"""Extract all certifications from the resume text below. Return a JSON array.

For each certification, extract:
- name (certification name)
- issuer (issuing organization)
- issue_date (format: YYYY-MM-DD or YYYY-MM or YYYY)
- expiry_date (format: YYYY-MM-DD or YYYY-MM or YYYY, or null if no expiry)
- credential_id (certificate/credential ID if mentioned)

Resume text:
{text}

Return ONLY valid JSON array, no additional text. If no certifications found, return empty array []."""

            result = self.llm.invoke(prompt, temperature=0.2).strip()

            result = re.sub(r'^```json\s*', '', result)
            result = re.sub(r'\s*```$', '', result)

            certifications = json.loads(result)

            if not isinstance(certifications, list):
                certifications = [certifications] if certifications else []

            return certifications

        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error in certifications extraction: {e}")
            return self._fallback_extract(text)
        except Exception as e:
            logger.error(f"Error extracting certifications: {e}")
            return self._fallback_extract(text)

    def _fallback_extract(self, text: str) -> List[Dict[str, Any]]:
        certifications = []
        text_lower = text.lower()

        for cert in self.COMMON_CERTS:
            if cert.lower() in text_lower:
                certifications.append({
                    "name": cert,
                    "issuer": None,
                    "issue_date": None,
                    "expiry_date": None,
                    "credential_id": None
                })

        return certifications

    def validate(self, match: str) -> bool:
        return bool(match and len(match) > 0)

