import numpy as np

def normalize(vec):
    v = np.array(vec, dtype=float)
    n = float(np.linalg.norm(v))
    if n == 0.0:
        return v.tolist()
    return (v / n).tolist()

def cosine_similarity(a, b):
    va = np.array(a, dtype=float); vb = np.array(b, dtype=float)
    na = float(np.linalg.norm(va)); nb = float(np.linalg.norm(vb))
    if na == 0.0 or nb == 0.0:
        return 0.0
    return float((va @ vb) / (na * nb))
