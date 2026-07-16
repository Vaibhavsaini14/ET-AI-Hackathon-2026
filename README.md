# NEXUS — Industrial Knowledge Intelligence Platform

> ET AI Hackathon 2.0 | Problem Statement 8 | Industrial Intelligence

[![Python](https://img.shields.io/badge/Python-3.11-blue)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-green)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-blue)](https://react.dev)
[![Groq](https://img.shields.io/badge/LLM-Groq%20Llama%203.3-orange)](https://groq.com)

---

## The Problem

India's heavy industrial facilities — steel plants, oil refineries, power stations, chemical plants — operate across 7 to 12 disconnected document systems. A maintenance engineer facing equipment failure at 2 AM must cross-reference OEM manuals, historical work orders, inspection records, and safety procedures across multiple software systems — often finding nothing because search is keyword-only and the answer lives inside a scanned PDF from 2009.

According to a 2024 McKinsey survey, professionals in asset-intensive industries spend **35% of their working hours** searching for information they already have. A NASSCOM-EY study found that this fragmentation contributes to **18–22% of unplanned downtime** in Indian heavy industry.

Worse — an estimated **25% of India's experienced industrial engineers will retire within the next decade**, taking decades of undocumented operational knowledge with them. Once gone, it cannot be recovered.

---

## The Solution — NEXUS

NEXUS is an AI-powered Industrial Knowledge Intelligence platform that ingests heterogeneous industrial documents — maintenance manuals, safety procedures, inspection reports, regulatory standards — and makes their collective knowledge queryable through natural language, with full source citations, a visual knowledge graph, and automated compliance auditing.

**Before NEXUS:** 45 minutes to find an answer across 7 systems.
**After NEXUS:** 8 seconds with cited sources.

---

## Key Features

### Expert Knowledge Copilot
Ask any question about your plant in plain English. NEXUS retrieves the most relevant sections from across all your documents using hybrid search

---

## Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| LLM | Groq LLaMA 3.3 70B | Answer generation (free) |
| Embeddings | all-MiniLM-L6-v2 | Semantic vectorisation (free, local) |
| Vector DB | ChromaDB | Semantic search storage |
| Keyword Search | BM25 (rank-bm25) | Keyword-based retrieval |
| Knowledge Graph | NetworkX + D3.js | Entity relationship mapping |
| Agent Framework | LangGraph | Multi-agent orchestration |
| Backend | FastAPI + Python 3.11 | REST API server |
| Database | PostgreSQL | Document metadata |
| Cache | Redis | Response caching |
| Frontend | React 18 + TypeScript | User interface |
| Styling | Tailwind CSS | Design system |
| Visualization | D3.js + Recharts | Graph and charts |
| Document Parsing | PyMuPDF + Tesseract | PDF and OCR processing |

---

