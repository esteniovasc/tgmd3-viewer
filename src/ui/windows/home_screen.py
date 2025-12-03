import json
import os
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QFrame, QListWidget, QListWidgetItem, 
                               QFileDialog, QDialog, QGraphicsDropShadowEffect)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QColor, QFont, QCursor, QIcon, QPixmap

from src.ui.utils_ui import DraggableMixin
from src.core.settings_manager import SettingsManager
from src.config import ASSETS_DIR

# --- Dialogo de Info (Mantido igual) ---
class InfoDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Popup)
        self.setStyleSheet("background-color: #0D2C5C; border: 1px solid #FFF; border-radius: 10px;")
        layout = QVBoxLayout(self)
        lbl = QLabel("Desenvolvido no Laboratório de\nAprendizagem de Máquina e\nProjetos Inovadores (LAMPI)")
        lbl.setStyleSheet("color: white; font-size: 14px; padding: 20px;")
        lbl.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl)
    
    def mousePressEvent(self, event):
        self.close()

# --- Widget de Item Recente (Mantido igual) ---
class RecentItemWidget(QWidget):
    def __init__(self, name, full_path):
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        
        lbl_icon = QLabel("📁") 
        lbl_icon.setStyleSheet("font-size: 24px; color: #CCC; margin-right: 10px; background: transparent;")
        
        text_layout = QVBoxLayout()
        lbl_name = QLabel(name)
        lbl_name.setStyleSheet("font-weight: bold; color: white; font-size: 14px; background: transparent;")
        
        lbl_path = QLabel(full_path)
        lbl_path.setStyleSheet("color: #AAA; font-size: 11px; background: transparent;")
        
        text_layout.addWidget(lbl_name)
        text_layout.addWidget(lbl_path)
        
        lbl_filename = QLabel(os.path.basename(full_path))
        lbl_filename.setStyleSheet("color: #007ACC; font-size: 12px; font-style: italic; background: transparent;")
        
        layout.addWidget(lbl_icon)
        layout.addLayout(text_layout)
        layout.addStretch()
        layout.addWidget(lbl_filename)
        
        self.setStyleSheet("background-color: transparent;")

class HomeScreen(DraggableMixin, QWidget):
    create_project_clicked = Signal()
    open_project_loaded = Signal(str, dict)

    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(1000, 650)
        
        self.settings = SettingsManager()

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        # Container Principal (Vidro Escuro)
        self.container = QFrame()
        self.container.setStyleSheet("""
            QFrame {
                background-color: rgba(13, 44, 92, 0.95); /* A cor que você pediu */
                border-radius: 20px;
                border: 1px solid rgba(255, 255, 255, 30);
            }
        """)
        self.main_layout.addWidget(self.container)

        # Layout Interno
        content_layout = QVBoxLayout(self.container)
        content_layout.setContentsMargins(40, 20, 40, 30) # Ajustado margem superior para a barra de título

        # --- 0. BARRA DE TÍTULO CUSTOMIZADA (Botões Minimizar/Fechar) ---
        title_bar_layout = QHBoxLayout()
        title_bar_layout.addStretch() # Empurra botões para a direita

        # Estilo dos botões de janela
        window_btn_style = """
            QPushButton {
                background-color: transparent;
                border: none;
                color: #AAA;
                font-weight: bold;
                font-size: 14px;
                border-radius: 5px;
            }
            QPushButton:hover { background-color: rgba(255, 255, 255, 30); color: white; }
        """
        
        btn_minimize = QPushButton("─")
        btn_minimize.setFixedSize(30, 30)
        btn_minimize.setStyleSheet(window_btn_style)
        btn_minimize.clicked.connect(self.showMinimized) # Função nativa do Qt

        btn_close = QPushButton("✕")
        btn_close.setFixedSize(30, 30)
        # Estilo especial para o fechar (vermelho ao passar o mouse)
        btn_close.setStyleSheet("""
            QPushButton { background-color: transparent; border: none; color: #AAA; font-weight: bold; font-size: 14px; border-radius: 5px; }
            QPushButton:hover { background-color: #C42B1C; color: white; }
        """)
        btn_close.clicked.connect(self.close) # Função nativa do Qt

        title_bar_layout.addWidget(btn_minimize)
        title_bar_layout.addSpacing(5)
        title_bar_layout.addWidget(btn_close)
        
        content_layout.addLayout(title_bar_layout)
        # -------------------------------------------------------------

        # 1. Título
        lbl_title = QLabel("O que você vai fazer hoje?")
        lbl_title.setStyleSheet("font-size: 32px; font-weight: bold; color: white; background: transparent; border: none;")
        content_layout.addWidget(lbl_title)
        
        content_layout.addSpacing(20)

        # 2. Botões de Ação
        btns_layout = QHBoxLayout()
        btns_layout.setSpacing(25)

        self.btn_create = self._create_action_button("CRIAR UM\nPROJETO NOVO", "criar_projeto.png") 
        self.btn_create.clicked.connect(self.emit_create_clicked)
        
        self.btn_open = self._create_action_button("ABRIR UM\nPROJETO EXISTENTE", "abrir_projeto.png") 
        self.btn_open.clicked.connect(self.browse_project)

        btns_layout.addWidget(self.btn_create)
        btns_layout.addWidget(self.btn_open)
        content_layout.addLayout(btns_layout)

        content_layout.addSpacing(30)

        # 3. Seção Recentes
        lbl_recents = QLabel("Recentes:")
        lbl_recents.setStyleSheet("font-size: 18px; color: #DDD; background: transparent; border: none;")
        content_layout.addWidget(lbl_recents)

        self.list_recent = QListWidget()
        self.list_recent.setStyleSheet("""
            QListWidget { background: transparent; border: none; outline: none; }
            QListWidget::item { border-bottom: 1px solid rgba(255,255,255,30); padding: 5px; margin-bottom: 5px; }
            QListWidget::item:hover { background-color: rgba(255, 255, 255, 20); border-radius: 10px; }
        """)
        self.list_recent.itemClicked.connect(self.on_recent_clicked)
        content_layout.addWidget(self.list_recent)
        
        self.refresh_recents()

        # 4. Rodapé
        footer_layout = QHBoxLayout()
        v_layout = QVBoxLayout()
        
        info_row = QHBoxLayout()
        lbl_version = QLabel("TGMD-3 Viewer - versão 0.1")
        lbl_version.setStyleSheet("color: #CCC; font-size: 12px; background: transparent; border: none;")
        
        btn_info = QPushButton("i")
        btn_info.setFixedSize(20, 20)
        btn_info.setCursor(QCursor(Qt.PointingHandCursor))
        btn_info.setStyleSheet("""
            QPushButton { 
                background-color: transparent; 
                border: 2px solid white; 
                border-radius: 10px; 
                color: white; 
                font-weight: bold; 
            }
            QPushButton:hover { background-color: rgba(255,255,255,50); }
        """)
        btn_info.clicked.connect(self.show_info)
        
        info_row.addWidget(lbl_version)
        info_row.addWidget(btn_info)
        info_row.addStretch()
        v_layout.addLayout(info_row)
        footer_layout.addLayout(v_layout)
        footer_layout.addStretch()

        for text in ["LAMPI", "GCOMPH"]:
            lbl_logo = QLabel(text)
            lbl_logo.setFixedSize(80, 40)
            lbl_logo.setAlignment(Qt.AlignCenter)
            lbl_logo.setStyleSheet("""
                background-color: rgba(255,255,255,0.2); 
                border-radius: 8px; 
                color: white; 
                font-weight: bold;
            """)
            footer_layout.addWidget(lbl_logo)
            footer_layout.addSpacing(10)

        content_layout.addLayout(footer_layout)

    def _create_action_button(self, text, icon_filename):
        container = QPushButton()
        container.setFixedSize(400, 120)
        container.setCursor(QCursor(Qt.PointingHandCursor))
        container.setStyleSheet("""
            QPushButton {
                background-color: rgba(30, 30, 30, 150);
                border: 1px solid rgba(255,255,255,50);
                border-radius: 15px;
            }
            QPushButton:hover {
                background-color: rgba(50, 50, 50, 200);
                border: 1px solid #007ACC;
            }
            QPushButton:pressed {
                background-color: rgba(20, 20, 20, 200);
            }
        """)
        
        layout = QHBoxLayout(container)
        layout.setContentsMargins(20, 10, 20, 10)
        
        lbl_text = QLabel(text)
        lbl_text.setStyleSheet("color: white; font-size: 18px; font-weight: bold; background: transparent; border: none;")
        
        lbl_img = QLabel()
        lbl_img.setAlignment(Qt.AlignCenter)
        lbl_img.setStyleSheet("background: transparent; border: none;")

        icon_path = os.path.join(ASSETS_DIR, icon_filename)
        
        if os.path.exists(icon_path):
            pixmap = QPixmap(icon_path)
            scaled_pixmap = pixmap.scaled(QSize(80, 80), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            lbl_img.setPixmap(scaled_pixmap)
        else:
            lbl_img.setText(icon_filename) 
            lbl_img.setStyleSheet("font-size: 50px; color: white; background: transparent; border: none;")
        
        layout.addWidget(lbl_text, 1)
        layout.addWidget(lbl_img, 1)
        
        return container

    # ... (refresh_recents, browse_project, on_recent_clicked, load_and_emit, emit_create_clicked, show_info permanecem iguais) ...
    def refresh_recents(self):
        self.list_recent.clear()
        recents = self.settings.get_recents()
        for item in recents:
            name = item.get('name', 'Sem Nome')
            path = item.get('path', '')
            list_item = QListWidgetItem(self.list_recent)
            list_item.setSizeHint(QSize(0, 60))
            widget = RecentItemWidget(name, path)
            self.list_recent.setItemWidget(list_item, widget)
            list_item.setData(Qt.UserRole, path)

    def browse_project(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Abrir Projeto", "", "TGMD Project (*.json)")
        if file_path:
            self.load_and_emit(file_path)

    def on_recent_clicked(self, item):
        path = item.data(Qt.UserRole)
        if os.path.exists(path):
            self.load_and_emit(path)
        else:
            print(f"Arquivo não encontrado: {path}")

    def load_and_emit(self, path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if "infoProjeto" in data:
                project_name = data["infoProjeto"].get("nome", "Sem Nome")
                self.settings.add_recent(project_name, path)
                self.open_project_loaded.emit(path, data)
            else:
                print("JSON inválido: Schema incorreto")
        except Exception as e:
            print(f"Erro ao abrir projeto: {e}")

    def emit_create_clicked(self):
        self.create_project_clicked.emit()
        self.close()

    def show_info(self):
        dlg = InfoDialog(self)
        dlg.move(QCursor.pos())
        dlg.exec()