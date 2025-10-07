# app/services/face_service.py

from sqlalchemy.orm import Session
from app.models import User, FaceData
from pgvector.sqlalchemy import Vector # Used for typing hints

# --- Placeholder for InsightFace Model Initialization ---
# In a real app, the model is initialized here or passed in.
# For now, assume a function that returns the 128-dim vector:
def generate_embedding(image_data: bytes) -> list[float]:
    """
    Placeholder for calling the insightface model (the logic from test_insightface.py).
    It takes an image and returns a 128-dimensional embedding vector.
    """
    # ... Your InsightFace logic goes here ...
    # Example: return [0.123, 0.456, -0.789, ...] (128 floats)
    # Since this is placeholder, let's return a dummy one for structure:
    return [0.0] * 128 


class FaceRecognitionService:
    def __init__(self, db: Session):
        self.db = db

    def enroll_user(self, username: str, email: str, image_data: bytes):
        """
        Registers a new user and stores their face embedding.
        """
        # 1. Generate the face embedding vector
        embedding_vector = generate_embedding(image_data)

        # 2. Create the new User record
        new_user = User(username=username, email=email)
        self.db.add(new_user)
        self.db.flush()  # Flushes the session to get the new_user.id

        # 3. Create the FaceData record linked to the User
        face_data = FaceData(
            user_id=new_user.id,
            embedding=embedding_vector # pgvector handles list -> vector conversion
        )
        self.db.add(face_data)
        self.db.commit()

        return new_user

    def recognize_face(self, image_data: bytes):
        """
        Compares the live face with all stored embeddings.
        """
        # 1. Generate the embedding for the live image
        target_embedding = generate_embedding(image_data)
        
        # 2. Perform a fast vector similarity search using pgvector
        # The '<->' operator calculates the L2 (Euclidean) distance
        match = self.db.query(FaceData).order_by(
            FaceData.embedding.l2_distance(target_embedding)
        ).first()

        # Check if the closest match is below a recognition threshold
        # (You will need to define a threshold value like 0.6)
        # Note: pgvector doesn't return the distance in the object, 
        # so you often query for the distance separately or use raw SQL.
        
        if match: # Replace with distance check in production
            return self.db.query(User).filter(User.id == match.user_id).first()
        
        return None