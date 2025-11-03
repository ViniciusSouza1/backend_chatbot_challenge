# src/app/api/routes/ingest.py
from fastapi import APIRouter, Query, Depends
from typing import List
import traceback
from app.api.routes.debug import _to_plain, _coerce_dict

from app.services.vector_client import pc, PINECONE_HOST, NAMESPACE, embed_query
from app.api.routes.debug import _to_plain, _coerce_dict, _safe_get_dimension
from app.data.faq_seed import FAQ_ENTRIES
from app.api.deps.permissions import require_admin, User

router = APIRouter(prefix="/api/ingest", tags=["ingest"])

def _adjust_to_dim(vec: List[float], target: int) -> List[float]:
    """Pad (or cut) an embedding to 'target' dimensions."""
    n = len(vec)
    if n == target:
        return vec
    if n > target:
        return vec[:target]
    return vec + [0.0] * (target - n)


@router.post("/faq")
def ingest_faq(
    namespace: str | None = Query(None),
    batch_size: int = Query(32, ge=1, le=100),
    _: User = Depends(require_admin),
):
    """
    🚀 Ingests the synthetic FAQ dataset into Pinecone.
    Detects index dimension (e.g., 1536) and pads embeddings automatically.
    """
    try:
        ns = namespace or NAMESPACE or "default"
        idx = pc.Index(host=PINECONE_HOST)

        # Detect index dimension
        stats_raw = idx.describe_index_stats()
        stats = _to_plain(stats_raw)
        target_dim = _safe_get_dimension(stats, default=1536)

        # Build vectors
        vectors = []
        for entry in FAQ_ENTRIES:
            doc = f"{entry['category']}\nQ: {entry['question']}\nA: {entry['answer']}"
            emb = embed_query(doc)  # 1024 dims
            emb_adj = _adjust_to_dim(emb, target_dim)
            vectors.append({
                "id": entry["id"],
                "values": emb_adj,
                "metadata": {
                    "category": entry["category"],
                    "question": entry["question"],
                    "answer": entry["answer"]
                }
            })

        # Upsert in batches
        total = 0
        for i in range(0, len(vectors), batch_size):
            chunk = vectors[i:i+batch_size]
            idx.upsert(vectors=chunk, namespace=ns)
            total += len(chunk)

        # Sanity check: simple query
        test_vec = _adjust_to_dim(embed_query("How do I create an account?"), target_dim)
        qr = idx.query(vector=test_vec, top_k=5, include_metadata=True, namespace=ns)

        qr_plain = _to_plain(qr)
        qr_d = _coerce_dict(qr_plain)
        matches = qr_d.get("matches", []) or []

        # Safe preview (dict or object)
        preview = []
        for m in matches:
            if isinstance(m, dict):
                md = m.get("metadata") or {}
                preview.append({
                    "id": m.get("id"),
                    "score": m.get("score"),
                    "category": md.get("category")
                })
            else:
                # fallback with objects attributes
                mid = getattr(m, "id", None)
                mscore = getattr(m, "score", None)
                mmeta = getattr(m, "metadata", {}) or {}
                if not isinstance(mmeta, dict):
                    mmeta = _coerce_dict(_to_plain(mmeta))
                preview.append({
                    "id": mid,
                    "score": mscore,
                    "category": (mmeta or {}).get("category")
                })

        return {
            "ok": True,
            "namespace_used": ns,
            "index_dim": target_dim,
            "ingested_count": total,
            "preview_matches_for_create_account": preview[:3],
        }

    except Exception as e:
        return {
            "ok": False,
            "error": str(e),
            "traceback": traceback.format_exc(),
        }
