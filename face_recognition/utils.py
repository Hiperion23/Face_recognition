import os
from pathlib import Path
import cv2

def create_user_directory(user_id):
    user_directory = Path(f"face_recognition/known_faces/user_{user_id}")
    user_directory.mkdir(parents=True, exist_ok=True)
    return user_directory

def save_face(image, user_id, face_id):
    user_directory = create_user_directory(user_id)
    face_path = user_directory / f"face_{face_id}.jpg"
    cv2.imwrite(str(face_path), image)
    print(f"Imagen guardada en: {face_path}")
