# -*- coding: utf-8 -*-
# Time : 2024/12/16 1:06
# Author : lirunsheng
# User : l'r's
# Software: PyCharm
# File : test.py
import time

import cv2
import numpy as np
import os
from PIL import Image, ImageDraw, ImageFont


class FaceRecognition:
    def __init__(self, trainer_path, face_cascade_path, photos_path):
        # Initialize paths
        self.trainer_path = trainer_path
        self.face_cascade_path = face_cascade_path
        self.photos_path = photos_path
        self.names = []
        self.warningtime = 0
        self.recognizer = cv2.face.LBPHFaceRecognizer_create()
        self.load_model()

    def load_model(self):
        """Load the trained face recognizer model."""
        if os.path.exists(self.trainer_path):
            self.recognizer.read(self.trainer_path)
        else:
            print("Trainer file not found!")
        # Load the names of recognized individuals from the photos folder
        self.load_names()

    def load_names(self):
        """Load names from the photos directory."""
        image_paths = [os.path.join(self.photos_path, f) for f in os.listdir(self.photos_path)]
        for image_path in image_paths:
            name = str(os.path.split(image_path)[1].split('.', 2)[1])
            self.names.append(name)

    def cv2ImgAddText(self, img, text, left, top, text_color=(0, 255, 0), text_size=20):
        """Add text to an image."""
        if isinstance(img, np.ndarray):  # Check if the image is an OpenCV type
            img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))

        # Create drawing object
        draw = ImageDraw.Draw(img)
        font_style = ImageFont.truetype("STSONG.TTF", text_size, encoding="utf-8")
        draw.text((left, top), text, text_color, font=font_style)

        return cv2.cvtColor(np.asarray(img), cv2.COLOR_RGB2BGR)

    def face_detect_demo(self, img):
        """Detect faces in the image and recognize them."""
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # Convert to grayscale
        face_detector = cv2.CascadeClassifier(self.face_cascade_path)
        faces = face_detector.detectMultiScale(gray, 1.1, 5, cv2.CASCADE_SCALE_IMAGE, (100, 100), (640, 640))
        # faces = face_detector.detectMultiScale(gray, 1.1, 5, cv2.CASCADE_SCALE_IMAGE)
        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x + w, y + h), color=(0, 0, 255), thickness=2)
            cv2.circle(img, center=(x + w // 2, y + h // 2), radius=w // 2, color=(0, 255, 0), thickness=1)

            # Face recognition
            ids, confidence = self.recognizer.predict(gray[y:y + h, x:x + w])
            print('Label ID:', ids, 'Confidence Score:', confidence)
            label = None
            if confidence > 80:
                self.warningtime += 1
                if self.warningtime > 100:
                    # Handle warning if needed
                    self.warningtime = 0
                label = 'Unknown'
                # cv2.putText(img, 'Unknown', (x + 10, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0), 1)
            else:
                label = self.names[ids - 1]
                img = self.cv2ImgAddText(img, str(self.names[ids - 1]), x + 10, y - 10, (255, 0, 0), 30)
        #     return img, label
        # return None, None
        cv2.imshow('Result', img)

# Usage example
if __name__ == "__main__":
    trainer_path = 'trainer/trainerCat.yml'
    face_cascade_path = r'K:\working\YOLOv5-Lite-master\face_cat\catface-master\data\haarcascades\haarcascade_frontalcatface_extended.xml'
    photos_path = './data/photos/'

    face_recognition = FaceRecognition(trainer_path, face_cascade_path, photos_path)
    # 摄像头检测
    cap = cv2.VideoCapture(0)
    # cap = cv2.VideoCapture(r'K:\BaiduNetdiskDownload\Cats\Cats\5.mp4')
    while True:
        flag, frame = cap.read()
        if not flag:
            break
        time_s = time.time()
        face_recognition.face_detect_demo(frame)
        print(time.time() - time_s)
        if ord(' ') == cv2.waitKey(10):
            break
    # # Example: Read an image from a file
    # img = cv2.imread('test_image.jpg')
    # face_recognition.face_detect_demo(img)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
