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
        self.stack.addWidget(self.video_container) # Index 1
        
        # --- Página 2: Loading (Dedicada) ---
        self.loading_page = QWidget()
        self.loading_page.setStyleSheet("background-color: #000; border-radius: 8px;")
        load_layout = QVBoxLayout(self.loading_page)
        load_layout.setAlignment(Qt.AlignCenter)
        
        self.lbl_loading = QLabel("Carregando...")
        self.lbl_loading.setStyleSheet("color: white; font-size: 24px; font-weight: bold;")
        load_layout.addWidget(self.lbl_loading)
        
        spinner_placeholder = QLabel("⏳") # Futuro: QMovie
        spinner_placeholder.setStyleSheet("color: #007ACC; font-size: 48px;")
        spinner_placeholder.setAlignment(Qt.AlignCenter)
        load_layout.addWidget(spinner_placeholder)
        
        self.stack.addWidget(self.loading_page) # Index 2

        # Mídia Player
        self.player = QMediaPlayer()
        self.audio = QAudioOutput()
        self.player.setAudioOutput(self.audio)
        self.player.setVideoOutput(self.video_surface)
        self.audio.setVolume(0)

        # Inicia no estado zero
        self.stack.setCurrentIndex(0)

    def resizeEvent(self, event):
        super().resizeEvent(event)

    def set_has_video(self, has_video: bool):
        # Se tiver vídeo mas não estiver carregando, vai pro player (1), senão zero (0)
        if self.stack.currentIndex() != 2:
            self.stack.setCurrentIndex(1 if has_video else 0)

    def show_loading(self, message="Carregando..."):
        self.lbl_loading.setText(message)
        self.stack.setCurrentIndex(2)

    def hide_loading(self):
        # Retorna para o Video Player
        self.stack.setCurrentIndex(1)

    def reset(self):
        self.player.stop()
        self.player.setSource(QUrl())
        self.hide_loading()
        self.set_has_video(False)

    def load_video(self, file_path):
        self.player.setSource(QUrl.fromLocalFile(file_path))

    def play(self):
        self.player.play()

    def pause(self):
        self.player.pause()

    def toggle_play(self):
        if self.player.playbackState() == QMediaPlayer.PlayingState:
            self.player.pause()
        else:
            self.player.play()

    def set_position(self, position):
        self.player.setPosition(position)
        
    def get_duration(self):
        return self.player.duration()