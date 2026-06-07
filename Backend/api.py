"""
api.py — FastAPI backend
────────────────────────
Routes:
  POST /query          — RAG query
  POST /documents      — Upload a PDF (stores in S3, embeds, saves metadata)
  GET  /documents      — List all uploaded documents
  DELETE /documents/{id} — Remove a document + its vectors
  GET  /health         — Health check
"""

import os
import re
import tempfile
import numpy as np
from dotenv import load_dotenv
load_dotenv()

import traceback
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from rag_query_handler import TextRAGHandler
import db
import s3_storage
import qdrant_store

from paddleocr import PaddleOCR
from sentence_transformers import SentenceTransformer
import fitz

app = FastAPI(title="BoG Assist API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── STARTUP ──────────────────────────────────────────────────────────────────

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
paddle_ocr  = None
embedder    = None
rag_handler = None


@app.on_event("startup")
async def startup():
    global paddle_ocr, embedder, rag_handler

    db.init_db()
    qdrant_store.ensure_collection()

    paddle_ocr = PaddleOCR(use_angle_cls=True, lang="en")
    embedder   = SentenceTransformer(EMBEDDING_MODEL)

    rag_handler = TextRAGHandler(groq_api_key=os.getenv("GROQ_API_KEY"))
    print("✅ API ready")


# ─── MODELS ───────────────────────────────────────────────────────────────────

class QueryRequest(BaseModel):
    query: str
    top_k: int = 10


# ─── HELPERS ──────────────────────────────────────────────────────────────────

def extract_meeting_no(filename: str):
    m = re.search(r"(\d{1,3})(?:st|nd|rd|th)", filename.lower())
    return m.group(1) if m else None


def clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def ocr_page(page: fitz.Page) -> str:
    pix = page.get_pixmap()
    img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(
        pix.height, pix.width, pix.n
    )
    try:
        result = paddle_ocr.ocr(img, cls=True)
        text = ""
        if result:
            for line in result:
                for word in line:
                    text += word[1][0] + " "
        return text
    except Exception:
        return ""


def process_and_embed(local_path: str, filename: str) -> tuple[list[dict], list[list[float]]]:
    """OCR a PDF and return (chunks, vectors)."""
    meeting_no = extract_meeting_no(filename)
    doc = fitz.open(local_path)
    chunks = []

    for page_num, page in enumerate(doc):
        text = ocr_page(page)
        if len(text.strip()) < 50:
            continue
        item_match = re.search(r"\d+\.\d+", text)
        item_no    = item_match.group() if item_match else None
        content    = clean_text(f"Meeting: {meeting_no}\nPage: {page_num}\n{text}")
        chunks.append({
            "page_content": content,
            "source":       filename,
            "meeting_no":   meeting_no,
            "item_no":      item_no,
            "page":         page_num,
        })

    if not chunks:
        return [], []

    texts   = [c["page_content"] for c in chunks]
    vectors = embedder.encode(texts, normalize_embeddings=True).tolist()
    return chunks, vectors


# ─── ROUTES ───────────────────────────────────────────────────────────────────

@app.post("/query")
async def query(req: QueryRequest):
    try:
        print(f"\n🔍 Query: {req.query}")
        response = rag_handler.handle_input(req.query, req.top_k)
        return {
            "text":     response or "",
            "answer":   response or "",
            "response": response or "",
            "message":  {"text": response or ""},
            "status":   "success",
        }
    except Exception:
        traceback.print_exc()
        msg = "Error occurred while processing query."
        return {"text": msg, "answer": msg, "response": msg,
                "message": {"text": msg}, "status": "error"}


@app.post("/documents")
async def upload_document(file: UploadFile = File(...)):
    """Upload a PDF → S3 → embed → Qdrant + PostgreSQL."""
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    filename = file.filename

    if db.document_exists(filename):
        raise HTTPException(
            status_code=409, detail=f"{filename} already processed"
        )

    # Save to temp file
    data = await file.read()
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp.write(data)
        tmp_path = tmp.name

    try:
        # Upload to S3
        s3_key = s3_storage.upload_bytes(data, filename)

        # OCR + embed
        chunks, vectors = process_and_embed(tmp_path, filename)
        if not chunks:
            raise HTTPException(status_code=422, detail="No text extracted from PDF")

        # Upsert to Qdrant
        point_ids = qdrant_store.upsert_points(vectors, chunks)

        # Store metadata in PostgreSQL
        meeting_no = extract_meeting_no(filename)
        doc_id = db.insert_document(filename, s3_key, meeting_no)
        db.insert_chunks(doc_id, [
            {"qdrant_id": pid, "page": c["page"], "item_no": c["item_no"]}
            for pid, c in zip(point_ids, chunks)
        ])

        # Refresh in-memory payloads in RAG handler
        rag_handler.all_docs = qdrant_store.scroll_all()

        return {
            "status":   "success",
            "filename": filename,
            "chunks":   len(chunks),
            "doc_id":   doc_id,
        }

    finally:
        os.unlink(tmp_path)


@app.get("/documents")
async def list_documents():
    docs = db.get_all_documents()
    return {"documents": [dict(d) for d in docs]}


@app.delete("/documents/{doc_id}")
async def delete_document(doc_id: int):
    point_ids = db.get_qdrant_ids_for_document(doc_id)
    qdrant_store.delete_by_ids(point_ids)
    db.delete_document(doc_id)          # cascades chunks
    rag_handler.all_docs = qdrant_store.scroll_all()
    return {"status": "deleted", "doc_id": doc_id, "vectors_removed": len(point_ids)}


@app.get("/health")
async def health():
    info = qdrant_store.collection_info()
    return {"status": "ok", "qdrant": info}
