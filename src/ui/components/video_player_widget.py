from PySide6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QLabel, QStackedLayout, QFrame)
from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtCore import Qt, Signal, QUrl

class VideoPlayerWidget(QWidget):
    add_video_clicked = Signal()
    positionChanged = Signal(int)
    durationChanged = Signal(int)
    mediaStatusChanged = Signal(QMediaPlayer.MediaStatus)
    errorOccurred = Signal(object)

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

        # --- Página 3: Erro / Placeholder ---
        self.error_page = QWidget()
        self.error_page.setStyleSheet("background-color: #111; border-radius: 8px;")
        error_layout = QVBoxLayout(self.error_page)
        error_layout.setAlignment(Qt.AlignCenter)
        
        # Tenta carregar imagem logo
        # Import local para evitar circular se config usar widget
        from src.config import ASSETS_DIR
        import os
        logo_path = os.path.join(ASSETS_DIR, "splash_logo.png")
        
        self.lbl_error_icon = QLabel()
        if os.path.exists(logo_path):
             from PySide6.QtGui import QPixmap
             pix = QPixmap(logo_path).scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
             self.lbl_error_icon.setPixmap(pix)
        else:
             self.lbl_error_icon.setText("⚠️")
             self.lbl_error_icon.setStyleSheet("font-size: 48px;")
             
        error_layout.addWidget(self.lbl_error_icon, 0, Qt.AlignCenter)
        
        self.lbl_error_msg = QLabel("Vídeo Indisponível")
        self.lbl_error_msg.setStyleSheet("color: #FF5252; font-size: 16px; margin-top: 10px;")
        error_layout.addWidget(self.lbl_error_msg, 0, Qt.AlignCenter)
        
        self.stack.addWidget(self.error_page) # Index 3

        # Mídia Player
        self.player = QMediaPlayer()
        self.audio = QAudioOutput()
        self.player.setAudioOutput(self.audio)
        self.player.setVideoOutput(self.video_surface)
        self.audio.setVolume(0)
        
        # Conexões
        self.player.positionChanged.connect(self.positionChanged.emit)
        self.player.durationChanged.connect(self.durationChanged.emit)
        self.player.mediaStatusChanged.connect(self.mediaStatusChanged.emit)
        self.player.errorOccurred.connect(self.errorOccurred.emit)

        # Inicia no estado zero
        self.stack.setCurrentIndex(0)

    # ... resizeEvent ...

    def set_has_video(self, has_video: bool):
        # Se tiver vídeo mas não estiver carregando/erro, vai pro player (1), senão zero (0)
        idx = self.stack.currentIndex()
        if idx != 2 and idx != 3:
            self.stack.setCurrentIndex(1 if has_video else 0)

    def show_loading(self, message="Carregando..."):
        self.lbl_loading.setText(message)
        self.stack.setCurrentIndex(2)

    def show_error(self, message="Erro ao carregar vídeo"):
        self.lbl_error_msg.setText(message)
        self.stack.setCurrentIndex(3)

    def hide_loading(self):
        # Se não estiver em erro, volta pro player
        if self.stack.currentIndex() != 3:
            self.stack.setCurrentIndex(1)

    def reset(self):
        self.player.stop()
        self.player.setSource(QUrl())
        self.stack.setCurrentIndex(0) # Força volta pro zero
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