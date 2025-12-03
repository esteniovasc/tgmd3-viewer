from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QFrame, QSlider)
from PySide6.QtCore import Qt
from PySide6.QtMultimediaWidgets import QVideoWidget

class VideoPlayerWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(5)

        # 1. Área do Vídeo
        self.video_surface = QVideoWidget()
        self.video_surface.setStyleSheet("background-color: black; border-radius: 8px;")
        # Placeholder visual enquanto não tem vídeo
        self.video_surface.setMinimumHeight(400) 
        main_layout.addWidget(self.video_surface)

        # 2. Barra de Controles e Exportação
        controls_container = QWidget()
        controls_layout = QHBoxLayout(controls_container)
        controls_layout.setContentsMargins(0, 5, 0, 5)

        # --- Grupo Esquerda (IA e Undo) ---
        grp_left = self._create_button_group(["🏃 IA", "✅ Check", "↩", "↪"])
        controls_layout.addWidget(grp_left)
        
        controls_layout.addStretch()

        # --- Grupo Centro (Playback) ---
        # Loop, Prev, Play, Next, Time, Speed, Fullscreen
        btn_loop = QPushButton("🔄")
        btn_prev = QPushButton("⏮")
        btn_play = QPushButton("▶")
        btn_play.setFixedSize(40, 40) # Maior
        btn_next = QPushButton("⏭")
        
        lbl_time = QLabel("00:00 / 00:00")
        lbl_time.setStyleSheet("background: #333; color: white; padding: 5px 10px; border-radius: 15px;")
        
        btn_speed = QPushButton("1x")
        btn_full = QPushButton("⛶")
        btn_help = QPushButton("?")
        btn_help.setStyleSheet("background-color: #2196F3; border-radius: 15px;")

        controls_layout.addWidget(btn_loop)
        controls_layout.addWidget(btn_prev)
        controls_layout.addWidget(btn_play)
        controls_layout.addWidget(btn_next)
        controls_layout.addSpacing(10)
        controls_layout.addWidget(lbl_time)
        controls_layout.addSpacing(10)
        controls_layout.addWidget(btn_speed)
        controls_layout.addWidget(btn_full)
        controls_layout.addWidget(btn_help)

        controls_layout.addStretch()

        # --- Grupo Direita (Exportação) ---
        btn_relatorio = QPushButton("📄 Exportar Relatório")
        btn_cortes = QPushButton("🎬 Exportar Cortes")
        # Estilo diferenciado para exportação
        for btn in [btn_relatorio, btn_cortes]:
            btn.setStyleSheet("background-color: #3F51B5; padding: 5px 10px;")
        
        controls_layout.addWidget(btn_relatorio)
        controls_layout.addWidget(btn_cortes)

        main_layout.addWidget(controls_container)

    def _create_button_group(self, labels):
        grp = QFrame()
        grp.setStyleSheet("background: #333; border-radius: 5px;")
        l = QHBoxLayout(grp)
        l.setContentsMargins(2, 2, 2, 2)
        l.setSpacing(2)
        for txt in labels:
            b = QPushButton(txt)
            b.setFixedSize(30, 30)
            b.setStyleSheet("background: transparent; border: none;")
            l.addWidget(b)
        return grp