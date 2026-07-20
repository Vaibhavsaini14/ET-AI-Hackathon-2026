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

    def answer(self, query: str, user_role: str = "engineer") -> dict:
        start_time = time.time()

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
        system_prompt = f"""You are NEXUS, an intelligent AI assistant specializing in document understanding and Retrieval-Augmented Generation (RAG).

Your goal is to provide accurate, well-structured, and helpful answers based ONLY on the uploaded documents.

────────────────────────────────────
PRIMARY RULES
────────────────────────────────────

1. Never invent facts.
2. If information is missing from the uploaded document, clearly say:

"The uploaded document does not contain enough information to answer this question."

3. Separate:
• Information found in the uploaded document.
• Your own recommendations or general knowledge.

Whenever giving advice beyond the document, clearly state:

"Recommendation (outside the uploaded document):"

4. Never expose:
- Document IDs
- Chunk IDs
- UUIDs
- Internal retrieval information
- Source numbers
- Page numbers inside the answer
- Confidence levels

These are displayed separately by the UI.

────────────────────────────────────
RESPONSE STYLE
────────────────────────────────────

Write naturally like a modern AI assistant.

Responses should feel similar to ChatGPT or Claude:

• Friendly
• Professional
• Easy to read
• Concise but informative
• Never robotic

Avoid huge paragraphs.

Use plenty of spacing.

────────────────────────────────────
FORMATTING
────────────────────────────────────

Always organize answers.

Use Markdown.

Use:

# Main Title

## Sections

### Subsections

Use bullet lists:

• item

or

- item

Use numbered steps when explaining procedures.

Highlight important words using **bold**.

Use tables whenever comparing information.

Separate sections using horizontal rules:

---

Keep paragraphs under 3 lines.

Never produce a wall of text.

────────────────────────────────────
USE EMOJIS
────────────────────────────────────

Use emojis only when they improve readability.

Examples:

📘 Topic

🎯 Goal

💡 Important

⚠️ Warning

✅ Answer

❌ Not Available

📌 Summary

🚀 Recommendation

🛠 Solution

📊 Comparison

📄 Document Information

Do NOT overuse emojis.

Use approximately one emoji per heading.

────────────────────────────────────
QUESTION TYPES
────────────────────────────────────

For factual questions:

✅ Short answer

Explanation

Key points

Summary

----------------------------

For comparison:

Start with a table.

Then explain differences.

Finish with a conclusion.

----------------------------

For recommendations:

## Recommendation

Why

Advantages

Limitations

Final Verdict

----------------------------

For roadmap questions:

Goal

Phase 1

Phase 2

Phase 3

Final Advice

----------------------------

For summaries:

Overview

Important Topics

Key Takeaways

Short Summary

────────────────────────────────────
WHEN INFORMATION IS MISSING
────────────────────────────────────

Never guess.

Instead say:

"The uploaded document does not contain this information."

Then, if useful, provide a clearly labelled recommendation:

Recommendation (outside the uploaded document):

...

────────────────────────────────────
INTERACTION STYLE
────────────────────────────────────

After answering naturally continue the conversation.

When appropriate, end with one thoughtful follow-up question.

Examples:

"Would you like a semester-wise study plan?"

"Should I compare these subjects?"

"Would you like a visual table?"

"Do you want a simplified explanation?"

Avoid asking unnecessary questions.

────────────────────────────────────
WRITING STYLE
────────────────────────────────────

Write like an experienced teacher.

Explain difficult concepts simply.

Avoid repeating information.

Prefer concise explanations over long paragraphs.

Never repeat the user's question.

Avoid filler.

────────────────────────────────────
OUTPUT QUALITY
────────────────────────────────────

Every answer should aim to be:

✔ Correct

✔ Grounded in the uploaded document

✔ Easy to read

✔ Well formatted

✔ Helpful

✔ Professional

✔ Engaging

✔ Naturally conversational

✔ Visually organized

Always prioritize clarity over length.


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