# 🎓 University Assistant

> A modern, conversational AI assistant for the **University of Science and Culture (USC)**. Powered by a high-precision RAG pipeline delivering cited, real-time answers for academic regulations, course schedules, and university procedures.

<p align="left">
  <img src="https://img.shields.io/badge/React_19-20232A?style=flat-square&logo=react&logoColor=61DAFB" alt="React 19" />
  <img src="https://img.shields.io/badge/Vite_8-646CFF?style=flat-square&logo=vite&logoColor=white" alt="Vite 8" />
  <img src="https://img.shields.io/badge/Tailwind_v4-38B2AC?style=flat-square&logo=tailwind-css&logoColor=white" alt="Tailwind CSS" />
  <img src="https://img.shields.io/badge/Spring_Boot_3-6DB33F?style=flat-square&logo=springboot&logoColor=white" alt="Spring Boot" />
  <img src="https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white" alt="FastAPI" />
  <img src="https://img.shields.io/badge/pgvector-336791?style=flat-square&logo=postgresql&logoColor=white" alt="pgvector" />
  <img src="https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white" alt="Docker" />
</p>

---

## 🏛 Architecture Overview

```mermaid
graph LR
    User([👤 Student / User]) <-->|HTTP / WS| UI["💻 React 19 Frontend\n(:80 / :5173)"]
    UI <-->|REST / JWT| Core["⚙️ Spring Boot Core\n(:8080)"]
    Core <-->|Task Queue| AI["🧠 RAG Engine\n(FastAPI :8000)"]
    AI <--> DB[("🗄️ PostgreSQL\n+ pgvector")]
```

---

## ✨ Key Features

- **Intuitive Interface:** Responsive dark-mode glassmorphic design, smooth message transitions, and active chat history.
- **Real-Time Streaming:** Live chat interaction powered by WebSocket connections and optimistic UI updates.
- **Smart Query Routing:** Intelligently directs inquiries between structured schedule data (SQL) and unstructured academic bylaws.
- **Precision RAG Pipeline:** Small-to-big parent document expansion paired with cross-encoder reranking (`bge-reranker-v2-m3`) for high-fidelity citations.
- **Async Resilience:** Non-blocking job processing via TaskIQ and Redis Streams with guaranteed webhook callback delivery.

---

## 🚀 Quickstart

### Option 1: Docker (Recommended)

Run the containerized application with a single command:

```bash
docker compose up -d --build
```

Access the UI at **[http://localhost](http://localhost)**.

---

### Option 2: Local Development

Run the frontend locally with Vite hot module replacement:

```bash
# 1. Navigate to the frontend directory
cd frontend

# 2. Install dependencies
npm install

# 3. Configure environment
cp .env.example .env

# 4. Start the development server
npm run dev
```

Access the app at **[http://localhost:5173](http://localhost:5173)**.

---

## ⚙️ Configuration

Set your environment variables in `frontend/.env`:

| Variable | Default Value | Description |
|---|---|---|
| `VITE_API_URL` | `http://localhost:8080` | Core Service backend REST API URL |
| `VITE_WS_URL` | `ws://localhost:8080/ws` | WebSocket endpoint for real-time messaging |

---

## 🛠 Tech Stack

| Layer | Technologies |
|---|---|
| **Frontend** | React 19, Vite 8, Tailwind CSS v4, React Router 8, React Hot Toast |
| **Core Service** | Spring Boot 3, Java 21, PostgreSQL 17, Spring Security (JWT), WebSockets |
| **AI & RAG** | Python 3.11, FastAPI, TaskIQ, Redis Streams, LlamaIndex, SQLAlchemy |
| **Models** | `BAAI/bge-m3` (Embeddings), `BAAI/bge-reranker-v2-m3` (Reranker), Gemini / GPT-4o |
| **Infrastructure** | Docker, Nginx, PostgreSQL (`pgvector`), Redis 7 |

---

## 📁 Repository Structure

```text
RAG-UI/
├── frontend/                # React 19 single-page application
│   ├── src/                 # Components, contexts, pages, and API clients
│   ├── Dockerfile           # Multi-stage production Nginx container
│   ├── nginx.conf           # SPA routing & WebSocket reverse proxy
│   └── package.json
├── docker-compose.yml       # Production deployment configuration
└── README.md                # Project documentation
```

---

<p align="center">
  Built with ❤️ for the students and faculty of the University of Science and Culture
</p>
