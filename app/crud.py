# app/crud.py
import json
from sqlalchemy.orm import Session
from . import models

def create_user(db: Session, username: str, email: str) -> models.User:
    user = models.User(username=username, email=email)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def add_face(db: Session, user_id: int, embedding: list, image_path: str = None) -> models.FaceData:
    ejson = json.dumps(embedding)
    face = models.FaceData(user_id=user_id, embedding=ejson, image_path=image_path)
    db.add(face)
    db.commit()
    db.refresh(face)
    return face

def get_user_by_id(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_all_faces(db: Session):
    return db.query(models.FaceData).all()
