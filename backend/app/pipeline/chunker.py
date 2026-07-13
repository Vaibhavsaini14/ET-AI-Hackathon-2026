from dataclasses import dataclass, field
from loguru import logger

@dataclass
class DocumentChunk:
    chunk_id: str
    doc_id: str
    doc_type: str
    title: str
    page_number: int
    chunk_index: int
    text: str
    token_count: int
    metadata: dict = field(default_factory=dict)

class HierarchicalChunker:

    def __init__(self, chunk_size: int = 512, chunk_overlap: int = 64):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk(self, parsed_doc, doc_id: str) -> list:
        chunks = []
        chunk_index = 0

        for page in parsed_doc.pages:
            page_text = page["text"].strip()
            if not page_text:
                continue

            page_chunks = self._split_text(page_text)

            for chunk_text in page_chunks:
                if len(chunk_text.strip()) < 30:
                    continue

                prefixed_text = f"{parsed_doc.title} | Page {page['page_num']}\n{chunk_text}"

                chunk = DocumentChunk(
                    chunk_id=f"{doc_id}_chunk_{chunk_index}",
                    doc_id=doc_id,
                    doc_type=parsed_doc.doc_type,
                    title=parsed_doc.title,
                    page_number=page["page_num"],
                    chunk_index=chunk_index,
                    text=prefixed_text,
                    token_count=len(chunk_text.split()),
                    metadata={
                        "doc_id": doc_id,
                        "doc_type": parsed_doc.doc_type,
                        "page_number": page["page_num"],
                        "chunk_index": chunk_index,
                        "title": parsed_doc.title,
                        "chunk_id": f"{doc_id}_chunk_{chunk_index}"
                    }
                )
                chunks.append(chunk)
                chunk_index += 1

        logger.info(f"Created {len(chunks)} chunks from {parsed_doc.title}")
        return chunks

    def _split_text(self, text: str) -> list:
        words = text.split()
        chunks = []
        start = 0

        while start < len(words):
            end = start + self.chunk_size
            chunk_words = words[start:end]
            chunks.append(" ".join(chunk_words))
            start += self.chunk_size - self.chunk_overlap

        return chunks