from typing import Dict, Any, Optional
import hashlib
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor
from sqlalchemy.orm import Session
from .contact_extractor import ContactExtractor
from .name_extractor import NameExtractor
from .experience_extractor import ExperienceExtractor
from .education_extractor import EducationExtractor
from .skills_extractor import SkillsExtractor
from .certifications_extractor import CertificationsExtractor
from .error_logger import ResumeParserErrorLogger

logger = logging.getLogger(__name__)

class ResumeParserManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self.contact_extractor = ContactExtractor()
        self.name_extractor = NameExtractor()
        self.experience_extractor = ExperienceExtractor()
        self.education_extractor = EducationExtractor()
        self.skills_extractor = SkillsExtractor()
        self.certifications_extractor = CertificationsExtractor()

        self._initialized = True
        self.executor = ThreadPoolExecutor(max_workers=6)
        logger.info("Resume Parser Manager initialized")

    async def parse_resume_async(self, text: str, resume_id: Optional[str] = None, db: Optional[Session] = None) -> Dict[str, Any]:
        """Async version that runs all extractions in parallel for speed"""
        logger.info("Starting parallel resume parsing")

        loop = asyncio.get_event_loop()

        tasks = [
            loop.run_in_executor(self.executor, self._extract_name, text, resume_id, db),
            loop.run_in_executor(self.executor, self._extract_contact, text, resume_id, db),
            loop.run_in_executor(self.executor, self._extract_experience, text, resume_id, db),
            loop.run_in_executor(self.executor, self._extract_education, text, resume_id, db),
            loop.run_in_executor(self.executor, self._extract_skills, text, resume_id, db),
            loop.run_in_executor(self.executor, self._extract_certifications, text, resume_id, db),
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        name_data, contact_data, experience, education, skills, certifications = results

        personal_info = {}
        if not isinstance(name_data, Exception):
            personal_info.update(name_data)
        if not isinstance(contact_data, Exception):
            personal_info["contact"] = contact_data

        structured_data = {
            "personal_info": personal_info,
            "experience": experience if not isinstance(experience, Exception) else [],
            "education": education if not isinstance(education, Exception) else [],
            "skills": skills if not isinstance(skills, Exception) else {"technical": [], "soft": [], "languages": []},
            "certifications": certifications if not isinstance(certifications, Exception) else []
        }

        logger.info("Parallel resume parsing completed")
        return structured_data

    def _extract_name(self, text: str, resume_id: Optional[str], db: Optional[Session]):
        """Extract name in separate thread"""
        try:
            return self.name_extractor.extract(text)
        except Exception as e:
            if db:
                ResumeParserErrorLogger.log_error(
                    db, e, "name_extraction_error", "NameExtractor",
                    resume_id, {"text_length": len(text)}, None, "error"
                )
            logger.warning(f"Name extraction failed: {e}")
            return {"full_name": None, "first_name": None, "last_name": None}

    def _extract_contact(self, text: str, resume_id: Optional[str], db: Optional[Session]):
        """Extract contact in separate thread"""
        try:
            return self.contact_extractor.extract(text)
        except Exception as e:
            if db:
                ResumeParserErrorLogger.log_error(
                    db, e, "contact_extraction_error", "ContactExtractor",
                    resume_id, {"text_length": len(text)}, None, "error"
                )
            logger.warning(f"Contact extraction failed: {e}")
            return {"email": None, "phone": [], "linkedin": None, "urls": []}

    def _extract_experience(self, text: str, resume_id: Optional[str], db: Optional[Session]):
        """Extract experience in separate thread"""
        try:
            return self.experience_extractor.extract(text)
        except Exception as e:
            if db:
                ResumeParserErrorLogger.log_error(
                    db, e, "experience_extraction_error", "ExperienceExtractor",
                    resume_id, {"text_length": len(text)}, None, "error"
                )
            logger.warning(f"Experience extraction failed: {e}")
            return []

    def _extract_education(self, text: str, resume_id: Optional[str], db: Optional[Session]):
        """Extract education in separate thread"""
        try:
            return self.education_extractor.extract(text)
        except Exception as e:
            if db:
                ResumeParserErrorLogger.log_error(
                    db, e, "education_extraction_error", "EducationExtractor",
                    resume_id, {"text_length": len(text)}, None, "error"
                )
            logger.warning(f"Education extraction failed: {e}")
            return []

    def _extract_skills(self, text: str, resume_id: Optional[str], db: Optional[Session]):
        """Extract skills in separate thread"""
        try:
            return self.skills_extractor.extract(text)
        except Exception as e:
            if db:
                ResumeParserErrorLogger.log_error(
                    db, e, "skills_extraction_error", "SkillsExtractor",
                    resume_id, {"text_length": len(text)}, None, "error"
                )
            logger.warning(f"Skills extraction failed: {e}")
            return {"technical": [], "soft": [], "languages": []}

    def _extract_certifications(self, text: str, resume_id: Optional[str], db: Optional[Session]):
        """Extract certifications in separate thread"""
        try:
            return self.certifications_extractor.extract(text)
        except Exception as e:
            if db:
                ResumeParserErrorLogger.log_error(
                    db, e, "certifications_extraction_error", "CertificationsExtractor",
                    resume_id, {"text_length": len(text)}, None, "error"
                )
            logger.warning(f"Certifications extraction failed: {e}")
            return []

    def parse_resume(self, text: str, resume_id: Optional[str] = None, db: Optional[Session] = None) -> Dict[str, Any]:
        logger.info("Starting resume parsing")

        personal_info = {}
        experience = []
        education = []
        skills = {}
        certifications = []

        try:
            logger.info("Extracting name...")
            try:
                name_data = self.name_extractor.extract(text)
                personal_info.update(name_data)
            except Exception as e:
                if db:
                    ResumeParserErrorLogger.log_error(
                        db, e, "name_extraction_error", "NameExtractor",
                        resume_id, {"text_length": len(text)}, None, "error"
                    )
                logger.warning(f"Name extraction failed: {e}")
                personal_info.update({"full_name": None, "first_name": None, "last_name": None})

            logger.info("Extracting contact information...")
            try:
                contact_data = self.contact_extractor.extract(text)
                personal_info["contact"] = contact_data
            except Exception as e:
                if db:
                    ResumeParserErrorLogger.log_error(
                        db, e, "contact_extraction_error", "ContactExtractor",
                        resume_id, {"text_length": len(text)}, None, "error"
                    )
                logger.warning(f"Contact extraction failed: {e}")
                personal_info["contact"] = {"email": None, "phone": [], "linkedin": None, "urls": []}

            logger.info("Extracting work experience...")
            try:
                experience = self.experience_extractor.extract(text)
            except Exception as e:
                if db:
                    ResumeParserErrorLogger.log_error(
                        db, e, "experience_extraction_error", "ExperienceExtractor",
                        resume_id, {"text_length": len(text)}, None, "error"
                    )
                logger.warning(f"Experience extraction failed: {e}")
                experience = []

            logger.info("Extracting education...")
            try:
                education = self.education_extractor.extract(text)
            except Exception as e:
                if db:
                    ResumeParserErrorLogger.log_error(
                        db, e, "education_extraction_error", "EducationExtractor",
                        resume_id, {"text_length": len(text)}, None, "error"
                    )
                logger.warning(f"Education extraction failed: {e}")
                education = []

            logger.info("Extracting skills...")
            try:
                skills = self.skills_extractor.extract(text)
            except Exception as e:
                if db:
                    ResumeParserErrorLogger.log_error(
                        db, e, "skills_extraction_error", "SkillsExtractor",
                        resume_id, {"text_length": len(text)}, None, "error"
                    )
                logger.warning(f"Skills extraction failed: {e}")
                skills = {"technical": [], "soft": [], "languages": []}

            logger.info("Extracting certifications...")
            try:
                certifications = self.certifications_extractor.extract(text)
            except Exception as e:
                if db:
                    ResumeParserErrorLogger.log_error(
                        db, e, "certifications_extraction_error", "CertificationsExtractor",
                        resume_id, {"text_length": len(text)}, None, "error"
                    )
                logger.warning(f"Certifications extraction failed: {e}")
                certifications = []

            structured_data = {
                "personal_info": personal_info,
                "experience": experience,
                "education": education,
                "skills": skills,
                "certifications": certifications
            }

            logger.info("Resume parsing completed successfully")
            return structured_data

        except Exception as e:
            if db:
                ResumeParserErrorLogger.log_error(
                    db, e, "resume_parsing_error", "ResumeParserManager",
                    resume_id, {"text_length": len(text)}, None, "critical"
                )
            logger.error(f"Critical error during resume parsing: {e}")
            raise

    def generate_resume_hash(self, file_content: bytes, file_name: str) -> str:
        hash_input = file_content + file_name.encode('utf-8')
        return hashlib.md5(hash_input).hexdigest()

_parser_manager_instance = None

def get_resume_parser():
    global _parser_manager_instance
    if _parser_manager_instance is None:
        _parser_manager_instance = ResumeParserManager()
    return _parser_manager_instance

