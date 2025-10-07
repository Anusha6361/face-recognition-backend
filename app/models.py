# app/models.py
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
# CRITICAL IMPORT: Used for native vector storage in PostgreSQL
from pgvector.sqlalchemy import Vector 
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)

    # Defines the one-to-many relationship: One user can have multiple face data records
    faces = relationship("FaceData", back_populates="user", cascade="all, delete-orphan")

    def to_dict(self):
        return {"id": self.id, "username": self.username, "email": self.email}

    def __repr__(self):
        return f"<User id={self.id} username={self.username}>"


class FaceData(Base):
    __tablename__ = "face_data"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # CRITICAL FIX: The embedding must be stored as a native vector type.
    # Vector(512) specifies a 512-dimensional vector, which is standard for InsightFace.
    embedding = Column(Vector(512), nullable=False)  
    
    image_path = Column(String, nullable=True) # Optional: stores path to original photo file

    user = relationship("User", back_populates="faces")

    def to_dict(self):
        # We exclude the long embedding vector for cleaner API responses
        return {"id": self.id, "user_id": self.user_id, "image_path": self.image_path}