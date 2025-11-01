import os
import time
from typing import List, Dict, Any
from dotenv import load_dotenv
from pinecone import Pinecone
from app.core.logging import get_logger

load_dotenv()
log = get_logger("rag.vector")

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_HOST = os.getenv("PINECONE_HOST")
EMBED_MODEL = os.getenv("PINECONE_EMBED_MODEL", "llama-text-embed-v2")
TOP_K = int(os.getenv("PINECONE_TOP_K", "3"))
NAMESPACE = os.getenv("PINECONE_NAMESPACE")  # may be None
DEBUG_RAW_MATCHES = os.getenv("DEBUG_RAW_MATCHES", "false").lower() == "true"
INDEX_DIM = int(os.getenv("PINECONE_INDEX_DIM", "1536"))

if not PINECONE_API_KEY or not PINECONE_HOST:
    raise RuntimeError("Please configure PINECONE_API_KEY and PINECONE_HOST in .env")

# One-time connection (reuse client + index)
pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(host=PINECONE_HOST)

log.info(f"Pinecone connected | host={PINECONE_HOST} | model={EMBED_MODEL} | "
         f"namespace={NAMESPACE or '(none)'} | top_k={TOP_K}")


def adjust_dim(vec, target_dim: int):
    """Ensures that the vector has the length required by the Pinecone index."""
    if vec is None:
        return None
    v = list(map(float, vec))
    n = len(v)
    if n == target_dim:
        return v
    if n > target_dim:
        return v[:target_dim]
    return v + [0.0] * (target_dim - n)

def embed_query(text: str) -> List[float]:
    """
    Generate a query embedding using Pinecone Inference with input_type='query'.
    Returns a 1024-dim vector for llama-text-embed-v2.
    """
    t0 = time.perf_counter()
    resp = pc.inference.embed(
        model=EMBED_MODEL,
        inputs=[text],
        parameters={"input_type": "query"}
    )
    vec = resp.data[0].values
    dt = (time.perf_counter() - t0) * 1000
    log.debug(f"embed_query ok | dims={len(vec)} | ms={dt:.1f}")
    return vec

def search(text: str, top_k: int = TOP_K) -> List[Dict[str, Any]]:
    """
    1) Embed the query (measures latency)
    2) Query the Pinecone index (measures latency)
    3) Return normalized matches (id/score/metadata)
    """
    # 1) embed
    qvec_raw = embed_query(text)
    qvec = adjust_dim(qvec_raw, INDEX_DIM)

    # 2) query
    t0 = time.perf_counter()
    kwargs = {
        "vector": qvec,
        "top_k": top_k,
        "include_metadata": True,
    }
    if NAMESPACE not in (None, ""):
        kwargs["namespace"] = NAMESPACE

    res = index.query(**kwargs)
    query_ms = (time.perf_counter() - t0) * 1000

    raw = res.get("matches", []) or []
    count = len(raw)
    top_scores = [round(m.get("score", 0.0), 4) for m in raw[:3]]
    log.info(f"pinecone.query | matches={count} | top_scores={top_scores} | ms={query_ms:.1f} "
             f"| ns={NAMESPACE or '(none)'}")

    if DEBUG_RAW_MATCHES:
        log.debug(f"raw_matches={raw}")

    # 3) normalize
    out: List[Dict[str, Any]] = []
    for m in raw:
        out.append({
            "id": m.get("id"),
            "score": m.get("score"),
            "metadata": m.get("metadata"),
        })
    return out

def build_context(matches: List[Dict[str, Any]]) -> str:
    """
    Format retrieved entries into a readable context block.
    """
    parts = []
    for i, m in enumerate(matches, start=1):
        md = m.get("metadata") or {}
        cat = md.get("category", "Unknown")
        q = md.get("question", "")
        a = md.get("answer", "")
        parts.append(f"[{i}] Category: {cat}\nQ: {q}\nA: {a}")
    return "\n\n".join(parts)
