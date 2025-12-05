from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QFrame, QMessageBox
from PySide6.QtCore import Qt, Signal, QDateTime
from PySide6.QtGui import QIcon

class TopBar(QFrame):
    save_clicked = Signal()
    home_clicked = Signal()
    settings_clicked = Signal()
    exit_clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(60) # Aumentei um pouco para caber as duas linhas de texto
        self.setStyleSheet("background-color: #2D2D30; border-bottom: 1px solid #444;")
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 0, 15, 0)
        layout.setSpacing(15)

        # --- ESQUERDA ---
        # Botão Home
        self.btn_home = QPushButton("🏠") # Placeholder
        self.btn_home.setFixedSize(40, 40)
        self.btn_home.setCursor(Qt.PointingHandCursor)
        self.btn_home.setStyleSheet("""
            QPushButton { background-color: transparent; border: none; font-size: 24px; }
            QPushButton:hover { background-color: #3E3E42; border-radius: 5px; }
        """)
        self.btn_home.clicked.connect(self.on_home_click)
        layout.addWidget(self.btn_home)

        layout.addStretch()

        # --- CENTRO ---
        center_container = QWidget()
        center_layout = QHBoxLayout(center_container)
        center_layout.setContentsMargins(0, 0, 0, 0)
        center_layout.setSpacing(10)

        # Botão Salvar
        self.btn_save = QPushButton("💾") # Placeholder
        self.btn_save.setFixedSize(40, 40)
        self.btn_save.setCursor(Qt.PointingHandCursor)
        self.btn_save.setStyleSheet("""
            QPushButton { background-color: transparent; border: none; font-size: 24px; }
            QPushButton:hover { background-color: #3E3E42; border-radius: 5px; }
        """)
        self.btn_save.clicked.connect(self.on_save_click)
        center_layout.addWidget(self.btn_save)

        # Infos do Projeto (Nome + Data)
        info_widget = QWidget()
        info_layout = QVBoxLayout(info_widget)
        info_layout.setContentsMargins(0, 5, 0, 5)
        info_layout.setSpacing(2)
        info_layout.setAlignment(Qt.AlignCenter)

        self.lbl_project_name = QLabel("Nome do Projeto")
        self.lbl_project_name.setStyleSheet("font-weight: bold; color: white; font-size: 16px;")
        self.lbl_project_name.setAlignment(Qt.AlignCenter)
        
        self.lbl_last_saved = QLabel("Última modificação salva às --:-- ✅")
        self.lbl_last_saved.setStyleSheet("color: #888; font-size: 12px;")
        self.lbl_last_saved.setAlignment(Qt.AlignCenter)

        info_layout.addWidget(self.lbl_project_name)
        info_layout.addWidget(self.lbl_last_saved)

        center_layout.addWidget(info_widget)

        layout.addWidget(center_container)

        layout.addStretch()

        # --- DIREITA ---
        # Botão Config
        self.btn_config = QPushButton("⚙️") # Placeholder
        self.btn_config.setFixedSize(40, 40)
        self.btn_config.setCursor(Qt.PointingHandCursor)
        self.btn_config.setStyleSheet("""
            QPushButton { background-color: transparent; border: none; font-size: 24px; }
            QPushButton:hover { background-color: #3E3E42; border-radius: 5px; }
        """)
        self.btn_config.clicked.connect(self.settings_clicked.emit)
        layout.addWidget(self.btn_config)

        # Separador (Pipe)
        lbl_pipe = QLabel("|")
        lbl_pipe.setStyleSheet("color: #666; font-size: 20px; margin: 0 5px;")
        layout.addWidget(lbl_pipe)

        # Botão Sair
        self.btn_exit = QPushButton("🚪") # Placeholder
        self.btn_exit.setFixedSize(40, 40)
        self.btn_exit.setCursor(Qt.PointingHandCursor)
        self.btn_exit.setStyleSheet("""
            QPushButton { background-color: transparent; border: none; font-size: 24px; }
            QPushButton:hover { background-color: #3E3E42; border-radius: 5px; }
        """)
        self.btn_exit.clicked.connect(self.on_exit_click)
        layout.addWidget(self.btn_exit)

    def set_project_name(self, name):
        self.lbl_project_name.setText(name)

    def set_dirty_state(self, is_dirty):
        current_text = self.lbl_project_name.text()
        if is_dirty:
            if not current_text.startswith("* "):
                self.lbl_project_name.setText(f"* {current_text}")
            self.lbl_last_saved.setText("Alterações não salvas (Pendente) ⚠️")
            self.lbl_project_name.setStyleSheet("font-weight: bold; color: #FFD700; font-size: 16px;") # Dourado para alerta
        else:
            if current_text.startswith("* "):
                self.lbl_project_name.setText(current_text[2:])
            self.lbl_project_name.setStyleSheet("font-weight: bold; color: white; font-size: 16px;")
            self.update_last_saved()

    def update_last_saved(self):
        current_time = QDateTime.currentDateTime().toString("HH:mm")
        self.lbl_last_saved.setText(f"Última modificação salva às {current_time} ✅")

    def on_home_click(self):
        # A responsabilidade de verificar se pode sair é da Janela Principal
        self.home_clicked.emit()

    def on_save_click(self):
        self.save_clicked.emit()
        # update_last_saved será chamado pelo controller após sucesso

    def on_exit_click(self):
        # A responsabilidade de verificar se pode sair é da Janela Principal
        self.exit_clicked.emit()