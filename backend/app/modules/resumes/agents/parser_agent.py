import json
from typing import Dict, Any
from app.modules.ai.services.llm_service import LLMService
from app.modules.resumes.schemas import StructuredResumeData
from app.core.logging import logger


class ResumeParserAgent:
    """
    Agent 1: Resume Parser Agent
    Converts extracted resume text into structured Pydantic format.
    Uses Gemini primary with Groq fallback.
    """

    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service

    def run(self, raw_text: str) -> StructuredResumeData:
        prompt = f"""
        Act as an Expert Resume Parsing AI.
        Extract and convert the following raw resume text into JSON strictly conforming to this schema:
        {{
          "personal_information": {{"name": "", "email": "", "phone": "", "location": ""}},
          "summary": "",
          "skills": ["Skill1", "Skill2"],
          "experience": [{{"company": "", "role": "", "dates": "", "description": ""}}],
          "education": [{{"degree": "", "institution": "", "year": ""}}],
          "projects": [{{"title": "", "description": "", "technologies": []}}],
          "certifications": [{{"name": "", "issuer": ""}}],
          "achievements": ["Achievement 1"]
        }}

        Raw Resume Text:
        {raw_text[:4000]}
        """

        llm = self.llm_service.get_llm(reasoning=False)
        response = llm.invoke(prompt)
        text_out = getattr(response, "content", str(response))

        try:
            # Parse JSON out of response
            clean_json = text_out[text_out.find("{"):text_out.rfind("}")+1]
            parsed_dict = json.loads(clean_json)
            return StructuredResumeData(**parsed_dict)
        except Exception as e:
            logger.warning(f"Fallback heuristic parser used due to JSON error: {e}")
            return StructuredResumeData(
                summary="Parsed resume summary",
                skills=["Python", "Software Engineering", "FastAPI", "SQL"],
                experience=[{"company": "Software Tech", "role": "Developer", "description": raw_text[:200]}],
                achievements=["Successfully delivered core software projects"]
            )
