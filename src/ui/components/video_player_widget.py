from PySide6.QtWidgets import (QWidget, QVBoxLayout)
from PySide6.QtMultimediaWidgets import QVideoWidget

class VideoPlayerWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 1. Área do Vídeo (Apenas superfície)
        self.video_surface = QVideoWidget()
        self.video_surface.setStyleSheet("background-color: black; border-radius: 8px;")
        # Placeholder visual enquanto não tem vídeo
        self.video_surface.setMinimumHeight(200) 
        main_layout.addWidget(self.video_surface)