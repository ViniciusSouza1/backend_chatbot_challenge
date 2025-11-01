from fastapi import APIRouter, Query, HTTPException
from app.services.vector_client import (
    search, EMBED_MODEL, PINECONE_HOST, NAMESPACE, index, embed_query, pc,
    INDEX_DIM, adjust_dim
)
from typing import Optional, Any, List, Dict
from fastapi.responses import JSONResponse
import traceback


router = APIRouter(prefix="/debug")


@router.get("/pinecone")
def debug_pinecone(q: str = Query(..., description="Query text")):
    """
    Returns raw matches so you can verify scores and metadata.
    """
    matches = search(q, top_k=5)
    return {
        "host": PINECONE_HOST,
        "model": EMBED_MODEL,
        "matches": matches
    }


@router.get("/emb")
def debug_embedding(q: str = Query(...)):
    vec = embed_query(q)
    return {
        "model": EMBED_MODEL,
        "len": len(vec),
        "sample": vec[:5],
        "host": PINECONE_HOST,
        "namespace": NAMESPACE
    }

@router.get("/stats")
def debug_stats():
    # sem namespace => retorna mapa por namespace
    stats = index.describe_index_stats()
    return stats


@router.get("/pinecone-raw")
def pinecone_raw(
    q: str = Query(..., description="Query text"),
    top_k: int = Query(5, ge=1, le=50),
    ns: Optional[str] = Query(None, description="Override namespace (optional)")
):
    """
    Safely returns the full raw Pinecone query response (scores, metadata, etc)
    without causing FastAPI JSON recursion errors.
    """
    try:
        # Generate embedding for the given query
        vec_raw = embed_query(q)                       # geralmente 1024
        vec = adjust_dim(vec_raw, INDEX_DIM)           # vira 1536

        # Build query parameters
        kwargs = {"vector": vec, "top_k": top_k, "include_metadata": True}
        if (ns or NAMESPACE) not in (None, ""):
            kwargs["namespace"] = ns or NAMESPACE

        # Execute Pinecone query
        res = index.query(**kwargs)

        try:
            if hasattr(res, "model_dump") and callable(res.model_dump):
                payload = res.model_dump()
            elif hasattr(res, "to_dict") and callable(res.to_dict):
                payload = res.to_dict()
            else:
                # Some SDKs already return plain dict-like objects
                if isinstance(res, dict):
                    payload = res
                elif hasattr(res, "__dict__"):
                    payload = res.__dict__
                else:
                    import json
                    try:
                        payload = json.loads(str(res))
                    except Exception:
                        payload = {"raw_str": str(res)}
        except Exception as conv_err:
            payload = {"error": f"Failed to serialize response: {conv_err}", "raw_type": str(type(res))}


        return JSONResponse(
            content={
                "host": PINECONE_HOST,
                "model": EMBED_MODEL,
                "namespace_used": kwargs.get("namespace", "(none)"),
                "top_k": top_k,
                "vector_len_raw": len(vec_raw),
                "vector_len_sent": len(vec),
                "raw": payload,
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pinecone error: {e}")
    

@router.get("/debug/pinecone-stats")
def pinecone_stats():
    try:
        idx = pc.Index(host=PINECONE_HOST)  # use o mesmo host já configurado
        stats = idx.describe_index_stats()
        # Resumo amigável
        ns = stats.get("namespaces", {}) or {}
        total = stats.get("total_vector_count", 0)
        return {
            "total_vector_count": total,
            "namespaces": {k: v.get("vector_count", 0) for k, v in ns.items()},
            "dimension": stats.get("dimension"),  # útil p/ conferir com seu embedder
        }
    except Exception as e:
        return {"error": str(e)}
    
# src/app/api/routes/debug.py


def _coerce_dict(x: Any) -> dict:
    """
    Ensures a dict. If a JSON string is received, attempts to use json.loads; otherwise, {}.
    """
    if isinstance(x, dict):
        return x
    if isinstance(x, str):
        try:
            import json
            j = json.loads(x)
            if isinstance(j, dict):
                return j
        except Exception:
            pass
    return {}

def _safe_get_dimension(stats: Any, default: int = 1536) -> int:
    """
    Try to extract all dimension info from stats. return default if fails.
    """
    try:
        # Se stats é uma string que parece dict, tenta converter
        if isinstance(stats, str) and stats.strip().startswith('{'):
            try:
                import ast
                stats_dict = ast.literal_eval(stats)
                if isinstance(stats_dict, dict) and 'dimension' in stats_dict:
                    return int(stats_dict['dimension'])
            except:
                pass
        
        # Tenta como dict normal
        d = _coerce_dict(stats)
        if 'dimension' in d:
            return int(d['dimension'])
            
    except Exception as e:
        print(f"DEBUG - Error extracting dimension: {e}")
    
    return default  # Agora default é 1536, já que sabemos do índice

def _to_plain(x: Any) -> Any:
    """
    Converts Pinecone/Pydantic objects to native types (dict/list/str/num)
    to avoid RecursionError in the FastAPI jsonable_encoder.
    """
    # Já é nativo?
    if isinstance(x, (str, int, float, bool, type(None))):
        return x
    if isinstance(x, (list, tuple)):
        return [_to_plain(i) for i in x]
    if isinstance(x, dict):
        return {k: _to_plain(v) for k, v in x.items()}

    # Tentativas para Pydantic v2 e v1
    for attr in ("model_dump", "dict"):
        fn = getattr(x, attr, None)
        if callable(fn):
            try:
                return _to_plain(fn())
            except Exception:
                pass

    # Tentativa via JSON do Pydantic v2
    fn_json = getattr(x, "model_dump_json", None)
    if callable(fn_json):
        try:
            import json
            return _to_plain(json.loads(fn_json()))
        except Exception:
            pass

    # Último recurso: transforma em string (pelo menos é serializável)
    return str(x)


@router.post("/pinecone-smoke")
def pinecone_smoke():
    """
    Smoke test do Pinecone: describe -> upsert 1 vetor -> query. 
    """
    try:
        if not PINECONE_HOST:
            return {
                "ok": False,
                "error": "PINECONE_HOST not configured.",
                "hint": "Define PINECONE_HOST=URL from service at index (svc.ap-...pinecone.io)."
            }

        idx = pc.Index(host=PINECONE_HOST)

        # 1) Stats (validate conection + dimension)
        stats_raw = idx.describe_index_stats()
        stats = _to_plain(stats_raw)
        
        # DEBUG: Veja a estrutura real
        print("=== DEBUG STATS STRUCTURE ===")
        print(stats)
        print("=============================")
        
        dim = _safe_get_dimension(stats, 1536)  # Agora default é 1536

        # 2) Upsert 1 vetor
        vec = [0.001 * i for i in range(dim)]
        ns = NAMESPACE or "default"
        
        print(f"Trying with dimension: {dim}")
        
        up_raw = idx.upsert(
            vectors=[{"id": "smoke-vec", "values": vec, "metadata": {"src": "smoke"}}],
            namespace=ns,
        )
        up = _to_plain(up_raw)
        up_d = _coerce_dict(up)
        upserted_count = up_d.get("upserted_count")

        # After upsert, add:
        print(f"DEBUG upsert raw: {up_raw}")
        print(f"DEBUG upsert converted: {up}")
        print(f"DEBUG upsert dict: {up_d}")

        # 3) Query
        qr_raw = idx.query(vector=vec, top_k=5, include_metadata=True, namespace=ns)
        qr = _to_plain(qr_raw)
        qr_d = _coerce_dict(qr)
        matches = qr_d.get("matches", []) or []
        top = []
        for m in matches:
            if isinstance(m, dict):
                top.append({"id": m.get("id"), "score": m.get("score")})
            else:
                # fallback: tenta atributos
                top.append({
                    "id": getattr(m, "id", None),
                    "score": getattr(m, "score", None)
                })

        return {
            "ok": True,
            "host": PINECONE_HOST,
            "namespace_used": ns,
            "stats_before": stats,
            "upsert_result": {"upserted_count": upserted_count},
            "query_matches": len(matches),
            "top": top,
        }

    except Exception as e:
        return {
            "ok": False,
            "error": str(e),
            "traceback": traceback.format_exc(),
            "context": {
                "host": PINECONE_HOST,
                "namespace": NAMESPACE or "default"
            }
        }