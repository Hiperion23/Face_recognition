import cv2
import mediapipe as mp
import os
import numpy as np
from pathlib import Path
import tkinter as tk
from tkinter import messagebox

mp_face_detection = mp.solutions.face_detection
mp_face_mesh = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils

Path("captured_faces").mkdir(parents=True, exist_ok=True)

def save_face(image, face_id):
    face_path = f"captured_faces/face_{face_id}.jpg"
    cv2.imwrite(face_path, image)
    print(f"Imagen guardada en: {face_path}")

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
    cap = cv2.VideoCapture(0)
    known_face_encodings = []
    known_face_names = []

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
                face_id = len(known_face_names) + 1
                save_face(frame, face_id)
                known_face_names.append(f"Persona {face_id}")
                with mp_face_mesh.FaceMesh(static_image_mode=True) as face_mesh:
                    results = face_mesh.process(rgb_frame)
                    if results.multi_face_landmarks:
                        for face_landmarks in results.multi_face_landmarks:
                            face_encoding = np.array([[(lm.x, lm.y, lm.z) for lm in face_landmarks.landmark]])
                            known_face_encodings.append(face_encoding)
                print("Rostro capturado y guardado.")
            
            elif key & 0xFF == ord('r'):
                name = recognize_faces(frame, known_face_encodings, known_face_names)
                print(f"Reconocimiento: {name}")
            
            elif key & 0xFF == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()

capture_and_recognize()
