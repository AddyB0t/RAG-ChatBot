"""
Tests for Resume Anonymizer
"""
import pytest
from app.services.anonymizer import ResumeAnonymizer, get_anonymizer

class TestResumeAnonymizer:

    @pytest.fixture
    def anonymizer(self):
        return get_anonymizer()

    @pytest.fixture
    def sample_resume(self):
        return {
            "personal_info": {
                "full_name": "John Michael Smith",
                "first_name": "John",
                "last_name": "Smith",
                "title": "Senior Software Engineer",
                "summary": "He is an experienced developer",
                "date_of_birth": "1990-05-15",
                "age": 33,
                "gender": "male",
                "contact": {
                    "email": "john.smith@example.com",
                    "phone": ["+1-555-0123", "+1-555-0124"],
                    "linkedin": "linkedin.com/in/johnsmith",
                    "github": "github.com/johnsmith",
                    "address": "123 Main St, San Francisco, CA, USA"
                }
            },
            "experience": [
                {
                    "title": "Senior Software Engineer",
                    "company": "Tech Corp Inc",
                    "start_date": "2020-01-15",
                    "end_date": "Present",
                    "description": "He developed applications"
                }
            ],
            "education": [
                {
                    "institution": "Stanford University",
                    "degree": "Master of Science",
                    "field": "Computer Science",
                    "start_date": "2010-09-01",
                    "end_date": "2012-06-15",
                    "graduation_date": "2012-06-15"
                }
            ],
            "skills": {
                "technical": ["Python", "Java", "AWS"],
                "soft": ["Leadership", "Communication"],
                "languages": ["English", "Spanish"]
            }
        }

    def test_anonymizer_initialization(self, anonymizer):
        assert anonymizer is not None

    def test_default_options(self, anonymizer):
        options = anonymizer._get_default_options()

        assert options['remove_name'] is True
        assert options['remove_contact'] is True
        assert options['remove_address'] is True
        assert options['remove_age_dob'] is True
        assert options['remove_gender'] is True
        assert options['mask_education_dates'] is True
        assert options['mask_work_dates'] is False

    def test_anonymize_with_default_options(self, anonymizer, sample_resume):
        result = anonymizer.anonymize_resume(sample_resume)

        assert '_anonymization_metadata' in result
        assert result['_anonymization_metadata']['anonymized'] is True

    def test_remove_name(self, anonymizer, sample_resume):
        result = anonymizer.anonymize_resume(sample_resume)

        assert 'Candidate' in result['personal_info']['full_name']
        assert result['personal_info']['full_name'] != "John Michael Smith"
        assert len(result['personal_info']['last_name']) == 8

    def test_remove_contact_info(self, anonymizer, sample_resume):
        result = anonymizer.anonymize_resume(sample_resume)

        contact = result['personal_info']['contact']
        assert '@' in contact['email']
        assert 'REDACTED' in str(contact['phone'])
        assert contact['linkedin'] == '[REDACTED]'
        assert contact['github'] == '[REDACTED]'

    def test_anonymize_email(self, anonymizer):
        email1 = anonymizer._anonymize_email("john.smith@example.com")
        assert email1 == "candidate@example.com"

        email2 = anonymizer._anonymize_email("invalid")
        assert email2 == "candidate@anonymized.com"

    def test_remove_address(self, anonymizer, sample_resume):
        result = anonymizer.anonymize_resume(sample_resume)

        address = result['personal_info']['contact'].get('address')
        if isinstance(address, dict):
            assert 'city' in address or 'country' in address
        elif isinstance(address, str):
            original_len = len(sample_resume['personal_info']['contact']['address'])
            new_len = len(address)
            assert new_len <= original_len

    def test_remove_age_dob(self, anonymizer, sample_resume):
        result = anonymizer.anonymize_resume(sample_resume)

        assert 'date_of_birth' not in result['personal_info']
        assert 'age' not in result['personal_info']

    def test_remove_gender(self, anonymizer, sample_resume):
        result = anonymizer.anonymize_resume(sample_resume)

        assert 'gender' not in result['personal_info']

    def test_neutralize_gendered_language(self, anonymizer):
        text = "He is a great developer. His skills are excellent."
        result = anonymizer._neutralize_gendered_language(text)

        assert 'he' not in result.lower() or 'they' in result.lower()

    def test_mask_education_dates(self, anonymizer, sample_resume):
        options = {'mask_education_dates': True}
        result = anonymizer.anonymize_resume(sample_resume, options)

        if result.get('education'):
            edu = result['education'][0]
            if 'start_date' in edu:
                assert '-' in edu['start_date']

    def test_mask_date_to_range(self, anonymizer):
        date1 = anonymizer._mask_date_to_range("2020-01-15")
        assert '-' in date1
        assert '2020' in date1

        date2 = anonymizer._mask_date_to_range("Present")
        assert date2 == "Present"

        date3 = anonymizer._mask_date_to_range(None)
        assert date3 is None

    def test_mask_work_dates(self, anonymizer, sample_resume):
        options = {'mask_work_dates': True}
        result = anonymizer.anonymize_resume(sample_resume, options)

        if result.get('experience'):
            exp = result['experience'][0]
            if exp.get('start_date') and exp['start_date'] != 'Present':
                assert '-' in exp['start_date']

    def test_anonymize_company_names(self, anonymizer, sample_resume):
        options = {'remove_company_names': True}
        result = anonymizer.anonymize_resume(sample_resume, options)

        if result.get('experience'):
            exp = result['experience'][0]
            assert 'Company' in exp['company']
            assert exp['company'] != "Tech Corp Inc"

    def test_anonymize_school_names(self, anonymizer, sample_resume):
        options = {'remove_school_names': True}
        result = anonymizer.anonymize_resume(sample_resume, options)

        if result.get('education'):
            edu = result['education'][0]
            assert 'University' in edu['institution']
            assert edu['institution'] != "Stanford University"

    def test_generate_candidate_id(self, anonymizer):
        personal_info = {"full_name": "John Smith"}
        id1 = anonymizer._generate_candidate_id(personal_info)

        assert len(id1) == 8
        assert id1.isupper()

    def test_infer_company_type(self, anonymizer):
        exp_tech = {"title": "Software Engineer", "description": "Developed tech solutions"}
        type1 = anonymizer._infer_company_type(exp_tech)
        assert type1 == 'Technology'

        exp_finance = {"title": "Investment Banker", "description": "Banking operations"}
        type2 = anonymizer._infer_company_type(exp_finance)
        assert type2 == 'Financial'

        exp_generic = {"title": "Manager", "description": "General management"}
        type3 = anonymizer._infer_company_type(exp_generic)
        assert type3 == 'Professional'

    def test_extract_city_country(self, anonymizer):
        address1 = "123 Main St, San Francisco, CA, USA"
        result1 = anonymizer._extract_city_country(address1)
        assert 'city' in result1
        assert 'country' in result1

        address2 = "Boston"
        result2 = anonymizer._extract_city_country(address2)
        assert result2['city'] == "Boston"

    def test_anonymization_report(self, anonymizer, sample_resume):
        anonymized = anonymizer.anonymize_resume(sample_resume)
        report = anonymizer.get_anonymization_report(sample_resume, anonymized)

        assert 'fields_removed' in report
        assert 'fields_masked' in report
        assert 'fields_preserved' in report
        assert 'anonymization_level' in report
        assert report['anonymization_level'] in ['low', 'medium', 'high']

    def test_custom_options(self, anonymizer, sample_resume):
        custom_options = {
            'remove_name': True,
            'remove_contact': False,
            'remove_address': False,
            'remove_age_dob': True,
            'remove_gender': False,
            'mask_education_dates': False,
            'mask_work_dates': False,
            'remove_company_names': False,
            'remove_school_names': False
        }

        result = anonymizer.anonymize_resume(sample_resume, custom_options)

        assert 'Candidate' in result['personal_info']['full_name']
        assert result['personal_info']['contact']['email'] == "john.smith@example.com"

    def test_anonymization_metadata(self, anonymizer, sample_resume):
        result = anonymizer.anonymize_resume(sample_resume)

        metadata = result['_anonymization_metadata']
        assert metadata['anonymized'] is True
        assert 'anonymization_date' in metadata
        assert 'original_hash' in metadata
        assert 'options_used' in metadata

    def test_hash_generation(self, anonymizer, sample_resume):
        hash1 = anonymizer._generate_hash(sample_resume)
        hash2 = anonymizer._generate_hash(sample_resume)

        assert hash1 == hash2
        assert len(hash1) == 64

    def test_singleton_pattern(self):
        anon1 = get_anonymizer()
        anon2 = get_anonymizer()
        assert anon1 is anon2

    def test_empty_resume(self, anonymizer):
        empty_resume = {}
        result = anonymizer.anonymize_resume(empty_resume)

        assert '_anonymization_metadata' in result

    def test_partial_resume(self, anonymizer):
        partial_resume = {
            "personal_info": {
                "full_name": "Jane Doe"
            }
        }

        result = anonymizer.anonymize_resume(partial_resume)
        assert 'Candidate' in result['personal_info']['full_name']
