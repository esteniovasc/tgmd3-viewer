from PySide6.QtWidgets import (QWidget, QHBoxLayout, QPushButton, QLabel, QFrame)
from PySide6.QtCore import Qt

class VideoControlsWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: #1E1E1E;") # Fundo para integrar com a área
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(10)

        # --- Grupo Esquerda (IA e Undo) ---
        grp_left = self._create_button_group(["🏃 IA", "✅ Check", "↩", "↪"])
        layout.addWidget(grp_left)
        
        layout.addStretch()

        # --- Grupo Centro (Playback) ---
        btn_loop = QPushButton("🔄")
        btn_prev = QPushButton("⏮")
        btn_play = QPushButton("▶")
        btn_play.setFixedSize(40, 40)
        btn_play.setStyleSheet("border-radius: 20px; background-color: #EEE; color: black; font-size: 20px;")
        btn_next = QPushButton("⏭")
        
        lbl_time = QLabel("00:10 / 00:45")
        lbl_time.setStyleSheet("background: #333; color: white; padding: 5px 10px; border-radius: 15px;")
        
        btn_speed = QPushButton("⏱") # Icone de relogio
        btn_speed.setStyleSheet("background-color: #2196F3; border-radius: 15px; min-width: 30px;")
        
        btn_full = QPushButton("⛶")
        btn_full.setStyleSheet("background-color: #333; border-radius: 5px; min-width: 30px;")

        btn_help = QPushButton("?")
        btn_help.setStyleSheet("background-color: #2196F3; border-radius: 15px; min-width: 30px; color: white; font-weight: bold;")

        # Estilização básica dos botões de playback
        for btn in [btn_loop, btn_prev, btn_next]:
            btn.setStyleSheet("background: transparent; color: white; font-size: 18px; border: none;")

        layout.addWidget(btn_loop)
        layout.addWidget(btn_prev)
        layout.addWidget(btn_play)
        layout.addWidget(btn_next)
        layout.addSpacing(10)
        layout.addWidget(lbl_time)
        layout.addSpacing(10)
        layout.addWidget(btn_speed)
        layout.addWidget(btn_full)
        layout.addWidget(btn_help)

        layout.addStretch()
        
        # Placeholder para manter simetria ou espaço extra
        dummy = QWidget()
        dummy.setFixedWidth(100)
        layout.addWidget(dummy)

    def _create_button_group(self, labels):
        grp = QFrame()
        grp.setStyleSheet("background: #333; border-radius: 5px;")
        l = QHBoxLayout(grp)
        l.setContentsMargins(2, 2, 2, 2)
        l.setSpacing(2)
        for txt in labels:
            b = QPushButton(txt)
            b.setFixedSize(30, 30)
            b.setStyleSheet("background: transparent; border: none; color: #FFD700;" if "IA" in txt else "background: transparent; border: none; color: white;")
            l.addWidget(b)
        return grp
