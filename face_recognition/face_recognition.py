import cv2
import mediapipe as mp
import numpy as np
import os
from pathlib import Path
import tkinter as tk
from tkinter import messagebox
from pymongo import MongoClient
from bson import ObjectId
from dotenv import load_dotenv
import shutil

load_dotenv()

MONGO_DETAILS = os.getenv("MONGODB_URI")
client = MongoClient(MONGO_DETAILS)
db = client.get_database("Facial")
user_collection = db.get_collection("66632bacbe55d726600a717d")

mp_face_detection = mp.solutions.face_detection
mp_face_mesh = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils

def save_face(image, user_id):
    photo_directory = f"face_recognition/known_faces/user_{user_id}"
    Path(photo_directory).mkdir(parents=True, exist_ok=True)
    face_count = len(os.listdir(photo_directory))
    face_path = f"{photo_directory}/face_{face_count + 1}.jpg"
    cv2.imwrite(face_path, image)
    print(f"Imagen guardada en: {face_path}")

def load_known_faces():
    known_face_encodings = []
    known_face_names = []
    users = user_collection.find()
    for user in users:
        known_face_names.append(f"{user['first_name']} {user['last_name']}")
        face_encoding = np.array(user['face_encoding'])
        known_face_encodings.append(face_encoding)
    return known_face_encodings, known_face_names

def recognize_faces(image, known_face_encodings, known_face_names):
    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    with mp_face_mesh.FaceMesh(static_image_mode=True) as face_mesh:
        results = face_mesh.process(rgb_image)
        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                face_encoding = np.array([[(lm.x, lm.y, lm.z) for lm in face_landmarks.landmark]])
                name = "Desconocido"
                for known_encoding, known_name in zip(known_face_encodings, known_face_names):
                    if np.allclose(known_encoding, face_encoding, atol=0.03):
                        name = known_name
                        show_notification("Rostro reconocido", f"El rostro de {name} ha sido reconocido.")
                        break
                print(f"Rostro reconocido: {name}")
                return name
    return "Desconocido"

def show_notification(title, message):
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    root.after(1000, lambda: root.destroy())
    root.update_idletasks()
    messagebox.showinfo(title, message)
    root.mainloop()

def capture_and_recognize():
    known_face_encodings, known_face_names = load_known_faces()
    cap = cv2.VideoCapture(0)

    with mp_face_detection.FaceDetection(model_selection=1, min_detection_confidence=0.5) as face_detection:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = face_detection.process(rgb_frame)

            if results.detections:
                for detection in results.detections:
                    mp_drawing.draw_detection(frame, detection)

            cv2.imshow('Reconocimiento Facial', frame)

            key = cv2.waitKey(1)
            if key & 0xFF == ord('c'):
                user_id = input("Ingrese el ID del usuario: ")
                save_face(frame, user_id)
                with mp_face_mesh.FaceMesh(static_image_mode=True) as face_mesh:
                    results = face_mesh.process(rgb_frame)
                    if results.multi_face_landmarks:
                        for face_landmarks in results.multi_face_landmarks:
                            face_encoding = np.array([[(lm.x, lm.y, lm.z) for lm in face_landmarks.landmark]])
                            user_collection.update_one(
                                {"_id": ObjectId(user_id)},
                                {"$set": {"face_encoding": face_encoding.tolist()}}
                            )
                print("Rostro capturado y guardado.")

            elif key & 0xFF == ord('r'):
                name = recognize_faces(frame, known_face_encodings, known_face_names)
                print(f"Reconocimiento: {name}")

            elif key & 0xFF == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    capture_and_recognize()
