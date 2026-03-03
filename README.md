# Agentic Marketing

An intelligent agentic system that transforms product/project ideas into complete marketing assets—static websites and Instagram posts—using AI-powered research, design, and content generation.

## What It Does

1. **Research** your idea's market landscape, domain, novelty, and competition
2. **Design** a responsive static website from research insights and user preferences
3. **Generate** Instagram posts with AI-created images and engagement-optimized captions
4. **Publish** directly to Instagram with user consent (optional)

## Tech Stack

- **Backend**: Python FastAPI (async-first)
- **Frontend**: Next.js (TypeScript, App Router)
- **AI/GenAI**: Google Generative AI (Gemini + Imagen via Vertex AI)
- **Agent Framework**: Google ADK (ADK-native agent implementations)
- **Database**: MySQL with SQLAlchemy (async via AIOMySQL)
- **Hosting**: Google Cloud Storage (public bucket) + TinyURL

## Agents

| Agent | Purpose |
|-------|---------|
| **IdeaResearcherAgent** | Analyzes domain, identifies novelty, researches competitors |
| **WebpageDesignerAgent** | Creates Material Design static HTML; integrates user preferences |
| **WebpageReviewerAgent** | Iterative review loop (max 3 cycles), uploads to GCS, returns TinyURL |
| **InstagramTrendResearchAgent** | Researches social media trends, identifies influencers, analyzes captions |
| **InstagramPostAgent** | Generates AI images & captions with hashtags; supports secure posting |

## Execution Flow

```
IdeaResearcher 
    ↓
[WebpageDesigner ↔ WebpageReviewer] + [InstagramTrendResearcher] (parallel)
    ↓
InstagramPostAgent
```

## Project Structure

```
agentic_marketing/
├── backend/
│   ├── agents/          # ADK agent definitions
│   ├── tools/           # Custom tools & integrations
│   ├── routers/         # FastAPI route handlers
│   ├── models/          # SQLAlchemy ORM models
│   ├── schemas/         # Pydantic request/response schemas
│   ├── auth/            # JWT authentication
│   ├── config.py        # Configuration management
│   ├── database.py      # DB connection & session management
│   └── main.py          # FastAPI app entry point
├── frontend/
│   ├── app/             # Next.js App Router pages
│   └── components/      # Reusable React components
├── documentation/       # Project plans & specs
└── .claude/            # Agent specs & coding rules
```

## Getting Started

### Prerequisites

- Python 3.10+
- Node.js 18+
- MySQL 8.0+
- Google Cloud Project with Vertex AI API enabled
- Instagram API credentials (for posting feature)

### Backend Setup

```bash
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --reload
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

## Security & Best Practices

- ✅ Credentials never visible in plaintext; encrypted transmission + backend-side handling
- ✅ Consent-first posting: agent asks user confirmation before any Instagram action
- ✅ Async-first: all I/O-bound operations use `async`/`await`
- ✅ Token-efficient: research uses targeted queries (3–5 max), summarizes before chaining agents
