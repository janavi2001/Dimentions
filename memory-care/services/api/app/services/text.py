from typing import Dict, Any, List
import numpy as np
from ..core.utils import normalize, cosine_similarity

TEXT_EMBS: List[List[float]] = []
TEXT_META: List[Dict[str, Any]] = []

def stub_text_embed(texts: List[str]) -> List[List[float]]:
    out = []
    for t in texts:
        h = sum(ord(c) for c in t) % 10000
        rng = np.random.RandomState(h)
        v = rng.rand(64).astype('float32')
        out.append(normalize(v.tolist()))
    return out

def chunk_text(s: str) -> List[str]:
    return [c.strip() for c in s.split('. ') if len(c.strip()) > 20]

def upsert_chunks(person_id: str, transcript: str) -> int:
    chunks = chunk_text(transcript)
    if not chunks: return 0
    embs = stub_text_embed(chunks)
    for i, ch in enumerate(chunks):
        TEXT_EMBS.append(embs[i]); TEXT_META.append({'person_id': person_id, 'text': ch})
    return len(chunks)

def search_person_chunks(person_id: str, query: str, k: int = 6) -> List[Dict[str, Any]]:
    if not TEXT_EMBS: return []
    q = stub_text_embed([query])[0]
    scored = []
    for i, emb in enumerate(TEXT_EMBS):
        if TEXT_META[i]['person_id'] != person_id: continue
        s = cosine_similarity(q, emb); scored.append((s, i))
    scored.sort(reverse=True)
    return [{'text': TEXT_META[i]['text'], 'score': float(s)} for s, i in scored[:k]]
