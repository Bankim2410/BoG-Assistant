"""
qdrant_store.py — Qdrant vector store helpers.

Collection schema:
  vector : 384-dim float (all-MiniLM-L6-v2)
  payload: {
      page_content : str,
      source       : str,
      meeting_no   : str | None,
      item_no      : str | None,
      page         : int,
  }
"""

import os
import uuid
from dotenv import load_dotenv

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
)

load_dotenv()

COLLECTION = os.getenv("QDRANT_COLLECTION", "bog_documents")
VECTOR_SIZE = 384  # all-MiniLM-L6-v2 output dimension

_client: QdrantClient | None = None


def _get_client() -> QdrantClient:
    global _client
    if _client is None:
        url = os.getenv("QDRANT_URL", "")
        api_key = os.getenv("QDRANT_API_KEY", "")
        if api_key:
            _client = QdrantClient(url=url, api_key=api_key)
        else:
            # local / no-auth Qdrant
            _client = QdrantClient(url=url)
    return _client


def ensure_collection():
    """Create the Qdrant collection if it doesn't exist."""
    client = _get_client()
    existing = [c.name for c in client.get_collections().collections]
    if COLLECTION not in existing:
        client.create_collection(
            collection_name=COLLECTION,
            vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
        )
        print(f"✅ Qdrant collection '{COLLECTION}' created")
    else:
        print(f"📦 Qdrant collection '{COLLECTION}' already exists")


def upsert_points(embeddings: list[list[float]], metadatas: list[dict]) -> list[str]:
    """
    Insert points into Qdrant.
    Returns the list of generated point IDs (UUIDs as strings).
    """
    client = _get_client()
    points = []
    ids = []

    for vector, meta in zip(embeddings, metadatas):
        point_id = str(uuid.uuid4())
        ids.append(point_id)
        points.append(
            PointStruct(
                id=point_id,
                vector=vector,
                payload=meta,
            )
        )

    client.upsert(collection_name=COLLECTION, points=points)
    return ids


def similarity_search(
    query_vector: list[float],
    top_k: int = 10,
    filter_dict: dict | None = None,
) -> list[dict]:
    """
    Search for similar vectors.
    filter_dict keys map to Qdrant MatchValue filters on payload fields.
    Returns list of payload dicts sorted by score desc.
    """
    client = _get_client()

    qdrant_filter = None
    if filter_dict:
        conditions = [
            FieldCondition(key=k, match=MatchValue(value=v))
            for k, v in filter_dict.items()
            if v is not None
        ]
        if conditions:
            qdrant_filter = Filter(must=conditions)

    results = client.search(
        collection_name=COLLECTION,
        query_vector=query_vector,
        limit=top_k,
        query_filter=qdrant_filter,
        with_payload=True,
    )

    return [hit.payload for hit in results]


def scroll_all(limit: int = 10_000) -> list[dict]:
    """Fetch all payloads from the collection (for in-memory filtering)."""
    client = _get_client()
    records, _ = client.scroll(
        collection_name=COLLECTION,
        limit=limit,
        with_payload=True,
        with_vectors=False,
    )
    return [r.payload for r in records]


def delete_by_ids(point_ids: list[str]):
    """Delete points by their UUIDs."""
    if not point_ids:
        return
    from qdrant_client.models import PointIdsList
    _get_client().delete(
        collection_name=COLLECTION,
        points_selector=PointIdsList(points=point_ids),
    )
    print(f"🗑️  Deleted {len(point_ids)} Qdrant points")


def collection_info() -> dict:
    client = _get_client()
    info = client.get_collection(COLLECTION)
    return {
        "vectors_count": info.vectors_count,
        "points_count": info.points_count,
        "status": str(info.status),
    }
