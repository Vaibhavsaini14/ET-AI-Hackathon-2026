import json
import re
from groq import Groq
from loguru import logger
from app.config import settings

class IntentClassifier:
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

    def classify(self, query: str) -> dict:
        system_prompt = """Classify the user's query into exactly one intent for an industrial document assistant.

Return ONLY valid JSON, no preamble:
{"intent": "factual_lookup" | "relationship_query" | "compliance_check" | "comparison", "reasoning": "short reason"}

- factual_lookup: simple fact-finding, "what is X", "summarize Y"
- relationship_query: asks how things connect, depend on, or affect each other ("what's connected to X", "what happens if Y fails")
- compliance_check: asks about safety, regulations, standards, hazards, violations
- comparison: asks to compare two or more things"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                max_tokens=150,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": query}
                ]
            )
            raw = response.choices[0].message.content
            cleaned = re.sub(r"```json|```", "", raw).strip()
            return json.loads(cleaned)
        except Exception as e:
            logger.warning(f"Intent classification failed: {e}")
            return {"intent": "factual_lookup", "reasoning": "fallback"}