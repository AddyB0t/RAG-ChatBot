import json
import re
from typing import List, Dict, Any
from .base_extractor import BaseExtractor
from app.utils.openrouter_client import OpenRouterClient
import logging

logger = logging.getLogger(__name__)

class SkillsExtractor(BaseExtractor):

    TECHNICAL_SKILLS = [
        "Python", "Java", "JavaScript", "TypeScript", "C++", "C#", "Go", "Rust", "Ruby", "PHP", "Swift", "Kotlin",
        "React", "Angular", "Vue", "Node.js", "Django", "Flask", "FastAPI", "Spring", "Express",
        "PostgreSQL", "MySQL", "MongoDB", "Redis", "Cassandra", "DynamoDB", "Elasticsearch",
        "AWS", "Azure", "GCP", "Docker", "Kubernetes", "Jenkins", "GitLab", "CI/CD", "Terraform",
        "Machine Learning", "Deep Learning", "TensorFlow", "PyTorch", "Scikit-learn", "NLP", "Computer Vision",
        "Git", "Linux", "REST API", "GraphQL", "Microservices", "Agile", "Scrum"
    ]

    SOFT_SKILLS = [
        "Leadership", "Communication", "Problem Solving", "Team Player", "Critical Thinking",
        "Time Management", "Adaptability", "Collaboration", "Creative", "Analytical",
        "Project Management", "Presentation", "Negotiation", "Mentoring", "Strategic Planning"
    ]

    def __init__(self):
        self.llm = OpenRouterClient()

    def extract(self, text: str) -> Dict[str, Any]:
        try:
            prompt = f"""Extract skills from the resume text below. Return a JSON object with this structure:

{{
  "technical": [
    {{"category": "Programming Languages", "items": ["Python", "Java"]}},
    {{"category": "Frameworks", "items": ["Django", "React"]}},
    {{"category": "Databases", "items": ["PostgreSQL", "MongoDB"]}},
    {{"category": "Cloud/DevOps", "items": ["AWS", "Docker"]}},
    {{"category": "Tools", "items": ["Git", "Jenkins"]}}
  ],
  "soft": ["Leadership", "Communication", "Problem Solving"],
  "languages": [
    {{"language": "English", "proficiency": "Native"}},
    {{"language": "Spanish", "proficiency": "Conversational"}}
  ]
}}

Resume text:
{text}

Return ONLY valid JSON object, no additional text."""

            result = self.llm.invoke(prompt, temperature=0.2).strip()

            result = re.sub(r'^```json\s*', '', result)
            result = re.sub(r'\s*```$', '', result)

            skills = json.loads(result)

            return skills

        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error in skills extraction: {e}")
            return self._fallback_extract(text)
        except Exception as e:
            logger.error(f"Error extracting skills: {e}")
            return self._fallback_extract(text)

    def _fallback_extract(self, text: str) -> Dict[str, Any]:
        text_lower = text.lower()

        found_technical = [skill for skill in self.TECHNICAL_SKILLS if skill.lower() in text_lower]
        found_soft = [skill for skill in self.SOFT_SKILLS if skill.lower() in text_lower]

        return {
            "technical": [{"category": "General", "items": found_technical}] if found_technical else [],
            "soft": found_soft,
            "languages": []
        }

    def validate(self, match: str) -> bool:
        return bool(match and len(match) > 0)

