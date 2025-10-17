from typing import Dict, Any, List, Tuple
import numpy as np
from ..core.utils import normalize, cosine_similarity
try:
    import faiss  # type: ignore
    _HAS_FAISS = True
except Exception:
    _HAS_FAISS = False

FACE_META: List[Dict[str, Any]] = []
if _HAS_FAISS:
    FACE_DIM = 128
    face_index = faiss.IndexFlatIP(FACE_DIM)
    def _add_vec(v):
        import numpy as _np
        face_index.add(_np.array([v], dtype='float32'))
    def _search_vec(v, k):
        import numpy as _np
        D, I = face_index.search(_np.array([v], dtype='float32'), k)
        return [float(x) for x in D[0]], [int(i) for i in I[0]]
else:
    FACE_VECS: List[List[float]] = []
    def _add_vec(v): FACE_VECS.append(v)
    def _search_vec(v, k):
        sims = [cosine_similarity(v, e) for e in FACE_VECS]
        order = sorted(range(len(sims)), key=lambda i: sims[i], reverse=True)[:k]
        return [float(sims[i]) for i in order], order

def stub_face_embed(img_bytes: bytes) -> List[float]:
    seed = sum(img_bytes[:64]) % 2**32
    rng = np.random.RandomState(seed)
    v = rng.rand(128).astype('float32')
    return normalize(v.tolist())

def add_face_embedding(person_id: str, img_bytes: bytes) -> Dict[str, Any]:
    v = stub_face_embed(img_bytes)
    _add_vec(v)
    FACE_META.append({'person_id': person_id})
    return {'person_id': person_id, 'embedding_len': len(v)}

def search_face(img_bytes: bytes, k: int = 3) -> Tuple[float, Dict[str, Any]]:
    if len(FACE_META) == 0:
        return 0.0, {}
    v = stub_face_embed(img_bytes)
    D, I = _search_vec(v, k)
    if not I:
        return 0.0, {}
    best = 0
    return float(D[best]), FACE_META[I[best]]
