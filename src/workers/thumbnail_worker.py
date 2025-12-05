import cv2
from PySide6.QtCore import QThread, Signal
from PySide6.QtGui import QImage
from src.config import THUMBNAIL_HEIGHT, THUMBNAIL_INTERVAL_SECONDS

class ThumbnailWorker(QThread):
    # video_path, index, image, video_id (optional, using path for now)
    thumbnail_generated = Signal(str, int, QImage)
    finished = Signal()

    def __init__(self, videos_data):
        super().__init__()
        self.videos_data = videos_data
        self.is_running = True

    def run(self):
        for video in self.videos_data:
            if not self.is_running: break
            
            path = video['caminho']
            duration = video.get('duracao', 0)
            
            cap = cv2.VideoCapture(path)
            if not cap.isOpened():
                continue

            fps = cap.get(cv2.CAP_PROP_FPS)
            if fps <= 0: fps = 30 # Fallback

            time_pos = 0.0
            idx = 0
            
            while time_pos < duration and self.is_running:
                # Set position
                cap.set(cv2.CAP_PROP_POS_MSEC, time_pos * 1000)
                ret, frame = cap.read()
                
                if ret:
                    # Resize mantendo aspect ratio ou fixando altura? 
                    # Fixando altura conforme config
                    h, w, c = frame.shape
                    new_h = THUMBNAIL_HEIGHT
                    scale = new_h / h
                    new_w = int(w * scale)
                    
                    frame_resized = cv2.resize(frame, (new_w, new_h))
                    
                    # Converter para RGB (QImage usa RGB, OpenCV usa BGR)
                    frame_rgb = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)
                    
                    height, width, channel = frame_rgb.shape
                    bytes_per_line = 3 * width
                    q_img = QImage(frame_rgb.data, width, height, bytes_per_line, QImage.Format_RGB888)
                    
                    # Faz uma cópia para evitar problemas de memória com buffer do opencv
                    self.thumbnail_generated.emit(path, idx, q_img.copy())
                
                time_pos += THUMBNAIL_INTERVAL_SECONDS
                idx += 1
                
            cap.release()
            
        self.finished.emit()

    def stop(self):
        self.is_running = False
        self.wait()
