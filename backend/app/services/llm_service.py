import time
from groq import Groq
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential
from app.config import settings
from app.services.retrieval import HybridRetrievalService

class RAGService:
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
        self.retrieval = HybridRetrievalService()
        self.model = "llama-3.3-70b-versatile"
        self._initialized = True
        logger.info("RAG service ready with Groq LLM")

    def answer(self, query: str, user_role: str = "engineer", doc_ids: list = None) -> dict:
        start_time = time.time()
        retrieved = self.retrieval.retrieve(query, top_k=5, doc_ids=doc_ids)

        # Step 1: Retrieve relevant chunks
        retrieved = self.retrieval.retrieve(query, top_k=5)

        if not retrieved:
            return {
                "answer": "No documents have been indexed yet. Please upload documents first using the /api/documents/upload endpoint.",
                "sources": [],
                "confidence": "LOW",
                "processing_time_ms": 0
            }

        # Step 2: Build context with source markers
        context_parts = []
        sources = []

        for i, chunk in enumerate(retrieved):
            meta = chunk["metadata"]
            context_parts.append(
                f"[SOURCE {i + 1}]\n"
                f"Document: {meta.get('title', 'Unknown')}\n"
                f"Page: {meta.get('page_number', 'N/A')}\n"
                f"Content: {chunk['text']}\n"
            )
            sources.append({
                "index": i + 1,
                "title": meta.get("title", "Unknown"),
                "page": meta.get("page_number", 1),
                "doc_id": meta.get("doc_id", ""),
                "doc_type": meta.get("doc_type", "unknown"),
                "snippet": chunk["text"][:200]
            })

        context = "\n\n".join(context_parts)

        # Step 3: Role-based instructions
        role_instructions = {
            "technician": "Use simple, clear language. Focus on step-by-step practical instructions and safety warnings.",
            "engineer": "Provide full technical detail including specifications, standards references, and engineering rationale.",
            "manager": "Give a concise executive summary focusing on risks, impacts, and required actions."
        }

        instruction = role_instructions.get(
            user_role, role_instructions["engineer"]
        )

        # Step 4: Call Groq LLM
        system_prompt = f"""You are NEXUS, an expert industrial knowledge assistant.

        You must answer ONLY using the information provided in the context.

        RULES:
        1. Never invent or assume information that is not present in the provided context.
        2. Write the answer in natural, fluent English.
        3. Do NOT mention:
        - Source 1, Source 2, etc.
        - Document IDs
        - Page numbers
        - Chunk IDs
        - Confidence levels
        4. Do NOT write phrases like:
        - "According to Source 1..."
        - "[Source 1]"
        - "CONFIDENCE: HIGH"
        5. If the answer is not available in the provided context, reply exactly:
        "The uploaded document does not contain sufficient information to answer this question."
        6. Use proper Markdown formatting:
        - Use headings (##)
        - Use bullet points
        - Use numbered lists when appropriate
        - Use tables whenever comparing information
        7. Keep the answer concise, readable, and professional.

        Communication style:
        {instruction}

        Context:
        {context}
        """

        response = self._call_groq(system_prompt, query)
        answer_text = response

       # Step 5: Estimate confidence automatically
        confidence = "HIGH"

        if "does not contain sufficient information" in answer_text.lower():
            confidence = "LOW"
        elif len(retrieved) < 3:
            confidence = "MEDIUM"

        processing_time = int((time.time() - start_time) * 1000)

        logger.info(
            f"RAG complete — confidence: {confidence}, time: {processing_time}ms"
        )

        return {
            "answer": answer_text,
            "sources": sources,
            "confidence": confidence,
            "processing_time_ms": processing_time
        }

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def _call_groq(self, system_prompt: str, query: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            max_tokens=1500,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ]
        )
        return response.choices[0].message.content