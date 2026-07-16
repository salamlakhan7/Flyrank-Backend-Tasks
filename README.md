# Flyrank Backend & AI Engineer Tasks

Assignments completed for the FlyRank AI **Backend and AI Engineer**
internship (July 2026 cohort). Each folder is one assignment,
self-contained with its own code, README, and proof screenshots.

## About the internship

FlyRank AI is a US-based, remote internship built around a dual focus:
solid backend engineering fundamentals paired with practical AI
integration. Rather than treating these as separate tracks, the program
builds up a single small service week over week — starting from the
smallest possible HTTP server and progressively adding real
infrastructure (persistence, containerization, caching) alongside AI-
specific concerns (model integration, prompt-driven features, RAG-style
pipelines) as the weeks progress. The recurring theme across
assignments is architecture that survives change: swapping an
implementation detail — a storage backend, a model provider, a
deployment target — should never require touching the service or route
layer.

## Assignments

| Code | Title | Focus |
|------|-------|-------|
| [BE-01](./BE-01) | Build your first API endpoint | Smallest possible backend — two JSON endpoints, tested via curl and browser |
| [BE-04](./BE-04) | Containerize your stack | Postgres in Docker, repository pattern swapping in-memory storage for a real database, persistence proven across restarts |

*(Table updated as each new assignment — backend or AI-focused — is completed.)*

## Conventions used across all assignments

- One folder per assignment (`BE-01`, `BE-04`, ...), each with its own
  `README.md`, `requirements.txt`, and a `Screenshots/` folder as proof
  of working code.
- `.env` is always gitignored; a committed `.env.example` documents the
  required variables (API keys, connection strings, model names)
  without exposing secrets.
- `__pycache__/`, virtual environments, and other local build artifacts
  are excluded via the root `.gitignore` — never committed.
- Each assignment's README documents what was built, how to run it, and
  includes screenshot evidence of it actually working — not just code
  that looks correct.

## Tech stack across these tasks

**Backend:** Python, FastAPI, Uvicorn, PostgreSQL, Docker, Docker
Compose, Git/GitHub.

**AI integration (as later assignments introduce it):** LLM APIs (Groq,
Gemini), prompt engineering, RAG pipelines, vector stores (ChromaDB),
embeddings (Sentence Transformers / HuggingFace).

The same repository-pattern discipline used for swapping storage
backends (see BE-04) applies equally to swapping model providers —
routes and service logic shouldn't need to know which LLM is answering
a request, only that something implements the expected interface.

## Notes

- BE-04 was tested on GitHub Codespaces rather than a local machine,
  since Play with Docker was deprecated as of March 2026. Codespaces
  gives the same real Docker environment in the browser with no local
  install required.
- BE-04's repository layer includes both an `InMemoryRepository` (the
  original storage) and a `PostgresRepository` (the required backend),
  both implementing the same interface — this makes the architecture
  claim ("switching storage only changes one file") verifiable by
  reading the code, not just asserted in the README.
