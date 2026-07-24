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

    def route(self, query: str, user_role: str = "engineer", doc_ids: list = None) -> dict:
        doc_ids = doc_ids or []
        cached_result = self.cache.get(query, user_role)
        if cached_result:
            cached_result["cached"] = True
            return cached_result

        classification = self.classifier.classify(query)
        intent = classification.get("intent", "factual_lookup")

        logger.info(f"Detected intent: {intent}")
        logger.info(f"Query: {query}")

        if intent == "relationship_query":
            result = self.graph_rag.answer_with_graph(query, user_role)
            agent_used = "Graph RAG Agent"

        elif intent == "compliance_check":
            result = self.rag.answer(query, user_role, doc_ids)
            result["compliance_flag"] = True
            agent_used = "Compliance Agent"

        else:
            result = self.rag.answer(query, user_role, doc_ids)
            agent_used = "Hybrid RAG Agent"

        result["intent"] = intent
        result["agent_used"] = agent_used
        result["cached"] = False

        self.cache.set(query, user_role, result)

        return result