# camera_stream.py
import cv2
from flask import Response

class CameraStream:
    def __init__(self, camera_ids):
        self.cams = []
        for cam_id in camera_ids:
            cap = cv2.VideoCapture(cam_id)
            if not cap.isOpened():
                raise RuntimeError(f"Не удалось открыть камеру {cam_id}")
            
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            cap.set(cv2.CAP_PROP_FPS, 30)

            self.cams.append(cap)

    def generate_feed(self, camera_index):
        """Генератор кадров для MJPEG"""
        while True:
            success, frame = self.cams[camera_index].read()
            if not success:
                break
            _, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

    def get_camera_count(self):
        return len(self.cams)

    def release(self):
        for cap in self.cams:
            cap.release()