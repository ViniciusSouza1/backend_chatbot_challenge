# 📘 Eloquent RAG Chat API

**Eloquent RAG Chat API** is a production-ready **FastAPI** application that integrates **Pinecone vector search** and **SQLite persistence** to build a **Retrieval-Augmented Generation (RAG)** chatbot with full user/session/message history management.

It supports both **guest sessions** (no login required) and **registered users**, while maintaining structured chat history and embeddings for FAQ retrieval.

---

## 🧩 Tech Stack

- **Python 3.11+**
- **FastAPI** — high-performance REST framework  
- **SQLAlchemy ORM** — SQLite database layer  
- **Pinecone** — vector similarity search for FAQ retrieval  
- **dotenv** — environment configuration  
- **Pydantic** — request/response validation  
- **Uvicorn** — ASGI server for production and development  
- **Gunicorn** — optional for multi-worker deployment  
- **JWT Authentication** — user sessions and authorization  
- **Docker-ready** — easy deployment in production

---

## ⚙️ Environment Setup

### 1️⃣ Create and activate a virtual environment
```bash
python -m venv .venv
source .venv/bin/activate     # Linux/macOS
# or
.venv\Scripts\activate        # Windows PowerShell
```

### 2️⃣ Install dependencies
```bash
pip install -r requirements.txt
```

### 3️⃣ Create your `.env` file in the project root

```env
# === API ===
API_NAME=Eloquent RAG Chat API
API_CORS_ORIGINS=http://localhost:3000

# === Database ===
DATABASE_URL=sqlite:///./data/app.db
DATABASE_ECHO=false

# === Pinecone ===
PINECONE_API_KEY=<api_key_here>
PINECONE_HOST=<pinecone_host_here>
PINECONE_EMBED_MODEL=llama-text-embed-v2
PINECONE_TOP_K=3
PINECONE_NAMESPACE=default
PINECONE_INDEX_DIM=1536

# === Logging & Debug ===
LOG_LEVEL=DEBUG
DEBUG_RAW_MATCHES=true

# === RAG Parameters ===
RAG_CONFIDENCE_THRESHOLD=0.25

# === Auth ===
JWT_SECRET=super_secret_key
JWT_ALGORITHM=HS256
JWT_EXP_MINUTES=60
ADMIN_EMAILS=admin@example.com
```

> ⚠️ `.env` contains sensitive credentials — it’s ignored by `.gitignore`.

---

## 🚀 Running the API

### Development mode
```bash
uvicorn app.main:app --reload --app-dir src
```
Then visit: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### Production (example)
```bash
gunicorn app.main:app -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 --workers 4
```

---

## 🐳 Docker Deployment (Production)

A lightweight Dockerfile is included for production builds:

```dockerfile
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \\
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \\
    build-essential libffi-dev libssl-dev curl \\
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Build & Run

```bash
docker build -t eloquent-chat-api .
docker run -d -p 8000:8000 --env-file .env eloquent-chat-api
```

---

## 🔐 Authentication & Authorization

The API supports **JWT-based authentication** for registered users while maintaining **guest access** for unauthenticated sessions.

### Auth Flow

| Endpoint | Method | Auth | Description |
|-----------|---------|------|-------------|
| `/api/auth/register` | POST | ❌ | Create a new user |
| `/api/auth/login` | POST | ❌ | Obtain JWT token |
| `/api/auth/me` | GET | ✅ | Return the authenticated user's info |

**JWT Example:**
```http
Authorization: Bearer <access_token>
```

### Admin Access
Set `ADMIN_EMAILS` in `.env` to define privileged accounts:
```
ADMIN_EMAILS=admin@example.com,burce@eloquent.ai
```

Admins can:
- List all users (`/api/users`)
- Access debug endpoints
- Manage all sessions and messages

---

## 💬 Chat with RAG + Database Persistence

Once the FAQ data is loaded, you can chat via `/api/chat`.  
Every conversation is tied to a **session**, which can belong to a **user** or be **guest (no user)**.

Example:
```bash
curl -X POST http://127.0.0.1:8000/api/chat   -H "Content-Type: application/json"   -d '{
        "sessionId": "SESSION-UUID-HERE",
        "message": "How do I create an account?"
      }'
```

Response:
```json
{
  "sessionId": "SESSION-UUID-HERE",
  "messages": [
    {"role": "user", "content": "How do I create an account?"},
    {"role": "assistant", "content": "Here are the most relevant answers found in the FAQ..."}
  ]
}
```

> 💾 Both the user’s question and the assistant’s answer are saved in the `messages` table.

---

## 🧑‍💻 Users, Sessions, and Messages

The application includes **persistent storage** for users and chat sessions, supporting both **guest** and **registered** usage.

### **Users**
| Method | Endpoint | Description |
|---------|-----------|-------------|
| `GET` | `/api/users` | List all users (Admin only) |
| `POST` | `/api/users` | Create a new user |

---

### **Sessions**
| Method | Endpoint | Auth | Description |
|---------|-----------|------|-------------|
| `GET` | `/api/sessions` | ✅ (Admin) | List all sessions |
| `GET` | `/api/sessions/by-user/{user_id}` | ✅ (Self/Admin) | List sessions by user |
| `POST` | `/api/sessions` | ✅/❌ | Create session (guest or user) |
| `POST` | `/api/sessions/claim` | ✅ | Link guest sessions to a logged-in user |

#### Example: Create Guest Session
```bash
curl -X POST http://127.0.0.1:8000/api/sessions   -H "Content-Type: application/json"   -d '{"title": "Guest chat"}'
```

#### Example: Claim Sessions after Login
```bash
curl -X POST http://127.0.0.1:8000/api/sessions/claim   -H "Authorization: Bearer <token>"   -H "Content-Type: application/json"   -d '{"sessionIds": ["sess_123", "sess_456"]}'
```

---

### **Messages**
| Method | Endpoint | Auth | Description |
|---------|-----------|------|-------------|
| `GET` | `/api/messages` | ✅ (Admin) | List all messages |
| `GET` | `/api/messages/by-session/{session_id}` | ✅/❌ | Guest allowed if session is anonymous |
| `POST` | `/api/messages` | ✅/❌ | Guest allowed if session is anonymous |

---

### **Chat API**
| Method | Endpoint | Auth | Description |
|---------|-----------|------|-------------|
| `POST` | `/api/chat` | ✅/❌ | Send message (guest or authenticated) |
| `GET` | `/api/history` | ✅/❌ | Retrieve session chat history |

---

## 🧠 FAQ Vector Ingestion (Pinecone Seed)

Before using `/api/chat`, ingest FAQ data into Pinecone:

```bash
curl -X POST "http://127.0.0.1:8000/api/ingest/faq"
```

---

## 🧠 RAG Confidence Threshold

The environment variable `RAG_CONFIDENCE_THRESHOLD` controls the minimum similarity score for returning answers from Pinecone.

| Threshold | Behavior |
|------------|-----------|
| `0.25` (default) | Balanced precision/recall |
| `0.15` | More permissive, can include weak matches |
| `0.35+` | More strict, filters vague answers |

---

## 🔍 Debug & Maintenance Endpoints

| Endpoint | Method | Purpose | Access |
|-----------|---------|---------|--------|
| `/debug/stats` | `GET` | View Pinecone stats | Admin |
| `/debug/pinecone` | `GET` | Run manual vector query | Admin |
| `/debug/pinecone-raw` | `GET` | Inspect raw Pinecone response | Admin |
| `/debug/pinecone-smoke` | `POST` | Test index connection | Admin |
| `/api/ingest/faq` | `POST` | Load FAQ dataset | Admin |

---

## 🧾 Database Schema

**SQLite Tables:**
- `users` → `id`, `email`, `password`
- `sessions` → `id`, `user_id (nullable)`, `title`
- `messages` → `id`, `session_id`, `role`, `content`

Each `Session` belongs to a `User` (optional), and contains multiple `Message` entries.

---

## 🩺 Health Check

You can check service status using:
```bash
curl http://localhost:8000/health
```

---

## 🏭 Production Readiness Checklist

| Area | Description | Status |
|------|--------------|--------|
| JWT Auth | Implemented (guest + user) | ✅ |
| Guest Sessions | Allowed (no user_id required) | ✅ |
| Session Claim | Update guest sessions after signup | ✅ |
| Pinecone | Integrated via environment variables | ✅ |
| Database | SQLite with ORM | ✅ |
| Logging | Configurable verbosity | ✅ |
| Docker | Lightweight slim image | ✅ |
| Docs | Swagger at `/docs` | ✅ |

---

## 📜 License

This project is part of the **Eloquent AI Technical Assignment** and is intended for technical demonstration, educational, and evaluation purposes.
