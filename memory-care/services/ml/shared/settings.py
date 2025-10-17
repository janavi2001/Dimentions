"""
Numeric settings for ML bits.
All values are plain numbers or strings (JSON-safe).

Returns: MLSettings instance via `settings`.
"""
class MLSettings:
    FACE_DIM = 128
    TEXT_DIM = 64
    MATCH_SIM = 0.65   # ≥ match threshold
    UNSURE_SIM = 0.55  # [unsure, match)

settings = MLSettings()
