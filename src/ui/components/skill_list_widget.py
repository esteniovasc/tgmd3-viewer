from PySide6.QtWidgets import (QWidget, QVBoxLayout, QTabWidget, QLabel, 
                               QScrollArea, QFrame, QHBoxLayout)
from PySide6.QtCore import Qt
from src.config import SKILLS

class SkillListWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(350) # Largura fixa para o painel lateral

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
        
        # --- Aba 3: Filtros ---
        tab_filters = QWidget() # Placeholder
        self.tabs.addTab(tab_filters, "Filtros")

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

        for i, skill in enumerate(SKILLS):
            # Simula o botão colorido (Laranja para 1-6, Azul para 7-13)
            color = "#FF9800" if i < 6 else "#00BCD4"
            btn = QLabel(f"{i+1}. {skill}")
            btn.setStyleSheet(f"""
                background-color: {color}; 
                color: black; 
                font-weight: bold; 
                padding: 15px; 
                border-radius: 8px;
                font-size: 16px;
            """)
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