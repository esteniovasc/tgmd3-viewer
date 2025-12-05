from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QFrame, QHBoxLayout, QPushButton)
from PySide6.QtCore import Qt, Signal
from src.config import RULER_HEIGHT, ANNOTATION_TRACK_HEIGHT, THUMBNAIL_HEIGHT

class TrackHeaderWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: #252526; border-right: 1px solid #444;")
        
        # Altura deve bater com a TimelineWidget
        # Mas como a TimelineWidget tem altura dinâmica baseada no conteúdo, 
        # aqui vamos fixar as alturas das "faixas" para alinhar.
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 1. Espaço da Régua (Vazio ou Título)
        ruler_header = QLabel("")
        ruler_header.setFixedHeight(RULER_HEIGHT)
        ruler_header.setStyleSheet("border-bottom: 1px solid #444;")
        layout.addWidget(ruler_header)

        # 2. Header da Faixa de Anotações
        ann_header = self._create_track_header("Rótulos", ANNOTATION_TRACK_HEIGHT, "#4CAF50")
        layout.addWidget(ann_header)

        # 3. Header da Faixa de Vídeo
        video_header = self._create_track_header("Vídeo", THUMBNAIL_HEIGHT, "#007ACC")
        layout.addWidget(video_header)

        layout.addStretch()

    video_add_clicked = Signal()
    
    def _create_track_header(self, title, height, color_code):
        frame = QFrame()
        frame.setFixedHeight(height)
        frame.setStyleSheet("border-bottom: 1px solid #333;")
        
        l = QHBoxLayout(frame)
        l.setContentsMargins(5, 0, 5, 0)
        
        # Ícone/Cor
        icon = QLabel("🏷️" if "Rótulos" in title else "🎬")
        l.addWidget(icon)
        
        lbl = QLabel(title)
        lbl.setStyleSheet("color: #DDD; font-weight: bold; font-size: 11px;")
        l.addWidget(lbl)
        
        l.addStretch()
        
        # Botão Adicionar Video (Apenas na track de video)
        if "Vídeo" in title:
            btn_add = QPushButton("+")
            btn_add.setFixedSize(20, 20)
            btn_add.setCursor(Qt.PointingHandCursor)
            btn_add.setFocusPolicy(Qt.NoFocus)
            # Verde sutil para ação positiva
            btn_add.setStyleSheet("""
                QPushButton { background-color: #2E7D32; border: none; color: white; border-radius: 2px; }
                QPushButton:hover { background-color: #388E3C; }
            """)
            btn_add.setToolTip("Adicionar Vídeo")
            btn_add.clicked.connect(self.video_add_clicked.emit)
            l.addWidget(btn_add)
        
        # Botões de controle da faixa (Mute/Lock)
        btn_lock = QPushButton("🔒")
        btn_lock.setFixedSize(20, 20)
        btn_lock.setFocusPolicy(Qt.NoFocus)
        btn_lock.setStyleSheet("background: transparent; border: none; color: #888;")
        l.addWidget(btn_lock)

        return frame
