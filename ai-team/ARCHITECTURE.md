# AI-Team Architecture Guide

## Overview

This document describes the architecture and design patterns used in the RAG (Retrieval-Augmented Generation) service of the University Assistant project.

The architecture is designed for **7 developers working in parallel**, each owning an independent module. It uses a combination of design patterns to minimize merge conflicts and maximize developer independence.

---

## Design Patterns Used

### 1. Plugin-based Modular Architecture

Each functional concern (SQL retrieval, text retrieval, reranking, LLM, embedding, chat history, web API) lives in its own **self-contained Python package** under `app/`.

```
app/
├── common/              # Shared infrastructure (config, logging, DB, interfaces)
├── query_router/        # Module: Query routing (SQL vs Text classification)
├── retrieval/
│   ├── sql_pipeline/    # Module: SQL-based retrieval
│   ├── text_pipeline/   # Module: Text/vector-based retrieval
│   └── reranker/        # Module: Result reranking
├── llm/                 # Module: LLM interaction
├── embedding/           # Module: Embedding generation
├── history/             # Module: Chat history management
├── api/                 # Module: FastAPI web service
├── orchestrator/        # Pipeline: Wires all modules together
└── server.py            # App factory: Creates and configures the application
```

**Key rule:** Each developer works only inside their own package directory. This eliminates merge conflicts.

---

### 2. Strategy Pattern (via Abstract Base Classes)

All modules implement a **shared contract** defined as abstract base classes in `common/interfaces.py`. This allows:

- **Swappability:** Any implementation can be replaced without affecting other modules.
- **Independent development:** Developers code against the interface, not against each other's code.
- **Testability:** Mock implementations can be used for testing.

#### Interfaces

| Interface | Purpose | Owner |
|---|---|---|
| `BaseQueryRouter` | Classify queries to route to SQL or Text | Query Router Dev |
| `BaseRetriever` | Retrieve relevant content from a data source | Dev 1, Dev 2 |
| `BaseReranker` | Re-score and re-order retrieval results | Dev 3 |
| `BaseLLMService` | Generate answers from context | Dev 4 |
| `BaseEmbeddingService` | Convert text to vectors | Dev 5 |
| `BaseChatHistory` | Persist/retrieve conversation history | Dev 6 |

#### Shared Data Structure

All modules communicate using the `RetrievalResult` dataclass:

```python
@dataclass
class RetrievalResult:
    content: str                        # The retrieved text
    source: str                         # Document name or "sql_query"
    page: int | None = None             # Page number (if applicable)
    score: float = 0.0                  # Relevance score
    metadata: dict = field(default_factory=dict)
```

---

### 3. Dependency Injection (DI)

The `QueryOrchestrator` does NOT import concrete implementations. Instead, it receives all dependencies through its constructor:

```python
orchestrator = QueryOrchestrator(
    retrievers=[SQLRetriever(...), TextRetriever(...)],
    reranker=Reranker(...),
    llm=LLMService(...),
    history=ChatHistoryService(...),
)
```

**Benefits:**
- Modules don't know about each other — only the orchestrator knows.
- Easy to swap implementations (e.g., replace OpenAI with a local model).
- Easy to test (inject mock dependencies).

---

### 4. App Factory Pattern

The `create_app()` function in `main.py` is the **single composition root** — the only place where concrete implementations are imported and wired together.

```python
def create_app() -> FastAPI:
    orchestrator = QueryOrchestrator(
        retrievers=[SQLRetriever(), TextRetriever()],
        reranker=Reranker(),
        llm=LLMService(),
        history=ChatHistoryService(),
    )
    app = FastAPI()
    app.include_router(create_router(orchestrator))
    return app
```

---

## Pipeline Flow

```
User Question
     │
     ▼
┌─────────────┐
│  POST       │  ① Core Service sends question
│  /rag/query │     to RAG service
└─────┬───────┘
      │
      │  ACK {"status": "OK"}  → returned immediately
      │
      ▼ (Background Task)
┌─────────────────────────────────────────────────┐
│              QueryOrchestrator                  │
│                                                 │
│  ② Get chat history (BaseChatHistory)           │
│                    │                            │
│  ③ Retrieve from ALL retrievers in parallel     │
│     ┌──────────┐  ┌──────────────┐              │
│     │ SQL      │  │ Text/Vector  │              │
│     │ Retriever│  │ Retriever    │              │
│     └────┬─────┘  └──────┬───────┘              │
│          │               │                      │
│          └───────┬───────┘                      │
│                  ▼                              │
│  ④ Rerank combined results (BaseReranker)       │
│                  │                              │
│                  ▼                              │
│  ⑤ Generate answer (BaseLLMService)             │
│                  │                              │
│                  ▼                              │
│  ⑥ Save to history (BaseChatHistory)            │
│                  │                              │
└──────────────────┼──────────────────────────────┘
                   │
                   ▼
            ┌─────────────┐
            │  POST       │  ⑦ Send answer back
            │  /rag/      │     to Core Service
            │  callback   │
            └─────────────┘
```

---

## Module Ownership

| Developer | Module | Directory | Interface to Implement |
|---|---|---|---|
| Query Router | Query Routing | `app/query_router/` | `BaseQueryRouter` |
| Dev 1 | SQL Retrieval | `app/retrieval/sql_pipeline/` | `BaseRetriever` |
| Dev 2 | Text/Vector Retrieval | `app/retrieval/text_pipeline/` | `BaseRetriever` |
| Dev 3 | Reranker | `app/retrieval/reranker/` | `BaseReranker` |
| Dev 4 | LLM Interaction | `app/llm/` | `BaseLLMService` |
| Dev 5 | Embedding Service | `app/embedding/` | `BaseEmbeddingService` |
| Dev 6 | Chat History | `app/history/` | `BaseChatHistory` |
| Dev 7 | Web Service (API) | `app/api/` | FastAPI routes |

**Shared code** (`common/`, `orchestrator/`, `server.py`) requires team lead review for changes.

---

## Shared Infrastructure (`common/`)

### Configuration (`common/config.py`)

All environment variables are centralized in a Pydantic Settings class:

```python
from common.config import settings

# Access any config value
print(settings.database_url)
print(settings.llm_model)
```

**DO NOT** use `os.environ[...]` directly in your module. Always use `settings`.

### Logging (`common/logger.py`)

Each module gets a namespaced logger:

```python
from common.logger import get_logger

logger = get_logger("rag.sql_retriever")
logger.info("Processing query...")
logger.error("Something failed", exc_info=True)
```

Log output format:
```
[2026-09-23 01:30:00] INFO     [rag.sql_retriever] Processing query...
```

### Exceptions (`common/exceptions.py`)

Use the shared exception hierarchy in your module:

```python
from common.exceptions import RetrievalError

raise RetrievalError("SQL query execution failed")
```

Available exceptions:
- `RAGBaseError` — base for all RAG errors
- `RetrievalError` — retrieval pipeline failures
- `RerankingError` — reranker failures
- `LLMError` — LLM API failures
- `EmbeddingError` — embedding failures
- `ConfigurationError` — missing/invalid config
- `AuthenticationError` — API auth failures
- `CallbackError` — Core Service callback failures

### Database (`common/database.py`)

Shared SQLAlchemy engine:

```python
from common.database import get_engine, get_session

engine = get_engine()
session = get_session()
```

---

## How to Implement Your Module

### Step 1: Read the interface

Open `common/interfaces.py` and find the abstract class you need to implement.

### Step 2: Implement in your directory

Create your implementation class in your module directory. For example, Dev 3 (Reranker):

```python
# app/retrieval/reranker/reranker.py

from common.interfaces import BaseReranker, RetrievalResult
from common.logger import get_logger

class Reranker(BaseReranker):
    def __init__(self):
        self._logger = get_logger("rag.reranker")
        # Load your model here

    async def rerank(self, query, results, top_k=3):
        # Your implementation here
        ...
```

### Step 3: Test independently

You can test your module without depending on others:

```python
import asyncio
from retrieval.reranker.reranker import Reranker
from common.interfaces import RetrievalResult

async def test():
    reranker = Reranker()
    mock_results = [
        RetrievalResult(content="test", source="doc.pdf", score=0.5),
    ]
    ranked = await reranker.rerank("test query", mock_results)
    print(ranked)

asyncio.run(test())
```

### Step 4: The team lead wires it in `main.py`

Once your module is ready, it gets registered in `create_app()` in `main.py`.

---

## Running the Service

### Web server (default)
```bash
python app/main.py
```
Starts FastAPI on the configured port (default: 8000).

### Legacy script mode (original behavior)
```bash
python app/main.py --legacy
```
Runs the original SQL query script (unchanged).

### With Docker
```bash
docker-compose up
```

---

## Git Workflow

1. **Work on your own branch:** `feature/<module-name>` (e.g., `feature/reranker`)
2. **Only modify files in your directory.** Never modify another developer's module.
3. **Changes to `common/interfaces.py` require approval from all team members.**
4. **Changes to `main.py` and `orchestrator/` require team lead review.**
5. **PR to `develop` branch for integration testing** before merging to `main`.

---

## Important Rules

> ⚠️ **NEVER modify `common/interfaces.py` without team-wide review.**
> This file is the contract between all modules. Breaking it breaks everyone.

> ⚠️ **NEVER import another developer's concrete class in your module.**
> Only import from `common/` (interfaces, config, logger, exceptions).
> The only file that imports concrete classes is `main.py`.

> ⚠️ **ALWAYS use `common/config.settings` for configuration.**
> Do not use `os.environ` directly.

> ⚠️ **ALWAYS use `common/logger.get_logger()` for logging.**
> Do not use `print()` or create your own logger.

> ⚠️ **ALWAYS raise exceptions from `common/exceptions`.**
> Do not create module-specific exception classes outside the shared hierarchy.
