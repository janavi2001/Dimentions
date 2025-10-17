"""
Face index service with FAISS fallback and simple liveness stub.

Functions return JSON-safe primitives and dicts.
No explicit typecasting is used.
"""
from typing import Dict, Any, List, Tuple
import os
import uuid
import time
from datetime import datetime
import numpy as np
from ..core.utils import normalize, cosine_similarity

# Optional FAISS support
try:
    import faiss  # type: ignore
    _HAS_FAISS = True
except Exception:
    _HAS_FAISS = False

# ---- In-memory meta store; vectors live in FAISS or a Python list
FACE_META: List[Dict[str, Any]] = []

if _HAS_FAISS:
    FACE_DIM = 128
    _faiss_index = faiss.IndexFlatIP(FACE_DIM)

    def _add_vec(v: List[float]) -> None:
        _faiss_index.add(np.array([v], dtype="float32"))

    def _search_vec(v: List[float], k: int) -> Tuple[List[float], List[int]]:
        D, I = _faiss_index.search(np.array([v], dtype="float32"), k)
        return [float(x) for x in D[0]], [int(i) for i in I[0]]
else:
    _FACE_VECS: List[List[float]] = []

    def _add_vec(v: List[float]) -> None:
        _FACE_VECS.append(v)

    def _search_vec(v: List[float], k: int) -> Tuple[List[float], List[int]]:
        sims = [cosine_similarity(v, e) for e in _FACE_VECS]
        order = sorted(range(len(sims)), key=lambda i: sims[i], reverse=True)[:k]
        return [float(sims[i]) for i in order], order


def _stub_face_embed(img_bytes: bytes) -> List[float]:
    """
    Deterministic dev-only face embedding.
    Uses a hash-like seed so the same image bytes map to the same vector.

    Returns: list[float] of length 128, normalized to unit length.
    """
    seed = sum(img_bytes[:64]) % 2**32
    rng = np.random.RandomState(seed)
    v = rng.rand(128)
    return normalize(v)


def add_face_embedding(person_id: str, img_bytes: bytes) -> Dict[str, Any]:
    """
    Adds a face embedding to the index and records metadata.

    Returns: dict with keys:
      - person_id: str
      - embedding_len: int
      - created_at: str (ISO8601)
    """
    v = _stub_face_embed(img_bytes)
    _add_vec(v)
    created_at = datetime.utcnow().isoformat()
    FACE_META.append({"person_id": person_id, "created_at": created_at})

    # Optional: dev image dump for debugging if env is set
    out_dir = os.getenv("DEBUG_FACE_DIR", "")
    if out_dir:
        try:
            os.makedirs(os.path.join(out_dir, person_id), exist_ok=True)
            fname = os.path.join(out_dir, person_id, f"{uuid.uuid4()}.jpg")
            with open(fname, "wb") as f:
                f.write(img_bytes)
        except Exception:
            # Best-effort only; ignore file errors in dev
            pass

    return {"person_id": person_id, "embedding_len": len(v), "created_at": created_at}


def search_face(img_bytes: bytes, k: int = 3) -> Tuple[float, Dict[str, Any]]:
    """
    Searches the index for the closest match to the provided image bytes.

    Returns: (similarity: float in [0,1], meta: dict with at least person_id or empty {})
    """
    if len(FACE_META) == 0:
        return 0.0, {}

    v = _stub_face_embed(img_bytes)
    D, I = _search_vec(v, k)
    if not I:
        return 0.0, {}

    best = 0
    return float(D[best]), FACE_META[I[best]]


def liveness_check(frame_bytes_list: List[bytes]) -> bool:
    """
    Minimal liveness placeholder. Always returns True for now.

    Returns: bool
    """
    # Later: analyze motion/eye-blink across frames; here we just simulate latency.
    time.sleep(0.01)
    return True
