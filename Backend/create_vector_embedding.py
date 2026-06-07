"""
create_vector_embedding.py
──────────────────────────
Pipeline:
  1. List PDFs in S3
  2. Skip already-processed ones (checked via PostgreSQL)
  3. Download from S3 → temp file
  4. OCR with PaddleOCR via PyMuPDF
  5. Embed with sentence-transformers/all-MiniLM-L6-v2
  6. Upsert to Qdrant
  7. Store metadata in PostgreSQL

Usage:
  python create_vector_embedding.py
"""

import os
import re
import tempfile
import numpy as np
from tqdm import tqdm

import fitz  # PyMuPDF
from paddleocr import PaddleOCR
from sentence_transformers import SentenceTransformer

from dotenv import load_dotenv
load_dotenv()

import db
import s3_storage
import qdrant_store

# ─── CONFIG ───────────────────────────────────────────────────────────────────
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
MIN_CHUNK_CHARS  = 50

paddle_ocr = PaddleOCR(use_angle_cls=True, lang="en")
embedder   = SentenceTransformer(EMBEDDING_MODEL)


# ─── TEXT UTILS ───────────────────────────────────────────────────────────────

def clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def extract_meeting_no(filename: str) -> str | None:
    m = re.search(r"(\d{1,3})(?:st|nd|rd|th)", filename.lower())
    return m.group(1) if m else None


# ─── OCR ──────────────────────────────────────────────────────────────────────

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
    except Exception as e:
        print(f"⚠️  OCR failed on page: {e}")
        return ""


# ─── PDF → CHUNKS ─────────────────────────────────────────────────────────────

def pdf_to_chunks(local_path: str, filename: str) -> list[dict]:
    """
    Returns list of dicts:
      {page_content, source, meeting_no, item_no, page}
    """
    meeting_no = extract_meeting_no(filename)
    doc = fitz.open(local_path)
    chunks = []

    print(f"\n📄 Processing {filename} | Pages: {len(doc)}")

    for page_num, page in enumerate(doc):
        text = ocr_page(page)

        if len(text.strip()) < MIN_CHUNK_CHARS:
            continue

        item_match = re.search(r"\d+\.\d+", text)
        item_no = item_match.group() if item_match else None

        content = clean_text(f"Meeting: {meeting_no}\nPage: {page_num}\n{text}")

        chunks.append({
            "page_content": content,
            "source":       filename,
            "meeting_no":   meeting_no,
            "item_no":      item_no,
            "page":         page_num,
        })

    print(f"✅ {filename}: {len(chunks)} chunks")
    return chunks


# ─── EMBED ────────────────────────────────────────────────────────────────────

def embed_chunks(chunks: list[dict]) -> list[list[float]]:
    texts = [c["page_content"] for c in chunks]
    vecs  = embedder.encode(texts, normalize_embeddings=True, show_progress_bar=True)
    return vecs.tolist()


# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    print("\n🚀 Starting cloud embedding pipeline…\n")

    # Bootstrap DB tables + Qdrant collection
    db.init_db()
    qdrant_store.ensure_collection()

    # List PDFs in S3
    s3_files = s3_storage.list_pdfs()
    print(f"☁️  Found {len(s3_files)} PDF(s) in S3")

    new_count = 0

    for filename in tqdm(s3_files, desc="PDFs"):
        if db.document_exists(filename):
            print(f"⏭️  Already processed: {filename}")
            continue

        meeting_no = extract_meeting_no(filename)

        # Download to temp file
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            s3_storage.download_to_path(filename, tmp_path)

            chunks = pdf_to_chunks(tmp_path, filename)
            if not chunks:
                print(f"⚠️  No chunks from {filename}, skipping")
                continue

            vectors = embed_chunks(chunks)

            # Upsert to Qdrant
            point_ids = qdrant_store.upsert_points(vectors, chunks)

            # Store metadata in PostgreSQL
            s3_key   = s3_storage.s3_key(filename)
            doc_id   = db.insert_document(filename, s3_key, meeting_no)
            chunk_records = [
                {"qdrant_id": pid, "page": c["page"], "item_no": c["item_no"]}
                for pid, c in zip(point_ids, chunks)
            ]
            db.insert_chunks(doc_id, chunk_records)

            new_count += 1
            print(f"✅ {filename}: {len(chunks)} chunks embedded & stored")

        finally:
            os.unlink(tmp_path)

    if new_count == 0:
        print("\n⚠️  No new documents were processed")
    else:
        print(f"\n✅ DONE — processed {new_count} new document(s)\n")


if __name__ == "__main__":
    main()
