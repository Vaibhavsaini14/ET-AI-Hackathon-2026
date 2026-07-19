# 🧠 NEXUS — Industrial Knowledge Intelligence Platform

<p align="center">
  <b>Turning dense industrial documents into instant, cited, trustworthy answers.</b>
</p>

<p align="center">
  <img alt="Python" src="https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white">
  <img alt="FastAPI" src="https://img.shields.io/badge/FastAPI-Backend-009688?logo=fastapi&logoColor=white">
  <img alt="React" src="https://img.shields.io/badge/React-Frontend-61DAFB?logo=react&logoColor=white">
  <img alt="Groq" src="https://img.shields.io/badge/LLM-Groq%20Llama%203.3-F55036">
  <img alt="ChromaDB" src="https://img.shields.io/badge/VectorDB-ChromaDB-6A5ACD">
  <img alt="License" src="https://img.shields.io/badge/License-MIT-green">
  <img alt="Status" src="https://img.shields.io/badge/Status-Hackathon%20Submission-orange">
</p>

<p align="center">
  Built for <b>ET AI Hackathon 2026</b>
</p>

---

## 📖 Table of Contents

- [Overview](#-overview)
- [The Problem](#-the-problem)
- [Key Features](#-key-features)
- [Architecture](#-architecture)
- [Tech Stack](#-tech-stack)
- [Installation](#-installation)
- [Usage](#-usage)
- [API Reference](#-api-reference)
- [Project Structure](#-project-structure)
- [Roadmap](#-roadmap)
- [Contributing](#-contributing)
- [License](#-license)
- [Acknowledgements](#-acknowledgements)

---

## 🚀 Overview

**NEXUS** is an AI-powered industrial knowledge assistant that transforms scattered engineering manuals, safety procedures, inspection reports, and maintenance records into a single, queryable source of truth.

Ask a question in plain English — NEXUS retrieves the most relevant content using **hybrid search**, reasons across **entity relationships** in a knowledge graph, routes the query to the right **specialized agent**, and returns a clear answer with **mandatory source citations** and a **confidence score**. No hallucinations. No digging through 200-page PDFs.

> Not just another RAG chatbot — a multi-agent reasoning system built for environments where getting the wrong answer has real consequences.

---

## 🎯 The Problem

Heavy industrial facilities generate enormous volumes of technical documentation — and frontline engineers, technicians, and managers routinely waste hours searching for one fact buried in a scanned manual. Existing search tools return keyword matches, not answers. Generic chatbots hallucinate specifications that don't exist. NEXUS closes that gap safely, with **every claim traceable back to its source document and page**.

---

## ✨ Key Features

| Feature | Description |
|---|---|
| 🔍 **Hybrid Retrieval** | Combines BM25 keyword search with semantic vector search, fused via Reciprocal Rank Fusion (RRF) for best-of-both-worlds accuracy |
| 🤖 **Cited LLM Answers** | Every factual claim is grounded and cited as `[Source X: Document, Page Y]` — powered by Groq's Llama 3.3 70B |
| 🕸️ **Knowledge Graph** | Automatically extracts entities and relationships from documents, enabling multi-hop relationship reasoning beyond flat text search |
| 🧭 **Multi-Agent Orchestration** | An intent classifier routes each query to the right specialist: Hybrid RAG Agent, Graph RAG Agent, or Compliance Agent |
| 🎚️ **Role-Based Responses** | The same question yields different depth and tone for a Technician, Engineer, or Manager |
| 📊 **Confidence Scoring** | Every answer is labeled HIGH / MEDIUM / LOW confidence, so users know when to double-check |
| ⚡ **Semantic Caching** | Repeated or paraphrased questions are served instantly from cache instead of re-querying the LLM |
| 📈 **Analytics Dashboard** | Live visibility into query volume, agent usage, cache performance, and graph size |
| 🖥️ **Modern Web UI** | Clean React interface for uploading documents and chatting — no Postman or Swagger required |

---

## 🏗️ Architecture

```
                         ┌─────────────────────┐
                         │   Document Upload    │
                         └──────────┬───────────┘
                                    ▼
                    ┌───────────────────────────────┐
                    │   Ingestion Pipeline            │
                    │  Parse → Chunk → Embed → Index  │
                    └───────────────┬─────────────────┘
                                    │
              ┌─────────────────────┼─────────────────────┐
              ▼                     ▼                     ▼
      ┌──────────────┐     ┌────────────────┐     ┌──────────────────┐
      │   ChromaDB    │     │  BM25 Keyword   │     │  Knowledge Graph  │
      │  (Semantic)   │     │     Index       │     │  (Entities/Rels)  │
      └──────────────┘     └────────────────┘     └──────────────────┘
              │                     │                     │
              └─────────────────────┼─────────────────────┘
                                    ▼
                       ┌─────────────────────────┐
                       │   User Query Comes In     │
                       └────────────┬──────────────┘
                                    ▼
                       ┌─────────────────────────┐
                       │   Semantic Cache Check    │──── HIT ──▶ Instant Response
                       └────────────┬──────────────┘
                                 MISS
                                    ▼
                       ┌─────────────────────────┐
                       │   Intent Classifier       │
                       └────────────┬──────────────┘
                                    ▼
         ┌──────────────────────────┼──────────────────────────┐
         ▼                          ▼                          ▼
 ┌───────────────┐        ┌────────────────────┐      ┌──────────────────┐
 │ Hybrid RAG     │        │  Graph RAG Agent    │      │ Compliance Agent  │
 │ Agent          │        │  (multi-hop)        │      │  (safety focus)   │
 └───────┬────────┘        └──────────┬──────────┘      └─────────┬─────────┘
         └────────────────────────────┼──────────────────────────┘
                                       ▼
                        ┌─────────────────────────┐
                        │   Groq LLM (Llama 3.3)    │
                        │  Cited, role-based answer  │
                        └────────────┬──────────────┘
                                     ▼
                        ┌─────────────────────────┐
                        │  Cached + Returned to UI  │
                        └─────────────────────────┘
```

---

## 🛠️ Tech Stack

**Backend**
- **FastAPI** — high-performance async API framework
- **Groq API (Llama 3.3 70B Versatile)** — ultra-fast LLM inference
- **ChromaDB** — persistent vector store for semantic search
- **Sentence-Transformers** (`all-MiniLM-L6-v2`) — embedding model
- **rank-bm25** — keyword-based sparse retrieval
- **NetworkX** — in-memory knowledge graph
- **cachetools** — TTL-based semantic response caching
- **Loguru** — structured logging
- **Tenacity** — retry logic for resilient API calls

**Frontend**
- **React + Vite** — fast, modern SPA
- **Axios** — API communication

---

## ⚙️ Installation

### Prerequisites
- Python 3.11+
- Node.js 18+
- A [Groq API key](https://console.groq.com)

### 1. Clone the repository

```bash
git clone https://github.com/<your-username>/ET-AI-Hackathon-2026.git
cd ET-AI-Hackathon-2026
```

### 2. Backend setup

```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

pip install -r requirements.txt
```

Create a `.env` file inside `backend/`:

```env
GROQ_API_KEY=your_groq_api_key_here
CHROMA_PERSIST_DIR=./chroma_data
```

Start the backend:

```bash
python -m uvicorn app.main:app --reload
```

Backend runs at → `http://127.0.0.1:8000`
Interactive API docs → `http://127.0.0.1:8000/docs`

### 3. Frontend setup

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at → `http://localhost:5173`

---

## 📘 Usage

1. **Upload a document** — drag in a PDF (manual, safety report, inspection sheet, etc.) via the Documents tab.
2. **Choose your role** — Technician, Engineer, or Manager — to shape how detailed the answer should be.
3. **Ask a question** — type naturally, e.g. *"What safety procedures are outlined for Pump P-101?"*
4. **Review the answer** — every response includes:
   - The agent that handled it (Hybrid RAG / Graph RAG / Compliance)
   - A confidence score (HIGH / MEDIUM / LOW)
   - Full source citations with document name and page number
   - Whether it was served fresh or from cache
5. **Check Analytics** — see total queries, average response time, cache efficiency, and knowledge graph size in real time.

---

## 🔌 API Reference

| Endpoint | Method | Description |
|---|---|---|
| `/api/documents/upload` | `POST` | Upload and ingest a document |
| `/api/documents/{doc_id}/status` | `GET` | Check ingestion status |
| `/api/chat/query` | `POST` | Ask a question, routed through the multi-agent system |
| `/api/chat/history` | `GET` | Retrieve recent query history |
| `/api/graph/stats` | `GET` | Knowledge graph entity/relationship counts |
| `/api/graph/entities` | `GET` | List extracted entities |
| `/api/graph/neighbors` | `POST` | Get graph relationships for an entity |
| `/api/analytics/dashboard` | `GET` | Full system analytics summary |

Full interactive documentation available at `/docs` once the backend is running.

---

## 📁 Project Structure

```
ET-AI-Hackathon-2026/
├── backend/
│   ├── app/
│   │   ├── agents/            # Intent classifier + orchestrator
│   │   ├── api/routes/        # FastAPI route definitions
│   │   ├── pipeline/          # Parsing, chunking, embedding, ingestion
│   │   ├── services/          # BM25, retrieval, LLM, graph, cache services
│   │   ├── config.py
│   │   └── main.py
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── App.css
│   │   └── api.js
│   └── package.json
└── README.md
```

---

## 🗺️ Roadmap

- [ ] Persistent graph storage in a dedicated graph database (Neo4j)
- [ ] Multi-document cross-referencing at scale
- [ ] Voice query support
- [ ] Exportable audit trail for compliance reporting
- [ ] Fine-tuned domain-specific embedding model

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m "Add amazing feature"`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Please open an issue first for major changes so we can discuss what you'd like to add.

---


## Acknowledgements

- [Groq](https://groq.com) for blazing-fast LLM inference
- [ChromaDB](https://www.trychroma.com) for vector storage
- [Sentence-Transformers](https://www.sbert.net) for embeddings
- Built with ❤️ for **ET AI Hackathon 2026**

---

<p align="center">
  <i>⚠️ Known limitation: entity extraction is capped at 30 chunks per document for demo performance. Remove this cap in production for full-document graph coverage.</i>
</p>
