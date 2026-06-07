"""
rag_query_handler.py
─────────────────────
RAG handler backed by Qdrant (vector search) + Groq (LLM).

Query routing:
  agenda  → filter by item_no payload field
  latest  → find highest meeting_no, filter
  single  → filter by meeting_no
  multi   → filter by multiple meeting_nos (union)
  global  → pure similarity search
"""

import os
import re
from dotenv import load_dotenv
load_dotenv()

from sentence_transformers import SentenceTransformer
from langchain_groq import ChatGroq

import qdrant_store

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


class TextRAGHandler:
    def __init__(
        self,
        groq_api_key: str | None = None,
    ):
        self.embedder = SentenceTransformer(EMBEDDING_MODEL)

        self.llm = ChatGroq(
            groq_api_key=groq_api_key or os.getenv("GROQ_API_KEY", ""),
            model_name="llama-3.3-70b-versatile",
        )

        # Warm-up: pull all payloads for in-memory metadata filtering
        print("🔄 Loading all chunk payloads from Qdrant…")
        self.all_docs = qdrant_store.scroll_all()
        print(f"📦 TOTAL CHUNKS LOADED: {len(self.all_docs)}")

    # ─── EMBED ────────────────────────────────────────────────────────────────

    def _embed(self, text: str) -> list[float]:
        return self.embedder.encode(text, normalize_embeddings=True).tolist()

    # ─── QUERY PARSE ──────────────────────────────────────────────────────────

    def _parse_query(self, query: str) -> dict:
        q = query.lower()

        agenda = re.findall(r"\d+\.\d+", q)
        numbers = re.findall(r"\d{1,3}", q)

        if agenda:
            return {"type": "agenda", "item_no": agenda[0]}

        if any(w in q for w in ["latest", "last", "recent"]):
            return {"type": "latest"}

        if len(numbers) > 1:
            return {"type": "multi", "meetings": numbers}

        if len(numbers) == 1:
            return {"type": "single", "meeting": numbers[0]}

        return {"type": "global"}

    # ─── FILTER ───────────────────────────────────────────────────────────────

    def _filter_docs(self, parsed: dict, query: str) -> list[dict]:
        docs = self.all_docs

        if parsed["type"] == "agenda":
            item = parsed["item_no"]
            exact = [d for d in docs if d.get("item_no") == item]
            if exact:
                return exact
            # Fallback: substring match (handles OCR imperfections)
            return [d for d in docs if item in d.get("page_content", "")]

        if parsed["type"] == "latest":
            nums = [
                int(d["meeting_no"])
                for d in docs
                if d.get("meeting_no") and str(d["meeting_no"]).isdigit()
            ]
            if not nums:
                return []
            latest = str(max(nums))
            return [d for d in docs if str(d.get("meeting_no")) == latest]

        if parsed["type"] == "single":
            return [
                d for d in docs
                if str(d.get("meeting_no")) == str(parsed["meeting"])
            ]

        if parsed["type"] == "multi":
            return [
                d for d in docs
                if str(d.get("meeting_no")) in parsed["meetings"]
            ]

        # Global: pure vector search
        return qdrant_store.similarity_search(self._embed(query), top_k=50)

    # ─── SCORING ──────────────────────────────────────────────────────────────

    def _score_docs(self, docs: list[dict], query: str, top_n: int = 30) -> list[dict]:
        q_words = query.lower().split()
        DOMAIN_WORDS = ["phd", "finance", "academic", "infrastructure"]

        scored = []
        for d in docs:
            text  = d.get("page_content", "").lower()
            score = sum(2 for w in q_words if w in text)
            score += sum(5 for w in DOMAIN_WORDS if w in query.lower() and w in text)
            scored.append((score, d))

        scored.sort(reverse=True, key=lambda x: x[0])
        return [d for _, d in scored[:top_n]]

    # ─── MAIN ─────────────────────────────────────────────────────────────────

    def handle_input(self, query: str, top_k: int = 15) -> str:
        print("\n🔥 RAG invoked")

        parsed = self._parse_query(query)
        print(f"🧠 PARSED: {parsed}")

        docs = self._filter_docs(parsed, query)
        print(f"🎯 After filter: {len(docs)} docs")

        if not docs:
            # Hard fallback to vector search
            docs = qdrant_store.similarity_search(self._embed(query), top_k=top_k)

        docs = self._score_docs(docs, query)

        context = "\n\n".join([d.get("page_content", "") for d in docs])

        prompt = f"""Answer using the context below.

- Extract exact facts
- Count properly if required
- Combine multiple chunks

Question:
{query}

Context:
{context}

Answer:"""

        response = self.llm.invoke([{"role": "user", "content": prompt}])
        return response.content
