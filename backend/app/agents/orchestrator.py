from loguru import logger
from app.agents.intent_classifier import IntentClassifier
from app.services.llm_service import RAGService
from app.services.graph_rag_service import GraphRAGService
from app.services.cache_service import CacheService

class Orchestrator:
    def __init__(self):
        self.classifier = IntentClassifier()
        self.rag = RAGService()
        self.graph_rag = GraphRAGService()
        self.cache = CacheService()

    def route(self, query: str, user_role: str = "engineer") -> dict:
        # Check cache first
        cached_result = self.cache.get(query, user_role)
        if cached_result:
            cached_result["cached"] = True
            return cached_result

        classification = self.classifier.classify(query)
        intent = classification.get("intent", "factual_lookup")

        logger.info(f"Routed query as '{intent}': {query[:60]}")

        if intent in ("relationship_query", "comparison"):
            result = self.graph_rag.answer_with_graph(query, user_role)
            agent_used = "Graph RAG Agent"
        elif intent == "compliance_check":
            result = self.rag.answer(query, user_role)
            result["compliance_flag"] = True
            agent_used = "Compliance Agent"
        else:
            result = self.rag.answer(query, user_role)
            agent_used = "Hybrid RAG Agent"

        result["intent"] = intent
        result["agent_used"] = agent_used
        result["cached"] = False

        self.cache.set(query, user_role, result)
        return result