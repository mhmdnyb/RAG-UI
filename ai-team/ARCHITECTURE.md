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
    content: str  # The retrieved text
    source: str  # Document name or "sql_query"
    page: int | None = None  # Page number (if applicable)
    score: float = 0.0  # Relevance score
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

### 4. Composition Root

`app/composition.py` is the **single composition root** — the only place
where concrete implementations are imported and wired together. The API
(`app/server.py`) and the worker (`app/worker/tasks.py`) both build from it,
so they cannot drift apart.

```python
@lru_cache(maxsize=1)
def build_orchestrator() -> QueryOrchestrator:
    embedder = EmbeddingService()
    return QueryOrchestrator(
        retrievers={
            "sql": SQLRetriever(engine=get_engine()),
            "text": TextRetriever(embedder=embedder),
        },
        router=QueryRouter(),
        reranker=Reranker(),
        llm=LLMService(),
    )
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
| Dev 5 | Embedding Service | `app/embedding/` | `BaseEmbeddingService` — LlamaIndex adapter |
| Dev 6 | Chat History | `app/history/` | `BaseChatHistory` — **not wired yet, see below** |
| Dev 7 | Web Service (API) | `app/api/` | FastAPI routes |

**Shared code** (`common/`, `orchestrator/`, `composition.py`, `server.py`,
`api/schemas.py`, `worker/`) requires team lead review for changes.

### Embedding — how it is wired

`EmbeddingService` is an adapter around a **local LlamaIndex embedding
model**. The plumbing is already done: lazy one-per-process loading,
inference offloaded to a thread behind a semaphore, `warm_up()` at worker
startup (a worker whose model fails to load refuses to start), and
`get_model()` for LlamaIndex code. Pass the model explicitly —
`VectorStoreIndex(..., embed_model=await embedder.get_model())` — and do
not set the global `llama_index.core.Settings.embed_model`.

Dev 5 only fills in `_build_model()` (model choice and options) and the
two `*_sync` bodies (any prefix the chosen model requires).

`embed()` vs `embed_query()`: asymmetric models (e5, bge) need a different
prefix for queries than for documents, so retrieval code must call
`embed_query()`.

The same instance is injected into `TextRetriever` from `composition.py` —
one model per process, never one per module.

### Chat history — current status

The service is **stateless today**: `QueryOrchestrator` does not read or
write conversation history, and `ChatHistoryService` is not wired into
`composition.py`. The slot is deliberately kept in place
(`QueryOrchestrator(history=...)` and `BaseLLMService.generate(history=...)`)
so history can be plugged in later without changing shared signatures.

The open design question is where history comes from:

1. **Core Service sends it with the question** — the RAG service stays
   stateless and `app/history/` disappears. Simplest, preferred.
2. **The RAG service reads it from the database** — a second source of
   truth that has to stay in sync with Core.

Do not build on `app/history/` until this is decided.

---

## Shared Infrastructure (`common/`)

### Configuration (`common/config.py`)

> Values loaded from `.env` live only on the `settings` object. They are
> **not** pushed into `os.environ`, so `os.environ["DATABASE_URL"]` will
> raise even when the variable is present in `.env`.

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

### Step 4: The team lead wires it in `composition.py`

Once your module is ready, it gets registered in `build_orchestrator()` in `composition.py`.

---

## Running the Service

Always run from the `ai-team/` directory.

```bash
make install          # dependencies
cp .env.example .env  # then fill in the values
make infra            # Postgres + Redis
make dev              # API on :8000   (uvicorn --factory app.server:create_app)
make worker           # second terminal: TaskIQ worker
```

Set `USE_QUEUE=false` in `.env` to run jobs inside the API process and
skip Redis entirely. That mode loses jobs on restart — development only.

---

## Job Execution

A question is never processed inside the HTTP request. `/rag/query` ACKs
immediately and hands the work to `app/api/jobs.py`, which enqueues it on
a TaskIQ broker backed by Redis Streams.

```
POST /rag/query ──► ACK {"status":"OK"}   (~2 ms)
        │
        └─► Redis Stream ──► TaskIQ worker ──► QueryOrchestrator ──► POST /rag/callback
```

Why TaskIQ and not Celery:

- **The queue is async-native.** A RAG query spends ~95% of its wall time
  waiting on the network (vector store, LLM API). One asyncio worker keeps
  hundreds of those waits in flight; Celery's prefork pool would reserve a
  whole OS process — and a whole copy of the local embedding model — per
  in-flight question.
- **Jobs survive a restart.** Redis Streams consumer groups only drop a
  message once it is acknowledged, so a job whose worker died is
  re-delivered to another worker.
- **The callback is its own task.** `process_query_task` runs the pipeline
  and enqueues `deliver_callback_task`. Callback retries (exponential
  backoff inside `send_callback`) never re-run retrieval or the LLM, and a
  worker that dies after the LLM answered does not lose the answer.
- **Redelivery timeout is derived, not guessed.** `idle_timeout` is the
  slowest task (pipeline timeout, or the callback's worst case) plus a
  margin — see `Settings.job_idle_timeout_seconds`. Change a timeout and it
  follows.
- **Concurrency is a dial:** `MAX_CONCURRENT_JOBS` (used by both
  `--max-async-tasks` and the in-process broker). Size it to the LLM
  provider's quota, not to the embedding semaphore.

### Where CPU work belongs

The embedding model and the reranker are CPU/GPU-bound and must never run
directly on the worker's event loop. Today `EmbeddingService` offloads
inference with `asyncio.to_thread` behind a semaphore, which works because
torch/ONNX release the GIL inside their native kernels.

At real scale, move the models behind a dedicated inference service (TEI,
vLLM, ...). The worker then becomes purely I/O-bound, one copy of each
model serves every worker, and the inference server can batch concurrent
requests. Workers and GPUs scale independently.

Every accepted question results in a `POST /rag/callback`, success or
failure. Delivery is **at-least-once**, not exactly-once: a redelivered
message can produce a second callback, so Core should deduplicate. Doing
that reliably needs a `requestId` in the contract (open item with the Core
team).

"Nothing found" and "the search failed" are different answers: if no
results came back and any retriever failed or timed out, the pipeline
raises and the user gets the error message, not `NO_RESULTS_FOUND`.

---

## Shared Files You Should Know

| File | What it gives you |
|---|---|
| `app/common/interfaces.py` | the contracts — do not change alone |
| `app/common/fakes.py` | fake implementation of every interface, for local testing |
| `app/common/constants.py` | user-facing strings (error / no-results) |
| `app/common/context.py` | request id, automatically added to every log line |
| `app/composition.py` | the only place concrete classes are imported |
| `app/worker/broker.py` | queue configuration (Redis Streams / in-memory) |
| `tests/test_interfaces_contract.py` | add your class here when your module is ready |

---

## Git Workflow

1. **Work on your own branch:** `feature/<module-name>` (e.g., `feature/reranker`)
2. **Only modify files in your directory.** Never modify another developer's module.
3. **Changes to `common/interfaces.py` require approval from all team members.**
4. **Changes to `composition.py` and `orchestrator/` require team lead review.**
5. **PR to `develop` branch for integration testing** before merging to `main`.

---

## Important Rules

> ⚠️ **NEVER modify `common/interfaces.py` without team-wide review.**
> This file is the contract between all modules. Breaking it breaks everyone.

> ⚠️ **NEVER import another developer's concrete class in your module.**
> Only import from `common/` (interfaces, config, logger, exceptions).
> The only file that imports concrete classes is `composition.py`.

> ⚠️ **ALWAYS use `common/config.settings` for configuration.**
> Do not use `os.environ` directly.

> ⚠️ **ALWAYS use `common/logger.get_logger()` for logging.**
> Do not use `print()` or create your own logger.

> ⚠️ **ALWAYS raise exceptions from `common/exceptions`.**
> Do not create module-specific exception classes outside the shared hierarchy.

> ⚠️ **NEVER call blocking code directly inside `async def`.**
> Models, `requests`, llama-index and friends must run through
> `await asyncio.to_thread(...)`. One blocking call freezes every
> concurrent request in that process.

> ⚠️ **ALWAYS use absolute imports rooted at `app.`**
> `from app.common.interfaces import BaseRetriever` — never `from common...`.
> Run every command from the `ai-team/` directory.

> ⚠️ **NEVER add or rename a field in `api/schemas.py` on your own.**
> That file is the wire contract with the Java Core Service. Jackson
> rejects unknown properties by default, so an extra field breaks them.
