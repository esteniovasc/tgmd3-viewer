from PySide6.QtWidgets import (QWidget, QVBoxLayout, QTabWidget, QLabel, 
                                QScrollArea, QFrame, QHBoxLayout)
from PySide6.QtCore import Qt, QMimeData
import os
from PySide6.QtGui import QDrag, QPixmap
from src.config import SKILLS, ASSETS_DIR

class DraggableLabel(QFrame):
    def __init__(self, index, text, color, icon_path, parent=None):
        super().__init__(parent)
        # Fix payload to include "Index. Name" so TimelineWidget can parse it
        self.skill_text = f"{index}. {text}"
        self.setFrameShape(QFrame.StyledPanel)
        self.setCursor(Qt.PointingHandCursor)
        
        # Determine text color based on background (heuristic)
        text_color = "black" 
        
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {color};
                border-radius: 6px;
                border: 1px solid #333;
            }}
            QLabel {{
                border: none;
                background: transparent;
                color: {text_color};
                font-weight: bold;
                font-size: 14px;
            }}
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)
        
        # Icon
        icon_label = QLabel()
        icon_label.setFixedWidth(40)
        icon_label.setAlignment(Qt.AlignCenter)
        if icon_path and os.path.exists(icon_path):
            pixmap = QPixmap(icon_path)
            icon_label.setPixmap(pixmap.scaled(32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
             icon_label.setText("?")
             
        layout.addWidget(icon_label)
        
        # Separator Line
        line = QFrame()
        line.setFrameShape(QFrame.VLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet("border: 1px solid #000000;")
        line.setFixedWidth(2)
        layout.addWidget(line)
        
        # Text
        text_label = QLabel(f"{index}. {text}")
        layout.addWidget(text_label)
        layout.addStretch()

    def mouseMoveEvent(self, e):
        if e.buttons() == Qt.MouseButton.LeftButton:
            drag = QDrag(self)
            mime = QMimeData()
            mime.setText(self.skill_text)
            drag.setMimeData(mime)
            drag.exec(Qt.DropAction.CopyAction)

class SkillListWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # self.setFixedWidth(350) # Removido para permitir layout responsivo 70/30

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Abas
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane { border: 0; background: #252526; }
            QTabBar::tab { background: #333; color: #BBB; padding: 10px 20px; }
            QTabBar::tab:selected { background: #3F51B5; color: white; } 
        """)

        # --- Aba 1: Rótulos (Lista de Habilidades para Arrastar) ---
        tab_labels = self._create_labels_tab()
        self.tabs.addTab(tab_labels, "🏷️ Rótulos")

        # --- Aba 2: Lista de Rotulações (Editor de Lista) ---
        tab_list = self._create_list_tab()
        self.tabs.addTab(tab_list, "📋 Lista de Rotulações")

        layout.addWidget(self.tabs)

    def _create_labels_tab(self):
        container = QWidget()
        layout = QVBoxLayout(container)
        
        header = QLabel("HABILIDADES")
        header.setStyleSheet("background: white; color: black; font-weight: bold; padding: 5px; border-radius: 4px;")
        layout.addWidget(header)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setSpacing(10)

        icon_files = [
            "1-correr.png", "2-galopar.png", "3-saltar.png", "4-saltitar.png",
            "5-saltar-horizontal.png", "6-deslizar.png", "7-rebater2maos.png", 
            "8-rebater1mao.png", "9-quicar.png", "10-pegar.png", "11-chutar.png",
            "13-lançar-por-baixo.png", "12-arremessar-por-cima.png"
        ]

        for i, skill in enumerate(SKILLS):
            # Simula o botão colorido (Laranja para 1-6, Azul para 7-13)
            # 1-6 (indexes 0-5) -> Laranja
            # 7-13 (indexes 6-12) -> Azul
            color = "#FF9800" if i < 6 else "#00BCD4"
            
            icon_name = icon_files[i] if i < len(icon_files) else ""
            icon_path = os.path.join(ASSETS_DIR, "icones_habilidades", icon_name)
            
            # Pass 1-based index for display
            btn = DraggableLabel(i+1, skill, color, icon_path)
            content_layout.addWidget(btn)
        
        content_layout.addStretch()
        scroll.setWidget(content)
        layout.addWidget(scroll)
        return container

    def _create_list_tab(self):
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.addWidget(QLabel("Lista de Rotulações por Vídeo..."))
        layout.addStretch()
        return container