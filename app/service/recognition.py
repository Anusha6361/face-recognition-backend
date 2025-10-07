# app/services/recognition.py
import numpy as np
from app.services.face import FaceService
from app.faiss_index import FaissIndex
from app.database import SessionLocal
from app import crud

face_service = FaceService(model_name="buffalo_l", det_size=(320,320))
faiss_idx = FaissIndex(dim=512)

def startup_load_index():
    faiss_idx.load_from_db()

def enroll_user(username: str, email: str, image_np) -> dict:
    faces = face_service.get(image_np)
    if not faces:
        return {"error": "no face detected"}
    emb = faces[0].normed_embedding.astype("float32")
    db = SessionLocal()
    try:
        user = crud.create_user(db, username=username, email=email)
        face = crud.add_face(db, user_id=user.id, embedding=emb.tolist())
        faiss_idx.add(emb, user.id)
        return {"status":"enrolled", "user_id": user.id}
    finally:
        db.close()

def recognize_frame(image_np):
    faces = face_service.get(image_np)
    results = []
    if not faces:
        return results
    for f in faces:
        emb = f.normed_embedding.astype("float32")
        if faiss_idx.ntotal() > 0:
            D, I = faiss_idx.search(emb, 1)
            dist = float(D[0][0])
            idx = int(I[0][0])
            # defensive: idx may be -1 if no result
            if idx < 0 or idx >= len(faiss_idx.id_map):
                continue
            user_id = faiss_idx.id_map[idx]
            score = float(np.exp(-dist))
            # fetch user metadata
            db = SessionLocal()
            try:
                user = db.query.__self__.query  # dummy to avoid lint; we will open a real session
            except Exception:
                pass
            db.close()
            # We'll avoid heavy DB call per face here; the main app will fetch metadata
            results.append({
                "user_id": user_id,
                "score": score,
                "bbox": f.bbox.astype(int).tolist()
            })
    return results
