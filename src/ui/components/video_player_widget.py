from PySide6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QLabel, QStackedLayout, QFrame)
from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtCore import Qt, Signal, QUrl

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
        self.video_layout = QVBoxLayout(self.video_container)
        self.video_layout.setContentsMargins(0, 0, 0, 0)
        
        self.video_surface = QVideoWidget()
        self.video_surface.setStyleSheet("background-color: black; border-radius: 8px;")
        self.video_surface.setMinimumHeight(200) 
        
        self.video_layout.addWidget(self.video_surface)
        
        # Overlay de Loading (Inicialmente escondido)
        self.loading_overlay = QFrame(self.video_container)
        self.loading_overlay.setStyleSheet("background-color: rgba(0, 0, 0, 180); border-radius: 8px;")
        self.loading_overlay.hide()
        
        load_layout = QVBoxLayout(self.loading_overlay)
        load_layout.setAlignment(Qt.AlignCenter)
        self.lbl_loading = QLabel("Carregando...")
        self.lbl_loading.setStyleSheet("color: white; font-size: 18px; font-weight: bold;")
        load_layout.addWidget(self.lbl_loading)

        self.stack.addWidget(self.video_container)
        
        # Mídia Player
        self.player = QMediaPlayer()
        self.audio = QAudioOutput()
        self.player.setAudioOutput(self.audio)
        self.player.setVideoOutput(self.video_surface)
        self.audio.setVolume(0) # Mudo por padrão para performance/requisito

        # Inicia no estado zero
        self.stack.setCurrentIndex(0)

    def resizeEvent(self, event):
        if hasattr(self, 'loading_overlay'):
            self.loading_overlay.resize(self.size())
        super().resizeEvent(event)

    def set_has_video(self, has_video: bool):
        self.stack.setCurrentIndex(1 if has_video else 0)

    def show_loading(self, message="Carregando..."):
        self.lbl_loading.setText(message)
        self.loading_overlay.resize(self.video_container.size())
        self.loading_overlay.show()
        self.loading_overlay.raise_()

    def hide_loading(self):
        self.loading_overlay.hide()

    def load_video(self, file_path):
        self.player.setSource(QUrl.fromLocalFile(file_path))

    def play(self):
        self.player.play()

    def pause(self):
        self.player.pause()

    def set_position(self, position):
        self.player.setPosition(position)
        
    def get_duration(self):
        return self.player.duration()