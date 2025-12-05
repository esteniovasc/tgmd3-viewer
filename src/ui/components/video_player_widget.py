from PySide6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QLabel, QStackedLayout)
from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtCore import Qt, Signal

class VideoPlayerWidget(QWidget):
    add_video_clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Layout de Pilha para alternar entre "Vazio" e "Vídeo"
        self.stack = QStackedLayout(self)
        self.stack.setStackingMode(QStackedLayout.StackOne)

        # --- Página 0: Estado Zero (Vazio) ---
        self.empty_page = QWidget()
        self.empty_page.setStyleSheet("background-color: #000; border-radius: 8px;")
        empty_layout = QVBoxLayout(self.empty_page)
        empty_layout.setAlignment(Qt.AlignCenter)
        
        btn_add = QPushButton("Clique aqui para adicionar um vídeo ➕")
        btn_add.setCursor(Qt.PointingHandCursor)
        btn_add.setFixedSize(300, 60)
        btn_add.setStyleSheet("""
            QPushButton { 
                background-color: #333; 
                color: #DDD; 
                font-size: 16px; 
                border: 2px dashed #555; 
                border-radius: 10px;
            }
            QPushButton:hover { 
                background-color: #444; 
                border-color: #007ACC;
                color: white;
            }
        """)
        btn_add.clicked.connect(self.add_video_clicked.emit)
        
        empty_layout.addWidget(btn_add)
        self.stack.addWidget(self.empty_page)

        # --- Página 1: Player de Vídeo ---
        self.video_container = QWidget()
        video_layout = QVBoxLayout(self.video_container)
        video_layout.setContentsMargins(0, 0, 0, 0)
        
        self.video_surface = QVideoWidget()
        self.video_surface.setStyleSheet("background-color: black; border-radius: 8px;")
        self.video_surface.setMinimumHeight(200) 
        
        video_layout.addWidget(self.video_surface)
        self.stack.addWidget(self.video_container)
        
        # Inicia no estado zero
        self.stack.setCurrentIndex(0)

    def set_has_video(self, has_video: bool):
        self.stack.setCurrentIndex(1 if has_video else 0)