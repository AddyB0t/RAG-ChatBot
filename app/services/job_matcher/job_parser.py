import json
import re
from typing import Dict, List, Any
from app.utils.openai_client import OpenAIClient
import logging

logger = logging.getLogger(__name__)

class JobDescriptionParser:
    def __init__(self):
        self.llm = OpenAIClient()

    def parse_job_description(self, job_description: str, job_title: str) -> Dict[str, Any]:
        try:
            prompt = f"""Analyze this job description and extract structured information.

Job Title: {job_title}

Job Description:
{job_description}

Extract the following in JSON format:
- required_skills: List of required technical and soft skills
- preferred_skills: List of preferred/nice-to-have skills
- experience_required: Minimum years of experience (number)
- experience_preferred: Preferred years of experience (number)
- education_required: Minimum education level
- responsibilities: List of key responsibilities
- technologies: List of specific technologies/tools mentioned
- industry: Industry or domain
- job_level: Entry/Mid/Senior/Executive
- location_type: Remote/Hybrid/Onsite
- key_requirements: Top 5 most important requirements

Return ONLY valid JSON, no additional text."""

            result = self.llm.invoke(prompt, temperature=0.2).strip()

            result = re.sub(r'^```json\s*', '', result)
            result = re.sub(r'\s*```$', '', result)

            parsed_job = json.loads(result)

            return {
                "required_skills": parsed_job.get("required_skills", []),
                "preferred_skills": parsed_job.get("preferred_skills", []),
                "experience_required": parsed_job.get("experience_required", 0),
                "experience_preferred": parsed_job.get("experience_preferred", 0),
                "education_required": parsed_job.get("education_required", ""),
                "responsibilities": parsed_job.get("responsibilities", []),
                "technologies": parsed_job.get("technologies", []),
                "industry": parsed_job.get("industry", ""),
                "job_level": parsed_job.get("job_level", ""),
                "location_type": parsed_job.get("location_type", ""),
                "key_requirements": parsed_job.get("key_requirements", [])
            }

        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error in job parsing: {e}")
            return self._get_default_job_structure()
        except Exception as e:
            logger.error(f"Error parsing job description: {e}")
            return self._get_default_job_structure()

    def _get_default_job_structure(self) -> Dict[str, Any]:
        return {
            "required_skills": [],
            "preferred_skills": [],
            "experience_required": 0,
            "experience_preferred": 0,
            "education_required": "",
            "responsibilities": [],
            "technologies": [],
            "industry": "",
            "job_level": "",
            "location_type": "",
            "key_requirements": []
        }

