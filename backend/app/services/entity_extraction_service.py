import json
import re
from groq import Groq
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential
from app.config import settings

class EntityExtractionService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self.client = Groq(api_key=settings.groq_api_key)
        self.model = "llama-3.3-70b-versatile"
        self._initialized = True
        logger.info("Entity extraction service ready")

    def extract(self, chunk_text: str, chunk_id: str) -> dict:
        system_prompt = """You extract entities and relationships from industrial engineering text for a knowledge graph.

Return ONLY valid JSON, no preamble, in this exact format:
{
  "entities": [
    {"name": "Pump P-101", "type": "EQUIPMENT"},
    {"name": "Bearing Assembly", "type": "PART"}
  ],
  "relationships": [
    {"source": "Pump P-101", "relation": "HAS_PART", "target": "Bearing Assembly"}
  ]
}

Entity types: EQUIPMENT, PART, PROCEDURE, STANDARD, PERSON, LOCATION, HAZARD, MEASUREMENT.
Relation types: HAS_PART, REQUIRES, PRECEDES, LOCATED_AT, MAINTAINED_BY, COMPLIES_WITH, CAUSES, MITIGATED_BY.
If no entities are found, return {"entities": [], "relationships": []}.
Only extract entities explicitly named in the text — never invent them."""

        try:
            raw = self._call_groq(system_prompt, chunk_text)
            cleaned = re.sub(r"```json|```", "", raw).strip()
            data = json.loads(cleaned)
            data["chunk_id"] = chunk_id
            return data
        except Exception as e:
            logger.warning(f"Entity extraction failed for {chunk_id}: {e}")
            return {"entities": [], "relationships": [], "chunk_id": chunk_id}

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def _call_groq(self, system_prompt: str, chunk_text: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            max_tokens=800,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": chunk_text[:2000]}
            ]
        )
        return response.choices[0].message.content