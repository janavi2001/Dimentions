try:
    import faiss
    HAS_FAISS=True
except Exception:
    HAS_FAISS=False

def has_faiss()->bool:
    return HAS_FAISS
