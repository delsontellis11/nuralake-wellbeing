# Well Beings — AI WhatsApp Agent

An end-to-end AI agent for Well Beings spa in Dubai Marina. Handles WhatsApp enquiries 24/7, captures leads, and displays them on a mobile dashboard.

## Live URLs
- **Backend API:** https://wellbeing-agent.onrender.com
- **Mobile App:** Run locally via Expo Go (see below)
- **GitHub:** https://github.com/delsontellis11/nuralake-wellbeing

## Architecture

WhatsApp → FastAPI Webhook → LangGraph Agent → RAG / Web Search / Lead Capture → Supabase → Expo Mobile App

## Stack & Justification

| Component | Choice | Why |
|---|---|---|
| LLM | Mistral via Ollama (local) | Free, no API costs, good tool calling |
| Agent framework | LangGraph | Required; stateful multi-turn conversations |
| Vector store | ChromaDB | Simple, no extra service needed, runs in-process |
| Embeddings | sentence-transformers (all-MiniLM-L6-v2) | Free, runs locally, good semantic search |
| Web search | Tavily | Clean API, free tier, best results |
| Database | Supabase (Postgres) | Free tier, real-time, simple Python SDK |
| Backend | FastAPI + Uvicorn | Fast, async, easy webhook handling |
| Deployment | Render | Free tier, auto-deploy from GitHub |
| Mobile | Expo (React Native) | Required; works on iOS and Android |

## Agent Tools

1. **search_spa_knowledge** — RAG tool that queries ChromaDB vector store for Well Beings services, pricing, FAQs, location, and hours
2. **search_internet** — Tavily web search for real-time queries (weather, transport, nearby places)
3. **capture_lead** — Saves lead to Supabase with deduplication on phone number

## RAG Pipeline

- Knowledge base: 3 markdown files (services, FAQs, location/hours)
- Chunked with RecursiveCharacterTextSplitter (500 tokens, 50 overlap)
- Embedded with sentence-transformers all-MiniLM-L6-v2
- Stored in ChromaDB with cosine similarity search
- Top-3 chunks retrieved per query

## Lead Capture & Deduplication

Leads stored in Supabase `leads` table with `phone` as unique key. Upsert strategy: same phone number updates existing record instead of creating duplicates.

## WhatsApp Integration

WhatsApp Cloud API (Meta) integrated via FastAPI webhook at `/webhook`. Webhook verification and message processing implemented. Note: Phone number verification pending due to Meta OTP delivery issues during development — all code is complete and ready.

## Mobile App

Expo React Native app with two screens:
- **Leads list** — shows all captured leads, refreshes every 10 seconds
- **Lead detail** — full details for each lead

## Local Setup

### Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
python rag/ingest.py   # Build vector store once
uvicorn main:app --reload --port 8000
```

### Mobile
```bash
cd mobile
npm install
npx expo start --web
```

### Environment Variables
Copy `.env.example` to `.env` and fill in your keys.

## Trade-offs & Known Limitations

- Mistral (local) is used instead of a cloud LLM to avoid API costs — works well for tool calling
- ChromaDB is not persisted on Render free tier (stateless) — for production, use a hosted vector DB like Pinecone
- Render free tier spins down after inactivity — first request takes ~50 seconds to wake up
- WhatsApp phone verification blocked by Meta during development — webhook code is complete