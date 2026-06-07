# BoG Assist — Cloud Edition

RAG chatbot for Board of Governors meeting documents.
**Document storage → AWS S3 | Metadata → PostgreSQL | Vectors → Qdrant**

---

## Architecture

```
User → Frontend (React/Vite)
          ↓
     FastAPI (api.py)
     ├── Query → Qdrant (vector search) → Groq LLM → Answer
     └── Upload → S3 (raw PDF) + Qdrant (embeddings) + PostgreSQL (metadata)
```

---

## Prerequisites

| Service | Notes |
|---------|-------|
| **AWS S3** | Create a bucket; IAM user with `s3:GetObject`, `s3:PutObject`, `s3:DeleteObject`, `s3:ListBucket` |
| **PostgreSQL** | AWS RDS, Supabase, Railway, Neon, or local Docker |
| **Qdrant** | Qdrant Cloud (free tier works) or self-hosted |
| **Groq** | Free API key at console.groq.com |

---

## 1 — Environment Setup

```bash
cp Backend/.env.example Backend/.env
```

Fill in `Backend/.env`:

```env
# LLM
GROQ_API_KEY=gsk_...

# AWS S3
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...
AWS_REGION=ap-south-1          # change to your bucket region
S3_BUCKET_NAME=your-bucket

# PostgreSQL
POSTGRES_HOST=your-db-host
POSTGRES_PORT=5432
POSTGRES_DB=bog_assist
POSTGRES_USER=your-user
POSTGRES_PASSWORD=your-password

# Qdrant
QDRANT_URL=https://your-cluster.qdrant.io
QDRANT_API_KEY=your-qdrant-key
QDRANT_COLLECTION=bog_documents
```

---

## 2 — First-time: Embed existing PDFs

If you already have PDFs locally, upload them to S3 first:

```bash
# Install AWS CLI, then:
aws s3 cp /path/to/pdfs/ s3://your-bucket/pdfs/ --recursive --exclude "*" --include "*.pdf"
```

Then run the embedding pipeline:

```bash
cd Backend
pip install -r requirements.txt
python create_vector_embedding.py
```

This will:
1. List all PDFs in S3 under `pdfs/`
2. Skip already-processed ones (tracked in PostgreSQL)
3. OCR each PDF, embed chunks, upsert to Qdrant, store metadata in PostgreSQL

---

## 3 — Run Locally

### Option A — Docker Compose (recommended)

```bash
docker-compose up --build
```

> The `postgres` service in `docker-compose.yml` is for local dev.
> In production, point `POSTGRES_HOST` to your managed DB and remove that service.

### Option B — Manual

```bash
cd Backend
pip install -r requirements.txt
uvicorn api:app --reload --port 8000
```

Frontend:

```bash
cd Frontend
npm install
npm run dev
```

---

## 4 — API Reference

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/query` | RAG query — `{"query": "...", "top_k": 10}` |
| `POST` | `/documents` | Upload a PDF (multipart/form-data, field: `file`) |
| `GET`  | `/documents` | List all processed documents |
| `DELETE` | `/documents/{id}` | Delete document + its vectors |
| `GET`  | `/health` | Health check + Qdrant stats |

---

## 5 — Deploying to Production

### Backend — AWS EC2 / ECS / Railway / Render

```bash
# EC2 example
docker build -t bog-assist ./Backend
docker run -d --env-file Backend/.env -p 8000:8000 bog-assist
```

### Frontend — Vercel / Netlify

1. Set `VITE_API_URL=https://your-backend-url` in your hosting env vars  
   (or update the base URL in `Frontend/src/helpers/api-communicator.ts`)
2. `npm run build` → deploy `dist/`

---

## 6 — File Structure

```
BoG-assist-cloud/
├── Backend/
│   ├── api.py                    # FastAPI routes
│   ├── rag_query_handler.py      # RAG logic (Qdrant + Groq)
│   ├── create_vector_embedding.py# Offline embedding pipeline
│   ├── qdrant_store.py           # Qdrant helpers
│   ├── s3_storage.py             # AWS S3 helpers
│   ├── db.py                     # PostgreSQL helpers
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── Frontend/                     # React/Vite (unchanged)
└── docker-compose.yml
```

---

## 7 — Adding New Documents

**Via API (recommended for production):**

```bash
curl -X POST https://your-api/documents \
  -F "file=@/path/to/meeting.pdf"
```

**Via script (bulk):**

```bash
# Upload to S3 first, then:
python Backend/create_vector_embedding.py
```

---

## Notes

- The embedding pipeline is **incremental** — already-processed files are skipped.
- Deleting a document via `DELETE /documents/{id}` removes the PDF from PostgreSQL metadata and vectors from Qdrant. The S3 file is **not** deleted automatically (to preserve originals); call `s3_storage.delete_file(filename)` manually if needed.
- Qdrant free tier has a 1GB limit (~500k 384-dim vectors); well within range for typical BoG document sets.
