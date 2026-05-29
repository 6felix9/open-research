from __future__ import annotations

import os
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path

import chromadb


COLLECTION_NAME = "sponsor_profiles"
DEFAULT_TTL_DAYS = 7
_CACHE_EMBEDDING = [0.0]

_client = None
_collection = None


def _normalize_sponsor_name(sponsor_name: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "-", sponsor_name.strip().lower())
    return normalized.strip("-")


def _get_client():
    global _client
    if _client is not None:
        return _client

    chroma_host = os.getenv("CHROMA_HOST")
    if chroma_host:
        port = int(os.getenv("CHROMA_PORT", "8000"))
        _client = chromadb.HttpClient(host=chroma_host, port=port)
    else:
        default_path = Path(__file__).resolve().parents[1] / "chroma_db"
        _client = chromadb.PersistentClient(path=os.getenv("CHROMA_PATH", str(default_path)))

    return _client


def _get_collection():
    global _collection
    if _collection is None:
        _collection = _get_client().get_or_create_collection(COLLECTION_NAME)
    return _collection


def _is_stale(cached_at: str | None) -> bool:
    if not cached_at:
        return True

    try:
        cached_time = datetime.fromisoformat(cached_at)
    except ValueError:
        return True

    ttl_days = int(os.getenv("SPONSOR_PROFILE_TTL_DAYS", str(DEFAULT_TTL_DAYS)))
    return datetime.now(timezone.utc) - cached_time > timedelta(days=ttl_days)


def get_cached_profile(sponsor_name: str) -> str | None:
    # TODO: Provide a force-refresh trigger or an endpoint to invalidate specific sponsor caches on-demand.
    sponsor_id = _normalize_sponsor_name(sponsor_name)
    if not sponsor_id:
        return None

    result = _get_collection().get(ids=[sponsor_id], include=["documents", "metadatas"])
    documents = result.get("documents") or []
    metadatas = result.get("metadatas") or []

    if not documents:
        return None

    metadata = metadatas[0] if metadatas else {}
    if _is_stale(metadata.get("cached_at")):
        return None

    return documents[0]


def cache_profile(sponsor_name: str, profile_text: str) -> None:
    sponsor_id = _normalize_sponsor_name(sponsor_name)
    if not sponsor_id:
        raise ValueError("sponsor_name must contain at least one alphanumeric character")

    _get_collection().upsert(
        ids=[sponsor_id],
        documents=[profile_text],
        metadatas=[
            {
                "sponsor_name": sponsor_name.strip(),
                "cached_at": datetime.now(timezone.utc).isoformat(),
            }
        ],
        embeddings=[_CACHE_EMBEDDING],
    )
