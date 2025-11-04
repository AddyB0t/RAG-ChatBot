import re
from typing import List, Dict, Any
from .base_extractor import BaseExtractor

class ContactExtractor(BaseExtractor):

    EMAIL_PATTERN = re.compile(
        r"\b((([!#$%&'*+\-/=?^_`{|}~\w])|([!#$%&'*+\-/=?^_`{|}~\w][!#$%&'*+\-/=?^_`{|}~\.\w]{0,}[!#$%&'*+\-/=?^_`{|}~\w]))[@]\w+([-.]\w+)*\.\w+([-.]\w+)*)\b"
    )

    PHONE_PATTERN = re.compile(
        r'''
        (?<![.\d])
        (?:
            (?:
                (?:\+91[-\s]?)?
                (?:
                    [6-9]\d{9}
                    |
                    [6-9]\d{2}[-\s]\d{3}[-\s]\d{4}
                    |
                    [6-9]\d{4}[-\s]\d{5}
                )
            )
            |
            (?:
                (?:\+1|1)?
                (?:[-\s])?
                (?:
                    \d{3}[-\s]\d{3}[-\s]\d{4}
                    |
                    \(\d{3}\)[-\s]?\d{3}[-\s]\d{4}
                )
            )
        )
        (?![.\d])
        ''',
        re.VERBOSE
    )

    URL_PATTERN = re.compile(
        r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    )

    LINKEDIN_PATTERN = re.compile(
        r'(?:https?://)?(?:www\.)?linkedin\.com/in/[\w\-]+'
    )

    def extract(self, text: str) -> Dict[str, Any]:
        contact_info = {
            "email": None,
            "phone": [],
            "linkedin": None,
            "urls": []
        }

        email_matches = self.EMAIL_PATTERN.findall(text)
        if email_matches:
            contact_info["email"] = email_matches[0][0]

        phone_matches = self.PHONE_PATTERN.findall(text)
        contact_info["phone"] = [self.clean_phone(p) for p in phone_matches if self.validate_phone(p)]

        linkedin_matches = self.LINKEDIN_PATTERN.findall(text)
        if linkedin_matches:
            contact_info["linkedin"] = linkedin_matches[0]

        url_matches = self.URL_PATTERN.findall(text)
        contact_info["urls"] = [url for url in url_matches if 'linkedin' not in url.lower()]

        return contact_info

    def validate(self, match: str) -> bool:
        return bool(match and len(match) > 0)

    def validate_phone(self, phone: str) -> bool:
        digits = re.sub(r'\D', '', phone)
        return 10 <= len(digits) <= 15

    def clean_phone(self, phone: str) -> str:
        return phone.strip()

