from PySide6.QtWidgets import (QWidget, QHBoxLayout, QPushButton)
from PySide6.QtCore import Qt

class ExportPanelWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: #1E1E1E;")
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(10)

        btn_relatorio = QPushButton("Exportar relatório")
        btn_relatorio.setStyleSheet("""
            QPushButton {
                background-color: #3F51B5; 
                color: white; 
                border-radius: 5px; 
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #5C6BC0; }
        """)
        
        btn_cortes = QPushButton("Exportar Cortes")
        btn_cortes.setStyleSheet("""
            QPushButton {
                background-color: #3F51B5; 
                color: white; 
                border-radius: 5px; 
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #5C6BC0; }
        """)

        # Ícone de compartilhamento (simulado com texto por enquanto)
        btn_relatorio.setText("Exportar relatório 🔗")
        
        # Ícone de cortes (simulado)
        btn_cortes.setText("🎬 Exportar Cortes")

        layout.addWidget(btn_relatorio)
        layout.addStretch()
        layout.addWidget(btn_cortes)
