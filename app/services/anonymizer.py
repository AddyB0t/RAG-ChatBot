"""
Resume Anonymization Service
Removes personally identifiable information (PII) from resumes
"""
import logging
import re
import hashlib
from typing import Dict, List, Any, Optional
from datetime import datetime
from copy import deepcopy

logger = logging.getLogger(__name__)

class ResumeAnonymizer:
    """Anonymizes resume data by removing or masking PII"""

    def __init__(self):
        """Initialize anonymizer"""
        logger.info("Resume Anonymizer initialized")

    def anonymize_resume(
        self,
        resume_data: Dict[str, Any],
        options: Optional[Dict[str, bool]] = None
    ) -> Dict[str, Any]:
        """
        Anonymize resume data by removing PII

        Args:
            resume_data: Parsed resume data
            options: Anonymization options (what to remove)
                - remove_name (default: True)
                - remove_contact (default: True)
                - remove_address (default: True)
                - remove_photos (default: True)
                - remove_age_dob (default: True)
                - remove_gender (default: True)
                - mask_education_dates (default: True)
                - mask_work_dates (default: False)
                - remove_company_names (default: False)
                - remove_school_names (default: False)

        Returns:
            Anonymized resume data
        """
        logger.info("Starting resume anonymization")

        if options is None:
            options = self._get_default_options()

        anonymized_data = deepcopy(resume_data)

        metadata = {
            'anonymized': True,
            'anonymization_date': datetime.utcnow().isoformat(),
            'original_hash': self._generate_hash(resume_data),
            'options_used': options
        }

        if options.get('remove_name', True):
            anonymized_data = self._remove_name(anonymized_data)

        if options.get('remove_contact', True):
            anonymized_data = self._remove_contact_info(anonymized_data)

        if options.get('remove_address', True):
            anonymized_data = self._remove_address(anonymized_data)

        if options.get('remove_age_dob', True):
            anonymized_data = self._remove_age_dob(anonymized_data)

        if options.get('remove_gender', True):
            anonymized_data = self._remove_gender(anonymized_data)

        if options.get('mask_education_dates', True):
            anonymized_data = self._mask_education_dates(anonymized_data)

        if options.get('mask_work_dates', False):
            anonymized_data = self._mask_work_dates(anonymized_data)

        if options.get('remove_company_names', False):
            anonymized_data = self._anonymize_company_names(anonymized_data)

        if options.get('remove_school_names', False):
            anonymized_data = self._anonymize_school_names(anonymized_data)

        anonymized_data['_anonymization_metadata'] = metadata

        logger.info("Resume anonymization completed")
        return anonymized_data

    def _get_default_options(self) -> Dict[str, bool]:
        """Get default anonymization options"""
        return {
            'remove_name': True,
            'remove_contact': True,
            'remove_address': True,
            'remove_photos': True,
            'remove_age_dob': True,
            'remove_gender': True,
            'mask_education_dates': True,
            'mask_work_dates': False,
            'remove_company_names': False,
            'remove_school_names': False
        }

    def _remove_name(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Remove name information"""
        if 'personal_info' in data:
            personal_info = data['personal_info']
            candidate_id = self._generate_candidate_id(personal_info)

            personal_info['full_name'] = f"Candidate {candidate_id}"
            personal_info['first_name'] = "Candidate"
            personal_info['last_name'] = candidate_id

            if 'title' in personal_info:
                personal_info['title'] = self._anonymize_text_names(personal_info['title'])

            if 'summary' in personal_info:
                personal_info['summary'] = self._anonymize_text_names(personal_info['summary'])

        return data

    def _remove_contact_info(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Remove contact information"""
        if 'personal_info' in data and 'contact' in data['personal_info']:
            contact = data['personal_info']['contact']

            if 'email' in contact and contact['email']:
                contact['email'] = self._anonymize_email(contact['email'])

            if 'phone' in contact:
                contact['phone'] = ['[REDACTED]' for _ in contact.get('phone', [])]

            if 'linkedin' in contact:
                contact['linkedin'] = '[REDACTED]' if contact.get('linkedin') else None

            if 'github' in contact:
                contact['github'] = '[REDACTED]' if contact.get('github') else None

            if 'website' in contact:
                contact['website'] = '[REDACTED]' if contact.get('website') else None

            if 'urls' in contact:
                contact['urls'] = ['[REDACTED]' for _ in contact.get('urls', [])]

        return data

    def _remove_address(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Remove address information"""
        if 'personal_info' in data and 'contact' in data['personal_info']:
            contact = data['personal_info']['contact']

            if 'address' in contact:
                address = contact['address']
                if isinstance(address, dict):
                    if 'city' in address:
                        contact['address'] = {'city': address.get('city'), 'country': address.get('country')}
                elif isinstance(address, str):
                    contact['address'] = self._extract_city_country(address)

        return data

    def _remove_age_dob(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Remove age and date of birth"""
        if 'personal_info' in data:
            personal_info = data['personal_info']
            if 'date_of_birth' in personal_info:
                del personal_info['date_of_birth']
            if 'age' in personal_info:
                del personal_info['age']

        return data

    def _remove_gender(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Remove gender information"""
        if 'personal_info' in data:
            personal_info = data['personal_info']
            if 'gender' in personal_info:
                del personal_info['gender']

            if 'summary' in personal_info:
                personal_info['summary'] = self._neutralize_gendered_language(
                    personal_info['summary']
                )

        if 'experience' in data:
            for exp in data['experience']:
                if 'description' in exp:
                    exp['description'] = self._neutralize_gendered_language(exp['description'])

        return data

    def _mask_education_dates(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Mask education dates to ranges"""
        if 'education' in data:
            for edu in data['education']:
                if 'start_date' in edu:
                    edu['start_date'] = self._mask_date_to_range(edu['start_date'])
                if 'end_date' in edu:
                    edu['end_date'] = self._mask_date_to_range(edu['end_date'])
                if 'graduation_date' in edu:
                    edu['graduation_date'] = self._mask_date_to_range(edu['graduation_date'])

        return data

    def _mask_work_dates(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Mask work experience dates to ranges"""
        if 'experience' in data:
            for exp in data['experience']:
                if 'start_date' in exp:
                    exp['start_date'] = self._mask_date_to_range(exp['start_date'])
                if 'end_date' in exp:
                    exp['end_date'] = self._mask_date_to_range(exp['end_date'])

        return data

    def _anonymize_company_names(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Anonymize company names"""
        if 'experience' in data:
            for i, exp in enumerate(data['experience']):
                if 'company' in exp:
                    company_type = self._infer_company_type(exp)
                    exp['company'] = f"{company_type} Company {i + 1}"

        return data

    def _anonymize_school_names(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Anonymize school names"""
        if 'education' in data:
            for i, edu in enumerate(data['education']):
                if 'institution' in edu:
                    edu['institution'] = f"University {i + 1}"

        return data

    def _generate_candidate_id(self, personal_info: Dict[str, Any]) -> str:
        """Generate anonymous candidate ID"""
        hash_input = str(personal_info.get('full_name', '')) + str(datetime.utcnow())
        hash_value = hashlib.sha256(hash_input.encode()).hexdigest()
        return hash_value[:8].upper()

    def _generate_hash(self, data: Dict[str, Any]) -> str:
        """Generate hash of original data"""
        data_str = str(data)
        return hashlib.sha256(data_str.encode()).hexdigest()

    def _anonymize_email(self, email: str) -> str:
        """Anonymize email address"""
        if '@' in email:
            parts = email.split('@')
            domain = parts[1]
            return f"candidate@{domain}"
        return 'candidate@anonymized.com'

    def _anonymize_text_names(self, text: str) -> str:
        """Remove potential names from text"""
        name_patterns = [
            r'\b[A-Z][a-z]+ [A-Z][a-z]+\b',
            r'\b(?:Mr|Mrs|Ms|Dr|Prof)\.? [A-Z][a-z]+\b'
        ]

        anonymized = text
        for pattern in name_patterns:
            anonymized = re.sub(pattern, '[NAME]', anonymized)

        return anonymized

    def _neutralize_gendered_language(self, text: str) -> str:
        """Replace gendered pronouns with neutral ones"""
        if not text:
            return text

        replacements = {
            r'\bhe\b': 'they',
            r'\bhim\b': 'them',
            r'\bhis\b': 'their',
            r'\bshe\b': 'they',
            r'\bher\b': 'their',
            r'\bhers\b': 'theirs',
            r'\bHe\b': 'They',
            r'\bHim\b': 'Them',
            r'\bHis\b': 'Their',
            r'\bShe\b': 'They',
            r'\bHer\b': 'Their',
            r'\bHers\b': 'Theirs'
        }

        result = text
        for pattern, replacement in replacements.items():
            result = re.sub(pattern, replacement, result)

        return result

    def _extract_city_country(self, address: str) -> Dict[str, Optional[str]]:
        """Extract only city and country from full address"""
        parts = [p.strip() for p in address.split(',')]
        if len(parts) >= 2:
            return {'city': parts[-2], 'country': parts[-1]}
        elif len(parts) == 1:
            return {'city': parts[0], 'country': None}
        return {'city': None, 'country': None}

    def _mask_date_to_range(self, date_str: Optional[str]) -> Optional[str]:
        """Mask specific date to year range"""
        if not date_str or date_str == 'Present':
            return date_str

        year_match = re.search(r'(\d{4})', str(date_str))
        if year_match:
            year = int(year_match.group(1))
            range_start = (year // 5) * 5
            range_end = range_start + 4
            return f"{range_start}-{range_end}"

        return date_str

    def _infer_company_type(self, experience: Dict[str, Any]) -> str:
        """Infer company type from experience"""
        title = (experience.get('title') or '').lower()
        description = (experience.get('description') or '').lower()

        if any(word in title + description for word in ['software', 'developer', 'engineer', 'tech']):
            return 'Technology'
        elif any(word in title + description for word in ['finance', 'banking', 'investment']):
            return 'Financial'
        elif any(word in title + description for word in ['healthcare', 'medical', 'hospital']):
            return 'Healthcare'
        elif any(word in title + description for word in ['retail', 'sales', 'store']):
            return 'Retail'
        elif any(word in title + description for word in ['education', 'teaching', 'university']):
            return 'Education'
        else:
            return 'Professional'

    def get_anonymization_report(
        self,
        original_data: Dict[str, Any],
        anonymized_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate report of what was anonymized

        Args:
            original_data: Original resume data
            anonymized_data: Anonymized resume data

        Returns:
            Anonymization report
        """
        report = {
            'fields_removed': [],
            'fields_masked': [],
            'fields_preserved': [],
            'anonymization_level': 'standard'
        }

        if '_anonymization_metadata' in anonymized_data:
            metadata = anonymized_data['_anonymization_metadata']
            options = metadata.get('options_used', {})

            for option, enabled in options.items():
                if enabled:
                    field_name = option.replace('_', ' ').replace('remove ', '').replace('mask ', '')
                    if 'remove' in option:
                        report['fields_removed'].append(field_name)
                    elif 'mask' in option:
                        report['fields_masked'].append(field_name)

        pii_removed_count = len(report['fields_removed']) + len(report['fields_masked'])
        if pii_removed_count >= 6:
            report['anonymization_level'] = 'high'
        elif pii_removed_count >= 3:
            report['anonymization_level'] = 'medium'
        else:
            report['anonymization_level'] = 'low'

        return report

_anonymizer_instance = None

def get_anonymizer() -> ResumeAnonymizer:
    """Get or create anonymizer instance (singleton)"""
    global _anonymizer_instance
    if _anonymizer_instance is None:
        _anonymizer_instance = ResumeAnonymizer()
    return _anonymizer_instance
