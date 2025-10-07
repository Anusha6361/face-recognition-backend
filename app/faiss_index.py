# app/faiss_index.py
import faiss
import numpy as np
import json
from typing import List, Tuple
from app.database import SessionLocal
from app.models import FaceData

class FaissIndex:
    def __init__(self, dim: int = 512):
        self.dim = dim
        self.index = faiss.IndexFlatL2(dim)
        self.id_map = []  # parallel list of user_ids (or face ids)
    
    def load_from_db(self):
        """Load embeddings stored as JSON string in FaceData.embedding"""
        db = SessionLocal()
        try:
            rows = db.query(FaceData).all()
            vectors = []
            ids = []
            for r in rows:
                try:
                    vec = np.array(json.loads(r.embedding), dtype='float32')
                    if vec.shape[0] != self.dim:
                        continue
                    vectors.append(vec)
                    ids.append(r.user_id)
                except Exception:
                    continue
            if vectors:
                arr = np.vstack(vectors).astype('float32')
                self.index.add(arr)
                self.id_map.extend(ids)
        finally:
            db.close()

    def add(self, vec: np.ndarray, user_id: int):
        """Add single vector and user_id mapping"""
        vec = vec.astype('float32').reshape(1, -1)
        self.index.add(vec)
        self.id_map.append(user_id)

    def search(self, vec: np.ndarray, k: int = 1) -> Tuple[np.ndarray, np.ndarray]:
        vec = vec.astype('float32').reshape(1, -1)
        D, I = self.index.search(vec, k)
        return D, I

    def ntotal(self) -> int:
        return self.index.ntotal
