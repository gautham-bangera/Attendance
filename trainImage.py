# trainImage.py
import cv2
import os
import numpy as np
from PIL import Image

def trainImages():
    """
    Trains LBPH recognizer from images in TrainingImage/
    Filename convention: name.enrollment.num.jpg  (enrollment should be numeric)
    Saves model to TrainingImageLabel/Trainer.yml
    """
    try:
        recognizer = cv2.face.LBPHFaceRecognizer_create()
        detector = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")

        image_paths = [os.path.join("TrainingImage", f) for f in os.listdir("TrainingImage")]
        face_samples = []
        ids = []

        for path in image_paths:
            if not path.lower().endswith(('.jpg', '.png')):
                continue
            img = Image.open(path).convert('L')
            img_np = np.array(img, 'uint8')
            parts = os.path.basename(path).split(".")
            if len(parts) < 3:
                continue
            try:
                enrollment = int(parts[1])
            except Exception:
                continue
            faces = detector.detectMultiScale(img_np)
            for (x,y,w,h) in faces:
                face_samples.append(img_np[y:y+h, x:x+w])
                ids.append(enrollment)

        if not face_samples:
            print("No face images found for training.")
            return "No Images"

        os.makedirs("TrainingImageLabel", exist_ok=True)
        recognizer.train(face_samples, np.array(ids))
        recognizer.write("TrainingImageLabel/Trainer.yml")
        print("Training completed")
        return "OK"
    except Exception as e:
        print("trainImages error:", e)
        return "Error"