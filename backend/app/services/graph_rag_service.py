from loguru import logger
from app.services.llm_service import RAGService
from app.services.knowledge_graph_service import KnowledgeGraphService

class GraphRAGService:
    def __init__(self):
        self.rag = RAGService()
        self.kg = KnowledgeGraphService()

    def answer_with_graph(self, query: str, user_role: str = "engineer") -> dict:
        base_result = self.rag.answer(query, user_role)

        # naive entity spotting: reuse graph node names present in the query
        query_lower = query.lower()
        matched_entities = [n for n in self.kg.graph.nodes if n.lower() in query_lower]

        graph_context = []
        for ent in matched_entities:
            neighbors = self.kg.get_neighbors(ent, hops=1)
            for n in neighbors["neighbors"][:5]:
                graph_context.append(f"{n['from']} —{n['relation']}→ {n['to']}")

        base_result["graph_context"] = graph_context
        base_result["matched_entities"] = matched_entities
        return base_result